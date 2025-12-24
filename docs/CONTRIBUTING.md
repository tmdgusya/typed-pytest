# Contributing Guide - typed-pytest

## 1. 개발 환경 설정

### 1.1 필수 요구사항

- Python 3.13+
- uv 패키지 매니저

### 1.2 초기 설정

```bash
# 저장소 클론
git clone https://github.com/your-org/typed-pytest.git
cd typed-pytest

# 의존성 설치
uv sync --all-extras

# pre-commit 훅 설치 (선택)
uv run pre-commit install
```

### 1.3 개발 의존성

```bash
# 모든 개발 도구 설치
uv sync --extra dev
```

---

## 2. 코드 스타일 컨벤션

### 2.1 Python 스타일 가이드

**기본 원칙**: PEP 8 + Google Python Style Guide

#### 포매팅

```bash
# ruff로 자동 포매팅
uv run ruff format src/ tests/

# ruff로 린팅 체크
uv run ruff check src/ tests/
```

#### 네이밍 컨벤션

| 항목 | 규칙 | 예시 |
|------|------|------|
| 클래스 | PascalCase | `TypedMock`, `MockedMethod` |
| 함수/메소드 | snake_case | `typed_mock()`, `assert_called_once()` |
| 상수 | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT` |
| Private | 언더스코어 접두사 | `_internal_method()`, `_cache` |
| TypeVar | 단일 대문자 또는 설명적 | `T`, `T_co`, `ReturnType` |
| Protocol | 형용사/동사+able | `Callable`, `MockProtocol` |

#### 임포트 순서

```python
# 1. 표준 라이브러리
from typing import TYPE_CHECKING, Generic, TypeVar
from unittest.mock import MagicMock

# 2. 서드파티
import pytest
from pytest_mock import MockerFixture

# 3. 로컬
from typed_pytest._mock import TypedMock
from typed_pytest._protocols import MockProtocol

if TYPE_CHECKING:
    # 타입 체킹 전용 임포트
    from typing import ParamSpec
```

### 2.2 타입 힌트 컨벤션

#### 필수 타입 힌트

모든 공개 API는 **반드시** 타입 힌트를 포함해야 합니다:

```python
# Good
def typed_mock(cls: type[T], /, **kwargs: Any) -> TypedMock[T]:
    """타입 안전한 mock 객체를 생성합니다."""
    ...

# Bad - 타입 힌트 누락
def typed_mock(cls, **kwargs):
    ...
```

#### Generic 타입 표기

```python
# Python 3.12+ 신규 문법 사용 권장
class TypedMock[T](MagicMock):
    ...

# 또는 전통적 방식 (하위 호환성 필요시)
T = TypeVar('T')

class TypedMock(MagicMock, Generic[T]):
    ...
```

#### Union 타입

```python
# Python 3.10+ 문법 사용
def process(value: str | int | None) -> str:
    ...

# X 연산자 사용 (Union 대신)
from collections.abc import Callable
callback: Callable[[int], str] | None = None
```

### 2.3 Docstring 컨벤션

**Google Style Docstring** 사용:

```python
def typed_mock(
    cls: type[T],
    /,
    *,
    spec_set: bool = False,
    **kwargs: Any,
) -> TypedMock[T]:
    """타입 안전한 mock 객체를 생성합니다.

    원본 클래스의 타입 정보를 유지하면서 Mock 기능을 제공하는
    TypedMock 인스턴스를 반환합니다.

    Args:
        cls: Mock으로 만들 원본 클래스.
        spec_set: True일 경우 spec에 없는 속성 접근 시 AttributeError 발생.
        **kwargs: MagicMock에 전달할 추가 인자.

    Returns:
        원본 클래스의 타입 정보를 가진 TypedMock 인스턴스.

    Raises:
        TypeError: cls가 클래스가 아닐 경우.

    Example:
        >>> mock_service = typed_mock(UserService)
        >>> mock_service.get_user.return_value = {"id": 1}
        >>> mock_service.get_user(1)
        {'id': 1}
    """
