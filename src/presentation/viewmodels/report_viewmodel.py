"""Report view model."""

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from src.application.usecases.export_data_usecase import ExportDataUseCase
from src.application.usecases.generate_report_usecase import GenerateReportUseCase


class ReportViewModel(QObject):
    """レポートの状態管理を行う ViewModel."""

    # Signals
    report_updated = Signal(object)  # ReportDTO
    export_completed = Signal(dict)  # dict[str, str] - exported file paths
    error_occurred = Signal(str)

    def __init__(
        self,
        generate_use_case: GenerateReportUseCase,
        export_use_case: ExportDataUseCase,
        logger: logging.Logger | None = None,
    ) -> None:
        """初期化.

        Args:
            generate_use_case: レポート生成ユースケース
            export_use_case: データエクスポートユースケース
            logger: ロガー（省略時は標準ロガー）
        """
        super().__init__()
        self.generate_use_case = generate_use_case
        self.export_use_case = export_use_case
        self.logger = logger or logging.getLogger(__name__)

    @Slot()
    def on_generate_requested(self) -> None:
        """レポート生成を要求.

        Signal:
            report_updated: レポートを更新
            error_occurred: エラーが発生した場合
        """
        try:
            report_data = self.generate_use_case.execute()
            self.report_updated.emit(report_data)
            self.logger.info("Report generated successfully")
        except Exception as e:
            error_message = f"レポート生成に失敗しました: {e}"
            self.logger.error(error_message, exc_info=True)
            self.error_occurred.emit(error_message)

    @Slot(str, str)
    def on_export_requested(self, export_format: str, output_dir: str) -> None:
        """データエクスポートを要求.

        Args:
            export_format: エクスポート形式（"csv" または "json"）
            output_dir: 出力先ディレクトリ

        Signal:
            export_completed: エクスポート完了
            error_occurred: エラーが発生した場合
        """
        try:
            exported_files = self.export_use_case.execute(export_format, output_dir)
            self.export_completed.emit(exported_files)
            self.logger.info(f"Data exported to: {output_dir}")
        except (ValueError, OSError) as e:
            error_message = f"データエクスポートに失敗しました: {e}"
            self.logger.error(error_message, exc_info=True)
            self.error_occurred.emit(error_message)
