"""Lekce 36 — vícenásobná dědičnost a mixiny."""

import json


class JsonMixin:
    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)


class ReprMixin:
    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{type(self).__name__}({attrs})"


class LoggableMixin:
    def loguj(self, zprava: str) -> None:
        print(f"[{type(self).__name__}.{self.__dict__.get('jmeno','?')}] {zprava}")


class Pes(JsonMixin, ReprMixin, LoggableMixin):
    def __init__(self, jmeno: str, vek: int):
        self.jmeno = jmeno
        self.vek = vek


def main() -> None:
    rex = Pes("Rex", 5)
    print(rex)
    print(rex.to_json())
    rex.loguj("Štěkám na pošťáka")


if __name__ == "__main__":
    main()
