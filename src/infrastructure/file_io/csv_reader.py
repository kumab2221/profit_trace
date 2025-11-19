"""CSV file reader for projects and work records."""

import csv
from datetime import date
from pathlib import Path

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord


class CSVReader:
    """CSV ファイルからエンティティを読み込むクラス."""

    @staticmethod
    def read_projects(file_path: str) -> list[Project]:
        """プロジェクト CSV ファイルを読み込む.

        CSV 形式:
        project_id,name,start_date,end_date,contracted_hours

        Args:
            file_path: CSV ファイルのパス

        Returns:
            プロジェクトのリスト

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: CSV フォーマットが不正な場合
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        projects: list[Project] = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # ヘッダー行の次から
                try:
                    project = Project(
                        project_id=row["project_id"],
                        name=row["name"],
                        start_date=date.fromisoformat(row["start_date"]),
                        end_date=date.fromisoformat(row["end_date"]),
                        contracted_hours=float(row["contracted_hours"]),
                    )
                    projects.append(project)
                except KeyError as e:
                    raise ValueError(
                        f"Missing required column in CSV at line {row_num}: {e}"
                    ) from e
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Invalid data format in CSV at line {row_num}: {e}"
                    ) from e

        return projects

    @staticmethod
    def read_work_records(file_path: str) -> list[WorkRecord]:
        """工数実績 CSV ファイルを読み込む.

        CSV 形式:
        record_id,date,hours,member_name,project_name,memo

        Args:
            file_path: CSV ファイルのパス

        Returns:
            工数実績のリスト

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: CSV フォーマットが不正な場合
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        records: list[WorkRecord] = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # ヘッダー行の次から
                try:
                    record = WorkRecord(
                        record_id=row["record_id"],
                        date=date.fromisoformat(row["date"]),
                        hours=float(row["hours"]),
                        member_name=row["member_name"],
                        project_name=row["project_name"],
                        memo=row.get("memo", ""),  # memo は省略可能
                    )
                    records.append(record)
                except KeyError as e:
                    raise ValueError(
                        f"Missing required column in CSV at line {row_num}: {e}"
                    ) from e
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Invalid data format in CSV at line {row_num}: {e}"
                    ) from e

        return records
