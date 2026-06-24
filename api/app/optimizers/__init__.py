from app.optimizers.base import OptimizerResult, Strategy
from app.optimizers.classical import (
    EqualWeightOptimizer,
    HRPOptimizer,
    MaxSharpeOptimizer,
    MinVolatilityOptimizer,
)
from app.optimizers.drl import DRLReplayOptimizer, LiveDRLOptimizer, list_live_models

CLASSICAL_REGISTRY: dict[str, type] = {
    "equal_weight": EqualWeightOptimizer,
    "max_sharpe": MaxSharpeOptimizer,
    "min_volatility": MinVolatilityOptimizer,
    "hrp": HRPOptimizer,
}

# Legacy NIFTY-20 DRL replay (precomputed action CSVs from the undergrad capstone)
DRL_REPLAY_REGISTRY: dict[str, str] = {
    "drl_ppo_nifty": "ppo_test_weights.csv",
    "drl_ddpg_nifty": "ddpg_test_weights.csv",
    "drl_a2c_nifty": "a2c_test_weights.csv",
    "drl_sac_nifty": "sac_test_weights.csv",
    "drl_td3_nifty": "td3_test_weights.csv",
}

# Real-time DRL inference via ONNX (trained on US data 2015-2022)
# Maps user-facing strategy id → ONNX model file stem
DRL_LIVE_REGISTRY: dict[str, str] = {
    "drl_ppo_dow30": "ppo_dow30",
    "drl_a2c_dow30": "a2c_dow30",
    "drl_ppo_mag7": "ppo_mag7",
    "drl_a2c_mag7": "a2c_mag7",
}


def _available_live() -> dict[str, str]:
    """Filter the live registry to only what's actually on disk."""
    on_disk = set(list_live_models())
    return {k: v for k, v in DRL_LIVE_REGISTRY.items() if v in on_disk}


AVAILABLE_LIVE_DRL: dict[str, str] = _available_live()

ALL_STRATEGIES: list[str] = (
    list(CLASSICAL_REGISTRY.keys())
    + list(AVAILABLE_LIVE_DRL.keys())
    + list(DRL_REPLAY_REGISTRY.keys())
)

# Map of DRL strategy id → the universe key it was trained on (UI filter)
DRL_STRATEGY_UNIVERSE: dict[str, str] = {
    "drl_ppo_dow30": "DOW30",
    "drl_a2c_dow30": "DOW30",
    "drl_ppo_mag7": "MAG7",
    "drl_a2c_mag7": "MAG7",
    "drl_ppo_nifty": "DRL_NIFTY20",
    "drl_ddpg_nifty": "DRL_NIFTY20",
    "drl_a2c_nifty": "DRL_NIFTY20",
    "drl_sac_nifty": "DRL_NIFTY20",
    "drl_td3_nifty": "DRL_NIFTY20",
}

__all__ = [
    "ALL_STRATEGIES",
    "AVAILABLE_LIVE_DRL",
    "CLASSICAL_REGISTRY",
    "DRL_LIVE_REGISTRY",
    "DRL_REPLAY_REGISTRY",
    "DRL_STRATEGY_UNIVERSE",
    "DRLReplayOptimizer",
    "LiveDRLOptimizer",
    "OptimizerResult",
    "Strategy",
]
