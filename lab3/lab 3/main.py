# ============================================================
# ВАРИАНТ 3E9
# АВТОМАТИЧЕСКАЯ МИНИМИЗАЦИЯ КАРТ КАРНО
# ============================================================

from itertools import product

# ============================================================
# ЧАСТЬ 1: ОДС-3 В СКНФ
# ============================================================
print("=" * 80)
print("ЧАСТЬ 1: ОДНОРАЗРЯДНЫЙ ДВОИЧНЫЙ СУММАТОР НА 3 ВХОДА (ОДС-3)")
print("=" * 80)

# --- Таблица истинности ---
print("\n1.1 ТАБЛИЦА ИСТИННОСТИ:")
print("┌───┬───┬─────┬─────┬──────┐")
print("│ A │ B │ Cin │ Sum │ Cout │")
print("├───┼───┼─────┼─────┼──────┤")

table = []
for a, b, cin in product([0, 1], repeat=3):
    s = (a + b + cin) % 2
    cout = (a + b + cin) // 2
    table.append((a, b, cin, s, cout))
    print(f"│ {a} │ {b} │  {cin}  │  {s}  │  {cout}   │")
print("└───┴───┴─────┴─────┴──────┘")


# --- Функция для СКНФ ---
def to_sknf(table, output_idx, input_names=['A', 'B', 'Cin']):
    terms = []
    for row in table:
        if row[output_idx] == 0:
            term = []
            for i, name in enumerate(input_names):
                if row[i] == 1:
                    term.append(f"¬{name}")
                else:
                    term.append(f"{name}")
            terms.append("(" + " ∨ ".join(term) + ")")
    return " ∧ ".join(terms)


print("\n1.2 ВЫХОДНЫЕ ФУНКЦИИ В СКНФ (немминимизированные):")
sum_sknf = to_sknf(table, 3)
cout_sknf = to_sknf(table, 4)
print(f"Sum  = {sum_sknf}")
print(f"Cout = {cout_sknf}")


# --- Функция для построения карты Карно ---
def build_kmap(table, output_idx):
    kmap = {}
    for a, b in product([0, 1], repeat=2):
        for cin in [0, 1]:
            for row in table:
                if row[0] == a and row[1] == b and row[2] == cin:
                    kmap[(a, b, cin)] = row[output_idx]
    return kmap


def print_kmap(kmap, func_name):
    print(f"\nКарта Карно для {func_name}:")
    print("         Cin=0   Cin=1")
    print("       ┌─────┬─────┐")
    ab_order = [(0, 0), (0, 1), (1, 1), (1, 0)]
    for i, (a, b) in enumerate(ab_order):
        val0 = kmap.get((a, b, 0), '?')
        val1 = kmap.get((a, b, 1), '?')
        print(f"AB={a}{b}  │  {val0}  │  {val1}  │")
        if i < 3:
            print("       ├─────┼─────┤")
    print("       └─────┴─────┘")


# --- АВТОМАТИЧЕСКАЯ МИНИМИЗАЦИЯ ---
def minimize_function(kmap, func_name, var_names=['A', 'B', 'Cin']):
    A, B, Cin = var_names
    ones = [(a, b, cin) for (a, b, cin), val in kmap.items() if val == 1]

    print(f"\n  Единицы функции {func_name}: {ones}")

    # Проверка на XOR
    xor_pattern = [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)]
    if sorted(ones) == sorted(xor_pattern):
        print(f"  Обнаружена шахматная доска (XOR) — нет соседних единиц.")
        return f"{A} ⊕ {B} ⊕ {Cin}"

    # Поиск групп
    groups = []
    used_cells = set()
    ab_order = [(0, 0), (0, 1), (1, 1), (1, 0)]

    def check_group(cells, expr):
        nonlocal groups, used_cells
        if all(kmap.get(cell, 0) == 1 for cell in cells):
            if not any(cell in used_cells for cell in cells):
                groups.append(expr)
                for cell in cells:
                    used_cells.add(cell)
                return True
        return False

    # Пары по горизонтали (разные Cin)
    for a, b in ab_order:
        cells = [(a, b, 0), (a, b, 1)]
        expr = f"{'¬' if a == 0 else ''}{A} ∧ {'¬' if b == 0 else ''}{B}"
        check_group(cells, expr)

    # Пары по вертикали
    for i in range(4):
        next_i = (i + 1) % 4
        a1, b1 = ab_order[i]
        a2, b2 = ab_order[next_i]
        for cin in [0, 1]:
            cells = [(a1, b1, cin), (a2, b2, cin)]
            if a1 == a2:
                expr = f"{'¬' if a1 == 0 else ''}{A} ∧ {'¬' if cin == 0 else ''}{Cin}"
            elif b1 == b2:
                expr = f"{'¬' if b1 == 0 else ''}{B} ∧ {'¬' if cin == 0 else ''}{Cin}"
            else:
                expr = None
            if expr:
                check_group(cells, expr)

    # Одиночки
    for a, b, cin in ones:
        if (a, b, cin) not in used_cells:
            expr = f"{'¬' if a == 0 else ''}{A} ∧ {'¬' if b == 0 else ''}{B} ∧ {'¬' if cin == 0 else ''}{Cin}"
            groups.append(expr)

    return " ∨ ".join(groups) if groups else "0"


