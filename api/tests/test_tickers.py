def test_list_universes(client):
    r = client.get("/api/v1/universes")
    assert r.status_code == 200
    names = {u["name"] for u in r.json()}
    assert {"NIFTY50", "DOW30", "DRL_NIFTY20"}.issubset(names)


def test_get_universe(client):
    r = client.get("/api/v1/universes/NIFTY50")
    assert r.status_code == 200
    assert len(r.json()["tickers"]) > 40


def test_unknown_universe(client):
    r = client.get("/api/v1/universes/FAKE")
    assert r.status_code == 404


def test_list_strategies(client):
    r = client.get("/api/v1/strategies")
    assert r.status_code == 200
    body = r.json()
    assert "max_sharpe" in body
    # Live DRL trained on US data (PPO on Dow 30)
    assert "drl_ppo_dow30" in body
    # Legacy NIFTY replay
    assert "drl_ppo_nifty" in body
