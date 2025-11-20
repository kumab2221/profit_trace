"""Import view model."""

import logging
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot

from src.application.usecases.import_project_usecase import ImportProjectUseCase
from src.application.usecases.import_work_record_usecase import ImportWorkRecordUseCase
from src.application.usecases.import_workday_calendar_usecase import (
    ImportWorkdayCalendarUseCase,
)


class ImportWorker(QObject):
    """インポート処理を行うワーカースレッド."""

    import_completed = Signal(object)  # ImportResult

    def __init__(self, use_case, file_path: str) -> None:
        """初期化.

        Args:
            use_case: インポートユースケース
            file_path: インポートするファイルパス
        """
        super().__init__()
        self.use_case = use_case
        self.file_path = file_path

    @Slot()
    def run(self) -> None:
        """インポート処理を実行.

        Signal:
            import_completed: インポート完了
        """
        result = self.use_case.execute(self.file_path)
        self.import_completed.emit(result)


class ImportViewModel(QObject):
    """ファイルインポートの状態管理を行う ViewModel."""

    # Signals
    import_completed = Signal(object)  # ImportResult
    progress_updated = Signal(int)  # progress percentage (0-100)
    error_occurred = Signal(str)

    def __init__(
        self,
        project_use_case: ImportProjectUseCase,
        work_record_use_case: ImportWorkRecordUseCase,
        calendar_use_case: ImportWorkdayCalendarUseCase,
        logger: logging.Logger | None = None,
    ) -> None:
        """初期化.

        Args:
            project_use_case: プロジェクトインポートユースケース
            work_record_use_case: 工数実績インポートユースケース
            calendar_use_case: 営業日カレンダーインポートユースケース
            logger: ロガー（省略時は標準ロガー）
        """
        super().__init__()
        self.project_use_case = project_use_case
        self.work_record_use_case = work_record_use_case
        self.calendar_use_case = calendar_use_case
        self.logger = logger or logging.getLogger(__name__)
        self._thread: QThread | None = None
        self._worker: ImportWorker | None = None

    @Slot(str, str)
    def on_file_selected(self, file_type: str, file_path: str) -> None:
        """ファイルが選択された時の処理.

        Args:
            file_type: ファイルタイプ（"project", "work_record", "calendar"）
            file_path: ファイルパス

        Signal:
            import_completed: インポート完了
            error_occurred: エラーが発生した場合
        """
        # ファイルの存在確認
        if not Path(file_path).exists():
            self.error_occurred.emit(f"ファイルが見つかりません: {file_path}")
            return

        # 適切なユースケースを選択
        use_case = self._get_use_case(file_type)
        if use_case is None:
            self.error_occurred.emit(f"不明なファイルタイプ: {file_type}")
            return

        # QThread でインポート処理を実行
        self._thread = QThread()
        self._worker = ImportWorker(use_case, file_path)
        self._worker.moveToThread(self._thread)

        # Signal/Slot 接続
        self._thread.started.connect(self._worker.run)
        self._worker.import_completed.connect(self._on_import_completed)

        # スレッド開始
        self._thread.start()
        self.logger.info(f"Import started: {file_type} from {file_path}")

    @Slot(object)
    def _on_import_completed(self, result) -> None:
        """インポート完了時の処理.

        Args:
            result: インポート結果（ImportResult）

        Signal:
            import_completed: インポート完了
            error_occurred: エラーが発生した場合
        """
        # スレッドを終了
        if self._thread:
            self._thread.quit()
            self._thread.wait()

        if result.success:
            self.import_completed.emit(result)
            self.logger.info(f"Import completed: {result.imported_count} records")
        else:
            error_message = "\n".join(result.errors)
            self.error_occurred.emit(error_message)
            self.logger.error(f"Import failed: {error_message}")

    def _get_use_case(self, file_type: str):
        """ファイルタイプに対応するユースケースを取得.

        Args:
            file_type: ファイルタイプ

        Returns:
            対応するユースケース、または None
        """
        use_cases = {
            "project": self.project_use_case,
            "work_record": self.work_record_use_case,
            "calendar": self.calendar_use_case,
        }
        return use_cases.get(file_type)
