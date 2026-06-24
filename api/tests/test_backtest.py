TICKERS = ["INFY.NS", "TCS.NS", "WIPRO.NS", "HDFCBANK.NS", "RELIANCE.NS"]


def test_backtest_equal_weight(client):
    r = client.post(
        "/api/v1/backtest",
        json={
            "tickers": TICKERS,
            "start": "2019-01-01",
            "end": "2021-12-31",
            "strategies": ["equal_weight"],
            "data_source": "local",
            "initial_capital": 100000,
        },
    )
    assert r.status_code == 200, r.text
    res = r.json()["results"][0]
    assert len(res["equity_curve"]) > 100
    assert res["metrics"]["n_periods"] > 100
    assert res["equity_curve"][0] == 100000  # day 0 = initial capital


def test_backtest_multi_strategy(client):
    r = client.post(
        "/api/v1/backtest",
        json={
            "tickers": TICKERS,
            "start": "2019-01-01",
            "end": "2021-12-31",
            "strategies": ["equal_weight", "max_sharpe", "hrp"],
            "data_source": "local",
        },
    )
    assert r.status_code == 200, r.text
    results = r.json()["results"]
    assert {r_["strategy"] for r_ in results} == {"equal_weight", "max_sharpe", "hrp"}


def test_backtest_drl_replay_nifty(client):
    """Legacy NIFTY-20 precomputed action replay backtest."""
    drl_tickers = [
        "ASIANPAINT.NS", "CIPLA.NS", "DRREDDY.NS", "GAIL.NS", "GRASIM.NS",
        "HDFCBANK.NS", "HEROMOTOCO.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS",
        "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "POWERGRID.NS",
        "SUNPHARMA.NS", "TATACHEM.NS", "TCS.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    ]
    r = client.post(
        "/api/v1/backtest",
        json={
            "tickers": drl_tickers,
            "start": "2021-03-01",
            "end": "2023-12-31",
            "strategies": ["drl_ppo_nifty"],
            "data_source": "local",
        },
    )
    assert r.status_code == 200, r.text
    res = r.json()["results"][0]
    assert res["strategy"] == "drl_ppo_nifty"
    assert len(res["equity_curve"]) > 100
