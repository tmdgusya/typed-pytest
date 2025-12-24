# Task Breakdown - typed-pytest

> TECH_SPEC.md 기반 작업 분해 문서
> 각 Task는 **개발(DEV) - 테스트(TEST)** 회귀 사이클로 진행됩니다.

---

## Task 개요

| Phase | Task 수 | 예상 복잡도 | 병렬 가능 |
|-------|---------|-------------|-----------|
| Phase 0: 프로젝트 설정 | 3 | 낮음 | 부분적 |
| Phase 1: 핵심 기능 | 6 | 높음 | 부분적 |
| Phase 2: pytest 통합 | 4 | 중간 | 부분적 |
| Phase 3: 타입 체커 지원 | 3 | 중간 | 가능 |
| Phase 4: 고급 기능 | 4 | 높음 | 가능 |

---

## Phase 0: 프로젝트 설정

### T000: 프로젝트 구조 및 의존성 설정

**담당자**: TBD
**선행 Task**: 없음
**우선순위**: P0 (Critical)

#### DEV

- [ ] `src/typed_pytest/` 디렉토리 구조 생성
- [ ] `pyproject.toml` 완성 (의존성, 도구 설정)
- [ ] `py.typed` 마커 파일 생성 (PEP 561)
- [ ] `.github/workflows/ci.yml` 생성

#### TEST

- [ ] `uv sync` 정상 동작 확인
- [ ] `uv run pytest` 실행 가능 확인
- [ ] `uv run mypy src/` 실행 가능 확인

#### 완료 기준

```bash
uv sync --all-extras  # 성공
uv run pytest --collect-only  # 테스트 수집 성공
uv run mypy src/  # 오류 없음
```

---

### T001: 테스트 인프라 구축

**담당자**: TBD
**선행 Task**: T000
**우선순위**: P0 (Critical)

#### DEV

- [ ] `tests/conftest.py` 공통 fixture 정의
- [ ] `tests/unit/`, `tests/integration/` 디렉토리 생성
- [ ] pytest 설정 (`pyproject.toml`의 `[tool.pytest]`)
- [ ] coverage 설정 (`[tool.coverage]`)

#### TEST

- [ ] 샘플 테스트 작성 및 실행 확인
- [ ] 커버리지 리포트 생성 확인

#### 완료 기준

```bash
uv run pytest tests/ --cov=src/typed_pytest --cov-report=term
# Coverage report 출력됨
```

---

### T002: 샘플 대상 클래스 정의

**담당자**: TBD
**선행 Task**: T001
**우선순위**: P0 (Critical)

#### DEV

- [ ] `tests/fixtures/sample_classes.py` 생성
- [ ] 테스트용 샘플 클래스 정의 (UserService, ProductRepository 등)
- [ ] 다양한 메소드 시그니처 포함 (동기, 프로퍼티, 클래스메소드 등)

```python
# tests/fixtures/sample_classes.py
class UserService:
    def get_user(self, user_id: int) -> dict[str, Any]: ...
    def create_user(self, name: str, email: str) -> dict[str, Any]: ...
    async def async_get_user(self, user_id: int) -> dict[str, Any]: ...

    @property
    def connection_status(self) -> str: ...

class ProductRepository:
    def find_by_id(self, product_id: str) -> Product | None: ...
    def find_all(self, limit: int = 10) -> list[Product]: ...
```

#### TEST

- [ ] 샘플 클래스 임포트 테스트
- [ ] 타입 체커에서 샘플 클래스 인식 확인

---

## Phase 1: 핵심 기능

### T100: MockProtocol 정의

**담당자**: TBD
**선행 Task**: T002
**우선순위**: P0 (Critical)
**병렬 가능**: T101과 병렬 가능

#### DEV

- [ ] `src/typed_pytest/_protocols.py` 생성
- [ ] `MockProtocol` Protocol 클래스 정의
- [ ] Mock의 모든 assertion 메소드 시그니처 정의
- [ ] Mock 속성 (return_value, side_effect, call_count 등) 정의

