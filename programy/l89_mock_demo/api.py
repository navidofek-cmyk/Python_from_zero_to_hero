"""Modul co volá externí API — k mockování."""


def stahni_pocasi(mesto: str) -> dict:
    import requests   # pomalá závislost
    r = requests.get(f"https://api.example.com/weather?city={mesto}")
    return r.json()
