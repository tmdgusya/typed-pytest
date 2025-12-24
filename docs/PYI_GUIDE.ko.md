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

**`typed_pytest/__init__.py`** (런타임 코드):
```python
class TypedMock:
    def __init__(self, spec=None, **kwargs):
        self._mock = ...  # 실제 구현

    def __getattr__(self, name):
        return MockedMethod()  # 여기서 마법이 일어남!
```

**`typed_pytest/__init__.pyi`** (타입 스텁):
```python
class TypedMock:
    _mock: Any

    def __init__(
        self,
        spec: type[_T] | None = None,
        *,
        wraps: _T | None = None,
        name: str | None = None,
        **kwargs: Any,
    ) -> None: ...

    def __getattr__(self, name: str) -> MockedMethod: ...
```

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
mock = TypedMock[UserService]()
mock.get_user(1)  # TypedMock.__getattr__("get_user")를 호출함
```

런타임에서:
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

### 2단계: `.py`와 `.pyi` 모두 업데이트하기

**항상 두 파일을 함께 업데이트하세요:**

| 파일 | 목적 |
|------|------|
| `.py` | 런타임 구현 (실제 동작) |
| `.pyi` | 타입 스텁 (IDE와 타입 체크어용) |

### 3단계: 예시 — 새로운 메서드 추가

**원래 코드:**
```python
# typed_pytest/__init__.py
class TypedMock:
    def reset_mock(self) -> None:
        """ mock을 초기 상태로 재설정합니다. """
        self._mock.reset_mock()
```

**새로운 기능으로 업데이트된 코드:**
```python
# typed_pytest/__init__.py
class TypedMock:
    def reset_mock(self, return_value: bool = False) -> None:
        """ mock을 초기 상태로 재설정합니다. """
        self._mock.reset_mock(return_value=return_value)
```

**`.pyi`도 업데이트해야 함:**
```python
# typed_pytest/__init__.pyi
class TypedMock:
    def reset_mock(self, return_value: bool = False) -> None: ...
```

### 4단계: 변경 사항 테스트하기

변경 사항을 확인하려면 다음 명령들을 실행하세요:

```bash
# 모든 체크 실행
uv run pytest tests/
uv run ruff check src/
uv run ruff format src/
uv run mypy src/
uv run pyright src/
```

### 5단계: 따를 일반적인 패턴

#### 프로퍼티 추가
```python
# .pyi에서
@property
def my_property(self) -> ReturnType: ...

@my_property.setter
def my_property(self, value: ReturnType) -> None: ...
```

#### 메서드 추가
```python
# .pyi에서
def my_method(self, param: ParamType, /, *, optional: OptType = None) -> ReturnType: ...
```

#### 타입 변수 사용
```python
# .pyi 상단에서
_T = TypeVar("_T")

# 클래스에서
class TypedMock(Generic[_T]):
    def get_typed(self) -> _T: ...
```

---

## 일반적인 문제 해결

### 문제: "타입 체크어가 내 변경을 인식하지 못함"

**해결책:** `.py`와 `.pyi` 파일 둘 다 업데이트했는지 확인하세요. 또한 타입 체크어/IDE를 재시작해보세요.

### 문제: "mock 메서드에 자동완성이 작동하지 않음"

**예상된 동작입니다!** `__getattr__` 한계로 인해:
- `mock.some_method.assert_called_once()`에 접근할 수 있음
- 하지만 IDE가 자동완성에서 `some_method`를 제안하지 않음

### 문제: "타입 체크어가 '알 수 없는 속성'이라고 함"

**확인:**
1. 메서드를 `.py`와 `.pyi` 둘 다 추가했나요?
2. 메서드 시그니처가 맞나요?
3. 변경 후 타입 체크어를 실행했나요?

### 문제: "메서드 이름 자동완성을 추가하고 싶음"

**안타깝게도, 이것은 Python 타입 시스템의 근본적인 한계입니다.** `.pyi` 형식은 "클래스 X의 모든 메서드가 여기서 사용 가능"을 표현할 수 없습니다. 다음이 필요합니다:
- IDE 특정 플러그인
- 또는 완전히 다른 접근 방식

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
- **런타임과 정적 타입은 다름** — `.pyi`는 코드가 실행되는 방식에 영향을 주지 않음
- **`__getattr__`에는 한계가 있음** — 타입 정보는 제공하지만 속성 이름 자동완성은 제공하지 않음
- **기여하려면 두 파일을 모두 업데이트해야 함** — 항상 `.py`와 `.pyi`를 동기화 유지
- **당황하지 마세요!** 혼란스럽다면, 올바른 질문을 하고 있는 것입니다

---

*기억하세요: 모든 전문가도 한때 초보였습니다. 이 가이드를 읽고 있다는 것은 올바른 길에 있다는 의미입니다!*
