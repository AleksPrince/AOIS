#!/usr/bin/env python
"""Запуск тестов с измерением покрытия кода"""

import subprocess
import sys
import os


def run_coverage():
    """Запускает coverage и выводит отчёт"""

    # Очищаем старые данные
    subprocess.run(["coverage", "erase"])

    # Запускаем тесты с coverage
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ С ИЗМЕРЕНИЕМ ПОКРЫТИЯ")
    print("=" * 60)

    result = subprocess.run(
        ["coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        capture_output=False
    )

    # Выводим отчёт по coverage
    print("\n" + "=" * 60)
    print("ОТЧЁТ О ПОКРЫТИИ КОДА")
    print("=" * 60)

    subprocess.run(["coverage", "report", "-m"])

    # Опционально: создаём HTML отчёт
    subprocess.run(["coverage", "html"])
    print("\nHTML отчёт создан в папке 'htmlcov'")


def run_specific_test(test_file: str):
    """Запускает конкретный тест"""
    subprocess.run([
        "coverage", "run", "-m", "unittest",
        f"tests.{test_file.replace('.py', '')}"
    ])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_specific_test(sys.argv[1])
    else:
        run_coverage()