```python
# src/typed_pytest/_protocols.py
from typing import Protocol, Any

class MockProtocol(Protocol):
    """Mock 객체가 구현해야 하는 프로토콜"""

    def assert_called(self) -> None: ...
    def assert_called_once(self) -> None: ...
    def assert_called_with(self, *args: Any, **kwargs: Any) -> None: ...
    def assert_called_once_with(self, *args: Any, **kwargs: Any) -> None: ...
    def assert_any_call(self, *args: Any, **kwargs: Any) -> None: ...
    def assert_not_called(self) -> None: ...
    def reset_mock(self) -> None: ...

    @property
    def return_value(self) -> Any: ...
    @property
    def side_effect(self) -> Any: ...
    @property
    def call_count(self) -> int: ...
    @property
    def call_args(self) -> Any: ...
    @property
    def call_args_list(self) -> list: ...
    @property
    def called(self) -> bool: ...
```

#### TEST

- [ ] `tests/unit/test_protocols.py` 생성
- [ ] MagicMock이 MockProtocol을 만족하는지 테스트
- [ ] Protocol 메소드 시그니처 검증

```python
# tests/unit/test_protocols.py
from unittest.mock import MagicMock
from typed_pytest._protocols import MockProtocol

def test_magicmock_satisfies_mock_protocol():
    mock = MagicMock()
    # Protocol의 모든 메소드가 존재하는지 확인
    assert hasattr(mock, 'assert_called')
    assert hasattr(mock, 'assert_called_once')
    assert hasattr(mock, 'return_value')
    # ...
```

#### 커버리지 목표: 100%

---

### T101: MockedMethod 제네릭 클래스 구현

**담당자**: TBD
**선행 Task**: T100
**우선순위**: P0 (Critical)
**병렬 가능**: T100 완료 후 T102와 병렬 가능

#### DEV

- [ ] `src/typed_pytest/_method.py` 생성
- [ ] `MockedMethod[P, R]` 제네릭 클래스 정의
- [ ] ParamSpec을 사용한 시그니처 보존
- [ ] Mock assertion 메소드에 타입 힌트 추가

```python
# src/typed_pytest/_method.py
from typing import Generic, ParamSpec, TypeVar, Any, Callable

P = ParamSpec('P')
R = TypeVar('R')

class MockedMethod(Generic[P, R]):
    """
    원본 메소드의 시그니처를 보존하면서 Mock 기능을 제공.

    타입 체커에게:
    - __call__: 원본 메소드와 동일한 시그니처
    - assert_*: 원본 파라미터 타입으로 검증
    - return_value: 원본 반환 타입
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def assert_called(self) -> None: ...
    def assert_called_once(self) -> None: ...
    def assert_called_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_any_call(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_not_called(self) -> None: ...

    @property
    def return_value(self) -> R: ...
    @return_value.setter
    def return_value(self, value: R) -> None: ...

    @property
    def side_effect(self) -> Callable[P, R] | Exception | None: ...
    @property
    def call_count(self) -> int: ...
```

#### TEST

- [ ] `tests/unit/test_mocked_method.py` 생성
- [ ] MockedMethod 인스턴스 생성 테스트
- [ ] 타입 힌트 검증 (TYPE_CHECKING 모드)
- [ ] 실제 Mock 동작 테스트

```python
# tests/unit/test_mocked_method.py
class TestMockedMethod:
    def test_call_preserves_signature(self):
        """MockedMethod 호출이 원본 시그니처를 따르는지"""
        ...

    def test_assert_called_with_type_hints(self):
        """assert_called_with가 원본 파라미터 타입 힌트를 가지는지"""
        ...

    def test_return_value_has_correct_type(self):
        """return_value가 원본 반환 타입을 가지는지"""
        ...
```

#### 커버리지 목표: 90%

---

### T102: TypedMock 제네릭 클래스 구현

**담당자**: TBD
**선행 Task**: T100, T101
**우선순위**: P0 (Critical)

#### DEV

