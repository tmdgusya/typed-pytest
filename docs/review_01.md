# typed-pytest Code Review #01

**Reviewer:** Tech Lead (Claude Code)
**Date:** 2024-12-24
**Branch:** main
**Status:** NEEDS IMPROVEMENT

---

## Executive Summary

전체적으로 Phase 1, 2 구현이 잘 되어 있으나, **`CONTRIBUTING.md`에서 정의한 커버리지 기준(80%)을 충족하지 못하고**, 일부 기능이 문서화된 명세와 다르게 동작하고 있습니다. 이 리뷰는 3개의 Critical Issue와 5개의 Improvement Issue를 식별했습니다.

---

## Critical Issues ( 즉시 수정 필요 )

### C001: Coverage Threshold가 Spec 대비 현저히 낮음

**위치:** `pyproject.toml:113`

**문제:** CONTRIBUTING.md 3.4절에서 **최소 커버리지 80%**를 요구하지만, 현재 `fail_under = 35`로 설정되어 있습니다.

```toml
# 현재 설정
fail_under = 35  # ❌ 80이어야 함

# 기대되는 설정
fail_under = 80  # ✅
```

**영향:** CI에서 실제 코드 품질 문제가 감지되지 않을 수 있습니다.

**수정 제안:**
```toml
fail_under = 80
```

**참고:** 주석에서 "pytest plugin loading order로 인한 실제 커버리지보다 낮게 측정된다"고 언급하고 있으나, 이는 측정 방식 개선으로 해결해야지 기준을 낮추는 것은 적절하지 않습니다.

---

### C002: `strict` 모드가 작동하지 않음 (noop)

**위치:** `src/typed_pytest/_factory.py:93-96`

**문제:** `typed_mock()`의 `strict` 파라미터가 문서화되어 있으나 실제로는 아무것도 하지 않습니다.

```python
# 현재 구현
if strict:
    # TODO: strict 모드 구현 (호출되지 않은 mock 경고)
    pass  # ❌ 아무것도 하지 않음
```

**문서화된 동작:**
```
strict: True일 경우 호출되지 않은 mock에 대해 경고 (향후 구현 예정).
```

**문제점:**
1. 문서에는 "향후 구현 예정"이라고 되어 있지만, `__init__.py`의 `__all__`에 포함되어 있어 공개 API로 노출됨
2. 사용자가 `strict=True`를 전달해도 경고 없이 통과되어 혼란을 줄 수 있음

**수정 제안 (둘 중 하나):**
1. **비활성화:** `strict` 파라미터 제거 또는 `**kwargs`로 이동
2. **구현:** MockStrictWarning 구현

```python
# Option 1: Remove strict from overload
@overload
def typed_mock(
    cls: type[T],
    /,
    *,
    spec_set: bool = False,
    name: str | None = None,
    **kwargs: Any,
) -> TypedMock[T]: ...

# Option 2: 구현
if strict:
    warnings.warn(
        "Unasserted mock warning: ...",
        MockStrictWarning,
        stacklevel=2
    )
```

---

### C003: Async 메소드 자동 감지 미구현

**위치:** `src/typed_pytest/_mock.py:116-128`

**문제:** `UserService`에는 `async_get_user` 같은 비동기 메소드가 있지만, `TypedMock`은 이 메소드들을 `MagicMock`으로 반환합니다. 문서에는 "각 메소드는 MockedMethod로 래핑"라고 되어 있으나, Async 메소드와 동기 메소드를 구분하지 않습니다.

```python
# sample_classes.py에 정의된 async 메소드
async def async_get_user(self, user_id: int) -> dict[str, Any]: ...

# 현재: async_get_user 접근 시 MagicMock 반환
mock.async_get_user  # ❌ AsyncMockedMethod가 아닌 MagicMock
```

**영향:**
- `await mock.async_get_user(1)` 문법 사용 불가
- `assert_awaited_*` assertion 메소드 접근 불가

**수정 제안:**
`__getattr__`에서 메소드 시그니처를 분석하여 적절한 타입 반환

```python
if TYPE_CHECKING:
    from typing import get_type_hints, iscoroutinefunction

    def __getattr__(self, name: str) -> MockedMethod[..., Any]:
        # async 메소드 감지 로직 필요
        original = self.typed_class.__dict__.get(name)
        if original is not None and getattr(original, '__call__'):
            if hasattr(original, '__wrapped__') and iscoroutinefunction(original):
                return AsyncMockedMethod[...]  # AsyncMockedMethod 반환
        return MockedMethod[...]  # 동기 MockedMethod 반환
```

---

## Improvement Issues ( 개선 권장 )

### I001: Property Mock 미검증

**위치:** `tests/unit/test_typed_mock.py`, `tests/fixtures/sample_classes.py:121-129`

**문제:** `UserService`에는 `connection_status`와 `is_connected` 프로퍼티가 정의되어 있으나, Property Mock 테스트가 없습니다. T401은 BACKLOG로 표시되어 있습니다.

**현재 테스트:**
```python
# 프로퍼티 접근만 테스트, PropertyMock 사용하지 않음
def test_method_call_works(self) -> None:
    mock: TypedMock[UserService] = TypedMock(spec=UserService)
    # 프로퍼티 mock 테스트 누락
```

**수정 제안:** `PropertyMock`을 사용한 테스트 추가

```python
from unittest.mock import PropertyMock

def test_property_mock(self) -> None:
    mock: TypedMock[UserService] = TypedMock(spec=UserService)
    type(mock).connection_status = PropertyMock(return_value="disconnected")
    assert mock.connection_status == "disconnected"
```

