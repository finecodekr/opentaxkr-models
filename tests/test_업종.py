import unittest

from otkmodels import 업종분류


class Test업종(unittest.TestCase):

    def test_search(self):
        self.assertIn('소프트웨어 개발 및 공급업', [업종.소분류 for 업종 in 업종분류.search('소프트웨어')])
        self.assertEqual('출장 및 이동 음식점업', 업종분류.pick('552105').세분류)

        found = 업종분류.search('응용 소프트웨어 개발 및 공급업')[0]
        self.assertEqual('응용 소프트웨어 개발 및 공급업', found.종목)
        self.assertEqual('정보통신업', found.업태)

    def test_normalize_name(self):
        업종분류.ensure_data_loaded()
        대분류_set = {v.대분류 for v in 업종분류.data.values()}
        self.assertIn('협회 및 단체, 수리 및 기타 개인 서비스업', 대분류_set)
        self.assertNotIn('협회 및 단체, 수리 및 기타 개인서비스', 대분류_set)
