"""JSON file writer for workday calendar."""

import json
from pathlib import Path

from src.domain.entities.workday_calendar import WorkdayCalendar


class JSONWriter:
    """営業日カレンダーを JSON ファイルに書き込むクラス."""

    @staticmethod
    def write_workday_calendar(
        calendars: list[WorkdayCalendar], file_path: str
    ) -> None:
        """営業日カレンダーを JSON ファイルに書き込む.

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
            calendars: 書き込む営業日カレンダーのリスト
            file_path: 出力先 JSON ファイルのパス

        Raises:
            IOError: ファイル書き込みに失敗した場合
        """
        path = Path(file_path)
        # ディレクトリが存在しない場合は作成
        path.parent.mkdir(parents=True, exist_ok=True)

        # 年月ごとにグループ化
        grouped: dict[str, list[dict[str, int | bool]]] = {}
        for calendar in calendars:
            if calendar.year_month not in grouped:
                grouped[calendar.year_month] = []
            grouped[calendar.year_month].append(
                {"day": calendar.day, "is_workday": calendar.is_workday}
            )

        # 各年月内で日付順にソート
        for year_month in grouped:
            grouped[year_month].sort(key=lambda x: x["day"])

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(grouped, f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise OSError(f"Failed to write JSON file: {e}") from e
