from hash_table import HashTable
#cd D:\AK\Лабораторные\2 курс\АОИС\4 семестр\lab4
#coverage report -m
def print_menu():
    print("\n" + "=" * 60)
    print("УПРАВЛЕНИЕ ХЕШ-ТАБЛИЦЕЙ (ЛЮДИ И ПРОФЕССИИ)")
    print("=" * 60)
    print("1. Вывести таблицу")
    print("2. Добавить запись (Insert)")
    print("3. Найти запись (Search)")
    print("4. Обновить запись (Update)")
    print("5. Удалить запись (Delete)")
    print("6. Заполнить тестовыми данными (20 человек)")
    print("7. Показать статистику")
    print("8. Очистить таблицу")
    print("0. Выход")
    print("-" * 60)


def main():
    ht = HashTable(size=20)

    while True:
        print_menu()
        choice = input("\nВыберите действие: ").strip()

        if choice == '1':
            ht.display()

        elif choice == '2':
            k = input("Введите фамилию: ").strip()
            d = input("Введите профессию: ").strip()
            if k and d:
                ht.insert(k, d)
            else:
                print("Фамилия и профессия не могут быть пустыми!")

        elif choice == '3':
            k = input("Введите фамилию для поиска: ").strip()
            res = ht.search(k)
            if res:
                print(f"\n[Найдено] {res.key}: {res.data}")
                print(f"Диагностика: V(K)={res.v}, h(V)={res.h_base}, шагов={res.probes}")
            else:
                print("\nЗапись не найдена.")

        elif choice == '4':
            k = input("Введите фамилию для обновления: ").strip()
            d = input("Новая профессия: ").strip()
            ht.update(k, d)

        elif choice == '5':
            k = input("Введите фамилию для удаления: ").strip()
            ht.delete(k)

        elif choice == '6':
            data = [
                ("Иванов", "Спортсмен"), ("Петров", "Программист"), ("Сидоров", "Художник"),
                ("Козлов", "Пианист"), ("Соколова", "Учитель"), ("Морозов", "Водитель"),
                ("Воробьёв", "Повар"), ("Соловьёв", "Строитель"), ("Сорокин", "Врач"),
                ("Лебедев", "Инженер"), ("Новиков", "Дизайнер"), ("Кузнецов", "Архитектор"),
                ("Попов", "Бухгалтер"), ("Васильев", "Менеджер"), ("Павлов", "Аналитик"),
                ("Михайлов", "Учёный"), ("Фёдоров", "Тренер"), ("Егорова", "Фотограф"),
                ("Николаев", "Хореограф"), ("Андреев", "Режиссёр")
            ]
            print("\nЗаполнение таблицы тестовыми данными...")
            for k, d in data:
                ht.insert(k, d)
            print("\nЗаполнение завершено!")

        elif choice == '7':
            ht.stats()

        elif choice == '8':
            confirm = input("Точно очистить таблицу? (y/n): ").strip().lower()
            if confirm == 'y':
                ht.clear()

        elif choice == '0':
            print("Выход из программы...")
            break
        else:
            print("Неверный ввод, попробуйте еще раз.")


if __name__ == "__main__":
    main()