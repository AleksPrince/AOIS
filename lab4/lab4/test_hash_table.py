import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hash_table import HashTable, State


class TestHashTable(unittest.TestCase):

    def setUp(self):
        """Создаём новую таблицу перед каждым тестом"""
        self.ht = HashTable(size=20)

    # ============ БАЗОВЫЕ ОПЕРАЦИИ ============

    def test_insert_and_search(self):
        """Тест вставки и поиска"""
        self.ht.insert("Иванов", "Спортсмен")
        res = self.ht.search("Иванов")
        self.assertIsNotNone(res)
        self.assertEqual(res.data, "Спортсмен")

    def test_insert_duplicate(self):
        """Тест вставки дубликата (должна быть ошибка)"""
        self.ht.insert("Петров", "Программист")
        result = self.ht.insert("Петров", "Художник")
        self.assertFalse(result)  # Должен вернуть False
        res = self.ht.search("Петров")
        self.assertEqual(res.data, "Программист")  # Данные не изменились

    def test_search_not_found(self):
        """Тест поиска несуществующего ключа"""
        res = self.ht.search("Несуществующий")
        self.assertIsNone(res)

    # ============ ОБНОВЛЕНИЕ ============

    def test_update(self):
        """Тест обновления существующего ключа"""
        self.ht.insert("Сидоров", "Художник")
        result = self.ht.update("Сидоров", "Архитектор")
        self.assertTrue(result)
        res = self.ht.search("Сидоров")
        self.assertEqual(res.data, "Архитектор")

    def test_update_not_found(self):
        """Тест обновления несуществующего ключа"""
        result = self.ht.update("Несуществующий", "Данные")
        self.assertFalse(result)

    # ============ УДАЛЕНИЕ ============

    def test_delete(self):
        """Тест удаления существующего ключа"""
        self.ht.insert("Козлов", "Пианист")
        result = self.ht.delete("Козлов")
        self.assertTrue(result)
        res = self.ht.search("Козлов")
        self.assertIsNone(res)

    def test_delete_not_found(self):
        """Тест удаления несуществующего ключа"""
        result = self.ht.delete("Несуществующий")
        self.assertFalse(result)

    # ============ КОЛЛИЗИИ ============

    def test_collision_handling(self):
        """Тест обработки коллизий"""
        # Соколова и Соловьёв имеют одинаковый V
        self.ht.insert("Соколова", "Учитель")
        self.ht.insert("Соловьёв", "Строитель")
        res1 = self.ht.search("Соколова")
        res2 = self.ht.search("Соловьёв")
        self.assertIsNotNone(res1)
        self.assertIsNotNone(res2)
        # Проверяем, что они в разных ячейках
        self.assertNotEqual(res1.h_base, res2.h_base)

    # ============ ЗАПОЛНЕНИЕ ============

    def test_fill_to_capacity(self):
        """Тест заполнения таблицы до предела"""
        for i in range(20):
            self.ht.insert(f"Ключ{i}", f"Данные{i}")
        self.assertEqual(self.ht.count, 20)
        # Попытка вставить 21-й элемент
        result = self.ht.insert("Лишний", "Данные")
        self.assertFalse(result)

    def test_load_factor(self):
        """Тест коэффициента заполнения"""
        self.assertEqual(self.ht.count / self.ht.size, 0.0)
        for i in range(10):
            self.ht.insert(f"Ключ{i}", f"Данные{i}")
        self.assertEqual(self.ht.count, 10)
        self.assertEqual(self.ht.count / self.ht.size, 0.5)

    # ============ ОЧИСТКА ============

    def test_clear(self):
        """Тест очистки таблицы"""
        self.ht.insert("Тест", "Данные")
        self.ht.clear()
        self.assertEqual(self.ht.count, 0)
        res = self.ht.search("Тест")
        self.assertIsNone(res)

    # ============ СТАТИСТИКА И ОТОБРАЖЕНИЕ ============

    def test_stats(self):
        """Тест вывода статистики (просто проверяем, что не падает)"""
        try:
            self.ht.stats()
            self.ht.insert("Иванов", "Спортсмен")
            self.ht.stats()
        except Exception as e:
            self.fail(f"stats() вызвал ошибку: {e}")

    def test_display(self):
        """Тест отображения таблицы (просто проверяем, что не падает)"""
        try:
            self.ht.display()
            self.ht.insert("Иванов", "Спортсмен")
            self.ht.display()
        except Exception as e:
            self.fail(f"display() вызвал ошибку: {e}")

    # ============ TOMBSTONE (УДАЛЁННЫЕ ЯЧЕЙКИ) ============

    def test_tombstone_reuse(self):
        """Тест переиспользования удалённой ячейки"""
        self.ht.insert("Первый", "Данные1")
        self.ht.delete("Первый")
        # Удалённая ячейка должна стать DELETED
        deleted_exists = any(e.state == State.DELETED for e in self.ht.table)
        self.assertTrue(deleted_exists)
        # Вставляем новый ключ — должен использовать удалённую ячейку
        self.ht.insert("Второй", "Данные2")
        res = self.ht.search("Второй")
        self.assertIsNotNone(res)

    # ============ ГРАНИЧНЫЕ СЛУЧАИ ============

    def test_empty_key(self):
        """Тест вставки пустого ключа"""
        # Метод insert должен корректно обработать пустую строку
        result = self.ht.insert("", "Данные")
        # V для пустой строки = 0
        self.assertTrue(result)



# ============ ЗАПУСК ============
if __name__ == "__main__":
    unittest.main()