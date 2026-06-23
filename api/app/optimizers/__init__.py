from app.optimizers.base import OptimizerResult, Strategy
from app.optimizers.classical import (
    EqualWeightOptimizer,
    HRPOptimizer,
    MaxSharpeOptimizer,
    MinVolatilityOptimizer,
)
from app.optimizers.drl import DRLReplayOptimizer

CLASSICAL_REGISTRY: dict[str, type] = {
    "equal_weight": EqualWeightOptimizer,
    "max_sharpe": MaxSharpeOptimizer,
    "min_volatility": MinVolatilityOptimizer,
    "hrp": HRPOptimizer,
}

DRL_REGISTRY: dict[str, str] = {
    "drl_ppo": "ppo_test_weights.csv",
    "drl_ddpg": "ddpg_test_weights.csv",
    "drl_a2c": "a2c_test_weights.csv",
    "drl_sac": "sac_test_weights.csv",
    "drl_td3": "td3_test_weights.csv",
}

ALL_STRATEGIES: list[str] = list(CLASSICAL_REGISTRY.keys()) + list(DRL_REGISTRY.keys())

__all__ = [
    "ALL_STRATEGIES",
    "CLASSICAL_REGISTRY",
    "DRL_REGISTRY",
    "DRLReplayOptimizer",
    "OptimizerResult",
    "Strategy",
]
