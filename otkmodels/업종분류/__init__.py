import logging
import os.path

import openpyxl

from otkmodels import 업종

업종코드미상 = 'ZZZZZZ'


data = {}


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


def guess(업종명):
    if not 업종명:
        return None

    result = search(업종명)
    if result:
        return result[0]
    return None


def ensure_data_loaded():
    if data:
        return

    data.update(추가업종코드)
    book = openpyxl.load_workbook(filename=os.path.dirname(__file__) + '/업종코드-표준산업분류 연계표_홈택스게시.xlsx', data_only=True)
    sheet = book.active

    for row in sheet.iter_rows(min_row=6):
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