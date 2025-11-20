"""Project detail widget."""

from PySide6.QtCore import Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.presentation.viewmodels.project_detail_viewmodel import (
    ProjectDetailViewModel,
)


class ProjectDetailWidget(QWidget):
    """プロジェクト詳細画面（バーンダウンチャート）."""

    def __init__(self, view_model: ProjectDetailViewModel) -> None:
        """初期化.

        Args:
            view_model: プロジェクト詳細 ViewModel
        """
        super().__init__()
        self.view_model = view_model

        # UI コンポーネント
        self.project_info = QLabel("プロジェクト情報")
        self.chart_view = QWebEngineView()
        self.factor_text = QTextEdit()
        self.factor_text.setReadOnly(True)
        self.factor_text.setMaximumHeight(150)
        self.refresh_button = QPushButton("更新")
        self.back_button = QPushButton("戻る")

        # レイアウト
        layout = QVBoxLayout()
        layout.addWidget(self.project_info)
        layout.addWidget(self.chart_view)
        layout.addWidget(QLabel("工数余剰要因分析:"))
        layout.addWidget(self.factor_text)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        # Signal/Slot 接続
        self.refresh_button.clicked.connect(self.view_model.on_refresh_requested)
        self.view_model.burndown_updated.connect(self.update_chart)
        self.view_model.factor_analysis_updated.connect(self.update_factor_analysis)
        self.view_model.error_occurred.connect(self.show_error)

    @Slot(object)
    def update_chart(self, chart_data) -> None:
        """バーンダウンチャートを更新する.

        Args:
            chart_data: バーンダウンチャート DTO
        """
        # プロジェクト情報の表示
        self.project_info.setText(f"プロジェクト: {chart_data.project_name}")

        # plotly でチャートを生成
        try:
            import plotly.graph_objects as go

            fig = go.Figure()

            # 理想線
            ideal_dates = [point.date for point in chart_data.ideal_line]
            ideal_hours = [point.remaining_hours for point in chart_data.ideal_line]
            fig.add_trace(
                go.Scatter(x=ideal_dates, y=ideal_hours, mode="lines", name="理想線")
            )

            # 実績線
            actual_dates = [point.date for point in chart_data.actual_line]
            actual_hours = [point.remaining_hours for point in chart_data.actual_line]
            fig.add_trace(
                go.Scatter(
                    x=actual_dates,
                    y=actual_hours,
                    mode="lines+markers",
                    name="実績線",
                )
            )

            # 現在日マーカー
            fig.add_vline(
                x=chart_data.current_date_marker, line_dash="dash", annotation_text="現在"
            )

            fig.update_layout(
                title="バーンダウンチャート", xaxis_title="日付", yaxis_title="残工数（時間）"
            )

            # HTML に変換して QWebEngineView に表示
            html = fig.to_html()
            self.chart_view.setHtml(html)

        except ImportError:
            # plotly がインストールされていない場合
            self.chart_view.setHtml(
                "<html><body><h1>plotly がインストールされていません</h1></body></html>"
            )

    @Slot(object)
    def update_factor_analysis(self, factor_data) -> None:
        """要因分析を更新する.

        Args:
            factor_data: 要因分析 DTO
        """
        if not factor_data.factors:
            self.factor_text.setText("工数余剰要因は検出されませんでした。")
            return

        text_lines = [
            f"確信度: {factor_data.confidence_level * 100:.1f}%\n",
            "要因一覧:",
        ]

        for i, factor in enumerate(factor_data.factors, 1):
            text_lines.append(
                f"{i}. [{factor.category}] {factor.description} "
                f"(影響工数: {factor.impact_hours:.2f}h, 確信度: {factor.confidence * 100:.1f}%)"
            )

        self.factor_text.setText("\n".join(text_lines))

    @Slot(str)
    def show_error(self, message: str) -> None:
        """エラーダイアログを表示する.

        Args:
            message: エラーメッセージ
        """
        QMessageBox.critical(self, "エラー", message)
