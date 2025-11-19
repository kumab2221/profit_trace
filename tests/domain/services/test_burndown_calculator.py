"""Tests for BurndownCalculator."""

from datetime import date
from unittest.mock import MagicMock

import pytest

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord
from src.domain.services.burndown_calculator import (
    BurndownCalculator,
    CalculationError,
)


def test_calculate_ideal_line_success() -> None:
    """理想線を正常に計算できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),  # 月曜日
        end_date=date(2025, 1, 10),  # 金曜日
        contracted_hours=40.0,
    )

    # モックカレンダー（全日営業日）
    calendar = MagicMock()
    calendar.count_workdays.return_value = 5  # 5営業日
    calendar.is_workday.return_value = True

    calculator = BurndownCalculator()
    points = calculator.calculate_ideal_line(project, calendar)

    assert len(points) == 5  # 5日分
    assert points[0].date == date(2025, 1, 6)
    assert points[0].remaining_hours == 32.0  # 40 - 8
    assert points[-1].date == date(2025, 1, 10)
    assert points[-1].remaining_hours == 0.0  # 完了


def test_calculate_ideal_line_with_holidays() -> None:
    """休日を含む場合の理想線計算を確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 10),
        contracted_hours=40.0,
    )

    # モックカレンダー（1/8が休日）
    calendar = MagicMock()
    calendar.count_workdays.return_value = 4  # 4営業日
    calendar.is_workday.side_effect = lambda d: d != date(2025, 1, 8)

    calculator = BurndownCalculator()
    points = calculator.calculate_ideal_line(project, calendar)

    assert len(points) == 5
    # 休日の日は工数が減らない
    assert points[2].remaining_hours == points[1].remaining_hours


def test_calculate_ideal_line_no_workdays() -> None:
    """営業日が0の場合にエラーが発生することを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 10),
        contracted_hours=40.0,
    )

    calendar = MagicMock()
    calendar.count_workdays.return_value = 0

    calculator = BurndownCalculator()
    with pytest.raises(CalculationError, match="No workdays found"):
        calculator.calculate_ideal_line(project, calendar)


def test_calculate_actual_line_success() -> None:
    """実績線を正常に計算できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 10),
        contracted_hours=40.0,
    )

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=8.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 7),
            hours=6.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-003",
            date=date(2025, 1, 8),
            hours=10.0,
            member_name="Bob",
            project_name="Test Project",
        ),
    ]

    calendar = MagicMock()

    calculator = BurndownCalculator()
    points = calculator.calculate_actual_line(project, work_records, calendar)

    assert len(points) == 5
    assert points[0].date == date(2025, 1, 6)
    assert points[0].remaining_hours == 32.0  # 40 - 8
    assert points[1].remaining_hours == 26.0  # 32 - 6
    assert points[2].remaining_hours == 16.0  # 26 - 10
    assert points[3].remaining_hours == 16.0  # 変化なし
    assert points[4].remaining_hours == 16.0  # 変化なし


def test_calculate_actual_line_with_other_projects() -> None:
    """他のプロジェクトの実績が混在する場合の計算を確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 8),
        contracted_hours=20.0,
    )

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=8.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 6),
            hours=5.0,
            member_name="Alice",
            project_name="Other Project",  # 他のプロジェクト
        ),
        WorkRecord(
            record_id="rec-003",
            date=date(2025, 1, 7),
            hours=6.0,
            member_name="Alice",
            project_name="Test Project",
        ),
    ]

    calendar = MagicMock()

    calculator = BurndownCalculator()
    points = calculator.calculate_actual_line(project, work_records, calendar)

    # 他のプロジェクトの工数は含まれない
    assert points[0].remaining_hours == 12.0  # 20 - 8（5は含まない）
    assert points[1].remaining_hours == 6.0  # 12 - 6


def test_calculate_actual_line_no_records() -> None:
    """工数実績がない場合の実績線計算を確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 8),
        contracted_hours=20.0,
    )

    calendar = MagicMock()

    calculator = BurndownCalculator()
    points = calculator.calculate_actual_line(project, [], calendar)

    # 全ての日で残工数が契約時間と同じ
    assert all(p.remaining_hours == 20.0 for p in points)
