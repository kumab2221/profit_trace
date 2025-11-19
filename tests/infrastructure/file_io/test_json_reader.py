"""Tests for JSONReader."""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from src.infrastructure.file_io.json_reader import JSONReader


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """一時ディレクトリを提供する."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_read_workday_calendar_success(temp_dir: Path) -> None:
    """営業日カレンダー JSON を正常に読み込めることを確認する."""
    json_path = temp_dir / "calendar.json"
    data = {
        "2025-01": [
            {"day": 1, "is_workday": False},
            {"day": 2, "is_workday": True},
            {"day": 3, "is_workday": True},
        ],
        "2025-02": [
            {"day": 1, "is_workday": True},
            {"day": 2, "is_workday": False},
        ],
    }
    json_path.write_text(json.dumps(data), encoding="utf-8")

    calendars = JSONReader.read_workday_calendar(str(json_path))

    assert len(calendars) == 5
    assert calendars[0].year_month == "2025-01"
    assert calendars[0].day == 1
    assert calendars[0].is_workday is False
    assert calendars[1].day == 2
    assert calendars[1].is_workday is True


def test_read_workday_calendar_file_not_found() -> None:
    """存在しないファイルを読み込もうとした場合に例外が発生することを確認する."""
    with pytest.raises(FileNotFoundError):
        JSONReader.read_workday_calendar("nonexistent.json")


def test_read_workday_calendar_invalid_json(temp_dir: Path) -> None:
    """不正な JSON を読み込もうとした場合に例外が発生することを確認する."""
    json_path = temp_dir / "calendar.json"
    json_path.write_text("invalid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON format"):
        JSONReader.read_workday_calendar(str(json_path))


def test_read_workday_calendar_invalid_format_not_list(temp_dir: Path) -> None:
    """年月の値がリストでない場合に例外が発生することを確認する."""
    json_path = temp_dir / "calendar.json"
    data = {"2025-01": "not a list"}
    json_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="expected list"):
        JSONReader.read_workday_calendar(str(json_path))


def test_read_workday_calendar_missing_field(temp_dir: Path) -> None:
    """必須フィールドが欠けている場合に例外が発生することを確認する."""
    json_path = temp_dir / "calendar.json"
    data = {"2025-01": [{"day": 1}]}  # is_workday が欠けている
    json_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required field"):
        JSONReader.read_workday_calendar(str(json_path))


def test_read_workday_calendar_invalid_day(temp_dir: Path) -> None:
    """day が不正な値の場合に例外が発生することを確認する."""
    json_path = temp_dir / "calendar.json"
    data = {"2025-01": [{"day": "invalid", "is_workday": True}]}
    json_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid data"):
        JSONReader.read_workday_calendar(str(json_path))


def test_read_workday_calendar_empty(temp_dir: Path) -> None:
    """空の JSON を読み込んだ場合に空リストを返すことを確認する."""
    json_path = temp_dir / "calendar.json"
    data: dict[str, list[dict[str, int | bool]]] = {}
    json_path.write_text(json.dumps(data), encoding="utf-8")

    calendars = JSONReader.read_workday_calendar(str(json_path))
    assert len(calendars) == 0
