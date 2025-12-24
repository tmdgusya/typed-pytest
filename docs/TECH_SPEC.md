# Typed-Pytest 기술 스펙 문서

## 1. 개요

### 1.1 문제 정의

pytest와 unittest.mock을 사용할 때 다음과 같은 타입 추론 문제가 발생합니다:

```python
from unittest.mock import MagicMock, patch
from typing import cast

class UserService:
    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "John"}

    def create_user(self, name: str) -> dict:
        return {"id": 1, "name": name}

# 문제 1: fixture로 mocking 시 타입 추론 불가
@pytest.fixture
def mock_user_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("app.UserService")

def test_user(mock_user_service):  # mock_user_service의 타입이 MagicMock
    mock_user_service.get_user(1)  # get_user에 대한 자동완성/타입 힌트 없음

# 문제 2: cast 사용 시 mock 메소드 타입 힌트 누락
def test_user_with_cast(mock_user_service):
    service = cast(UserService, mock_user_service)
    service.get_user.assert_called_once()  # ❌ assert_called_once는 타입 힌트 없음
    # UserService.get_user에는 assert_called_once가 없기 때문

# 문제 3: Mock으로 cast하면 원본 메소드 타입 힌트 누락
def test_user_with_mock_cast(mock_user_service):
    service = cast(MagicMock, mock_user_service)
    service.get_user(1)  # ❌ get_user 파라미터 타입 힌트 없음
```

### 1.2 목표

Java Mockito처럼 **원본 클래스의 타입 지원**과 **Mock 메소드의 타입 추론**을 동시에 가능하게 하는 라이브러리 개발:

```python
# 목표하는 사용자 경험
from typed_pytest import TypedMock

def test_user(mocker: MockerFixture):
    # 원본 타입 + Mock 타입 동시 지원
    mock_service: TypedMock[UserService] = typed_mock(UserService)

    mock_service.get_user(1)  # ✅ 원본 메소드 시그니처 자동완성
    mock_service.get_user.assert_called_once_with(1)  # ✅ Mock 메소드도 타입 힌트 지원
    mock_service.get_user.return_value = {"id": 1}  # ✅ return_value 타입 힌트
```

---

## 2. 기술적 배경

### 2.1 Python 타입 시스템 현황

#### 현재 문제점

| 접근 방식 | 원본 타입 지원 | Mock 메소드 지원 | 단점 |
|-----------|---------------|-----------------|------|
| `MagicMock` | ❌ | ✅ | 원본 클래스 메소드 추론 불가 |
| `cast(OriginalClass, mock)` | ✅ | ❌ | Mock 메소드 추론 불가 |
| `create_autospec()` | 부분적 | ❌ | 런타임만 지원, 정적 분석 미지원 |

#### Python 3.13 새로운 기능

- **PEP 696**: TypeVar, ParamSpec, TypeVarTuple에 기본값 지원
- **PEP 705**: `typing.ReadOnly` - TypedDict 읽기 전용 필드
- **PEP 742**: `typing.TypeIs` - 더 직관적인 타입 좁히기
- **PEP 702**: `warnings.deprecated()` 데코레이터

### 2.2 핵심 Python API

#### 2.2.1 Generic과 TypeVar

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class TypedMock(Generic[T]):
    """T 타입의 인터페이스를 Mock으로 감싸는 제네릭 클래스"""
    pass
```

#### 2.2.2 Protocol (PEP 544)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class MockProtocol(Protocol):
    """Mock 객체가 가져야 할 메소드 정의"""
    def assert_called(self) -> None: ...
    def assert_called_once(self) -> None: ...
    def assert_called_with(self, *args, **kwargs) -> None: ...
    def assert_called_once_with(self, *args, **kwargs) -> None: ...
    @property
    def return_value(self) -> Any: ...
    @property
    def call_count(self) -> int: ...
```

#### 2.2.3 @overload 데코레이터

```python
from typing import overload, Callable

class TypedMocker:
    @overload
    def patch(self, target: type[T]) -> TypedMock[T]: ...

    @overload
    def patch(self, target: str) -> MagicMock: ...

    def patch(self, target):
        # 실제 구현
        pass
```

#### 2.2.4 __class_getitem__ (PEP 560)

