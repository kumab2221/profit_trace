"""Tests for WorkdayCalendarRepositoryImpl."""

import tempfile
from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest

from src.domain.entities.workday_calendar import WorkdayCalendar
from src.infrastructure.database.initializer import DatabaseInitializer
from src.infrastructure.repositories.workday_calendar_repository_impl import (
    WorkdayCalendarRepositoryImpl,
)


@pytest.fixture
def db_path() -> Generator[str, None, None]:
    """一時的なデータベースパスを提供する."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test.db"
        yield str(db_file)


@pytest.fixture
def repository(db_path: str) -> WorkdayCalendarRepositoryImpl:
    """テスト用のリポジトリインスタンスを提供する."""
    DatabaseInitializer.initialize_database(db_path)
    return WorkdayCalendarRepositoryImpl(db_path)


def test_is_workday_default(repository: WorkdayCalendarRepositoryImpl) -> None:
    """カレンダーデータがない場合はデフォルトで営業日と判定されることを確認する."""
    result = repository.is_workday(date(2025, 1, 10))
    assert result is True


def test_is_workday_with_data(repository: WorkdayCalendarRepositoryImpl) -> None:
    """カレンダーデータがある場合は正しく判定されることを確認する."""
    calendars = [
        WorkdayCalendar(year_month="2025-01", day=10, is_workday=True),
        WorkdayCalendar(year_month="2025-01", day=11, is_workday=False),
    ]
    repository.save_bulk(calendars)

    assert repository.is_workday(date(2025, 1, 10)) is True
    assert repository.is_workday(date(2025, 1, 11)) is False


def test_count_workdays_all_default(
    repository: WorkdayCalendarRepositoryImpl,
) -> None:
    """カレンダーデータがない場合は全ての日が営業日としてカウントされることを確認する."""
    # 2025/1/1 から 2025/1/10 までの10日間
    count = repository.count_workdays(date(2025, 1, 1), date(2025, 1, 10))
    assert count == 10


def test_count_workdays_with_holidays(
    repository: WorkdayCalendarRepositoryImpl,
) -> None:
    """休日を含む場合の営業日数カウントが正しいことを確認する."""
    # 2025/1/1 から 2025/1/10 までの10日間
    # 1/4, 1/5 を休日にする
    calendars = [
        WorkdayCalendar(year_month="2025-01", day=4, is_workday=False),
        WorkdayCalendar(year_month="2025-01", day=5, is_workday=False),
    ]
    repository.save_bulk(calendars)

    count = repository.count_workdays(date(2025, 1, 1), date(2025, 1, 10))
    assert count == 8  # 10日 - 2日(休日) = 8日


def test_count_workdays_single_day(
    repository: WorkdayCalendarRepositoryImpl,
) -> None:
    """1日だけの期間でカウントできることを確認する."""
    count = repository.count_workdays(date(2025, 1, 1), date(2025, 1, 1))
    assert count == 1


def test_save_bulk_update(repository: WorkdayCalendarRepositoryImpl) -> None:
    """既存のカレンダーデータを更新できることを確認する."""
    calendar = WorkdayCalendar(year_month="2025-01", day=10, is_workday=True)
    repository.save_bulk([calendar])

    # 同じ年月日で更新
    updated_calendar = WorkdayCalendar(
        year_month="2025-01", day=10, is_workday=False
    )
    repository.save_bulk([updated_calendar])

    result = repository.is_workday(date(2025, 1, 10))
    assert result is False


def test_delete_all(repository: WorkdayCalendarRepositoryImpl) -> None:
    """全てのカレンダーデータを削除できることを確認する."""
    calendars = [
        WorkdayCalendar(year_month="2025-01", day=10, is_workday=False),
    ]
    repository.save_bulk(calendars)

    repository.delete_all()
    # 削除後はデフォルト（営業日）に戻る
    result = repository.is_workday(date(2025, 1, 10))
    assert result is True


def test_save_bulk_empty_list(
    repository: WorkdayCalendarRepositoryImpl,
) -> None:
    """空のリストを保存しても問題ないことを確認する."""
    repository.save_bulk([])
    result = repository.is_workday(date(2025, 1, 10))
    assert result is True
