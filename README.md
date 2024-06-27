# opentaxkr-models
한국의 세무회계 데이터를 여러 도구에서 공통적으로 다루기 쉽도록 자주 사용하는 데이터의 스키마를 모델로 정의해둔다.

## dataclass와 Model
세무회계 데이터 모델은 모두 파이썬 dataclass를 사용하며, 세무회계 데이터의 특성상 문자열로 데이터가 전달되는 경우가 많기 때문에 간단한 타입 변환 기능을 제공하는 Model을 상속한다. default 값을 순서 상관 없이 정의할 수 있게 하기 위해 dataclass에 `kw_only=True` 옵션을 사용한다. 다음 예시 참고:

```python
@dataclass(kw_only=True)
class 납세자(Model):
    납세자번호: str
    납세자명: str
    휴대전화번호: str = None
    전자메일주소: str = None
```

## 코드 컨벤션
1. 모델의 이름, 필드의 이름 등은 모두 [국세청](https://nts.go.kr/)의 공식 문서, [세법](https://taxlaw.nts.go.kr/index.do;jsessionid=QfuwD6mDaAbZx-VmtR9u7SNxmfptjl-suQNa_R8T.cpesiwsp01_SE11) 또는 [홈택스](https://hometax.go.kr/websquare/websquare.html?w2xPath=/ui/pp/index_pp.xml)에서 사용하는 용어를 우선적으로 쓴다.
2. 한국어 용어가 있는 경우는 한국어를 쓰고, 없을 때만 영어를 쓴다.
3. 필수임이 확실한 필드를 제외하면 나머지는 모두 `default`를 `None`으로 대입해서 많은 인자를 다 채워넣지 않고도 사용할 수 있게 한다.
4. 필드의 타입은 파이썬에서 가장 풍부한 표현력을 가진 타입으로 정한다. 예를 들어, 날짜 필드는 `str`로 쓰기보다 `date`를 사용한다.
5. 필드 값의 목록이 정해져 있는 경우는 `Enum`을 사용한다.
