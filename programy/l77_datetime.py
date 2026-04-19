"""Lekce 77 — datetime, zoneinfo."""

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo


def main() -> None:
    narozen = date(2014, 5, 10)
    dni = (date.today() - narozen).days
    print(f"Žiješ už {dni} dní (~{dni/365:.1f} let)")

    print("\nČasové zóny:")
    teď_utc = datetime.now(ZoneInfo("UTC"))
    for zona in ["Europe/Prague", "America/New_York", "Asia/Tokyo"]:
        local = teď_utc.astimezone(ZoneInfo(zona))
        print(f"  {zona:25s}: {local.strftime('%Y-%m-%d %H:%M %Z')}")

    print("\nTimedelta:")
    zitra = date.today() + timedelta(days=1)
    pristi_tyden = date.today() + timedelta(weeks=1)
    print(f"  Zítra:        {zitra}")
    print(f"  Příští týden: {pristi_tyden}")


if __name__ == "__main__":
    main()
