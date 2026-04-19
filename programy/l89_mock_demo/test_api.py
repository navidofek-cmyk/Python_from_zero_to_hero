"""Lekce 89 — mock demo.

Spuštění:
    pytest l89_mock_demo/test_api.py -v
"""

from unittest.mock import patch, MagicMock


def test_stahni_pocasi():
    with patch("api.requests") as mock_req:
        mock_req.get.return_value.json.return_value = {"teplota": 20}

        from api import stahni_pocasi
        vysledek = stahni_pocasi("Praha")

        assert vysledek == {"teplota": 20}
        mock_req.get.assert_called_once()


def test_monkeypatch_env(monkeypatch):
    import os
    monkeypatch.setenv("API_KEY", "test123")
    assert os.environ["API_KEY"] == "test123"
