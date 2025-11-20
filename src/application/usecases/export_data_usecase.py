"""Export data use case."""

import logging
from pathlib import Path

from src.domain.repositories.project_repository import ProjectRepository
from src.domain.repositories.work_record_repository import WorkRecordRepository
from src.domain.repositories.workday_calendar_repository import (
    WorkdayCalendarRepository,
)
from src.infrastructure.file_io.csv_writer import CSVWriter
from src.infrastructure.file_io.json_writer import JSONWriter


class ExportDataUseCase:
    """データエクスポートユースケース."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        work_record_repo: WorkRecordRepository,
        calendar_repo: WorkdayCalendarRepository,
        csv_writer: CSVWriter | None = None,
        json_writer: JSONWriter | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """初期化.

        Args:
            project_repo: プロジェクトリポジトリ
            work_record_repo: 工数実績リポジトリ
            calendar_repo: 営業日カレンダーリポジトリ
            csv_writer: CSV ライター（省略時は新規インスタンス）
            json_writer: JSON ライター（省略時は新規インスタンス）
            logger: ロガー（省略時は標準ロガー）
        """
        self.project_repo = project_repo
        self.work_record_repo = work_record_repo
        self.calendar_repo = calendar_repo
        self.csv_writer = csv_writer or CSVWriter()
        self.json_writer = json_writer or JSONWriter()
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, export_format: str, output_dir: str | Path) -> dict[str, str]:
        """データをエクスポートする.

        Args:
            export_format: エクスポート形式（"csv" または "json"）
            output_dir: 出力先ディレクトリ

        Returns:
            エクスポートされたファイルのパスを含む辞書
            - "projects": プロジェクトデータのファイルパス
            - "work_records": 工数実績データのファイルパス
            - "calendar": 営業日カレンダーのファイルパス

        Raises:
            ValueError: 不明なエクスポート形式の場合
            OSError: ファイル書き込みに失敗した場合
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported_files: dict[str, str] = {}

        try:
            if export_format.lower() == "csv":
                # CSV 形式でエクスポート
                exported_files = self._export_as_csv(output_path)
            elif export_format.lower() == "json":
                # JSON 形式でエクスポート
                exported_files = self._export_as_json(output_path)
            else:
                raise ValueError(
                    f"Unknown export format: {export_format}. Supported formats: csv, json"
                )

            self.logger.info(f"Data exported successfully: {exported_files}")
            return exported_files

        except OSError as e:
            self.logger.error(f"Failed to export data: {e}", exc_info=True)
            raise

    def _export_as_csv(self, output_path: Path) -> dict[str, str]:
        """CSV 形式でデータをエクスポートする.

        Args:
            output_path: 出力先ディレクトリ

        Returns:
            エクスポートされたファイルのパスを含む辞書
        """
        # プロジェクトデータを取得してエクスポート
        projects = self.project_repo.find_all()
        projects_file = output_path / "projects.csv"
        self.csv_writer.write_projects(projects, str(projects_file))

        # 工数実績データを取得してエクスポート
        work_records = self.work_record_repo.find_all()
        work_records_file = output_path / "work_records.csv"
        self.csv_writer.write_work_records(work_records, str(work_records_file))

        # 営業日カレンダーは JSON 形式でエクスポート（CSV には適さないため）
        calendars = self.calendar_repo.find_all()
        calendar_file = output_path / "workday_calendar.json"
        self.json_writer.write_workday_calendar(calendars, str(calendar_file))

        return {
            "projects": str(projects_file),
            "work_records": str(work_records_file),
            "calendar": str(calendar_file),
        }

    def _export_as_json(self, output_path: Path) -> dict[str, str]:
        """JSON 形式でデータをエクスポートする.

        Args:
            output_path: 出力先ディレクトリ

        Returns:
            エクスポートされたファイルのパスを含む辞書
        """
        import json

        # プロジェクトデータを取得してエクスポート
        projects = self.project_repo.find_all()
        projects_file = output_path / "projects.json"
        projects_data = [
            {
                "project_id": p.project_id,
                "name": p.name,
                "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat(),
                "contracted_hours": p.contracted_hours,
            }
            for p in projects
        ]
        with open(projects_file, "w", encoding="utf-8") as f:
            json.dump(projects_data, f, ensure_ascii=False, indent=2)

        # 工数実績データを取得してエクスポート
        work_records = self.work_record_repo.find_all()
        work_records_file = output_path / "work_records.json"
        work_records_data = [
            {
                "record_id": r.record_id,
                "date": r.date.isoformat(),
                "hours": r.hours,
                "member_name": r.member_name,
                "project_name": r.project_name,
                "memo": r.memo,
            }
            for r in work_records
        ]
        with open(work_records_file, "w", encoding="utf-8") as f:
            json.dump(work_records_data, f, ensure_ascii=False, indent=2)

        # 営業日カレンダーをエクスポート
        calendars = self.calendar_repo.find_all()
        calendar_file = output_path / "workday_calendar.json"
        self.json_writer.write_workday_calendar(calendars, str(calendar_file))

        return {
            "projects": str(projects_file),
            "work_records": str(work_records_file),
            "calendar": str(calendar_file),
        }
