#!/usr/bin/env python3
"""Train Deep RL portfolio agents on US stock data and export to ONNX.

Run from `api/` directory:
    .venv/bin/python scripts/train_drl.py --universe DOW30 --algo ppo --timesteps 30000

Outputs:
    app/data_files/models/<algo>_<universe>.onnx          ONNX policy
    app/data_files/models/<algo>_<universe>_meta.json     Tickers + obs spec

The runtime API only needs onnxruntime to do inference — no torch / sb3.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# Make `app.*` importable when running from the api/ root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import A2C, DDPG, PPO, SAC, TD3
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.vec_env import DummyVecEnv

from app.data.universe import UNIVERSES
from app.data.fetcher import MarketDataFetcher

LOOKBACK = 20  # days of returns the agent sees as observation
TRAIN_START = date(2015, 1, 1)
TRAIN_END = date(2022, 12, 31)


class PortfolioEnv(gym.Env):
    """Minimal portfolio gym env.

    Observation: a flat vector of the last `lookback` daily returns for each
    of `n_assets`. Shape = (n_assets * lookback,).

    Action: a length-`n_assets` vector in [-1, 1]; softmax normalized to
    portfolio weights summing to 1.

    Reward: portfolio log-return on the next day, minus a small transaction
    cost proportional to weight churn.
    """

    metadata: dict = {}

    def __init__(self, returns: np.ndarray, lookback: int = LOOKBACK, cost_bps: float = 5.0):
        super().__init__()
        self.returns = returns.astype(np.float32)
        self.n_assets = returns.shape[1]
        self.lookback = lookback
        self.cost = cost_bps / 1e4

        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(self.n_assets * lookback,), dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(self.n_assets,), dtype=np.float32
        )

        self.cursor = 0
        self.prev_weights = np.full(self.n_assets, 1.0 / self.n_assets, dtype=np.float32)

    def _observation(self) -> np.ndarray:
        window = self.returns[self.cursor - self.lookback : self.cursor]
        return np.clip(window.reshape(-1), -1.0, 1.0)

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        e = np.exp(x - x.max())
        return e / e.sum()

    def reset(self, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self.cursor = self.lookback
        self.prev_weights = np.full(self.n_assets, 1.0 / self.n_assets, dtype=np.float32)
        return self._observation(), {}

    def step(self, action: np.ndarray):
        weights = self._softmax(np.asarray(action, dtype=np.float32))
        next_returns = self.returns[self.cursor]
        port_ret = float(np.dot(weights, next_returns))

        churn = float(np.abs(weights - self.prev_weights).sum())
        cost = self.cost * churn
        reward = np.log1p(port_ret - cost)
        self.prev_weights = weights

        self.cursor += 1
        done = self.cursor >= len(self.returns) - 1
        return self._observation(), float(reward), done, False, {}


def fetch_returns(tickers: list[str], start: date, end: date) -> tuple[pd.DataFrame, np.ndarray]:
    fetcher = MarketDataFetcher()
    prices = fetcher._from_yfinance(tickers, start, end)
    prices = prices[[t for t in tickers if t in prices.columns]].dropna()
    returns = prices.pct_change().dropna()
    return prices, returns.values


def export_policy_to_onnx(model, n_obs: int, out_path: Path) -> None:
    """Export the deterministic action of an SB3 policy to ONNX."""

    class OnPolicyWrapper(torch.nn.Module):
        """Wraps PPO/A2C policies: forward returns (actions, values, log_probs)."""

        def __init__(self, inner):
            super().__init__()
            self.inner = inner

        def forward(self, obs):
            actions, _, _ = self.inner(obs, deterministic=True)
            return actions

    class OffPolicyActorWrapper(torch.nn.Module):
        """Wraps DDPG/TD3 actor: forward returns deterministic action."""

        def __init__(self, inner):
            super().__init__()
            self.inner = inner

        def forward(self, obs):
            return self.inner(obs)

    class SACActorWrapper(torch.nn.Module):
        """Wraps SAC actor: take the mean action (no sampling)."""

        def __init__(self, actor):
            super().__init__()
            self.actor = actor

        def forward(self, obs):
            return self.actor(obs, deterministic=True)

    policy = model.policy
    policy.eval()
    # Pick the right wrapper based on policy type
    if hasattr(policy, "actor") and hasattr(policy.actor, "mu"):  # DDPG / TD3
        wrapper = OffPolicyActorWrapper(policy.actor)
    elif hasattr(policy, "actor"):  # SAC
        wrapper = SACActorWrapper(policy.actor)
    else:  # PPO / A2C
        wrapper = OnPolicyWrapper(policy)

    dummy = torch.zeros(1, n_obs, dtype=torch.float32)
    torch.onnx.export(
        wrapper,
        dummy,
        out_path.as_posix(),
        input_names=["observation"],
        output_names=["action"],
        dynamic_axes={"observation": {0: "batch"}, "action": {0: "batch"}},
        opset_version=17,
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--universe", default="DOW30", choices=list(UNIVERSES.keys()))
    p.add_argument("--algo", default="ppo", choices=["ppo", "a2c", "ddpg", "sac", "td3"])
    p.add_argument("--timesteps", type=int, default=30000)
    p.add_argument("--start", default=TRAIN_START.isoformat())
    p.add_argument("--end", default=TRAIN_END.isoformat())
    args = p.parse_args()

    tickers = UNIVERSES[args.universe]
    print(f"[train] universe={args.universe}  n_tickers={len(tickers)}  algo={args.algo}")
    print(f"[train] fetching {args.start} → {args.end}")

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    prices, returns_arr = fetch_returns(tickers, start, end)
    actual_tickers = list(prices.columns)
    print(f"[train] got {len(prices)} days, {len(actual_tickers)} tickers")

    env = DummyVecEnv([lambda: PortfolioEnv(returns_arr, lookback=LOOKBACK)])
    n_obs = len(actual_tickers) * LOOKBACK

    print(f"[train] training {args.algo.upper()} for {args.timesteps} timesteps…")
    n_actions = len(actual_tickers)
    if args.algo == "ppo":
        model = PPO("MlpPolicy", env, verbose=0, n_steps=256, batch_size=64, learning_rate=3e-4)
    elif args.algo == "a2c":
        model = A2C("MlpPolicy", env, verbose=0, learning_rate=7e-4)
    elif args.algo == "ddpg":
        noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
        model = DDPG(
            "MlpPolicy", env, verbose=0, learning_rate=1e-3,
            buffer_size=50_000, batch_size=128, action_noise=noise,
        )
    elif args.algo == "sac":
        model = SAC(
            "MlpPolicy", env, verbose=0, learning_rate=3e-4,
            buffer_size=50_000, batch_size=64, learning_starts=100, ent_coef="auto_0.1",
        )
    elif args.algo == "td3":
        noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
        model = TD3(
            "MlpPolicy", env, verbose=0, learning_rate=1e-3,
            buffer_size=50_000, batch_size=100, action_noise=noise,
        )
    else:
        raise ValueError(f"unknown algo {args.algo}")

    model.learn(total_timesteps=args.timesteps, progress_bar=False)
    print("[train] done")

    out_dir = Path(__file__).resolve().parent.parent / "app" / "data_files" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)

    onnx_path = out_dir / f"{args.algo}_{args.universe.lower()}.onnx"
    meta_path = out_dir / f"{args.algo}_{args.universe.lower()}_meta.json"

    print(f"[train] exporting → {onnx_path.name}")
    export_policy_to_onnx(model, n_obs, onnx_path)

    meta_path.write_text(
        json.dumps(
            {
                "algo": args.algo,
                "universe": args.universe,
                "tickers": actual_tickers,
                "lookback": LOOKBACK,
                "obs_dim": n_obs,
                "train_start": args.start,
                "train_end": args.end,
                "timesteps": args.timesteps,
            },
            indent=2,
        )
    )
    print(f"[train] meta → {meta_path.name}")
    print("[train] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
