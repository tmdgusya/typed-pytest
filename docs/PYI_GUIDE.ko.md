# 기여자를 위한 `.pyi` 파일 히치하이커 가이드

> *"당황하지 마세요!" — 이 가이드는 `.pyi` 파일을 이해하고 typed-pytest에 기여하는 것을 도와줍니다.*

---

**[English Version](PYI_GUIDE.md)**

---

## 목차

1. [`.pyi` 파일이란?](#pyi-파일이란)
2. [왜 `.pyi` 파일이 필요한가?](#왜-pyi-파일이-필요한가)
3. [타입 체크어는 `.pyi` 파일을 어떻게 사용하는가?](#타입-체크어는-pyi-파일을-어떻게-사용하는가)
4. [런타임 타입과 정적 타입의 차이](#런타임-타입과-정적-타입의-차이)
5. [`.pyi` 파일의 일반적인 패턴](#pyi-파일의-일반적인-패턴)
6. [이해해야 할 주요 한계](#이해해야-할-주요-한계)
7. [typed-pytest에 기여하기: 실용적 가이드](#typed-pytest에-기여하기-실용적-가이드)
8. [일반적인 문제 해결](#일반적인-문제-해결)

---

## `.pyi` 파일이란?

`.pyi` 파일은 Python을 위한 **타입 스텁 파일**입니다. 실제 코드를 포함하지 않고 IDE와 타입 체크어에게 모듈에 어떤 타입이 존재하는지 알려주는 "타입 힌트 사전"이라고 생각하면 됩니다.

### 비유: 레스토랑 메뉴

레스토랑 메뉴를 생각해보세요:
- **주방** (`.py` 파일) — 음식을 실제로 요리하는 실제 코드
- **메뉴** (`.pyi` 파일) — 고객에게 어떤 요리가 있고 어떤 재료가 들어가는지 알려줌

메뉴는 음식을 요리하지 않습니다 — 그냥 무엇이 있는지 설명할 뿐입니다. 마찬가지로 `.pyi` 파일은 코드를 실행하지 않습니다 — 그냥 타입을 설명할 뿐입니다.

### 예시

**표준 `.pyi` 방식** (typed-pytest는 이 방식을 사용하지 않음):
```python
# module.py - 런타임 코드
class TypedMock:
    def __init__(self, spec=None, **kwargs):
        self._mock = ...

# module.pyi - 타입 스텁 (별도 파일)
class TypedMock:
    def __init__(self, spec: type[_T] | None = None) -> None: ...
```

**typed-pytest의 방식** — 런타임 스텁을 생성합니다:
```python
# typed_pytest_stubs/_runtime.py (typed-pytest-generator가 생성)
@typing.overload
def typed_mock(cls: type[UserService], ...) -> UserService_TypedMock: ...

class UserService_TypedMock:
    @property
    def get_user(self) -> MockedMethod[[int], dict]: ...
```

이렇게 생성된 스텁은 여러분의 클래스에 대해 완벽한 IDE 자동완성을 제공합니다!

---

## 왜 `.pyi` 파일이 필요한가?

Python은 **동적 타입 언어**입니다, 이는 다음을 의미합니다:

```python
# 이것은 유효한 Python — 하지만 result의 타입은?
result = some_mock.some_method(123)
```

타입 체크어(mypy, pyright 등)는 `some_method`가 무엇을 반환하거나 어떤 파라미터를 받는지 자동으로 알 수 없습니다. 이것이 `.pyi` 파일이 도움이 되는 곳입니다!

### `.pyi` 파일이 없을 때의 문제

```python
from unittest.mock import MagicMock

mock = MagicMock()
mock.get_user(1)  # IDE는 get_user가 무엇을 반환하는지 모름!
mock.get_user.assert_called_once_with(1)  # 타입 체크가 안 됨!
```

### `.pyi` 파일이 있을 때의 해결책

```python
from typed_pytest import TypedMock, typed_mock

mock_service: TypedMock[UserService] = typed_mock(UserService)
mock_service.get_user.assert_called_once_with(1)  # ✅ 완벽한 타입 체크!
```

---

## 타입 체크어는 `.pyi` 파일을 어떻게 사용하는가?

타입 체크어(mypy, pyright 등)를 실행할 때, 다음과 같은 일이 일어납니다:

```
1. 코드를 작성함
   ↓
2. 타입 체크어가 .py 파일을 읽음
   ↓
3. 타입 체크어가 일치하는 .pyi 스텁 파일을 찾음
   ↓
4. 타입 체크어가 .pyi를 사용하여 타입을 이해함
   ↓
5. 타입 체크어가 오류를 보고하거나 정확성을 확인함
```

### 예시: pyright가 스텁을 사용하는 방식

```
user_code.py          user_code.pyi (존재하면)
┌──────────────┐      ┌──────────────┐
│ typed_mock() │ ───▶ │ "나는         │
│      ↓       │      │  TypedMock   │
│ get_user.    │      │  [T]를 반환함"│
│ assert_...   │      └──────────────┘
└──────────────┘
```

**중요**: 타입 체크어는 둘 다 존재할 때 `.py` 파일보다 `.pyi` 파일을 우선시합니다. `.pyi` 파일은 타입 체크 목적으로 실제 구현을 "가립니다".

---

## 런타임 타입과 정적 타입의 차이

이것은 **가장 중요한 개념**입니다!

### 런타임: 실제로 일어나는 일

Python이 코드를 실행할 때, 문장을 한 줄씩 실행합니다:

```python
# 이것은 실제로 실행되고 객체를 생성함
mock = typed_mock(UserService)  # TypedMock 인스턴스 생성
mock.get_user(1)  # TypedMock.__getattr__("get_user")를 호출함
```

런타임에서:
- `typed_mock()`이 `spec=UserService`로 `TypedMock` 인스턴스를 생성함
- `__getattr__`이 실제 속성 이름과 함께 호출됨
- `MockedMethod` 객체가 생성됨
- 코드가 계속 실행됨

### 정적: 타입 체크어가 보는 것

타입 체크어는 코드를 **실행하지 않고** 분석합니다:

```python
mock: TypedMock[UserService] = typed_mock(UserService)
mock.get_user(1)
```

타입 체크어가 보는 것:
- `mock`은 `TypedMock[UserService]` 타입
- `mock.get_user`은 `MockedMethod`를 반환함 (`__getattr__`에서)

**문제점**: 타입 체크어는 어떤 속성 이름에 접근할지 예측할 수 없습니다! `__getattr__`가 존재하는 것을 알지만, `"get_user"`, `"create_user"` 같은 구체적인 이름은 모릅니다.

---

## `.pyi` 파일의 일반적인 패턴

typed-pytest의 `.pyi` 파일에서 보게 될 패턴들:

### 1. 메서드 본문을 위한 줄임표 (`...`)

```python
def __init__(self, spec: type[_T] | None = None) -> None: ...
```

`...`(줄임표)는 "이 메서드는 존재하지만 스텁에는 본문이 없다"는 의미입니다. 타입 정보를 위한 플레이스홀더일 뿐입니다.

### 2. 제네릭을 위한 타입 변수

```python
_T = TypeVar("_T")

class TypedMock(Generic[_T]):
    # _T가 실제 타입으로 대체됨 (예: UserService)
    def get_typed_class(self) -> type[_T] | None: ...
```

### 3. `|` 를 사용한 선택적 타입

```python
def __init__(self, name: str | None = None) -> None: ...
# 동등함: name: Optional[str] = None
```

### 4. 프로퍼티 (게터/세터)

```python
@property
def return_value(self) -> Any: ...

@return_value.setter
def return_value(self, value: Any) -> None: ...
```

### 5. `Any` 타입

```python
def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
```

`Any`는 "어떤 타입이든 허용됨"을 의미합니다 — 타입 체크어에게 "이건 신경 쓰지 말고 그냥 받아들여"라고 알려줍니다.

---

## 이해해야 할 주요 한계

기여하기 전에, `.pyi` 파일이 **못 하는 것**을 알아야 합니다:

### ❌ `__getattr__`은 속성 이름 자동완성을 제공하지 않음

```python
class TypedMock:
    def __getattr__(self, name: str) -> MockedMethod: ...
```

**의미:**
- ✅ 타입 체크어는 `mock.get_user`가 `MockedMethod`를 반환함을 앎
- ❌ 타입 체크어는 "get_user"를 완성 옵션으로 제안할 수 없음

**왜?** 타입 체크어는 런타임에 어떤 속성 이름을 사용할지 모릅니다. 패턴(`__getattr__`가 어떤 이름에 대해서도 `MockedMethod`를 반환함)만 알 뿐입니다.

### ❌ 원래 메서드 시그니처가 보존되지 않음

```python
# UserService.get_user 시그니처:
# def get_user(self, user_id: int) -> dict

mock.get_user(1)  # 파라미터가 타입 체크되지 않음!
```

**의미:**
- ❌ `mock.get_user(1)`은 `1`이 올바른 타입인지 알려주지 않음
- ✅ 하지만 `mock.get_user.assert_called_once_with(1)`은 타입 체크됨!

### ❌ 메서드 이름을 "자동 발견"할 수 없음

```python
# .pyi에서 이렇게 표현할 방법이 없음:
# "UserService를 보고 get_user, create_user 등을 자동 생성해줘"
```

`.pyi` 파일은 모든 가능한 속성을 명시적으로 나열해야 합니다, 그래서 우리는 포괄자로 `__getattr__`를 사용합니다.

---

## typed-pytest에 기여하기: 실용적 가이드

이제 기본을 이해했으니, 기여하는 방법:

### 1단계: 추가하는 것을 이해하기

스스로에게 물어보세요:
- 런타임 코드에 **새로운 기능**을 추가하는 건가?
- **타입 힌트**를 업데이트하는 건가?
- **버그**를 수정하는 건가?
- **스텁 생성기**를 수정하는 건가?

### 2단계: typed-pytest 아키텍처 이해하기

typed-pytest는 전통적인 `.pyi` 파일을 사용하지 않습니다. 대신:

| 컴포넌트 | 목적 |
|----------|------|
| `src/typed_pytest/*.py` | 코어 라이브러리 (TypedMock, MockedMethod 등) |
| `src/typed_pytest_generator/` | 스텁을 생성하는 CLI 도구 |
| `typed_pytest_stubs/_runtime.py` | **자동 생성된** IDE 자동완성용 스텁 |

**중요:** `typed_pytest_stubs/`는 자동 생성됩니다! 수동으로 편집하지 마세요.

### 3단계: 예시 — TypedMock에 새로운 메서드 추가

**런타임 코드 업데이트:**
```python
# src/typed_pytest/_mock.py
class TypedMock:
    def reset_mock(self, return_value: bool = False) -> None:
        """mock을 초기 상태로 재설정합니다."""
        self._mock.reset_mock(return_value=return_value)
```

타입 힌트가 이미 `.py` 파일에 있으므로 별도의 `.pyi` 파일이 필요 없습니다!

### 4단계: 스텁 생성기 수정 시

스텁 생성 방식을 변경하면 (`src/typed_pytest_generator/`), 재생성하고 테스트하세요:

```bash
# 스텁 재생성
uv run typed-pytest-generator

# 생성된 출력 확인
cat typed_pytest_stubs/_runtime.py
```

### 5단계: 변경 사항 테스트하기

변경 사항을 확인하려면 다음 명령들을 실행하세요:

```bash
# 모든 체크 실행
uv run pytest tests/
uv run ruff check src/
uv run ruff format src/

# 타입 체커 (4개 모두 통과해야 함)
uv run mypy src/
uv run pyright src/
uv run pyrefly check src/typed_pytest/
uv run ty check src/typed_pytest/
```

### 6단계: 따를 일반적인 패턴

#### 프로퍼티 추가
```python
# src/typed_pytest/_mock.py에서
@property
def my_property(self) -> ReturnType:
    return self._value

@my_property.setter
def my_property(self, value: ReturnType) -> None:
    self._value = value
```

#### 메서드 추가
```python
def my_method(self, param: ParamType, *, optional: OptType = None) -> ReturnType:
    ...
```

#### 타입 변수 사용
```python
from typing import TypeVar, Generic

T = TypeVar("T")

class TypedMock(Generic[T]):
    def get_typed(self) -> T:
        ...
```

---

## 일반적인 문제 해결

### 문제: "타입 체크어가 내 변경을 인식하지 못함"

**해결책:**
1. `.py` 파일에 적절한 타입 힌트를 업데이트했는지 확인하세요
2. 타입 체크어/IDE를 재시작하세요
3. `uv sync`를 실행하여 패키지를 재설치하세요

### 문제: "mock 메서드에 자동완성이 작동하지 않음"

**스텁을 생성했나요?** 실행하세요:
```bash
uv run typed-pytest-generator
```

스텁이 있는데도 자동완성이 안 되면:
- `typed_pytest`가 아닌 `typed_pytest_stubs`에서 `typed_mock`을 import하세요
- 타입 체커 설정을 확인하세요 (README의 pyrefly/ty 설정 참조)

### 문제: "타입 체크어가 '알 수 없는 속성'이라고 함"

**확인:**
1. 클래스 변경 후 스텁을 재생성했나요?
2. 클래스가 `[tool.typed-pytest-generator].targets`에 포함되어 있나요?
3. 스텁 재생성 후 타입 체커를 실행했나요?

### 문제: "메서드 이름 자동완성을 추가하고 싶음"

**그게 바로 typed-pytest-generator가 하는 일입니다!** 실행하세요:
```bash
uv run typed-pytest-generator -t your.module.YourClass
```

이렇게 하면 IDE 자동완성을 위해 클래스의 실제 메서드 이름이 포함된 스텁이 생성됩니다.

---

## 빠른 참조

| 개념 | 의미 |
|------|------|
| `.pyi` | 타입 스텁 파일 — 코드 없이 타입을 설명 |
| 런타임 | 코드가 실제로 실행될 때 일어나는 일 |
| 정적 | 타입 체크어가 분석하는 것 (실행 없이) |
| `__getattr__` | 알 수 없는 속성에 대해 호출되는 마법 메서드 |
| `...` (줄임표) | "여기 구현 없음"을 의미하는 플레이스홀더 |
| `Generic` | 여러 타입으로 작동할 수 있는 클래스 |
| `TypeVar` | 나중에 지정될 타입의 플레이스홀더 |

---

## 추가 읽기

- [PEP 484 — 타입 힌트](https://peps.python.org/pep-0484/)
- [mypy 문서](https://mypy.readthedocs.io/)
- [pyright 문서](https://microsoft.github.io/pyright/)
- [Python typing 모듈](https://docs.python.org/3/library/typing.html)

---

## 요약

- **`.pyi` 파일은 타입 스텁** — IDE와 타입 체크어가 코드를 이해하는 것을 도와줌
- **typed-pytest는 생성된 스텁을 사용** — 수동 `.pyi` 대신 `typed-pytest-generator` 실행
- **런타임과 정적 타입은 다름** — 스텁은 코드가 실행되는 방식에 영향을 주지 않음
- **4개의 타입 체커 지원** — mypy, pyright, pyrefly, ty
- **당황하지 마세요!** 혼란스럽다면, 올바른 질문을 하고 있는 것입니다

---

*기억하세요: 모든 전문가도 한때 초보였습니다. 이 가이드를 읽고 있다는 것은 올바른 길에 있다는 의미입니다!*
