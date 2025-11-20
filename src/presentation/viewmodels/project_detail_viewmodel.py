"""Project detail view model."""

import logging

from PySide6.QtCore import QObject, Signal, Slot

from src.application.usecases.get_burndown_chart_usecase import (
    GetBurndownChartUseCase,
)
from src.application.usecases.get_factor_analysis_usecase import (
    GetFactorAnalysisUseCase,
)


class ProjectDetailViewModel(QObject):
    """プロジェクト詳細の状態管理を行う ViewModel."""

    # Signals
    burndown_updated = Signal(object)  # BurndownChartDTO
    factor_analysis_updated = Signal(object)  # FactorAnalysisDTO
    error_occurred = Signal(str)

    def __init__(
        self,
        burndown_use_case: GetBurndownChartUseCase,
        factor_use_case: GetFactorAnalysisUseCase,
        logger: logging.Logger | None = None,
    ) -> None:
        """初期化.

        Args:
            burndown_use_case: バーンダウンチャート取得ユースケース
            factor_use_case: 要因分析取得ユースケース
            logger: ロガー（省略時は標準ロガー）
        """
        super().__init__()
        self.burndown_use_case = burndown_use_case
        self.factor_use_case = factor_use_case
        self.logger = logger or logging.getLogger(__name__)
        self._current_project_name: str | None = None

    @Slot(str)
    def on_project_changed(self, project_name: str) -> None:
        """プロジェクトが変更された時の処理.

        Args:
            project_name: プロジェクト名

        Signal:
            burndown_updated: バーンダウンチャートを更新
            factor_analysis_updated: 要因分析を更新
            error_occurred: エラーが発生した場合
        """
        self._current_project_name = project_name
        self._load_burndown_chart()
        self._load_factor_analysis()

    @Slot()
    def on_refresh_requested(self) -> None:
        """再読み込みを要求.

        Signal:
            burndown_updated: バーンダウンチャートを更新
            factor_analysis_updated: 要因分析を更新
            error_occurred: エラーが発生した場合
        """
        if self._current_project_name:
            self._load_burndown_chart()
            self._load_factor_analysis()

    def _load_burndown_chart(self) -> None:
        """バーンダウンチャートを読み込む."""
        if not self._current_project_name:
            return

        try:
            chart_data = self.burndown_use_case.execute(self._current_project_name)
            self.burndown_updated.emit(chart_data)
            self.logger.info(
                f"Burndown chart updated for project: {self._current_project_name}"
            )
        except Exception as e:
            error_message = f"バーンダウンチャートの取得に失敗しました: {e}"
            self.logger.error(error_message, exc_info=True)
            self.error_occurred.emit(error_message)

    def _load_factor_analysis(self) -> None:
        """要因分析を読み込む."""
        if not self._current_project_name:
            return

        try:
            factor_data = self.factor_use_case.execute(self._current_project_name)
            self.factor_analysis_updated.emit(factor_data)
            self.logger.info(
                f"Factor analysis updated for project: {self._current_project_name}"
            )
        except Exception as e:
            error_message = f"要因分析の取得に失敗しました: {e}"
            self.logger.error(error_message, exc_info=True)
            self.error_occurred.emit(error_message)