kmap_sum = build_kmap(table, 3)
kmap_cout = build_kmap(table, 4)

print_kmap(kmap_sum, "Sum")
print_kmap(kmap_cout, "Cout")

print("\n" + "=" * 50)
print("1.3 АВТОМАТИЧЕСКАЯ МИНИМИЗАЦИЯ:")
print("=" * 50)

sum_minimized = minimize_function(kmap_sum, "Sum")
cout_minimized = minimize_function(kmap_cout, "Cout")

print(f"\n  Sum  = {sum_minimized}")
print(f"  Cout = {cout_minimized}")

# Сохраняем результаты для итогов
part1_sum = f"Sum  = {sum_minimized}"
part1_cout = f"Cout = {cout_minimized}"

# ============================================================
# ЧАСТЬ 2: 2421 BCD СУММАТОР СО СМЕЩЕНИЕМ n=9
# ============================================================
print("\n" + "=" * 80)
print("ЧАСТЬ 2: 2421 BCD СУММАТОР СО СМЕЩЕНИЕМ n=9")
print("=" * 80)

code_2421 = {
    0: [0, 0, 0, 0], 1: [0, 0, 0, 1], 2: [0, 0, 1, 0], 3: [0, 0, 1, 1],
    4: [0, 1, 0, 0], 5: [1, 0, 1, 1], 6: [1, 1, 0, 0], 7: [1, 1, 0, 1],
    8: [1, 1, 1, 0], 9: [1, 1, 1, 1],
}

print("\n2.1 КОД 2421 BCD:")
print("┌─────────┬─────────────┐")
print("│ Десятич │  2421 BCD   │")
print("├─────────┼─────────────┤")
for d in range(10):
    print(f"│    {d}    │    {code_2421[d][0]}{code_2421[d][1]}{code_2421[d][2]}{code_2421[d][3]}     │")
print("└─────────┴─────────────┘")


def add_2421_with_shift(a_dec, b_dec, n=9):
    s = a_dec + b_dec + n
    if s >= 20:
        return s - 20, 2
    elif s >= 10:
        return s - 10, 1
    else:
        return s, 0


# Пример 8+6
a, b = 8, 6
res_8_6, ovf_8_6 = add_2421_with_shift(8, 6, 9)
part2_example = f"8 + 6 + 9 = {8 + 6 + 9} → результат {res_8_6} (2421: {code_2421[res_8_6]}), OVF={ovf_8_6}"

print("\n2.2 ПРИМЕР: 8 + 6")
print(f"   8 в 2421 BCD = {code_2421[8]}")
print(f"   6 в 2421 BCD = {code_2421[6]}")
print(f"   {part2_example}")

# ============================================================
# ЧАСТЬ 3: ДВОИЧНЫЙ СЧЁТЧИК НА 8 СОСТОЯНИЙ
# ============================================================
print("\n" + "=" * 80)
print("ЧАСТЬ 3: ДВОИЧНЫЙ СЧЁТЧИК НАКАПЛИВАЮЩЕГО ТИПА")
print("8 СОСТОЯНИЙ, БАЗИС: НЕ, И-ИЛИ, Т-ТРИГГЕР")
print("=" * 80)

# Таблица переходов
counter_table = []
for state in range(8):
    q2 = (state >> 2) & 1
    q1 = (state >> 1) & 1
    q0 = state & 1
    next_state = (state + 1) % 8
    nq2 = (next_state >> 2) & 1
    nq1 = (next_state >> 1) & 1
    nq0 = next_state & 1
    t2 = q2 ^ nq2
    t1 = q1 ^ nq1
    t0 = q0 ^ nq0
    counter_table.append((q2, q1, q0, nq2, nq1, nq0, t2, t1, t0))

