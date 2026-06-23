from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

import pandas as pd


class Strategy(StrEnum):
    EQUAL_WEIGHT = "equal_weight"
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    HRP = "hrp"
    DRL_PPO = "drl_ppo"
    DRL_DDPG = "drl_ddpg"
    DRL_A2C = "drl_a2c"
    DRL_SAC = "drl_sac"
    DRL_TD3 = "drl_td3"


@dataclass(frozen=True)
class OptimizerResult:
    strategy: str
    weights: dict[str, float]
    expected_annual_return: float | None
    expected_annual_volatility: float | None
    expected_sharpe: float | None
    notes: str | None = None


class Optimizer(Protocol):
    name: str

    def fit(self, prices: pd.DataFrame) -> OptimizerResult: ...
