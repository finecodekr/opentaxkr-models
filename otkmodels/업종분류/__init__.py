import logging
import os.path
from difflib import SequenceMatcher
from typing import Dict, Callable, Iterable, TypeVar

import openpyxl

from otkmodels import 업종

업종코드미상 = 'ZZZZZZ'


data: Dict[str, 업종] = {}
대분류_set = set()


def pick(code, notify_not_found=False):
    ensure_data_loaded()
    try:
        return data[code]
    except KeyError:
        if notify_not_found:
            logging.exception(f'등록되지 않은 업종코드 {code}')
        return None


def search(query):
    ensure_data_loaded()

    found = []
    for item in [v for v in data.values() if v.코드]:
        if any([query in value for value in [item.코드, item.중분류, item.소분류, item.세분류, item.세세분류]]):
            found.append(item)
    return found


def guess(업태, 종목) -> 업종 | None:
    """업태는 업종의 대분류, 종목은 업종의 소분류 역할을 하는데, 이 값이 정확한 명칭이 아니더라도 전체 업종 검색을 통해 가장 비슷한 업종을 찾는다."""
    ensure_data_loaded()

    if not 업태 or not 종목:
        return None

    if 업태 in 대분류_set:
        found_대분류 = 업태
    else:
        found_대분류, _ = find_best_match(업태, 대분류_set)

    # 대분류 안에서 먼저 찾고 그 결과가 만족스럽지 않으면 대분류 상관없이 전체 검색해서 세분류가 가장 비슷한 것을 찾되, 이때는 더 높아져야 한다.
    found, ratio = find_best_match(종목, [i for i in data.values() if i.대분류 == found_대분류], lambda i: i.세분류)
    if ratio < 0.6:
        fullscan_found, fullscan_ratio = find_best_match(종목, [i for i in data.values()], lambda i: i.세분류)

        if fullscan_ratio > 0.6:
            return fullscan_found

    return found


def pick_or_guess(업종코드, 업태, 종목):
    found = pick(업종코드)
    if found:
        return found

    return guess(업태, 종목)


def ensure_data_loaded():
    if data:
        return

    data.update(추가업종코드)
    book = openpyxl.load_workbook(filename=os.path.dirname(__file__) + '/업종코드-표준산업분류 연계표_홈택스게시.xlsx', data_only=True)
    sheet = book.active

    for row in sheet.iter_rows(min_row=6):
        if not row[4].value:
            continue

        data[row[4].value] = 업종(
            코드=row[4].value,
            대분류=normalize_대분류(row[6].value),
            중분류=row[8].value,
            소분류=row[10].value,
            세분류=row[12].value,
            세세분류=row[13].value,
            세부설명=row[27].value or '',
            표준산업분류=dict(
                코드=row[15].value,
                대분류=row[17].value,
                중분류=row[19].value,
                소분류=row[21].value,
                세분류=row[23].value,
                세세분류=row[24].value,
            )
        )

        대분류_set.add(data[row[4].value].대분류)

    data[업종코드미상] = 업종(
        코드=업종코드미상,
        대분류='',
        중분류='',
        소분류='',
        세분류='',
        세세분류='',
        표준산업분류={}
    )


대분류_match = {
    '건 설 업': '건설업',
    '부동산업 및 임대업': '부동산업',
    '사업시설관리 및 사업지원서비스업': '사업시설 관리, 사업 지원 및 임대 서비스업',
    '전기, 가스, 증기 및 수도사업': '전기, 가스, 증기 및 공기 조절 공급업',
    '전문, 과학 및 기술서비스업': '전문, 과학 및 기술 서비스업',
    '협회 및 단체, 수리 및 기타 개인서비스': '협회 및 단체, 수리 및 기타 개인 서비스업'
}


def normalize_대분류(value):
    return 대분류_match.get(value, value)


추가업종코드 = {
    '525105': 업종(
        코드='525105',
        대분류='도매 및 소매업',
        중분류='소매업; 자동차 제외',
        소분류='소매업',  # 소분류는 홈택스에서 제공하지 않아서 중분류에서 소매업만 가져옴.
        세분류='통신 판매업',
        세세분류='해외직구대행업',
        표준산업분류={
            '대분류': '도매 및 소매업',
            '중분류': '소매업; 자동차 제외',
            '소분류': '무점포 소매업',
            '세분류': '통신 판매업',
            '세세분류': '해외직구대행업',
        }
    )
}


T = TypeVar('T')
def find_best_match(text, data_set: Iterable[T], picker: Callable[[T], str] = lambda t: t):
    ratio = 0
    found = None
    for item in data_set:
        new_ratio = SequenceMatcher(None, text, picker(item)).ratio()

        if new_ratio > ratio:
            ratio = new_ratio
            found = item

    return found, ratio