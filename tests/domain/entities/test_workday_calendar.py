"""Test for WorkdayCalendar entity."""

import pytest

from src.domain.entities import WorkdayCalendar


class TestWorkdayCalendar:
    """WorkdayCalendar エンティティのテストクラス."""

    def test_valid_workday_calendar(self) -> None:
        """正常な営業日カレンダーを作成できることを確認."""
        calendar = WorkdayCalendar(
            year_month="2025-01",
            day=15,
            is_workday=True,
        )
        assert calendar.year_month == "2025-01"
        assert calendar.day == 15
        assert calendar.is_workday is True

    def test_year_month_format_validation(self) -> None:
        """year_month が "YYYY-MM" 形式でない場合に ValueError を発生させることを確認."""
        with pytest.raises(ValueError, match="year_month must be in YYYY-MM format"):
            WorkdayCalendar(year_month="2025/01", day=15, is_workday=True)

        with pytest.raises(ValueError, match="year_month must be in YYYY-MM format"):
            WorkdayCalendar(year_month="2025-1", day=15, is_workday=True)

        with pytest.raises(ValueError, match="year_month must be in YYYY-MM format"):
            WorkdayCalendar(year_month="25-01", day=15, is_workday=True)

        with pytest.raises(ValueError, match="year_month must be in YYYY-MM format"):
            WorkdayCalendar(year_month="2025-13", day=15, is_workday=True)

    def test_day_range_validation(self) -> None:
        """day が 1-31 の範囲外の場合に ValueError を発生させることを確認."""
        with pytest.raises(ValueError, match="day must be between 1 and 31"):
            WorkdayCalendar(year_month="2025-01", day=0, is_workday=True)

        with pytest.raises(ValueError, match="day must be between 1 and 31"):
            WorkdayCalendar(year_month="2025-01", day=32, is_workday=True)

    def test_valid_day_boundaries(self) -> None:
        """day の境界値（1 と 31）が有効であることを確認."""
        calendar1 = WorkdayCalendar(year_month="2025-01", day=1, is_workday=True)
        assert calendar1.day == 1

        calendar31 = WorkdayCalendar(year_month="2025-01", day=31, is_workday=False)
        assert calendar31.day == 31

    def test_is_workday_boolean(self) -> None:
        """is_workday が True/False の両方で作成できることを確認."""
        workday = WorkdayCalendar(year_month="2025-01", day=15, is_workday=True)
        assert workday.is_workday is True

        holiday = WorkdayCalendar(year_month="2025-01", day=1, is_workday=False)
        assert holiday.is_workday is False