- [ ] `src/typed_pytest/_mock.py` 생성
- [ ] `TypedMock[T]` 제네릭 클래스 정의
- [ ] MagicMock 상속
- [ ] `__class_getitem__` 구현
- [ ] `__getattr__` 오버라이드로 MockedMethod 반환

```python
# src/typed_pytest/_mock.py
from typing import Generic, TypeVar, Any, TYPE_CHECKING
from unittest.mock import MagicMock

T = TypeVar('T')

class TypedMock(MagicMock, Generic[T]):
    """
    원본 타입 T의 인터페이스를 유지하면서 Mock 기능을 제공하는 클래스.

    Usage:
        mock_service: TypedMock[UserService] = TypedMock(spec=UserService)
        mock_service.get_user(1)  # 원본 시그니처 자동완성
        mock_service.get_user.assert_called_once_with(1)  # Mock 메소드 타입 힌트
    """

    _typed_class: type[T] | None = None

    def __class_getitem__(cls, item: type[T]) -> type["TypedMock[T]"]:
        """TypedMock[UserService] 문법 지원"""
        ...

    if TYPE_CHECKING:
        def __getattr__(self, name: str) -> MockedMethod[..., Any]:
            """타입 체커에게 MockedMethod 반환을 알림"""
            ...
```

#### TEST

- [ ] `tests/unit/test_typed_mock.py` 생성
- [ ] 기본 생성 테스트
- [ ] spec 파라미터 동작 테스트
- [ ] 원본 클래스 메소드 접근 테스트
- [ ] Mock assertion 메소드 동작 테스트

```python
# tests/unit/test_typed_mock.py
from typed_pytest import TypedMock
from tests.fixtures.sample_classes import UserService

class TestTypedMock:
    def test_creation_with_spec(self):
        """spec으로 TypedMock 생성"""
        mock = TypedMock(spec=UserService)
        assert hasattr(mock, 'get_user')
        assert hasattr(mock, 'create_user')

    def test_method_returns_mocked_method(self):
        """메소드 접근 시 MockedMethod 반환"""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
        method = mock.get_user
        assert hasattr(method, 'assert_called')
        assert hasattr(method, 'return_value')

    def test_class_getitem_stores_type(self):
        """__class_getitem__이 타입 정보를 저장하는지"""
        MockType = TypedMock[UserService]
        # 타입 정보 확인
        ...
```

#### 커버리지 목표: 90%

---

### T103: typed_mock 팩토리 함수 구현

**담당자**: TBD
**선행 Task**: T102
**우선순위**: P0 (Critical)

#### DEV

- [ ] `src/typed_pytest/_factory.py` 생성
- [ ] `typed_mock()` 함수 구현
- [ ] `@overload` 데코레이터로 다양한 시그니처 지원
- [ ] 옵션 파라미터 (spec_set, strict 등) 지원

```python
# src/typed_pytest/_factory.py
from typing import TypeVar, overload, Any

T = TypeVar('T')

@overload
def typed_mock(cls: type[T], /) -> TypedMock[T]: ...

@overload
def typed_mock(
    cls: type[T],
    /,
    *,
    spec_set: bool = False,
    strict: bool = False,
    **kwargs: Any,
) -> TypedMock[T]: ...

def typed_mock(cls, /, **kwargs):
    """
    타입 안전한 Mock 객체를 생성합니다.

    Args:
        cls: Mock으로 만들 원본 클래스
        spec_set: True면 spec에 없는 속성 접근 시 에러
        strict: True면 호출되지 않은 mock에 대해 경고
        **kwargs: MagicMock 추가 인자

    Returns:
        TypedMock[T]: 타입 정보를 가진 Mock 인스턴스
    """
    spec = kwargs.pop('spec', cls)
    spec_set_val = kwargs.pop('spec_set', False)

    if spec_set_val:
        return TypedMock(spec_set=cls, **kwargs)
    return TypedMock(spec=spec, **kwargs)
```

#### TEST

- [ ] `tests/unit/test_factory.py` 생성
- [ ] 기본 사용법 테스트
- [ ] 옵션 파라미터 테스트
- [ ] 오류 케이스 테스트 (잘못된 인자 등)