```

---

## 3. 테스트 컨벤션

### 3.1 테스트 구조

```
tests/
├── conftest.py              # 공통 fixture
├── unit/                    # 단위 테스트
│   ├── test_typed_mock.py
│   ├── test_mocked_method.py
│   └── test_protocols.py
├── integration/             # 통합 테스트
│   ├── test_pytest_integration.py
│   └── test_type_checker.py
└── e2e/                     # E2E 테스트 (실제 사용 시나리오)
    └── test_real_world.py
```

### 3.2 테스트 네이밍

```python
# 패턴: test_<대상>_<조건>_<예상결과>
def test_typed_mock_with_class_returns_mock_with_spec():
    ...

def test_mocked_method_assert_called_once_raises_when_not_called():
    ...

# 클래스 기반 테스트
class TestTypedMock:
    """TypedMock 클래스 테스트"""

    def test_creates_mock_with_original_type_hints(self):
        ...

    def test_supports_mock_assertion_methods(self):
        ...
```

### 3.3 테스트 작성 규칙

#### AAA 패턴 (Arrange-Act-Assert)

```python
def test_typed_mock_return_value():
    # Arrange
    mock_service = typed_mock(UserService)
    expected = {"id": 1, "name": "John"}
    mock_service.get_user.return_value = expected

    # Act
    result = mock_service.get_user(1)

    # Assert
    assert result == expected
    mock_service.get_user.assert_called_once_with(1)
```

#### Fixture 활용

```python
# conftest.py
import pytest
from typed_pytest import TypedMock, typed_mock

@pytest.fixture
def mock_user_service() -> TypedMock[UserService]:
    """UserService의 TypedMock 인스턴스"""
    return typed_mock(UserService)

# test_*.py
def test_with_fixture(mock_user_service: TypedMock[UserService]):
    mock_user_service.get_user.return_value = {"id": 1}
    ...
```

#### 파라미터화 테스트

```python
import pytest

@pytest.mark.parametrize(
    "method_name,expected_type",
    [
        ("assert_called", type(None)),
        ("assert_called_once", type(None)),
        ("call_count", int),
    ],
)
def test_mocked_method_has_mock_attributes(method_name: str, expected_type: type):
    mock = typed_mock(UserService)
    attr = getattr(mock.get_user, method_name)
    if callable(attr):
        result = attr()
    else:
        result = attr
    assert isinstance(result, expected_type)
```

### 3.4 커버리지 요구사항

**최소 커버리지: 80%**

```bash
# 커버리지 측정
uv run pytest --cov=src/typed_pytest --cov-report=term-missing --cov-report=html

# 커버리지 실패 시 CI 실패
uv run pytest --cov=src/typed_pytest --cov-fail-under=80
```

#### 커버리지 제외 항목

```python
# pragma: no cover 주석으로 제외 가능 (합리적 사유 필요)
if TYPE_CHECKING:  # pragma: no cover
    from typing import ParamSpec
