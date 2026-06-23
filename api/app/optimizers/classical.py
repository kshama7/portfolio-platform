from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, HRPOpt, expected_returns, risk_models

from app.optimizers.base import OptimizerResult

warnings.filterwarnings("ignore", category=UserWarning, module="pypfopt")


class EqualWeightOptimizer:
    name = "equal_weight"

    def fit(self, prices: pd.DataFrame) -> OptimizerResult:
        cols = prices.columns.tolist()
        n = len(cols)
        w = {c: 1.0 / n for c in cols}
        returns = prices.pct_change().dropna()
        port_ret = returns.dot(pd.Series(w))
        ann_return = float(port_ret.mean() * 252)
        ann_vol = float(port_ret.std() * np.sqrt(252))
        sharpe = float(ann_return / ann_vol) if ann_vol > 0 else 0.0
        return OptimizerResult(
            strategy=self.name,
            weights=w,
            expected_annual_return=ann_return,
            expected_annual_volatility=ann_vol,
            expected_sharpe=sharpe,
        )


class _PyPfOptBase:
    name = ""

    def _build_inputs(self, prices: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
        mu = expected_returns.mean_historical_return(prices)
        sigma = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
        return mu, sigma

    def _clean(self, raw: dict[str, float]) -> dict[str, float]:
        total = sum(raw.values())
        if total <= 0:
            return raw
        return {k: float(v / total) for k, v in raw.items()}


class MaxSharpeOptimizer(_PyPfOptBase):
    name = "max_sharpe"

    def fit(self, prices: pd.DataFrame) -> OptimizerResult:
        mu, sigma = self._build_inputs(prices)
        ef = EfficientFrontier(mu, sigma, weight_bounds=(0, 1))
        ef.max_sharpe(risk_free_rate=0.02)
        weights = self._clean(dict(ef.clean_weights()))
        perf = ef.portfolio_performance(verbose=False, risk_free_rate=0.02)
        return OptimizerResult(
            strategy=self.name,
            weights=weights,
            expected_annual_return=float(perf[0]),
            expected_annual_volatility=float(perf[1]),
            expected_sharpe=float(perf[2]),
        )


class MinVolatilityOptimizer(_PyPfOptBase):
    name = "min_volatility"

    def fit(self, prices: pd.DataFrame) -> OptimizerResult:
        mu, sigma = self._build_inputs(prices)
        ef = EfficientFrontier(mu, sigma, weight_bounds=(0, 1))
        ef.min_volatility()
        weights = self._clean(dict(ef.clean_weights()))
        perf = ef.portfolio_performance(verbose=False, risk_free_rate=0.02)
        return OptimizerResult(
            strategy=self.name,
            weights=weights,
            expected_annual_return=float(perf[0]),
            expected_annual_volatility=float(perf[1]),
            expected_sharpe=float(perf[2]),
        )


class HRPOptimizer:
    name = "hrp"

    def fit(self, prices: pd.DataFrame) -> OptimizerResult:
        returns = prices.pct_change().dropna()
        hrp = HRPOpt(returns)
        hrp.optimize()
        weights = {k: float(v) for k, v in hrp.clean_weights().items()}
        port_ret = returns.dot(pd.Series(weights))
        ann_return = float(port_ret.mean() * 252)
        ann_vol = float(port_ret.std() * np.sqrt(252))
        sharpe = float(ann_return / ann_vol) if ann_vol > 0 else 0.0
        return OptimizerResult(
            strategy=self.name,
            weights=weights,
            expected_annual_return=ann_return,
            expected_annual_volatility=ann_vol,
            expected_sharpe=sharpe,
        )