```python
class TypedMock:
    def __class_getitem__(cls, item: type[T]) -> type["TypedMock[T]"]:
        """TypedMock[UserService] 문법 지원"""
        # 런타임에서 제네릭 타입 정보 접근
        return super().__class_getitem__(item)
```

#### 2.2.5 ParamSpec (PEP 612)

```python
from typing import ParamSpec, Callable

P = ParamSpec('P')
R = TypeVar('R')

class MockedMethod(Generic[P, R]):
    """원본 메소드의 시그니처를 보존하는 Mock 메소드"""
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
```

---

## 3. 설계 방안

### 3.1 핵심 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                        typed_pytest                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   TypedMock[T]   │    │  MockedMethod    │                  │
│  │  (Generic[T])    │◄───│  [P, R]          │                  │
│  │                  │    │                  │                  │
│  │ - 원본 T의 모든  │    │ - 원본 시그니처  │                  │
│  │   메소드 시그니처│    │   P 보존         │                  │
│  │ - Mock 프로토콜  │    │ - Mock 메소드    │                  │
│  │   메소드         │    │   타입 힌트      │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │  typed_mock()    │    │  TypedMocker     │                  │
│  │  Factory 함수    │    │  (pytest 통합)   │                  │
│  └──────────────────┘    └──────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 구현 전략

#### 전략 A: Protocol Intersection 접근법

Python에는 공식적인 Intersection 타입이 없으므로, 다중 상속을 활용한 Protocol 조합:

```python
from typing import Protocol, Generic, TypeVar

T = TypeVar('T')

class MockMethods(Protocol):
    """Mock 고유 메소드"""
    def assert_called(self) -> None: ...
    def assert_called_once(self) -> None: ...
    # ...

# 문제: T의 메소드와 MockMethods를 동적으로 결합하기 어려움
```

#### 전략 B: 타입 스텁(.pyi) 생성 접근법

빌드 타임에 원본 클래스를 분석하여 타입 스텁 자동 생성:

```python
# 자동 생성되는 user_service.pyi
class MockedUserService(UserService, MockProtocol):
    def get_user(self, user_id: int) -> MockedMethod[..., dict]: ...
```

#### 전략 C: Generic + @overload 조합 (권장)

```python
from typing import Generic, TypeVar, overload, TYPE_CHECKING
from unittest.mock import MagicMock

T = TypeVar('T')

class TypedMock(MagicMock, Generic[T]):
    """
    원본 타입 T의 인터페이스를 유지하면서 Mock 기능을 제공하는 클래스

    타입 체커는 T의 모든 메소드를 인식하고,
    각 메소드는 MockedMethod로 래핑되어 assert_* 메소드 접근 가능
    """

    if TYPE_CHECKING:
        # 타입 체커만 이 정의를 봄
        def __getattr__(self, name: str) -> MockedMethod: ...

@overload
def typed_mock(cls: type[T], /) -> TypedMock[T]: ...

@overload
def typed_mock(cls: type[T], /, **kwargs) -> TypedMock[T]: ...

def typed_mock(cls, /, **kwargs):
    """타입 안전한 Mock 객체 생성"""
    return TypedMock(spec=cls, **kwargs)
```

### 3.3 MockedMethod 설계

```python
from typing import Generic, ParamSpec, TypeVar, Callable

P = ParamSpec('P')
R = TypeVar('R')

class MockedMethod(Generic[P, R]):
    """
    원본 메소드의 시그니처를 보존하면서 Mock 기능을 제공

    예: UserService.get_user(user_id: int) -> dict
    → MockedMethod[[int], dict]
    """

    # 원본 메소드처럼 호출 가능
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    # Mock assertion 메소드들
    def assert_called(self) -> None: ...
    def assert_called_once(self) -> None: ...
    def assert_called_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_any_call(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_not_called(self) -> None: ...

    # Mock 속성들
    @property
    def return_value(self) -> R: ...
    @return_value.setter
    def return_value(self, value: R) -> None: ...

    @property
    def side_effect(self) -> Callable[P, R] | Exception | None: ...
    @side_effect.setter
    def side_effect(self, value: Callable[P, R] | Exception | list) -> None: ...

    @property
    def call_count(self) -> int: ...

    @property
    def call_args(self) -> tuple[tuple, dict] | None: ...

    @property
    def call_args_list(self) -> list[tuple[tuple, dict]]: ...
```