```

---

## 4. Git 워크플로우

### 4.1 브랜치 전략

```
main                 # 안정 버전, 배포 대상
├── develop          # 개발 통합 브랜치
│   ├── feature/*    # 기능 개발
│   ├── fix/*        # 버그 수정
│   └── refactor/*   # 리팩토링
└── release/*        # 릴리스 준비
```

### 4.2 브랜치 네이밍

```bash
# 패턴: <type>/<task-id>-<short-description>
feature/T001-typed-mock-core
fix/T003-assertion-type-hints
refactor/T005-protocol-cleanup
```

### 4.3 커밋 메시지

**Conventional Commits** 사용:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 종류

| Type | 설명 |
|------|------|
| `feat` | 새로운 기능 |
| `fix` | 버그 수정 |
| `test` | 테스트 추가/수정 |
| `docs` | 문서 변경 |
| `refactor` | 리팩토링 |
| `style` | 코드 스타일 (포매팅 등) |
| `chore` | 빌드, 설정 변경 |

#### 예시

```bash
feat(mock): TypedMock 제네릭 클래스 구현

- Generic[T] 기반 TypedMock 클래스 추가
- MagicMock 상속으로 기존 mock 기능 유지
- __class_getitem__ 오버라이드로 런타임 타입 정보 저장

Closes #12

---

test(mock): TypedMock 단위 테스트 추가

- 기본 생성 테스트
- spec 파라미터 테스트
- 타입 힌트 검증 테스트

Coverage: 85%
```

### 4.4 Pull Request 규칙

#### PR 템플릿

```markdown
## 변경 사항
- [ ] 기능 구현 완료
- [ ] 테스트 추가 (커버리지 80% 이상)
- [ ] 타입 체크 통과 (mypy, pyright)
- [ ] 문서 업데이트

## 관련 Task
- Closes #<task-number>

## 테스트 방법
1. `uv run pytest tests/unit/test_xxx.py`
2. 예상 결과: ...

## 스크린샷 (해당시)
```

#### 리뷰 체크리스트

- [ ] 타입 힌트가 올바른가?
- [ ] 테스트가 충분한가?
- [ ] Docstring이 작성되었는가?
- [ ] Breaking change가 있는가?

---

## 5. 개발-테스트 회귀 사이클

### 5.1 TDD 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│                    Development Cycle                        │
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │  RED    │───▶│  GREEN  │───▶│ REFACTOR│                │
│   │ (Test)  │    │ (Code)  │    │         │                │
│   └─────────┘    └─────────┘    └─────────┘                │
│        │                              │                     │
│        └──────────────────────────────┘                     │
│                    Iterate                                  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 각 Task의 개발 순서

1. **테스트 먼저 작성** (RED)
   ```bash
   # 실패하는 테스트 작성
   uv run pytest tests/unit/test_new_feature.py -v
   # Expected: FAILED
   ```

2. **구현** (GREEN)
   ```bash
   # 테스트 통과하는 최소 코드 작성
   uv run pytest tests/unit/test_new_feature.py -v
   # Expected: PASSED
   ```

3. **리팩토링** (REFACTOR)
   ```bash
   # 코드 정리 후 테스트 재실행
   uv run pytest tests/unit/test_new_feature.py -v
   # Expected: PASSED
   ```

4. **전체 검증**
   ```bash
   # 타입 체크
   uv run mypy src/
   uv run pyright src/

   # 전체 테스트 + 커버리지
   uv run pytest --cov=src/typed_pytest --cov-fail-under=80

   # 린트
   uv run ruff check src/ tests/
   ```

### 5.3 CI/CD 파이프라인

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Lint
        run: uv run ruff check src/ tests/

      - name: Type check (mypy)
        run: uv run mypy src/

      - name: Type check (pyright)
        run: uv run pyright src/

      - name: Test with coverage
        run: uv run pytest --cov=src/typed_pytest --cov-fail-under=80 --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

---

## 6. 릴리스 프로세스

### 6.1 버전 규칙

**Semantic Versioning (SemVer)** 사용:

```
MAJOR.MINOR.PATCH
  │     │     └── 버그 수정 (하위 호환)
  │     └──────── 기능 추가 (하위 호환)
  └────────────── Breaking changes
```

### 6.2 Changelog 작성

```markdown
# Changelog

## [0.2.0] - 2024-12-XX

### Added
- TypedMocker pytest fixture 추가
- AsyncMock 지원

### Changed
- MockedMethod 시그니처 개선

### Fixed
- 중첩 mock 타입 추론 오류 수정
```

---

## 7. 문의 및 도움

- **Issue**: GitHub Issues 사용
- **Discussion**: GitHub Discussions
- **Code Review**: PR 코멘트

---

*문서 버전: 1.0*
*최종 수정: 2024-12*
