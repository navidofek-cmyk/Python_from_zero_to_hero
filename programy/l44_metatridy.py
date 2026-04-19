"""Lekce 44 — __init_subclass__ jako lepší alternativa metatříd."""


class Plugin:
    plugins: list[type] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.plugins.append(cls)
        print(f"📦 Registruji plugin: {cls.__name__}")

    def start(self) -> None:
        raise NotImplementedError


class CronPlugin(Plugin):
    def start(self):
        print("⏰ Cron běží")


class HttpPlugin(Plugin):
    def start(self):
        print("🌐 HTTP server běží")


def main() -> None:
    print(f"\nVšechny pluginy: {[p.__name__ for p in Plugin.plugins]}")
    for p in Plugin.plugins:
        p().start()

    # Dynamické vytvoření třídy
    NovyPlugin = type("NovyPlugin", (Plugin,), {"start": lambda self: print("dyn")})
    NovyPlugin().start()


if __name__ == "__main__":
    main()
