# main.py
from __future__ import annotations
import os
import argparse

from benchmark import BenchmarkLauncher
# from txtfx import tstream



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bench",
        action="store_true",
        help="Ejecutar el benchmark de modelos",
    )
    parser.set_defaults(mode="manual")
    return parser

def resolve_mode(args: argparse.Namespace) -> str:
    if args.bench:
        return "bench"

def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    parser = build_parser()
    args = parser.parse_args()
    mode = resolve_mode(args)
    


    if mode == "bench":
        try:
            BenchmarkLauncher().launch()
        except ImportError as exc:
            print(f"Error al ejecutar el benchmark: {exc}")
            print("El benchmark no está instalado o configurado correctamente.")
        return



if __name__ == "__main__":
    main()