---

## 4. pytest 통합

### 4.1 TypedMocker Fixture

```python
from pytest_mock import MockerFixture
from typing import TypeVar, overload
import pytest

T = TypeVar('T')

class TypedMocker:
    """pytest-mock의 MockerFixture를 확장한 타입 안전 모커"""

    def __init__(self, mocker: MockerFixture):
        self._mocker = mocker

    @overload
    def mock(self, cls: type[T]) -> TypedMock[T]: ...

    @overload
    def patch(
        self,
        target: str,
        new: type[T] | None = None,
    ) -> TypedMock[T]: ...

    def patch(self, target, new=None, **kwargs):
        """타입 안전한 patch"""
        if new is not None:
            mock = TypedMock(spec=new)
            return self._mocker.patch(target, mock, **kwargs)
        return self._mocker.patch(target, **kwargs)

    def create_autospec(self, cls: type[T]) -> TypedMock[T]:
        """타입 안전한 autospec 생성"""
        from unittest.mock import create_autospec
        mock = create_autospec(cls, instance=True)
        # TypedMock으로 래핑
        return TypedMock(spec=cls, wraps=mock)

@pytest.fixture
def typed_mocker(mocker: MockerFixture) -> TypedMocker:
    """타입 안전한 mocker fixture"""
    return TypedMocker(mocker)
```

### 4.2 사용 예시

```python
# tests/test_user_service.py
from typed_pytest import TypedMock, typed_mocker, TypedMocker
from app.services import UserService

def test_get_user(typed_mocker: TypedMocker):
    # 방법 1: 직접 mock 생성
    mock_service: TypedMock[UserService] = typed_mocker.mock(UserService)

    # 원본 타입의 메소드 시그니처 지원 ✅
    mock_service.get_user.return_value = {"id": 1, "name": "John"}

    # Mock 메소드 타입 힌트 지원 ✅
    mock_service.get_user(1)
    mock_service.get_user.assert_called_once_with(1)  # 파라미터 타입 체크됨

def test_with_patch(typed_mocker: TypedMocker):
    # 방법 2: patch 사용
    with typed_mocker.patch("app.services.UserService", UserService) as mock_service:
        mock_service.create_user.return_value = {"id": 1, "name": "Test"}

        # 테스트 로직
        result = some_function_using_user_service()

        mock_service.create_user.assert_called_once_with("Test")
```

---

## 5. 기술적 도전과 해결책

### 5.1 동적 메소드 속성 타입 추론

**문제**: `mock_service.get_user`가 `MockedMethod`임을 타입 체커에게 알려야 함

**해결책**: `__getattr__` 타입 힌트 + 타입 스텁

```python
# typed_pytest.pyi (타입 스텁)
from typing import Generic, TypeVar, overload

T = TypeVar('T')

class TypedMock(Generic[T]):
    @overload
    def __getattr__(self, name: str) -> MockedMethod: ...

    # 또는 더 정교하게:
    # T의 각 메소드에 대해 동적으로 MockedMethod 타입 반환
```

### 5.2 원본 클래스 메소드 시그니처 보존

**문제**: `TypedMock[UserService]`가 `UserService`의 모든 메소드를 알아야 함

**해결책**:
1. **TYPE_CHECKING 분기**: 타입 체커에게만 보이는 정의
2. **Plugin 접근법**: mypy/pyright 플러그인으로 타입 정보 주입

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import _SpecialForm
    # 타입 체커 전용 정의
    class TypedMock(Generic[T]):
        # T의 모든 어트리뷰트를 MockedMethod로 변환
        pass
else:
    # 런타임 정의
    class TypedMock(MagicMock):
        pass
