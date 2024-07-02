from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from itertools import chain
from typing import List

from addresskr import 도로명주소

from otkmodels.util import Model


class 납세자종류(Enum):
    개인 = '01'
    개인사업자 = '02'
    법인사업자 = '03'

    @classmethod
    def detect(cls, 납세자ID):
        num = str(납세자ID).replace('-', '')
        if len(num) == 13 and int(num[2:4]) in range(1, 13) and int(num[4:6]) in range(1, 32):
            return cls.개인

        # TODO 맞는 규칙인지 확인할 것.
        if 납세자ID == '0000000000':
            return cls.개인

        if len(num) == 10:
            middle_number = int(num[3:5])
            if middle_number in chain(range(1, 80), range(90, 100), [80, 89]):
                return cls.개인사업자
            if middle_number in range(81, 89):
                return cls.법인사업자

        raise ValueError(f'사업자번호 오류: {납세자ID}')


@dataclass(kw_only=True)
class 업종(Model):
    코드: str
    업태: str = None
    종목: str = None
    대분류: str = None
    중분류: str = None
    소분류: str = None
    세분류: str = None
    세세분류: str = None
    세부설명: str = None
    표준산업분류: dict = None

    def __post_init__(self):
        self.업태 = self.업태 or self.대분류
        self.종목 = self.종목 or self.세세분류


@dataclass(kw_only=True)
class 납세자(Model):
    납세자ID: str
    납세자명: str
    휴대전화번호: str = None
    전자메일주소: str = None
    주소: str = None
    납세자종류: 납세자종류; 납세자종류 = None
    업종: 업종; 업종 = None
    개업일: date = None
    폐업일: date = None
    사업장소재지: str = None
    사업장전화번호: str = None
    간이과세여부: bool = False
    국적코드: str = 'KR'
    거주지국가코드: str = 'KR'
    홈택스ID: str = None
    # 법인에만 해당하는 정보
    대표자주민등록번호: str = None
    법인등록번호: str = None
    대표자명: str = None

    def __post_init__(self):
        self.납세자ID = self.납세자ID.replace('-', '')
        self.휴대전화번호 = self.휴대전화번호 and self.휴대전화번호.replace('-', '')
        self.대표자주민등록번호 = self.대표자주민등록번호 or self.납세자ID
        self.대표자명 = self.대표자명 or self.납세자명

        if self.납세자종류 is None:
            self.납세자종류 = 납세자종류.detect(self.납세자ID)

    @property
    def 도로명주소(self):
        if not hasattr(self, '_도로명주소'):
            self._도로명주소 = 도로명주소.parse(self.주소)

        return self._도로명주소


@dataclass(kw_only=True)
class 세무대리인:
    대표자주민등록번호: str
    법인등록번호: str = None
    대표자성명: str
    법인명_상호: str = None
    전화번호: str
    사업자등록번호: str
    관리번호: str
    성명: str
    생년월일: date
    사업장소재지: str = None
    우편번호: str = None
    세무서코드: str = None
    법정동코드: str = None
    홈택스ID: str = None

    def __post_init__(self):
        self.전화번호 = self.전화번호.replace('-', '')


class 세금계산서분류(Enum):
    세금계산서 = '01'
    수정세금계산서 = '02'
    계산서 = '03'
    수정계산서 = '04'


class 세금계산서종류(Enum):
    일반 = '01'
    영세율 = '02'
    위수탁 = '03'
    수입 = '04'
    영세율위수탁 = '05'
    수입납부유예 = '06'


@dataclass(kw_only=True)
class 세금계산서(Model):
    승인번호: str
    작성일자: date
    세금계산서분류: 세금계산서분류
    세금계산서종류: 세금계산서종류
    영수청구코드: str
    수정코드: str = None
    당초승인번호: str = None
    비고: str = None
    수입문서참조: '수입문서' = None

    공급자: 납세자
    공급자연락처: '연락처'
    공급받는자: 납세자
    공급받는자연락처: '연락처'
    공급받는자연락처2: '연락처' = None
    위수탁자: 납세자 = None
    위수탁자연락처: '연락처' = None

    결제방법코드: str
    결제금액: Decimal
    공급가액: Decimal
    세액: Decimal
    총금액: Decimal

    품목: List['세금계산서품목']


@dataclass(kw_only=True)
class 수입문서(Model):
    신고번호: str
    일괄발급시작일: date
    일괄발급종료일: date
    총건: int


@dataclass(kw_only=True)
class 연락처(Model):
    부서명: str
    이름: str
    전화번호: str
    이메일: str


@dataclass(kw_only=True)
class 세금계산서품목(Model):
    일련번호: int
    공급일자: date
    품목명: str
    규격: str = None
    비고: str = None
    수량: int = None # `-` 허용. 단위는 attribute로 들어간다.
    단가: Decimal  # 소수점 2자리까지 표현. `-` 허용
    공급가액: Decimal  # 원단위까지. `-` 허용
    세액: Decimal


@dataclass(kw_only=True)
class 카드매입(Model):
    거래일시: datetime
    카드번호: str
    승인번호: str
    카드사: str
    공급가액: Decimal
    부가세: Decimal
    봉사료: Decimal
    총금액: Decimal
    가맹점: 납세자
    가맹점유형: str
    공제여부: str
    비고: str


@dataclass(kw_only=True)
class 현금영수증(Model):
    거래일시: datetime
    매출매입: str
    승인번호: str
    승인구분: str
    발행구분: str = None
    발급수단: str
    거래구분: str = None
    공급가액: Decimal
    부가세: Decimal
    봉사료: Decimal
    총금액: Decimal
    매입자명: str = None
    가맹점: 납세자
    공제여부: bool = None


__version__ = '0.1.0'
