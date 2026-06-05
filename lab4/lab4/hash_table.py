from enum import Enum
import math


class State(Enum):
    EMPTY = 0
    OCCUPIED = 1
    DELETED = 2


class HashEntry:
    def __init__(self):
        self.state = State.EMPTY
        self.key = None
        self.v = None
        self.h_base = None
        self.data = None
        self.probes = 0


class HashTable:
    def __init__(self, size=20):
        self.size = size
        self.table = [HashEntry() for _ in range(size)]
        self.count = 0
        self.prime = 17

    def _calc_v(self, key):
        return sum(ord(char) for char in key)

    def _hash1(self, v):
        return v % self.size

    def _hash2(self, v):
        step = self.prime - (v % self.prime)
        # Гарантируем взаимную простоту с size
        while math.gcd(step, self.size) != 1:
            step += 1
            if step >= self.size:
                step = 1
        return step

    def insert(self, key, data):
        if self.count >= self.size:
            print(f"Ошибка: таблица уже заполнена")
            return False

        v = self._calc_v(key)
        h_base = self._hash1(v)
        step = self._hash2(v)

        # Проверка существования ключа
        index = h_base
        for i in range(self.size):
            entry = self.table[index]
            if entry.state == State.EMPTY:
                break
            if entry.state == State.OCCUPIED and entry.key == key:
                print(f"Ошибка: Ключ '{key}' уже существует!")
                return False
            index = (h_base + (i + 1) * step) % self.size

        # Поиск места для вставки
        index = h_base
        probes = 0

        while self.table[index].state == State.OCCUPIED:
            probes += 1
            index = (h_base + probes * step) % self.size

        e = self.table[index]
        e.state = State.OCCUPIED
        e.key = key
        e.v = v
        e.h_base = h_base
        e.data = data
        e.probes = probes
        self.count += 1

        if probes > 0:
            print(f"Коллизия! Вставлено с {probes} шагами: '{key}' → '{data}'")
        else:
            print(f"Вставлено: '{key}' → '{data}'")
        return True

    def search(self, key):
        v = self._calc_v(key)
        h_base, step = self._hash1(v), self._hash2(v)
        idx = h_base
        for i in range(self.size):
            entry = self.table[idx]
            if entry.state == State.EMPTY:
                print(f"Ключ '{key}' не найден")
                return None
            if entry.state == State.OCCUPIED and entry.key == key:
                print(f"Найдено: '{entry.key}' → '{entry.data}'")
                print(f"Диагностика: V(K)={entry.v}, h(V)={entry.h_base}, шагов={entry.probes}")
                return entry
            idx = (h_base + (i + 1) * step) % self.size
        print(f"Ключ '{key}' не найден")
        return None

    def update(self, key, new_data):
        entry = self.search(key)
        if entry:
            old_data = entry.data
            entry.data = new_data
            print(f"Обновлено: '{key}' было '{old_data}' → стало '{new_data}'")
            return True
        print(f"Ошибка: Ключ '{key}' не найден для обновления.")
        return False

    def delete(self, key):
        v = self._calc_v(key)
        h_base, step = self._hash1(v), self._hash2(v)
        index = h_base
        for i in range(self.size):
            entry = self.table[index]
            if entry.state == State.EMPTY:
                print(f"Ключ '{key}' не найден")
                return False
            if entry.state == State.OCCUPIED and entry.key == key:
                entry.state = State.DELETED
                entry.key = None
                entry.v = None
                entry.h_base = None
                entry.data = None
                self.count -= 1
                print(f"Удалено: '{key}'")
                return True
            index = (h_base + (i + 1) * step) % self.size
        print(f"Ключ '{key}' не найден")
        return False

    def display(self):
        print("\n" + "-" * 115)
        print(
            f"| {'Индекс':^6} | {'Статус':^8} | {'Ключ (ID)':^15} | {'V(K)':^6} | {'h(V)':^4} | {'Шаги':^4} | {'Данные (Pi)':^45} |")
        print("-" * 115)
        for i in range(self.size):
            e = self.table[i]
            st = e.state.name
            if e.state == State.OCCUPIED:
                print(f"| {i:^6} | {st:^8} | {e.key:<15} | {e.v:^6} | {e.h_base:^4} | {e.probes:^4} | {e.data:<45} |")
            else:
                print(f"| {i:^6} | {st:^8} | {'---':^15} | {'---':^6} | {'---':^4} | {'---':^4} | {'---':<45} |")
        print("-" * 115)
        print(f"Коэффициент заполнения: {self.count / self.size:.2%} | Записей: {self.count}/{self.size}")

    def stats(self):
        print("\nСТАТИСТИКА ХЕШ-ТАБЛИЦЫ:")
        print(f"Размер таблицы: {self.size}")
        print(f"Записей: {self.count}")
        print(f"Коэффициент заполнения: {self.count / self.size:.2%}")

        empty = sum(1 for e in self.table if e.state == State.EMPTY)
        deleted = sum(1 for e in self.table if e.state == State.DELETED)
        print(f"Пустых ячеек: {empty}")
        print(f"Удалённых (tombstone): {deleted}")

    def clear(self):
        self.table = [HashEntry() for _ in range(self.size)]
        self.count = 0
        print("Таблица полностью очищена")