```python
# tests/unit/test_factory.py
class TestTypedMockFactory:
    def test_basic_creation(self):
        """기본 typed_mock 호출"""
        mock = typed_mock(UserService)
        assert isinstance(mock, TypedMock)

    def test_spec_set_raises_on_unknown_attr(self):
        """spec_set=True일 때 없는 속성 접근 시 에러"""
        mock = typed_mock(UserService, spec_set=True)
        with pytest.raises(AttributeError):
            mock.nonexistent_method()

    def test_kwargs_passed_to_magicmock(self):
        """추가 kwargs가 MagicMock에 전달되는지"""
        mock = typed_mock(UserService, name="test_mock")
        assert mock._mock_name == "test_mock"
```

#### 커버리지 목표: 95%

---

### T104: 공개 API 정의 (__init__.py)

**담당자**: TBD
**선행 Task**: T100, T101, T102, T103
**우선순위**: P1 (High)

#### DEV

- [ ] `src/typed_pytest/__init__.py` 작성
- [ ] 공개 API 명시적 export
- [ ] `__all__` 정의
- [ ] 버전 정보 추가

```python
# src/typed_pytest/__init__.py
"""
typed-pytest: Type-safe mocking for pytest

타입 안전한 pytest mocking 라이브러리.
원본 클래스의 타입 정보를 유지하면서 Mock 기능을 제공합니다.
"""

from typed_pytest._mock import TypedMock
from typed_pytest._method import MockedMethod
from typed_pytest._factory import typed_mock
from typed_pytest._protocols import MockProtocol
from typed_pytest._version import __version__

__all__ = [
    "TypedMock",
    "MockedMethod",
    "typed_mock",
    "MockProtocol",
    "__version__",
]
```

#### TEST

- [ ] 공개 API 임포트 테스트
- [ ] `__all__` 항목과 실제 export 일치 테스트

```python
# tests/unit/test_public_api.py
def test_public_api_imports():
    """공개 API가 정상적으로 임포트되는지"""
    from typed_pytest import TypedMock, MockedMethod, typed_mock, MockProtocol
    assert TypedMock is not None
    assert MockedMethod is not None
    ...

def test_all_matches_exports():
    """__all__이 실제 export와 일치하는지"""
    import typed_pytest
    for name in typed_pytest.__all__:
        assert hasattr(typed_pytest, name)
```

#### 커버리지 목표: 100%

---

### T105: 기본 타입 체커 호환성 검증

**담당자**: TBD
**선행 Task**: T104
**우선순위**: P1 (High)

#### DEV

- [ ] mypy strict 모드 설정
- [ ] pyright strict 모드 설정
- [ ] 타입 오류 수정

#### TEST

- [ ] `tests/typecheck/` 디렉토리 생성
- [ ] 타입 체킹 테스트 케이스 작성
- [ ] mypy/pyright 통과 검증

```python
# tests/typecheck/test_type_inference.py
"""
이 파일은 타입 체커에 의해 검사됩니다.
런타임 테스트가 아닌 정적 타입 검사용입니다.
"""
from typed_pytest import TypedMock, typed_mock
from tests.fixtures.sample_classes import UserService

def test_type_inference() -> None:
    # 타입 체커가 이 코드를 검사
    mock: TypedMock[UserService] = typed_mock(UserService)

    # 원본 메소드 시그니처 - 타입 체커가 파라미터 타입 검사
    mock.get_user(1)  # OK
    # mock.get_user("string")  # 타입 에러 (주석 처리)

    # Mock 메소드 - 타입 힌트 존재
    mock.get_user.assert_called_once_with(1)
    result: dict = mock.get_user.return_value  # OK
```

```bash
# CI에서 실행
uv run mypy tests/typecheck/
uv run pyright tests/typecheck/
```

---

## Phase 2: pytest 통합

### T200: TypedMocker 클래스 구현

**담당자**: TBD
**선행 Task**: T104
**우선순위**: P1 (High)

#### DEV

