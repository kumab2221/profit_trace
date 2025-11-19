"""Tests for ConsumptionRateCalculator."""

from datetime import date

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord
from src.domain.services.consumption_rate_calculator import (
    ConsumptionRateCalculator,
)


def test_calculate_rate_success() -> None:
    """消化率を正常に計算できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        contracted_hours=100.0,
    )

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 10),
            hours=20.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 11),
            hours=30.0,
            member_name="Bob",
            project_name="Test Project",
        ),
    ]

    calculator = ConsumptionRateCalculator()
    rate = calculator.calculate_rate(project, work_records)

    assert rate == 0.5  # 50 / 100


def test_calculate_rate_over_100_percent() -> None:
    """消化率が100%を超える場合でも1.0を返すことを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        contracted_hours=100.0,
    )

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 10),
            hours=80.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 11),
            hours=50.0,
            member_name="Bob",
            project_name="Test Project",
        ),
    ]

    calculator = ConsumptionRateCalculator()
    rate = calculator.calculate_rate(project, work_records)

    assert rate == 1.0  # max(130 / 100, 1.0) = 1.0


def test_calculate_rate_with_other_projects() -> None:
    """他のプロジェクトの実績が混在する場合の計算を確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        contracted_hours=100.0,
    )

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 10),
            hours=30.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 10),
            hours=50.0,
            member_name="Alice",
            project_name="Other Project",  # 他のプロジェクト
        ),
    ]

    calculator = ConsumptionRateCalculator()
    rate = calculator.calculate_rate(project, work_records)

    assert rate == 0.3  # 30 / 100（50は含まない）


def test_calculate_rate_no_records() -> None:
    """工数実績がない場合に0.0を返すことを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        contracted_hours=100.0,
    )

    calculator = ConsumptionRateCalculator()
    rate = calculator.calculate_rate(project, [])

    assert rate == 0.0


def test_calculate_rate_zero_contracted_hours() -> None:
    """契約時間が0の場合に0.0を返すことを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 2),
        contracted_hours=0.1,  # 0にすると validation error
    )
    # contracted_hours を強制的に0に設定（バリデーションをバイパス）
    project.contracted_hours = 0.0

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 10),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        )
    ]

    calculator = ConsumptionRateCalculator()
    rate = calculator.calculate_rate(project, work_records)

    assert rate == 0.0