```

### 5.3 Intersection 타입 부재

**문제**: Python에는 공식 Intersection 타입이 없음

**해결책 옵션**:

1. **typing-protocol-intersection 라이브러리 사용**
   ```python
   from typing_protocol_intersection import ProtocolIntersection as Has

   def typed_mock(cls: type[T]) -> Has[T, MockProtocol]:
       ...
   ```

2. **다중 상속 Protocol 정의**
   ```python
   class TypedMock(Generic[T], MockProtocol):
       """T와 MockProtocol을 모두 구현"""
       pass
   ```

3. **타입 스텁에서 Union 활용** (부분적 해결)

---

## 6. 의존성 및 호환성

### 6.1 필수 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| Python | ≥3.13 | 기본 언어, 최신 typing 기능 활용 |
| pytest | ≥8.0 | 테스트 프레임워크 |
| pytest-mock | ≥3.11 | MockerFixture 기반 |

### 6.2 선택적 의존성

| 패키지 | 용도 |
|--------|------|
| typing-extensions | 하위 버전 호환성 (필요시) |
| typing-protocol-intersection | Intersection 타입 지원 |
| mypy | 타입 체킹 |
| pyright | 타입 체킹 (VS Code Pylance) |

### 6.3 개발 의존성

```toml
[project.optional-dependencies]
dev = [
    "mypy>=1.8",
    "pyright>=1.1.350",
    "ruff>=0.1.0",
    "pytest>=8.0",
    "pytest-mock>=3.11",
]
```

---

## 7. 프로젝트 구조

```
typed-pytest/
├── src/
│   └── typed_pytest/
│       ├── __init__.py          # 공개 API
│       ├── _mock.py             # TypedMock 구현
│       ├── _method.py           # MockedMethod 구현
│       ├── _mocker.py           # TypedMocker (pytest 통합)
│       ├── _protocols.py        # Protocol 정의
│       ├── py.typed             # PEP 561 마커
│       └── _version.py          # 버전 정보
├── stubs/
│   └── typed_pytest/
│       └── __init__.pyi         # 타입 스텁 (필요시)
├── tests/
│   ├── test_typed_mock.py
│   ├── test_mocked_method.py
│   └── test_integration.py
├── docs/
│   ├── TECH_SPEC.md             # 이 문서
│   └── REFERENCES.md            # 참고 자료
├── pyproject.toml
└── README.md
```

---

## 8. 구현 로드맵

### Phase 1: 핵심 기능
- [ ] `TypedMock[T]` 제네릭 클래스 구현
- [ ] `MockedMethod[P, R]` 구현
- [ ] 기본 팩토리 함수 `typed_mock()` 구현
- [ ] 단위 테스트 작성

### Phase 2: pytest 통합
- [ ] `TypedMocker` 클래스 구현
- [ ] `typed_mocker` fixture 구현
- [ ] `patch()` 메소드 타입 안전 버전 구현
- [ ] 통합 테스트 작성

### Phase 3: 타입 체커 지원
- [ ] mypy 호환성 검증
- [ ] pyright 호환성 검증
- [ ] 필요시 타입 스텁 작성
- [ ] 필요시 mypy 플러그인 개발

### Phase 4: 고급 기능
- [ ] Nested mock 지원
- [ ] Async 메소드 지원
- [ ] Property mock 지원
- [ ] Class method / Static method 지원

---

## 9. 위험 요소 및 대안

### 9.1 위험 요소

| 위험 | 영향도 | 대응 방안 |
|------|--------|-----------|
| 타입 체커 간 동작 차이 | 높음 | mypy/pyright 모두 테스트 |
| Python 버전별 typing 차이 | 중간 | 3.13+ 전용으로 범위 제한 |
| 복잡한 제네릭 타입 지원 한계 | 중간 | 문서화 및 제한 명시 |
| 성능 오버헤드 | 낮음 | 타입 힌트는 런타임 영향 없음 |

### 9.2 대안 검토

1. **mypy 플러그인만 개발**: 런타임 변경 없이 타입 체커 레벨에서만 해결
2. **IDE 확장 개발**: VS Code/PyCharm 전용 확장
3. **코드 생성기**: 원본 클래스에서 Mock 타입 스텁 자동 생성

---

## 10. 참고 자료

- [PEP 544 - Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [PEP 560 - Core support for typing module and generic types](https://peps.python.org/pep-0560/)
- [PEP 612 - Parameter Specification Variables](https://peps.python.org/pep-0612/)
- [PEP 696 - Type Defaults for Type Parameters](https://peps.python.org/pep-0696/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [mypy Generics documentation](https://mypy.readthedocs.io/en/stable/generics.html)
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [typing-protocol-intersection](https://pypi.org/project/typing-protocol-intersection/)

---

*문서 버전: 1.0*
*최종 수정: 2024-12*