- [ ] `src/typed_pytest/_mocker.py` 생성
- [ ] `TypedMocker` 클래스 정의
- [ ] pytest-mock의 `MockerFixture` 래핑
- [ ] 타입 안전한 `mock()`, `patch()` 메소드 구현

```python
# src/typed_pytest/_mocker.py
from typing import TypeVar, overload, Any, ContextManager
from pytest_mock import MockerFixture

T = TypeVar('T')

class TypedMocker:
    """pytest-mock의 MockerFixture를 확장한 타입 안전 모커"""

    def __init__(self, mocker: MockerFixture) -> None:
        self._mocker = mocker

    def mock(self, cls: type[T], /, **kwargs: Any) -> TypedMock[T]:
        """타입 안전한 Mock 객체 생성"""
        return typed_mock(cls, **kwargs)

    @overload
    def patch(
        self,
        target: str,
        new: type[T],
        **kwargs: Any,
    ) -> ContextManager[TypedMock[T]]: ...

    @overload
    def patch(
        self,
        target: str,
        **kwargs: Any,
    ) -> ContextManager[MagicMock]: ...

    def patch(self, target, new=None, **kwargs):
        """타입 안전한 patch"""
        if new is not None:
            mock = typed_mock(new, **kwargs)
            return self._mocker.patch(target, mock)
        return self._mocker.patch(target, **kwargs)

    def spy(self, obj: T, name: str) -> MockedMethod:
        """타입 안전한 spy"""
        return self._mocker.spy(obj, name)

    @property
    def mocker(self) -> MockerFixture:
        """원본 MockerFixture 접근"""
        return self._mocker
```

#### TEST

- [ ] `tests/unit/test_typed_mocker.py` 생성
- [ ] mock() 메소드 테스트
- [ ] patch() 메소드 테스트
- [ ] 컨텍스트 매니저 동작 테스트

```python
# tests/unit/test_typed_mocker.py
class TestTypedMocker:
    def test_mock_returns_typed_mock(self, mocker: MockerFixture):
        typed_mocker = TypedMocker(mocker)
        mock = typed_mocker.mock(UserService)
        assert isinstance(mock, TypedMock)

    def test_patch_with_type_returns_typed_mock(self, mocker: MockerFixture):
        typed_mocker = TypedMocker(mocker)
        with typed_mocker.patch("module.UserService", UserService) as mock:
            assert isinstance(mock, TypedMock)
```

#### 커버리지 목표: 90%

---

### T201: typed_mocker Fixture 구현

**담당자**: TBD
**선행 Task**: T200
**우선순위**: P1 (High)

#### DEV

- [ ] `src/typed_pytest/_fixtures.py` 생성
- [ ] `typed_mocker` pytest fixture 정의
- [ ] conftest.py 자동 등록 설정 (entry points)

```python
# src/typed_pytest/_fixtures.py
import pytest
from pytest_mock import MockerFixture
from typed_pytest._mocker import TypedMocker

@pytest.fixture
def typed_mocker(mocker: MockerFixture) -> TypedMocker:
    """타입 안전한 mocker fixture"""
    return TypedMocker(mocker)
```

```toml
# pyproject.toml
[project.entry-points.pytest11]
typed_pytest = "typed_pytest._fixtures"
```

#### TEST

- [ ] `tests/integration/test_fixture.py` 생성
- [ ] fixture 주입 테스트
- [ ] 실제 테스트 시나리오

```python
# tests/integration/test_fixture.py
def test_typed_mocker_fixture_available(typed_mocker: TypedMocker):
    """typed_mocker fixture가 주입되는지"""
    assert typed_mocker is not None
    assert isinstance(typed_mocker, TypedMocker)

def test_full_workflow(typed_mocker: TypedMocker):
    """전체 워크플로우 테스트"""
    mock_service = typed_mocker.mock(UserService)
    mock_service.get_user.return_value = {"id": 1, "name": "Test"}

    result = mock_service.get_user(1)

    assert result == {"id": 1, "name": "Test"}
    mock_service.get_user.assert_called_once_with(1)
```

#### 커버리지 목표: 90%

