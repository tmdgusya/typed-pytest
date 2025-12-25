"""버전 정보 테스트."""

from typed_pytest import __version__


def test_version_exists() -> None:
    """버전 정보가 존재하는지 확인."""
    assert __version__ is not None


def test_version_format() -> None:
    """버전 형식이 올바른지 확인 (SemVer)."""
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_version_value() -> None:
    """버전이 0.x.x 형식인지 확인 (아직 1.0 미만)."""
    assert __version__.startswith("0.")
