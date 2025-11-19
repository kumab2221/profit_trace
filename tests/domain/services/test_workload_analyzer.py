"""Tests for WorkloadAnalyzer."""

from datetime import date

import pytest

from src.domain.entities.work_record import WorkRecord
from src.domain.services.workload_analyzer import WorkloadAnalyzer


def test_analyze_member_workload_success() -> None:
    """メンバーの稼働状況を正常に分析できることを確認する."""
    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=8.0,
            member_name="Alice",
            project_name="Project A",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 7),
            hours=6.0,
            member_name="Alice",
            project_name="Project A",
        ),
        WorkRecord(
            record_id="rec-003",
            date=date(2025, 1, 8),
            hours=10.0,
            member_name="Alice",
            project_name="Project B",
        ),
        WorkRecord(
            record_id="rec-004",
            date=date(2025, 1, 9),
            hours=5.0,
            member_name="Bob",  # 他のメンバー
            project_name="Project A",
        ),
    ]

    analyzer = WorkloadAnalyzer()
    analysis = analyzer.analyze_member_workload(
        "Alice", work_records, date(2025, 1, 1), date(2025, 1, 31)
    )

    assert analysis.member_name == "Alice"
    assert analysis.total_hours == 24.0  # 8 + 6 + 10
    assert analysis.workdays_count == 3
    assert analysis.average_hours_per_day == 8.0  # 24 / 3
    assert analysis.max_hours_per_day == 10.0
    assert analysis.min_hours_per_day == 6.0


def test_analyze_member_workload_with_date_range() -> None:
    """期間指定でメンバーの稼働状況を分析できることを確認する."""
    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 5),  # 期間外
            hours=8.0,
            member_name="Alice",
            project_name="Project A",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 7),  # 期間内
            hours=6.0,
            member_name="Alice",
            project_name="Project A",
        ),
        WorkRecord(
            record_id="rec-003",
            date=date(2025, 1, 8),  # 期間内
            hours=10.0,
            member_name="Alice",
            project_name="Project B",
        ),
        WorkRecord(
            record_id="rec-004",
            date=date(2025, 1, 15),  # 期間外
            hours=5.0,
            member_name="Alice",
            project_name="Project A",
        ),
    ]

    analyzer = WorkloadAnalyzer()
    analysis = analyzer.analyze_member_workload(
        "Alice", work_records, date(2025, 1, 6), date(2025, 1, 10)
    )

    assert analysis.total_hours == 16.0  # 6 + 10（期間内のみ）
    assert analysis.workdays_count == 2


def test_analyze_member_workload_multiple_records_per_day() -> None:
    """1日に複数の実績がある場合の分析を確認する."""
    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=4.0,
            member_name="Alice",
            project_name="Project A",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 6),
            hours=4.0,
            member_name="Alice",
            project_name="Project B",
        ),
        WorkRecord(
            record_id="rec-003",
            date=date(2025, 1, 7),
            hours=8.0,
            member_name="Alice",
            project_name="Project A",
        ),
    ]

    analyzer = WorkloadAnalyzer()
    analysis = analyzer.analyze_member_workload(
        "Alice", work_records, date(2025, 1, 1), date(2025, 1, 31)
    )

    assert analysis.total_hours == 16.0  # 4 + 4 + 8
    assert analysis.workdays_count == 2  # 2日分
    assert analysis.average_hours_per_day == 8.0  # 16 / 2
    assert analysis.max_hours_per_day == 8.0  # 1/6: 8.0, 1/7: 8.0
    assert analysis.min_hours_per_day == 8.0


def test_analyze_member_workload_no_records() -> None:
    """該当するメンバーの実績がない場合にエラーが発生することを確認する."""
    work_records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 6),
            hours=8.0,
            member_name="Bob",
            project_name="Project A",
        )
    ]

    analyzer = WorkloadAnalyzer()
    with pytest.raises(ValueError, match="No work records found for member"):
        analyzer.analyze_member_workload(
            "Alice", work_records, date(2025, 1, 1), date(2025, 1, 31)
        )


def test_analyze_member_workload_empty_list() -> None:
    """空の実績リストでエラーが発生することを確認する."""
    analyzer = WorkloadAnalyzer()
    with pytest.raises(ValueError, match="No work records found for member"):
        analyzer.analyze_member_workload(
            "Alice", [], date(2025, 1, 1), date(2025, 1, 31)
        )
