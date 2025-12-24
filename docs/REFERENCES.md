# 참고 자료 정리

## 1. Python 공식 문서 및 PEP

### 1.1 Typing 관련 핵심 PEP

| PEP | 제목 | 버전 | 설명 |
|-----|------|------|------|
| [PEP 484](https://peps.python.org/pep-0484/) | Type Hints | 3.5+ | 타입 힌트 기본 문법 |
| [PEP 544](https://peps.python.org/pep-0544/) | Protocols: Structural subtyping | 3.8+ | Protocol 클래스, 구조적 서브타이핑 |
| [PEP 560](https://peps.python.org/pep-0560/) | Core support for typing module | 3.7+ | `__class_getitem__`, `__mro_entries__` |
| [PEP 612](https://peps.python.org/pep-0612/) | Parameter Specification Variables | 3.10+ | ParamSpec, Concatenate |
| [PEP 673](https://peps.python.org/pep-0673/) | Self Type | 3.11+ | `Self` 타입 |
| [PEP 695](https://peps.python.org/pep-0695/) | Type Parameter Syntax | 3.12+ | `class Foo[T]:` 문법 |
| [PEP 696](https://peps.python.org/pep-0696/) | Type Defaults for Type Parameters | 3.13+ | TypeVar 기본값 |
| [PEP 705](https://peps.python.org/pep-0705/) | TypedDict: Read-only items | 3.13+ | `ReadOnly` 타입 |
| [PEP 742](https://peps.python.org/pep-0742/) | TypeIs | 3.13+ | 타입 좁히기 개선 |

### 1.2 공식 문서 링크

- [Python typing 모듈](https://docs.python.org/3/library/typing.html)
- [Python 3.13 What's New](https://docs.python.org/3/whatsnew/3.13.html)
- [unittest.mock 모듈](https://docs.python.org/3/library/unittest.mock.html)
- [typing 명세서](https://typing.python.org/en/latest/)

---

## 2. 핵심 Python Typing API

### 2.1 Generic과 TypeVar

```python
from typing import TypeVar, Generic

T = TypeVar('T')                    # 일반 TypeVar
T_co = TypeVar('T_co', covariant=True)   # 공변 TypeVar
T_contra = TypeVar('T_contra', contravariant=True)  # 반공변 TypeVar

# Python 3.13+: 기본값 지정 가능
T = TypeVar('T', default=int)

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
```

**문서**: [Generic Types](https://typing.python.org/en/latest/spec/generics.html)

### 2.2 Protocol (구조적 서브타이핑)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

# 명시적 상속 없이도 프로토콜 만족
class Circle:
    def draw(self) -> None:
        print("Drawing circle")

def render(obj: Drawable) -> None:
    obj.draw()

render(Circle())  # OK - Circle은 Drawable 프로토콜 만족
```

**문서**: [Protocols](https://typing.python.org/en/latest/spec/protocol.html)

### 2.3 ParamSpec (매개변수 사양)

```python
from typing import ParamSpec, TypeVar, Callable

P = ParamSpec('P')
R = TypeVar('R')

def decorator(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("Before call")
        result = func(*args, **kwargs)
        print("After call")
        return result
    return wrapper

@decorator
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age}"

# greet의 시그니처가 보존됨: (name: str, age: int) -> str
```

**문서**: [PEP 612](https://peps.python.org/pep-0612/)

### 2.4 @overload 데코레이터

```python
from typing import overload, Literal

@overload
def process(data: str) -> str: ...
@overload
def process(data: bytes) -> bytes: ...
@overload
def process(data: int) -> int: ...

def process(data):
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, bytes):
        return data.upper()
    else:
        return data * 2

# 타입 체커가 입력 타입에 따라 반환 타입 추론
result1: str = process("hello")     # OK
result2: bytes = process(b"hello")  # OK
result3: int = process(42)          # OK
```

**문서**: [Overloads](https://typing.python.org/en/latest/spec/overload.html)

### 2.5 __class_getitem__

```python
class MyContainer:
    def __class_getitem__(cls, item):
        """MyContainer[int] 같은 문법 지원"""
        print(f"Subscripted with: {item}")
        return cls  # 또는 새로운 타입 반환

# 사용
MyContainer[int]  # 출력: Subscripted with: <class 'int'>
```

**문서**: [PEP 560](https://peps.python.org/pep-0560/)

### 2.6 TYPE_CHECKING

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 이 블록은 타입 체커만 실행
    from heavy_module import ExpensiveClass

def process(obj: "ExpensiveClass") -> None:
    # 런타임에는 heavy_module을 임포트하지 않음
    pass
```

---

## 3. unittest.mock API

### 3.1 핵심 클래스

| 클래스 | 설명 |
|--------|------|
| `Mock` | 기본 mock 객체 |
| `MagicMock` | 매직 메소드가 미리 설정된 Mock |
| `AsyncMock` | 비동기 메소드를 위한 Mock |
| `PropertyMock` | 프로퍼티 mocking용 |
| `NonCallableMock` | 호출 불가능한 Mock |

### 3.2 주요 메소드

```python
from unittest.mock import MagicMock, call

mock = MagicMock()

# 호출 기록 확인
mock.assert_called()                    # 호출되었는지
mock.assert_called_once()               # 정확히 한 번 호출
mock.assert_called_with(1, 2, x=3)      # 마지막 호출 인자 확인
mock.assert_called_once_with(1, 2)      # 한 번만 특정 인자로 호출
mock.assert_any_call(1, 2)              # 어느 시점에 이 인자로 호출
mock.assert_not_called()                # 호출되지 않음

# 호출 정보 접근
mock.call_count          # 호출 횟수
mock.call_args           # 마지막 호출 인자
mock.call_args_list      # 모든 호출 인자 목록
mock.method_calls        # 메소드 호출 목록
mock.mock_calls          # 모든 호출 (체인 포함)

# 반환값/부수효과 설정
mock.return_value = 42
mock.side_effect = ValueError("error")
mock.side_effect = [1, 2, 3]  # 순차적 반환
mock.side_effect = lambda x: x * 2  # 함수
```

### 3.3 create_autospec

```python
from unittest.mock import create_autospec

class UserService:
    def get_user(self, user_id: int) -> dict:
        pass

# 원본 클래스의 시그니처를 복사한 mock 생성
mock_service = create_autospec(UserService, instance=True)
mock_service.get_user(1)        # OK
mock_service.get_user("abc")    # OK (런타임에는 검사 안 함)
mock_service.nonexistent()      # AttributeError!
```

**문서**: [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 4. pytest-mock 라이브러리

### 4.1 MockerFixture

```python
from pytest_mock import MockerFixture

def test_example(mocker: MockerFixture):
    # patch
    mock_open = mocker.patch("builtins.open")

    # spy (원본 호출하면서 기록)
    spy_print = mocker.spy(builtins, "print")

    # stub (간단한 mock)
    stub = mocker.stub(name="my_stub")

    # MagicMock 생성
    mock = mocker.MagicMock()
    async_mock = mocker.AsyncMock()
```

### 4.2 주요 기능

| 메소드 | 설명 |
|--------|------|
| `mocker.patch()` | 객체/함수 패치 |
| `mocker.patch.object()` | 객체의 속성 패치 |
| `mocker.patch.dict()` | 딕셔너리 패치 |
| `mocker.patch.multiple()` | 여러 속성 패치 |
| `mocker.spy()` | 원본 호출하며 기록 |
| `mocker.stub()` | 간단한 stub 생성 |
| `mocker.stopall()` | 모든 patch 중지 |
| `mocker.resetall()` | 모든 mock 리셋 |

**문서**: [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/)

---

## 5. 타입 체커

### 5.1 mypy

```bash
# 설치
uv add mypy --dev

# 실행
mypy src/

# 설정 (pyproject.toml)
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_ignores = true
```

**문서**: [mypy documentation](https://mypy.readthedocs.io/)

### 5.2 pyright

```bash
# 설치
uv add pyright --dev

# 실행
pyright src/

# 설정 (pyproject.toml)
[tool.pyright]
pythonVersion = "3.13"
typeCheckingMode = "strict"
```

**문서**: [pyright](https://github.com/microsoft/pyright)

---

## 6. 관련 서드파티 라이브러리

### 6.1 typing-protocol-intersection

Protocol의 교집합 타입 지원 (mypy 플러그인)

```python
from typing_protocol_intersection import ProtocolIntersection as Has

class X(Protocol):
    def x_method(self) -> int: ...

class Y(Protocol):
    def y_method(self) -> str: ...

def foo(xy: Has[X, Y]) -> None:
    xy.x_method()  # OK
    xy.y_method()  # OK
```

**PyPI**: [typing-protocol-intersection](https://pypi.org/project/typing-protocol-intersection/)
**GitHub**: [klausweiss/typing-protocol-intersection](https://github.com/klausweiss/typing-protocol-intersection)

### 6.2 types-mock

unittest.mock의 타입 스텁 패키지

```bash
uv add types-mock --dev
```

**PyPI**: [types-mock](https://pypi.org/project/types-mock/)

### 6.3 typing-extensions

최신 typing 기능의 백포트

```python
# Python 3.10에서 3.11+ 기능 사용
from typing_extensions import Self, TypedDict, NotRequired
```

**PyPI**: [typing-extensions](https://pypi.org/project/typing-extensions/)

---

## 7. Java Mockito 참고

### 7.1 Mockito 타입 추론의 한계

Java도 제네릭 타입 추론에 한계가 있음:

```java
// 경고 발생: unchecked conversion
List<String> mockList = Mockito.mock(List.class);

// 해결책: @Mock 어노테이션
@Mock
List<String> mockList;  // 타입 안전
```

### 7.2 Mockito 주요 패턴

```java
// when-thenReturn (타입 안전)
when(mockList.get(0)).thenReturn("value");

// doReturn-when (제네릭 와일드카드에 유리)
doReturn("value").when(mockList).get(0);

// verify
verify(mockList).get(0);
verify(mockList, times(2)).add("item");
```

**참고 자료**:
- [Mockito Generics Issue #1531](https://github.com/mockito/mockito/issues/1531)
- [Baeldung: List Matchers with Generics](https://www.baeldung.com/mockito-generic-list-matchers)

---

## 8. 관련 GitHub 이슈 및 논의

### 8.1 Python typing 관련

| 이슈 | 제목 | 상태 |
|------|------|------|
| [python/typing#213](https://github.com/python/typing/issues/213) | Introduce an Intersection | Open |
| [python/mypy#1188](https://github.com/python/mypy/issues/1188) | Need a way to specify types for mock objects | Open |
| [python/mypy#11501](https://github.com/python/mypy/issues/11501) | mypy does not handle __class_getitem__ | Open |

### 8.2 pytest-mock 관련

| 이슈 | 제목 | 상태 |
|------|------|------|
| [pytest-dev/pytest-mock#152](https://github.com/pytest-dev/pytest-mock/issues/152) | add type annotations | Closed |
| [pytest-dev/pytest-mock#201](https://github.com/pytest-dev/pytest-mock/pull/201) | Type improvements | Merged |

### 8.3 Pylance 관련

| 이슈 | 제목 |
|------|------|
| [microsoft/pylance-release#5510](https://github.com/microsoft/pylance-release/issues/5510) | No type/autocomplete for pytest fixture |
| [microsoft/pylance-release#5633](https://github.com/microsoft/pylance-release/issues/5633) | list[MagicMock] incompatible with function parameter |

---

## 9. 추가 학습 자료

### 9.1 블로그/튜토리얼

- [Real Python: Python Protocols](https://realpython.com/python-protocol/)
- [Adam Johnson: Python @overload](https://adamj.eu/tech/2021/05/29/python-type-hints-how-to-use-overload/)
- [Medium: 7 New Typing Features in Python 3.13](https://medium.com/techtofreedom/7-new-typing-features-in-python-3-13-58caae5f2f10)
- [Using ParamSpec with Python Generics](https://cthoyt.com/2025/04/22/python-generic-with-paramspec.html)

### 9.2 공식 예제

- [mypy Generics](https://mypy.readthedocs.io/en/stable/generics.html)
- [pytest typing explanation](https://docs.pytest.org/en/stable/explanation/types.html)

---

## 10. 도구 및 환경 설정

### 10.1 pyproject.toml 예시

```toml
[project]
name = "typed-pytest"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "pytest>=8.0",
    "pytest-mock>=3.11",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.8",
    "pyright>=1.1.350",
    "ruff>=0.1.0",
    "types-mock",
]

[tool.mypy]
python_version = "3.13"
strict = true
plugins = []

[tool.pyright]
pythonVersion = "3.13"
typeCheckingMode = "strict"

[tool.ruff]
target-version = "py313"
select = ["E", "F", "I", "UP", "ANN"]
```

### 10.2 uv 패키지 매니저 명령어

```bash
# 의존성 추가
uv add pytest pytest-mock

# 개발 의존성 추가
uv add mypy pyright ruff --dev

# 동기화
uv sync

# 실행
uv run pytest
uv run mypy src/
```

---

*문서 버전: 1.0*
*최종 수정: 2024-12*
