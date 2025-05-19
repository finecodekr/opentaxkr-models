import unittest

from otkmodels.accounting.docparser import load_표준계정과목


class TestAccount(unittest.TestCase):
    def test_find_account(self):
        accounts = list(load_표준계정과목())

        self.assertEqual(['표준대차대조표_일반법인', '표준대차대조표_금융법인', '표준손익계산서_일반법인', '표준손익계산서_금융법인',
                          '제조원가명세서', '공사원가명세서', '임대원가명세서', '분양원가명세서', '운송원가명세서', '기타원가명세서',
                          '이익잉여금처분_결손금처리'], [a.name for a in accounts])
        self.assertEqual('상품매출', accounts[2].children[0].children[0].name)
