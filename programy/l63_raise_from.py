"""Lekce 63 — raise from."""


class UserNotFoundError(Exception):
    pass


def db_lookup(user_id: int) -> dict:
    db = {1: {"jmeno": "Anna"}, 2: {"jmeno": "Bob"}}
    return db[user_id]   # KeyError když chybí


def get_user(user_id: int) -> dict:
    try:
        return db_lookup(user_id)
    except KeyError as e:
        raise UserNotFoundError(f"Uživatel {user_id} neexistuje") from e


def get_user_clean(user_id: int) -> dict:
    try:
        return db_lookup(user_id)
    except KeyError:
        raise UserNotFoundError(f"Uživatel {user_id} neexistuje") from None


def main() -> None:
    for fn in [get_user, get_user_clean]:
        try:
            fn(99)
        except UserNotFoundError as e:
            print(f"❌ {e}")
            print(f"   __cause__:  {e.__cause__}")
            print(f"   __context__: {e.__context__}\n")


if __name__ == "__main__":
    main()