---

### T202: patch 데코레이터 지원

**담당자**: TBD
**선행 Task**: T201
**우선순위**: P2 (Medium)

#### DEV

- [ ] `TypedMocker.patch_object()` 메소드 구현
- [ ] `TypedMocker.patch_dict()` 메소드 구현
- [ ] 데코레이터 방식 지원

#### TEST

- [ ] 다양한 patch 시나리오 테스트
- [ ] 중첩 patch 테스트
- [ ] 데코레이터 방식 테스트

```python
# tests/integration/test_patch_scenarios.py
class TestPatchScenarios:
    def test_patch_object(self, typed_mocker: TypedMocker):
        """객체 속성 patch"""
        ...

    def test_nested_patches(self, typed_mocker: TypedMocker):
        """중첩 patch 동작"""
        ...
```

#### 커버리지 목표: 85%

---

### T203: 통합 테스트 시나리오

**담당자**: TBD
**선행 Task**: T200, T201, T202
**우선순위**: P1 (High)

#### DEV

- [ ] 실제 사용 시나리오 기반 예제 코드 작성
- [ ] 문서용 예제 추출

#### TEST

- [ ] `tests/integration/test_real_scenarios.py` 생성
- [ ] 다양한 실제 사용 패턴 테스트

```python
# tests/integration/test_real_scenarios.py
"""실제 사용 시나리오를 테스트합니다."""

class TestRealWorldScenarios:
    def test_service_with_repository(self, typed_mocker: TypedMocker):
        """서비스 레이어가 리포지토리를 mock으로 사용"""
        mock_repo = typed_mocker.mock(UserRepository)
        mock_repo.find_by_id.return_value = User(id=1, name="Test")

        service = UserService(repository=mock_repo)
        user = service.get_user(1)

        assert user.name == "Test"
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_external_api_mock(self, typed_mocker: TypedMocker):
        """외부 API 클라이언트 mock"""
        mock_client = typed_mocker.mock(HttpClient)
        mock_client.get.return_value = {"status": "ok"}

        result = fetch_data(client=mock_client)

        assert result["status"] == "ok"
        mock_client.get.assert_called()

    def test_side_effect_usage(self, typed_mocker: TypedMocker):
        """side_effect를 활용한 테스트"""
        mock_service = typed_mocker.mock(UserService)
        mock_service.get_user.side_effect = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
            ValueError("No more users"),
        ]

        assert mock_service.get_user(1)["name"] == "First"
        assert mock_service.get_user(2)["name"] == "Second"
        with pytest.raises(ValueError):
            mock_service.get_user(3)
```

#### 커버리지 목표: 85%

---

## Phase 3: 타입 체커 지원

### T300: mypy 호환성 검증 및 최적화

**담당자**: TBD
**선행 Task**: T203
**우선순위**: P1 (High)
**병렬 가능**: T301과 병렬 가능

#### DEV

- [ ] mypy strict 모드에서 모든 오류 해결
- [ ] reveal_type 테스트 추가
- [ ] mypy.ini 또는 pyproject.toml 최적화

#### TEST

- [ ] `tests/typecheck/mypy/` 디렉토리 생성
- [ ] mypy 전용 타입 검사 테스트

```python
# tests/typecheck/mypy/test_mypy_inference.py
from typed_pytest import TypedMock, typed_mock
from tests.fixtures.sample_classes import UserService

def test_mypy_infers_return_type() -> None:
    mock = typed_mock(UserService)
    # reveal_type(mock)  # Should be TypedMock[UserService]
    # reveal_type(mock.get_user)  # Should be MockedMethod
    mock.get_user.return_value = {"id": 1}  # No error
```

```bash
# 테스트 실행
uv run mypy tests/typecheck/mypy/ --strict
```

---

### T301: pyright 호환성 검증 및 최적화

**담당자**: TBD
**선행 Task**: T203
**우선순위**: P1 (High)
**병렬 가능**: T300과 병렬 가능

#### DEV

- [ ] pyright strict 모드에서 모든 오류 해결
- [ ] pyrightconfig.json 최적화

