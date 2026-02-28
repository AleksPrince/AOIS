"""
Утилиты для работы с двоичными массивами
"""
"""
Утилиты для работы с двоичными массивами
"""


class BinaryArrayUtils:
    """Класс утилит для работы с двоичными массивами"""

    # Константы
    BIT_COUNT = 32
    BITS_PER_GROUP = 8

    @staticmethod
    def create_zero_array():
        """Создание массива из 32 нулей"""
        return [0] * BinaryArrayUtils.BIT_COUNT

    @staticmethod
    def format_binary(binary_array, group_size=BITS_PER_GROUP):
        """
        Форматирование двоичного массива для вывода

        Args:
            binary_array: список битов
            group_size: размер группы для разделения

        Returns:
            отформатированная строка
        """
        if not binary_array:
            return ""

        # Если массив короче 32 бит, форматируем как есть
        if len(binary_array) < BinaryArrayUtils.BIT_COUNT:
            binary_string = ''.join(str(bit) for bit in binary_array)
            return binary_string

        binary_string = ''.join(str(bit) for bit in binary_array)
        grouped = ' '.join(
            binary_string[i:i + group_size]
            for i in range(0, len(binary_string), group_size)
        )
        return grouped

    @staticmethod
    def validate_binary_array(binary_array):
        """
        Проверка корректности двоичного массива

        Args:
            binary_array: список битов

        Raises:
            ValueError: если массив некорректен
        """
        if len(binary_array) != BinaryArrayUtils.BIT_COUNT:
            raise ValueError(f"Массив должен содержать {BinaryArrayUtils.BIT_COUNT} бит")

        for bit in binary_array:
            if bit not in (0, 1):
                raise ValueError("Биты должны быть 0 или 1")

    @staticmethod
    def print_binary_with_analysis(binary_array, title=""):
        """
        Вывод двоичного массива с анализом

        Args:
            binary_array: список битов
            title: заголовок
        """
        if title:
            print(f"\n{title}:")

        formatted = BinaryArrayUtils.format_binary(binary_array)
        print(f"  Двоичный вид: {formatted}")

        # Анализ
        sign = "отрицательное" if binary_array[0] == 1 else "положительное"
        print(f"  Знак: {sign}")

        # Подсчет единиц
        ones_count = sum(binary_array)
        print(f"  Количество единиц: {ones_count}")


class NumberConverter:
    """Класс для базового преобразования чисел"""

    @staticmethod
    def integer_to_binary_array(decimal_number):
        """
        Преобразование целого числа в массив двоичных цифр

        Args:
            decimal_number: целое число

        Returns:
            список двоичных цифр
        """
        if decimal_number == 0:
            return [0]

        binary_digits = []
        absolute_value = abs(decimal_number)

        while absolute_value > 0:
            remainder = absolute_value % 2
            binary_digits.insert(0, remainder)
            absolute_value = absolute_value // 2

        return binary_digits

    @staticmethod
    def binary_array_to_integer(binary_array, start_index=0):
        """
        Преобразование двоичного массива в целое число

        Args:
            binary_array: список битов
            start_index: индекс начала преобразования

        Returns:
            целое число
        """
        result = 0
        for index in range(start_index, len(binary_array)):
            result = result * 2 + binary_array[index]
        return result

    @staticmethod
    def fraction_to_binary(fraction, max_bits=20):
        """
        Преобразование десятичной дроби в двоичную

        Args:
            fraction: дробная часть (0 <= fraction < 1)
            max_bits: максимальное количество бит

        Returns:
            список двоичных цифр дробной части
        """
        binary_digits = []
        current = fraction

        for _ in range(max_bits):
            if current == 0:
                break
            current *= 2
            bit = int(current)
            binary_digits.append(bit)
            current -= bit

        return binary_digits

    @staticmethod
    def binary_fraction_to_decimal(binary_fraction):
        """
        Преобразование двоичной дроби в десятичную

        Args:
            binary_fraction: список битов дробной части

        Returns:
            десятичная дробь
        """
        result = 0.0
        for i, bit in enumerate(binary_fraction):
            if bit == 1:
                result += 2 ** (-(i + 1))
        return result