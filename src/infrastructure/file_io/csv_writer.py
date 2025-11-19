"""CSV file writer for projects and work records."""

import csv
from pathlib import Path

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord


class CSVWriter:
    """エンティティを CSV ファイルに書き込むクラス."""

    @staticmethod
    def write_projects(projects: list[Project], file_path: str) -> None:
        """プロジェクトを CSV ファイルに書き込む.

        CSV 形式:
        project_id,name,start_date,end_date,contracted_hours

        Args:
            projects: 書き込むプロジェクトのリスト
            file_path: 出力先 CSV ファイルのパス

        Raises:
            IOError: ファイル書き込みに失敗した場合
        """
        path = Path(file_path)
        # ディレクトリが存在しない場合は作成
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                # ヘッダー行を書き込む
                writer.writerow(
                    [
                        "project_id",
                        "name",
                        "start_date",
                        "end_date",
                        "contracted_hours",
                    ]
                )
                # データ行を書き込む
                for project in projects:
                    writer.writerow(
                        [
                            project.project_id,
                            project.name,
                            project.start_date.isoformat(),
                            project.end_date.isoformat(),
                            project.contracted_hours,
                        ]
                    )
        except OSError as e:
            raise OSError(f"Failed to write CSV file: {e}") from e

    @staticmethod
    def write_work_records(records: list[WorkRecord], file_path: str) -> None:
        """工数実績を CSV ファイルに書き込む.

        CSV 形式:
        record_id,date,hours,member_name,project_name,memo

        Args:
            records: 書き込む工数実績のリスト
            file_path: 出力先 CSV ファイルのパス

        Raises:
            IOError: ファイル書き込みに失敗した場合
        """
        path = Path(file_path)
        # ディレクトリが存在しない場合は作成
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                # ヘッダー行を書き込む
                writer.writerow(
                    [
                        "record_id",
                        "date",
                        "hours",
                        "member_name",
                        "project_name",
                        "memo",
                    ]
                )
                # データ行を書き込む
                for record in records:
                    writer.writerow(
                        [
                            record.record_id,
                            record.date.isoformat(),
                            record.hours,
                            record.member_name,
                            record.project_name,
                            record.memo or "",  # None の場合は空文字列
                        ]
                    )
        except OSError as e:
            raise OSError(f"Failed to write CSV file: {e}") from e
