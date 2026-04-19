"""Lekce 43 — deskriptor."""


class TypedField:
    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} musí být {self.expected_type.__name__}, "
                f"dostal {type(value).__name__}"
            )
        instance.__dict__[self.name] = value


class Pes:
    jmeno = TypedField(str)
    vek = TypedField(int)


def main() -> None:
    rex = Pes()
    rex.jmeno = "Rex"
    rex.vek = 5
    print(f"Rex: {rex.jmeno}, {rex.vek} let")

    try:
        rex.vek = "pět"
    except TypeError as e:
        print(f"❌ {e}")


if __name__ == "__main__":
    main()