#### TEST

- [ ] `tests/typecheck/pyright/` 디렉토리 생성
- [ ] pyright 전용 타입 검사 테스트

```bash
# 테스트 실행
uv run pyright tests/typecheck/pyright/
```

---

### T302: 타입 스텁 생성 (필요시)

**담당자**: TBD
**선행 Task**: T300, T301
**우선순위**: P2 (Medium)

#### DEV

- [ ] `stubs/typed_pytest/` 디렉토리 생성 (필요시)
- [ ] `.pyi` 파일 작성 (필요시)
- [ ] stubtest로 스텁 검증

#### TEST

- [ ] stubtest 통과 확인
- [ ] 스텁과 런타임 일치 검증

```bash
# stubtest 실행
uv run stubtest typed_pytest --allowlist stubtest_allowlist.txt
```

---

## Phase 4: 고급 기능

### T400: Async 메소드 지원

**담당자**: TBD
**선행 Task**: Phase 2 완료
**우선순위**: P2 (Medium)
**병렬 가능**: T401, T402, T403과 병렬 가능

#### DEV

- [ ] `AsyncMockedMethod` 클래스 구현
- [ ] TypedMock에서 async 메소드 인식
- [ ] AsyncMock 통합

```python
# src/typed_pytest/_async.py
from typing import Generic, ParamSpec, TypeVar, Coroutine

P = ParamSpec('P')
R = TypeVar('R')

class AsyncMockedMethod(Generic[P, R]):
    """비동기 메소드를 위한 MockedMethod"""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def assert_awaited(self) -> None: ...
    def assert_awaited_once(self) -> None: ...
    def assert_awaited_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    # ...
```

#### TEST

- [ ] async 메소드 mock 테스트
- [ ] await 동작 테스트
- [ ] assert_awaited_* 테스트

```python
# tests/unit/test_async.py
import pytest

class TestAsyncMockedMethod:
    @pytest.mark.asyncio
    async def test_async_mock_can_be_awaited(self, typed_mocker):
        mock = typed_mocker.mock(UserService)
        mock.async_get_user.return_value = {"id": 1}

        result = await mock.async_get_user(1)

        assert result == {"id": 1}
        mock.async_get_user.assert_awaited_once_with(1)
```

#### 커버리지 목표: 85%

---

### T401: Property Mock 지원

**담당자**: TBD
**선행 Task**: Phase 2 완료
**우선순위**: P2 (Medium)
**병렬 가능**: 가능

#### DEV

- [ ] Property 감지 로직 구현
- [ ] PropertyMock 통합
- [ ] getter/setter mock 지원

#### TEST

- [ ] property mock 테스트
- [ ] getter/setter 분리 테스트

```python
# tests/unit/test_property_mock.py
class TestPropertyMock:
    def test_property_can_be_mocked(self, typed_mocker):
        mock = typed_mocker.mock(UserService)
        type(mock).connection_status = PropertyMock(return_value="connected")

        assert mock.connection_status == "connected"
```

#### 커버리지 목표: 80%

---

### T402: Class Method / Static Method 지원

**담당자**: TBD
**선행 Task**: Phase 2 완료
**우선순위**: P2 (Medium)
**병렬 가능**: 가능

#### DEV

- [ ] classmethod/staticmethod 감지
- [ ] 적절한 mock 생성

#### TEST

- [ ] classmethod mock 테스트
- [ ] staticmethod mock 테스트

---

### T403: 중첩 Mock 지원

**담당자**: TBD
**선행 Task**: Phase 2 완료
**우선순위**: P3 (Low)
**병렬 가능**: 가능

#### DEV

- [ ] 중첩 객체에 대한 TypedMock 자동 생성
- [ ] 깊은 속성 접근 지원

#### TEST

- [ ] 중첩 mock 테스트
- [ ] 깊은 호출 체인 테스트

```python
# tests/unit/test_nested_mock.py
class TestNestedMock:
    def test_nested_attribute_is_typed_mock(self, typed_mocker):
        mock = typed_mocker.mock(ComplexService)
        # mock.user_service.get_user도 MockedMethod여야 함
        mock.user_service.get_user.return_value = {"id": 1}
        ...
```

