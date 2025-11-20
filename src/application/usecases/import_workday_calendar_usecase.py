"""Import workday calendar use case."""

import json
import logging
from pathlib import Path

from src.application.dtos.import_result import ImportResult
from src.domain.entities.workday_calendar import WorkdayCalendar
from src.domain.repositories.workday_calendar_repository import (
    WorkdayCalendarRepository,
)


class ImportWorkdayCalendarUseCase:
    """休日マスタの JSON インポートユースケース."""

    def __init__(
        self,
        calendar_repo: WorkdayCalendarRepository,
        logger: logging.Logger | None = None,
    ) -> None:
        """初期化.

        Args:
            calendar_repo: 営業日カレンダーリポジトリ
            logger: ロガー（省略時は標準ロガー）
        """
        self.calendar_repo = calendar_repo
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, file_path: str | Path) -> ImportResult:
        """休日マスタの JSON インポート.

        Args:
            file_path: JSON ファイルパス

        Returns:
            ImportResult: インポート結果
        """
        try:
            # JSON 読み込み
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # バリデーション
            validation_result = self._validate_format(data)
            if not validation_result.success:
                self.logger.error(f"Validation failed: {validation_result.errors}")
                return validation_result

            # エンティティ生成
            calendars: list[WorkdayCalendar] = []
            for year_month, days_data in data.items():
                if not isinstance(days_data, dict):
                    self.logger.warning(
                        f"Skipped invalid data for {year_month}: {days_data}"
                    )
                    continue

                for day_str, is_workday in days_data.items():
                    try:
                        calendar = WorkdayCalendar(
                            year_month=year_month,
                            day=int(day_str),
                            is_workday=bool(is_workday),
                        )
                        calendars.append(calendar)
                    except (ValueError, TypeError) as e:
                        self.logger.warning(
                            f"Skipped invalid calendar entry: {year_month}/{day_str}, error: {e}"
                        )

            # 既存データ削除
            self.calendar_repo.delete_all()

            # 新しいデータ保存
            self.calendar_repo.save_bulk(calendars)

            self.logger.info(f"Imported {len(calendars)} calendar entries")
            return ImportResult(success=True, imported_count=len(calendars))

        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return ImportResult(
                success=False, errors=[f"ファイルが見つかりません: {file_path}"]
            )
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return ImportResult(
                success=False, errors=[f"JSON フォーマットが不正です: {e}"]
            )
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return ImportResult(
                success=False, errors=[f"予期しないエラーが発生しました: {e}"]
            )

    def _validate_format(self, data: dict) -> ImportResult:
        """JSON フォーマットのバリデーション.

        Args:
            data: JSON データ（dict）

        Returns:
            ImportResult: バリデーション結果
        """
        if not isinstance(data, dict):
            return ImportResult(
                success=False, errors=["JSON のルート要素は辞書形式である必要があります"]
            )

        # 各年月のデータをチェック
        for year_month, days_data in data.items():
            # YYYY-MM 形式のチェック
            if not isinstance(year_month, str):
                return ImportResult(
                    success=False,
                    errors=[f"年月キーが文字列ではありません: {year_month}"],
                )

            # 日データが辞書形式かチェック
            if not isinstance(days_data, dict):
                return ImportResult(
                    success=False,
                    errors=[f"日データが辞書形式ではありません: {year_month}"],
                )

        return ImportResult(success=True)
