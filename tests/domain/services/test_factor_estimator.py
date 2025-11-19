"""Tests for FactorEstimator."""

from datetime import date
from unittest.mock import MagicMock

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord
from src.domain.services.factor_estimator import FactorEstimator


def test_estimate_factors_early_completion() -> None:
    """早期完了の要因を推定できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 20),  # 3週間
        contracted_hours=100.0,
    )

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 7),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        # 1/8 以降は作業なし（早期完了）
    ]

    calendar = MagicMock()
    calendar.count_workdays.return_value = 5  # 最終作業日から終了日まで5営業日

    estimator = FactorEstimator()
    factors = estimator.estimate_factors(project, work_records, calendar)

    # 早期完了の要因が含まれる
    early_completion_factors = [
        f for f in factors if f.factor_type == "early_completion"
    ]
    assert len(early_completion_factors) == 1
    assert early_completion_factors[0].impact_hours == 80.0  # 100 - 20


def test_estimate_factors_low_workload() -> None:
    """低稼働率の要因を推定できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 12),
        contracted_hours=100.0,
    )

    # 7日間のうち2日しか稼働していない（28%）
    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 10),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
    ]

    calendar = MagicMock()
    calendar.count_workdays.return_value = 7  # 7営業日
    calendar.is_workday.return_value = True

    estimator = FactorEstimator()
    factors = estimator.estimate_factors(project, work_records, calendar)

    # 低稼働率の要因が含まれる
    low_workload_factors = [f for f in factors if f.factor_type == "low_workload"]
    assert len(low_workload_factors) == 1
    # 稼働率が70%未満なので要因として検出される
    assert "稼働率が低い" in low_workload_factors[0].description


def test_estimate_factors_holidays() -> None:
    """休日・休暇の要因を推定できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 12),
        contracted_hours=100.0,
    )

    # 一部の日だけ稼働
    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 7),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
    ]

    calendar = MagicMock()
    calendar.count_workdays.return_value = 7  # 7営業日
    # 全日営業日だが、実際には2日しか稼働していない
    calendar.is_workday.return_value = True

    estimator = FactorEstimator()
    factors = estimator.estimate_factors(project, work_records, calendar)

    # 休日・休暇の要因が含まれる（未稼働営業日が5日 > 30%）
    holiday_factors = [f for f in factors if f.factor_type == "holidays"]
    assert len(holiday_factors) == 1
    assert "休日・休暇" in holiday_factors[0].description


def test_estimate_factors_no_surplus() -> None:
    """余剰工数がない場合は空リストを返すことを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 10),
        contracted_hours=20.0,
    )

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 7),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
    ]

    calendar = MagicMock()

    estimator = FactorEstimator()
    factors = estimator.estimate_factors(project, work_records, calendar)

    # 余剰工数がないので要因も空
    assert len(factors) == 0


def test_estimate_factors_with_other_projects() -> None:
    """他のプロジェクトの実績が混在する場合の推定を確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 10),
        contracted_hours=100.0,
    )

    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=10.0,
            member_name="Alice",
            project_name="Test Project",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 6),
            hours=50.0,
            member_name="Alice",
            project_name="Other Project",  # 他のプロジェクト
        ),
    ]

    calendar = MagicMock()
    calendar.count_workdays.return_value = 3

    estimator = FactorEstimator()
    factors = estimator.estimate_factors(project, work_records, calendar)

    # 他のプロジェクトの工数は含まれない（残工数 = 90）
    assert len(factors) > 0
    early_completion_factors = [
        f for f in factors if f.factor_type == "early_completion"
    ]
    if early_completion_factors:
        assert early_completion_factors[0].impact_hours == 90.0  # 100 - 10


def test_estimate_factors_no_work_records() -> None:
    """工数実績がない場合の推定を確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 6),
        end_date=date(2025, 1, 10),
        contracted_hours=100.0,
    )

    calendar = MagicMock()
    calendar.count_workdays.return_value = 5
    calendar.is_workday.return_value = True

    estimator = FactorEstimator()
    factors = estimator.estimate_factors(project, [], calendar)

    # 工数実績がないので複数の要因が推定される
    assert len(factors) > 0
