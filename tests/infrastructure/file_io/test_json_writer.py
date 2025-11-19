"""Tests for JSONWriter."""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from src.domain.entities.workday_calendar import WorkdayCalendar
from src.infrastructure.file_io.json_writer import JSONWriter


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """一時ディレクトリを提供する."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_write_workday_calendar_success(temp_dir: Path) -> None:
    """営業日カレンダーを JSON に正常に書き込めることを確認する."""
    calendars = [
        WorkdayCalendar(year_month="2025-01", day=1, is_workday=False),
        WorkdayCalendar(year_month="2025-01", day=2, is_workday=True),
        WorkdayCalendar(year_month="2025-01", day=3, is_workday=True),
        WorkdayCalendar(year_month="2025-02", day=1, is_workday=True),
        WorkdayCalendar(year_month="2025-02", day=2, is_workday=False),
    ]

    json_path = temp_dir / "calendar.json"
    JSONWriter.write_workday_calendar(calendars, str(json_path))

    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "2025-01" in data
    assert "2025-02" in data
    assert len(data["2025-01"]) == 3
    assert len(data["2025-02"]) == 2
    assert data["2025-01"][0] == {"day": 1, "is_workday": False}
    assert data["2025-01"][1] == {"day": 2, "is_workday": True}


def test_write_workday_calendar_sorted_by_day(temp_dir: Path) -> None:
    """日付順にソートされて書き込まれることを確認する."""
    calendars = [
        WorkdayCalendar(year_month="2025-01", day=3, is_workday=True),
        WorkdayCalendar(year_month="2025-01", day=1, is_workday=False),
        WorkdayCalendar(year_month="2025-01", day=2, is_workday=True),
    ]

    json_path = temp_dir / "calendar.json"
    JSONWriter.write_workday_calendar(calendars, str(json_path))

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 日付順にソートされているはず
    assert data["2025-01"][0]["day"] == 1
    assert data["2025-01"][1]["day"] == 2
    assert data["2025-01"][2]["day"] == 3


def test_write_workday_calendar_creates_directory(temp_dir: Path) -> None:
    """存在しないディレクトリを自動作成することを確認する."""
    calendars = [
        WorkdayCalendar(year_month="2025-01", day=1, is_workday=True)
    ]

    json_path = temp_dir / "subdir" / "calendar.json"
    JSONWriter.write_workday_calendar(calendars, str(json_path))

    assert json_path.exists()


def test_write_workday_calendar_empty_list(temp_dir: Path) -> None:
    """空のリストでも JSON を書き込めることを確認する."""
    json_path = temp_dir / "calendar.json"
    JSONWriter.write_workday_calendar([], str(json_path))

    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {}


def test_write_workday_calendar_multiple_months(temp_dir: Path) -> None:
    """複数の月のデータを正しくグループ化することを確認する."""
    calendars = [
        WorkdayCalendar(year_month="2025-01", day=1, is_workday=True),
        WorkdayCalendar(year_month="2025-02", day=1, is_workday=False),
        WorkdayCalendar(year_month="2025-01", day=2, is_workday=False),
        WorkdayCalendar(year_month="2025-03", day=1, is_workday=True),
    ]

    json_path = temp_dir / "calendar.json"
    JSONWriter.write_workday_calendar(calendars, str(json_path))

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 3  # 3つの月
    assert len(data["2025-01"]) == 2
    assert len(data["2025-02"]) == 1
    assert len(data["2025-03"]) == 1
