"""
Базовый класс для работы с двоичными операциями
"""
"""
Базовый класс для работы с двоичными операциями
"""

from src.utils import BinaryArrayUtils, NumberConverter


class BinaryProcessor:
    """
    Базовый класс процессора двоичных операций
    Содержит общие методы для всех типов операций
    """

    # Константы
    BIT_COUNT = 32
    SIGN_BIT_INDEX = 0
    INTEGER_BITS = 31

    def __init__(self):
        """Инициализация процессора"""
        self.utils = BinaryArrayUtils()
        self.converter = NumberConverter()

    def create_zero_array(self):
        """Создание массива из 32 нулей"""
        return self.utils.create_zero_array()

    def format_binary(self, binary_array, group_size=8):
        """Форматирование двоичного массива"""
        return self.utils.format_binary(binary_array, group_size)

    def add_binary_arrays(self, first_array, second_array):
        """
        Сложение двух двоичных массивов с переносом (32-битные)

        Args:
            first_array: первый массив битов
            second_array: второй массив битов

        Returns:
            массив результата сложения
        """
        self.utils.validate_binary_array(first_array)
        self.utils.validate_binary_array(second_array)

        result = self.create_zero_array()
        carry = 0

        for position in range(self.BIT_COUNT - 1, -1, -1):
            bit_sum = first_array[position] + second_array[position] + carry
            result[position] = bit_sum % 2
            carry = bit_sum // 2

        return result

    def invert_bits(self, binary_array, start_from=1):
        """
        Инверсия битов массива

        Args:
            binary_array: исходный массив
            start_from: индекс начала инверсии

        Returns:
            инвертированный массив
        """
        inverted = binary_array.copy()
        for index in range(start_from, self.BIT_COUNT):
            inverted[index] = 1 if inverted[index] == 0 else 0
        return inverted

    def get_binary_one(self):
        """Получение двоичного представления единицы"""
        one_array = self.create_zero_array()
        one_array[self.BIT_COUNT - 1] = 1
        return one_array

    def binary_to_decimal_unsigned(self, binary_array):
        """
        Преобразование беззнакового двоичного массива в десятичное число

        Args:
            binary_array: список битов

        Returns:
            десятичное число
        """
        result = 0
        for bit in binary_array:
            result = result * 2 + bit
        return result