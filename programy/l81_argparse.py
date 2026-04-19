"""Lekce 81 — argparse subkomandy."""

import argparse


def cmd_add(args):
    print(f"➕ Přidáno: {args.polozka} (priorita {args.priorita})")


def cmd_list(args):
    print("📝 Vše:")
    print("  (zde by byl seznam)")


def cmd_done(args):
    print(f"✅ Hotovo: {args.cislo}")


def main():
    parser = argparse.ArgumentParser(prog="todo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="přidá úkol")
    p_add.add_argument("polozka")
    p_add.add_argument("-p", "--priorita", type=int, default=1)
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="vypíše vše")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="označí hotovo")
    p_done.add_argument("cislo", type=int)
    p_done.set_defaults(func=cmd_done)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
