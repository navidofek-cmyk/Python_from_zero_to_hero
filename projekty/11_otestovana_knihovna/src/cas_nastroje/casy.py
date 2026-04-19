"""Užitečné funkce pro práci s časem."""

from datetime import date, datetime, timedelta


def doba_mezi(od: datetime, do: datetime) -> timedelta:
    """Vrátí kladnou dobu mezi dvěma datetime."""
    return abs(do - od)


def pristi_pondeli(od: date) -> date:
    """Vrátí datum příštího pondělí (NE dnes, i kdyby dnes bylo pondělí)."""
    dni = (7 - od.weekday()) % 7
    if dni == 0:
        dni = 7
    return od + timedelta(days=dni)


def formatuj_dobu(d: timedelta) -> str:
    """Hezký popis: '2h 30m', '5d 3h', '45s'."""
    sek = int(d.total_seconds())
    if sek < 60:
        return f"{sek}s"
    if sek < 3600:
        return f"{sek // 60}m {sek % 60}s"
    if sek < 86400:
        h, zbytek = divmod(sek, 3600)
        return f"{h}h {zbytek // 60}m"
    d_, zbytek = divmod(sek, 86400)
    return f"{d_}d {zbytek // 3600}h"


def je_vikend(d: date) -> bool:
    """True pokud je sobota nebo neděle."""
    return d.weekday() >= 5
