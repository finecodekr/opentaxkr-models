import unittest
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum

from otkmodels.util import Model, convert_type


class MyCode(Enum):
    A = 'a'
    B = 'b'


class TestModel(unittest.TestCase):
    def test_type_conversion(self):
        self.assertEqual(date(2020, 1, 1), convert_type('20200101', date))
        self.assertEqual(datetime(2020, 1, 1, 9, 30, 15, tzinfo=timezone.utc),
                         convert_type('2020-01-01T09:30:15Z', datetime))
        self.assertEqual(1, convert_type('1', int))
        self.assertEqual(Decimal('0.15'), convert_type('0.15', Decimal))
        self.assertEqual(MyCode.B, convert_type('b', MyCode))
        self.assertEqual(MyCode.B, convert_type(MyCode.B, MyCode))

    def test_model_field_conversion(self):
        @dataclass()
        class TestModel(Model):
            a: date
            b: MyCode

        model = TestModel('20200101', 'a')
        self.assertEqual(date(2020, 1, 1), model.a)
        self.assertEqual(MyCode.A, model.b)