---

### I002: ClassMethod/StaticMethod 미검증

**위치:** `tests/unit/test_typed_mock.py`, `tests/fixtures/sample_classes.py:131-141`

**문제:** `UserService.from_config()` (classmethod)와 `UserService.validate_email()` (staticmethod)가 정의되어 있으나, 이에 대한 Mock 테스트가 없습니다. T402는 BACKLOG로 표시되어 있습니다.

**수정 제안:** 해당 메소드들의 mock 테스트 추가

```python
def test_classmethod_mock(self) -> None:
    mock: TypedMock[UserService] = TypedMock(spec=UserService)
    mock.from_config.return_value = mock
    result = mock.from_config({"key": "value"})
    assert result is mock

def test_staticmethod_mock(self) -> None:
    mock: TypedMock[UserService] = TypedMock(spec=UserService)
    mock.validate_email.return_value = False
    assert mock.validate_email("test@test.com") is False
```

---

### I003: Nested Mock 미검증

**위치:** `tests/unit/test_typed_mock.py`, `tests/fixtures/sample_classes.py:165-176`

**문제:** `NestedService`는 `user_service`와 `product_repo` 속성을 가지며, T403은 BACKLOG입니다. 중첩된 mock의 타입 보존이 제대로 테스트되지 않았습니다.

```python
class NestedService:
    def __init__(self) -> None:
        self.user_service = UserService()  # 중첩된 속성
        self.product_repo = ProductRepository()

# 테스트에서 중첩 mock 검증 누락
```

---

### I004: Test命名 Convention 불일치

**위치:** `tests/unit/test_typed_mock.py:66-109`

**문제:** CONTRIBUTING.md 3.2절에서 `test_<대상>_<조건>_<예상결과>` 패턴을 권장하지만, 일부 테스트가 이 패턴을 따르지 않습니다.

**현재:**
```python
def test_method_returns_mock(self) -> None:  # ✅ good
def test_method_has_mock_attributes(self) -> None:  # ✅ good
def test_method_call_works(self) -> None:  # ✅ good
def test_method_assertion_works(self) -> None:  # ✅ good
def test_method_side_effect_works(self) -> None:  # ✅ good
```

**그러나:**
```python
# "child_mock" 보다 "typed_mock_child_mock"이 더 명확함
def test_child_mock_is_magicmock(self) -> None:  # ⚠️ naming 불일치
```

**수정 제안:** 일관된 명명 사용

```python
def test_typed_mock_child_mock_is_magicmock(self) -> None: ...
```

---

### I005: AsyncMockedMethod 사용률 낮음

**위치:** `tests/unit/test_mocked_method.py`

**문제:** `AsyncMockedMethod`가 구현되어 있으나, 실제 사용 시나리오 테스트에서 충분히 활용되지 않고 있습니다. `test_real_scenarios.py`에서 async 테스트가 없습니다.

**현재:** sync 메소드만 테스트됨
```python
# test_real_scenarios.py - async 테스트 누락
class TestSideEffectUsage:
    def test_sequential_return_values(self, typed_mocker: TypedMocker) -> None:
        # sync만 테스트
```

**수정 제안:** async 사용 시나리오 테스트 추가

```python
class TestAsyncMockUsage:
    async def test_async_service_mock(self, typed_mocker: TypedMocker) -> None:
        mock = typed_mocker.mock(UserService)
        mock.async_get_user.return_value = {"id": 1}

        result = await mock.async_get_user(1)

        assert result == {"id": 1}
        mock.async_get_user.assert_awaited_once_with(1)
```

---

## Phase Status Summary

| Phase | Tasks | Status | DoD 충족 |
|-------|-------|--------|----------|
| Phase 0 | T000-T002 | DONE | ✅ |
| Phase 1 | T100-T105 | DONE | ⚠️ C003 |
| Phase 2 | T200-T203 | DONE | ✅ |
| Phase 3 | T300-T302 | BACKLOG | N/A |
| Phase 4 | T400-T403 | BACKLOG | N/A |

---

## 강점 (Strengths)

1. **코드 구조:** Clean Architecture에 따른 적절한 모듈 분리
2. **Docstring:** Google Style Docstring이 일관되게 적용됨
3. **Type Hints:** 모든 공개 API에 타입 힌트 적용
4. **Test Patterns:** AAA 패턴이 잘 적용된 테스트 코드
5. **Configuration:** mypy/pyright strict 모드 설정 완료

---

## Recommendations

### 즉시 수행 (P0)
1. `fail_under`를 80으로 상향
2. `strict` 파라미터 처리 방식 결정 및 문서 동기화

### 단기 수행 (P1)
1. Async 메소드 자동 감지 구현
2. Property/ClassMethod/StaticMethod 테스트 추가

### 중기 수행 (P2)
1. Phase 3 (mypy/pyright 호환성 검증) 시작
2. Phase 4 (고급 기능) 구현

---

## 결론

**LGTM with conditions**

핵심 기능(Phase 1, 2)은 잘 구현되어 있으나, **`CONTRIBUTING.md`에서 명시한 커버리지 기준(80%)을 충족하지 못하는 것**과 **`strict` 모드가 작동하지 않는 것**은 즉시 해결해야 합니다. 이 두 가지 Critical Issue가 해결되면 "LGTM"으로 변경할 수 있습니다.

---

**Reviewer Signature:**
```
Tech Lead
Date: 2024-12-24
```
