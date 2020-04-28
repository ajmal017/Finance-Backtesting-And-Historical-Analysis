import unittest
from financeclasses import fclasses as fc
from apps import backtest as bt


class MyTestCases(unittest.TestCase):

    def test_import_of_equities_is_complete(self):
        self.assertEqual(len(bt.equities_list), len(fc.load_df_list(bt.equities_list, 'csv')))