---

## 담당자 배정 가이드

### 역할별 추천 Task

| 역할 | 추천 Task | 이유 |
|------|-----------|------|
| 테크 리드 | T000, T104, T105 | 프로젝트 설정 및 API 설계 |
| 시니어 개발자 A | T100, T101, T102 | 핵심 제네릭 구현 |
| 시니어 개발자 B | T200, T201, T202 | pytest 통합 |
| 미들 개발자 A | T103, T300, T301 | 팩토리 및 타입 체커 |
| 미들 개발자 B | T203, T400, T401 | 통합 테스트 및 고급 기능 |
| 주니어 개발자 | T001, T002, T302 | 인프라 및 스텁 |

### 병렬 작업 가능 그룹

```
그룹 1 (독립적):
  T000 → T001 → T002

그룹 2 (Phase 1 핵심, 순차적):
  T100 ─┬→ T101 ─→ T102 → T103 → T104 → T105
        └→ (T100 완료 후 T101 시작)

그룹 3 (Phase 2, T104 이후):
  T200 → T201 → T202 → T203

그룹 4 (Phase 3, 병렬 가능):
  T300 ─┬→ T302
  T301 ─┘

그룹 5 (Phase 4, 모두 병렬 가능):
  T400
  T401
  T402
  T403
```

---

## 진행 상태 추적

### Task 상태 정의

| 상태 | 설명 |
|------|------|
| `BACKLOG` | 아직 시작하지 않음 |
| `IN_PROGRESS` | 개발 중 |
| `IN_REVIEW` | 코드 리뷰 중 |
| `TESTING` | 테스트 검증 중 |
| `DONE` | 완료 |
| `BLOCKED` | 차단됨 (사유 명시) |

### 현재 상태

| Task | 담당자 | 상태 | 비고 |
|------|--------|------|------|
| T000 | Claude | DONE | 프로젝트 구조 완료 |
| T001 | Claude | DONE | 테스트 인프라 완료 |
| T002 | Claude | DONE | 샘플 클래스 정의 완료 |
| T100 | Claude | DONE | MockProtocol, AsyncMockProtocol 완료 |
| T101 | Claude | DONE | MockedMethod, AsyncMockedMethod 완료 |
| T102 | Claude | DONE | TypedMock 제네릭 클래스 완료 |
| T103 | Claude | DONE | typed_mock 팩토리 함수 완료 |
| T104 | Claude | DONE | 공개 API 정의 완료 |
| T105 | Claude | DONE | 기본 타입 체커 호환성 검증 완료 |
| T200 | Claude | DONE | TypedMocker 클래스 구현 완료 |
| T201 | Claude | DONE | typed_mocker fixture 구현 완료 |
| T202 | Claude | DONE | patch_object, patch_dict 메소드 구현 완료 |
| T203 | Claude | DONE | 실제 사용 시나리오 통합 테스트 완료 |
| T300 | Claude | DONE | mypy strict 호환성, reveal_type 테스트, 설정 최적화 완료 |
| T301 | - | BACKLOG | |
| T302 | - | BACKLOG | |
| T400 | - | BACKLOG | |
| T401 | - | BACKLOG | |
| T402 | - | BACKLOG | |
| T403 | - | BACKLOG | |

---

## Definition of Done (DoD)

각 Task는 다음 조건을 모두 만족해야 `DONE` 상태가 됩니다:

1. **코드 완성**: 모든 DEV 항목 완료
2. **테스트 통과**: 모든 TEST 항목 완료
3. **커버리지 충족**: 해당 Task의 커버리지 목표 달성
4. **타입 체크 통과**: mypy, pyright 오류 없음
5. **린트 통과**: ruff 오류 없음
6. **코드 리뷰 완료**: 최소 1명 승인
7. **문서화**: 필요시 docstring/주석 추가

---

*문서 버전: 1.0*
*최종 수정: 2024-12*
