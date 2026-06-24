TICKERS = ["INFY.NS", "TCS.NS", "WIPRO.NS", "HDFCBANK.NS", "RELIANCE.NS"]


def test_optimize_equal_weight(client):
    r = client.post(
        "/api/v1/optimize",
        json={
            "tickers": TICKERS,
            "start": "2020-01-01",
            "end": "2021-12-31",
            "strategies": ["equal_weight"],
            "data_source": "local",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["n_observations"] > 0
    result = body["results"][0]
    assert result["strategy"] == "equal_weight"
    weights = result["weights"]
    assert abs(sum(weights.values()) - 1.0) < 1e-6


def test_optimize_max_sharpe(client):
    r = client.post(
        "/api/v1/optimize",
        json={
            "tickers": TICKERS,
            "start": "2019-01-01",
            "end": "2021-12-31",
            "strategies": ["max_sharpe", "min_volatility", "hrp"],
            "data_source": "local",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["results"]) == 3
    for r_ in body["results"]:
        assert abs(sum(r_["weights"].values()) - 1.0) < 1e-3


def test_optimize_drl_ppo_nifty_replay(client):
    """Legacy NIFTY-20 DRL replay (precomputed action CSV)."""
    r = client.post(
        "/api/v1/optimize",
        json={
            "tickers": [
                "ASIANPAINT.NS", "CIPLA.NS", "DRREDDY.NS", "GAIL.NS", "GRASIM.NS",
                "HDFCBANK.NS", "HEROMOTOCO.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS",
                "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "POWERGRID.NS",
                "SUNPHARMA.NS", "TATACHEM.NS", "TCS.NS", "ULTRACEMCO.NS", "WIPRO.NS",
            ],
            "start": "2021-03-01",
            "end": "2023-12-31",
            "strategies": ["drl_ppo_nifty"],
            "data_source": "local",
        },
    )
    assert r.status_code == 200, r.text
    result = r.json()["results"][0]
    assert result["strategy"] == "drl_ppo_nifty"
    assert len(result["weights"]) > 0


def test_optimize_validation_errors(client):
    r = client.post(
        "/api/v1/optimize",
        json={
            "tickers": ["INFY.NS"],
            "start": "2020-01-01",
            "end": "2020-12-31",
            "strategies": ["equal_weight"],
            "data_source": "local",
        },
    )
    assert r.status_code == 422

    r = client.post(
        "/api/v1/optimize",
        json={
            "tickers": TICKERS,
            "start": "2021-01-01",
            "end": "2020-01-01",
            "strategies": ["equal_weight"],
            "data_source": "local",
        },
    )
    assert r.status_code == 422
