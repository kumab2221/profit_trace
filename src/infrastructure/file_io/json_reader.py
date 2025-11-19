"""JSON file reader for workday calendar."""

import json
from pathlib import Path

from src.domain.entities.workday_calendar import WorkdayCalendar


class JSONReader:
    """JSON ファイルから営業日カレンダーを読み込むクラス."""

    @staticmethod
    def read_workday_calendar(file_path: str) -> list[WorkdayCalendar]:
        """営業日カレンダー JSON ファイルを読み込む.

        JSON 形式:
        {
          "2025-01": [
            {"day": 1, "is_workday": false},
            {"day": 2, "is_workday": true},
            ...
          ],
          "2025-02": [...]
        }

        Args:
            file_path: JSON ファイルのパス

        Returns:
            営業日カレンダーのリスト

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: JSON フォーマットが不正な場合
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}") from e

        calendars: list[WorkdayCalendar] = []
        for year_month, days in data.items():
            if not isinstance(days, list):
                raise ValueError(
                    f"Invalid format: expected list for '{year_month}', got {type(days)}"
                )

            for day_data in days:
                try:
                    calendar = WorkdayCalendar(
                        year_month=year_month,
                        day=int(day_data["day"]),
                        is_workday=bool(day_data["is_workday"]),
                    )
                    calendars.append(calendar)
                except KeyError as e:
                    raise ValueError(
                        f"Missing required field in '{year_month}': {e}"
                    ) from e
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Invalid data in '{year_month}': {e}"
                    ) from e

        return calendars
