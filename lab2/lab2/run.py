#!/usr/bin/env python
#coverage run tests_minimal.py  coverage run --append tests_extra.py coverage report -m

"""Точка входа в программу"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from analyzer import BooleanAnalyzer


def print_welcome():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    АНАЛИЗАТОР БУЛЕВЫХ ФУНКЦИЙ                        ║
║                            Версия 4.2.1                             ║
╠══════════════════════════════════════════════════════════════════════╣
║  Операции: & (И), | (ИЛИ), ! (НЕ), -> (→), ~ (≡)                     ║
║  Переменные: a, b, c, d, e (до 5)                                    ║
║  Пример: !(!a->!b)|c                                                 ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print_welcome()
    analyzer = BooleanAnalyzer()

    if len(sys.argv) > 1:
        expr = ' '.join(sys.argv[1:])
        print(f"\nВыражение: {expr}")
        analyzer.analyze(expr)
    else:
        print("\nВведите 'exit' для выхода, 'test' для теста\n")
        while True:
            try:
                expr = input(">>> ").strip()
                if expr.lower() == 'exit':
                    print("\nДо свидания!")
                    break
                elif expr.lower() == 'test':
                    expr = "!(!a->!b)|c"
                    print(f"\nТест: {expr}")
                    analyzer.analyze(expr)
                elif expr:
                    analyzer.analyze(expr)
            except (KeyboardInterrupt, EOFError):
                print("\n\nДо свидания!")
                break


if __name__ == "__main__":
    main()