print("\n3.1 ТАБЛИЦА ПЕРЕХОДОВ:")
print("┌───────────┬─────────────┬─────────────┐")
print("│ Q2 Q1 Q0  │ Q2+ Q1+ Q0+ │ T2 T1 T0    │")
print("├───────────┼─────────────┼─────────────┤")
for row in counter_table:
    print(
        f"│  {row[0]}  {row[1]}  {row[2]}  │   {row[3]}  {row[4]}  {row[5]}   │   {row[6]}  {row[7]}  {row[8]}   │")
print("└───────────┴─────────────┴─────────────┘")


# Функции для счётчика
def build_kmap_counter(table, output_idx):
    kmap = {}
    for q2, q1 in product([0, 1], repeat=2):
        for q0 in [0, 1]:
            for row in table:
                if row[0] == q2 and row[1] == q1 and row[2] == q0:
                    kmap[(q2, q1, q0)] = row[output_idx]
    return kmap


def print_kmap_counter(kmap, func_name):
    print(f"\nКарта Карно для {func_name}:")
    print("         Q0=0   Q0=1")
    print("        ┌─────┬─────┐")
    ab_order = [(0, 0), (0, 1), (1, 1), (1, 0)]
    for i, (q2, q1) in enumerate(ab_order):
        val0 = kmap.get((q2, q1, 0), '?')
        val1 = kmap.get((q2, q1, 1), '?')
        print(f"Q2Q1={q2}{q1} │  {val0}  │  {val1}  │")
        if i < 3:
            print("        ├─────┼─────┤")
    print("        └─────┴─────┘")


def minimize_counter(kmap, func_name, var_names=['Q2', 'Q1', 'Q0']):
    Q2, Q1, Q0 = var_names
    ones = [(q2, q1, q0) for (q2, q1, q0), val in kmap.items() if val == 1]

    print(f"\n  Единицы {func_name}: {ones}")

    # T0 = 1
    if len(ones) == 8:
        return "1"
    # T1 = Q0
    if sorted(ones) == [(0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 1)]:
        return Q0
    # T2 = Q0 ∧ Q1
    if sorted(ones) == [(0, 1, 1), (1, 1, 1)]:
        return f"{Q0} ∧ {Q1}"

    return "?"


kmap_t0 = build_kmap_counter(counter_table, 6)
kmap_t1 = build_kmap_counter(counter_table, 7)
kmap_t2 = build_kmap_counter(counter_table, 8)

print("\n3.2 КАРТЫ КАРНО ДЛЯ ФУНКЦИЙ ВОЗБУЖДЕНИЯ:")
print_kmap_counter(kmap_t0, "T0")
print_kmap_counter(kmap_t1, "T1")
print_kmap_counter(kmap_t2, "T2")

print("\n3.3 АВТОМАТИЧЕСКАЯ МИНИМИЗАЦИЯ:")
print("-" * 50)

t0_min = minimize_counter(kmap_t0, "T0")
t1_min = minimize_counter(kmap_t1, "T1")
t2_min = minimize_counter(kmap_t2, "T2")

print(f"\n  T0 = {t0_min}")
print(f"  T1 = {t1_min}")
print(f"  T2 = {t2_min}")

# Сохраняем результаты для итогов
part3_t0 = f"T0 = {t0_min}"
part3_t1 = f"T1 = {t1_min}"
part3_t2 = f"T2 = {t2_min}"

# ============================================================
# ИТОГИ (ФОРМИРУЮТСЯ АВТОМАТИЧЕСКИ ИЗ ПЕРЕМЕННЫХ)
# ============================================================
print("\n" + "=" * 80)
print("ИТОГИ СИНТЕЗА И МИНИМИЗАЦИИ ДЛЯ ВАРИАНТА 3E9")
print("=" * 80)

print("\nЧАСТЬ 1 - ОДС-3 (СКНФ):")
print(f"   {part1_sum}")
print(f"   {part1_cout}")

print("\nЧАСТЬ 2 - 2421 BCD СУММАТОР (n=9):")
print(f"   Формула: (A + B + 9) mod 10")
print(f"   Пример: {part2_example}")

print("\nЧАСТЬ 3 - СЧЁТЧИК НА 8 СОСТОЯНИЙ (T-триггеры):")
print(f"   {part3_t0}")
print(f"   {part3_t1}")
print(f"   {part3_t2}")
print(f"   Последовательность: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 0")

print("\n" + "=" * 80)
print("ВЫПОЛНЕНИЕ ЗАВЕРШЕНО. ")
print("=" * 80)