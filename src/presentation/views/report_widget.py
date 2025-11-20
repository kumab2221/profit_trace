"""Report widget."""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.presentation.viewmodels.report_viewmodel import ReportViewModel


class ReportWidget(QWidget):
    """レポート画面."""

    def __init__(self, view_model: ReportViewModel) -> None:
        """初期化.

        Args:
            view_model: レポート ViewModel
        """
        super().__init__()
        self.view_model = view_model

        # UI コンポーネント
        self.summary_label = QLabel("サマリー情報")
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.generate_button = QPushButton("レポート生成")
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["csv", "json"])
        self.export_button = QPushButton("データエクスポート")

        # レイアウト
        layout = QVBoxLayout()
        layout.addWidget(self.summary_label)
        layout.addWidget(self.report_text)
        layout.addWidget(self.generate_button)
        layout.addWidget(QLabel("エクスポート形式:"))
        layout.addWidget(self.export_format_combo)
        layout.addWidget(self.export_button)
        self.setLayout(layout)

        # Signal/Slot 接続
        self.generate_button.clicked.connect(self.view_model.on_generate_requested)
        self.export_button.clicked.connect(self._on_export_clicked)
        self.view_model.report_updated.connect(self.update_report)
        self.view_model.export_completed.connect(self.show_export_success)
        self.view_model.error_occurred.connect(self.show_error)

        # 初期表示
        self.view_model.on_generate_requested()

    @Slot(object)
    def update_report(self, report_data) -> None:
        """レポートを更新する.

        Args:
            report_data: レポート DTO
        """
        # サマリー情報の表示
        summary = report_data.summary
        summary_text = (
            f"総プロジェクト数: {summary.total_projects} / "
            f"稼働中: {summary.active_projects} / "
            f"総メンバー数: {summary.total_members}"
        )
        self.summary_label.setText(summary_text)

        # レポートの表示
        text_lines = [
            "【サマリー】",
            f"総契約工数: {summary.total_contracted_hours:.2f}時間",
            f"総消化工数: {summary.total_consumed_hours:.2f}時間",
            f"全体消化率: {summary.overall_consumption_rate * 100:.1f}%\n",
            "【プロジェクト一覧】",
        ]

        for project in report_data.projects:
            text_lines.append(
                f"  - {project.name}: {project.consumption_rate * 100:.1f}% ({project.status})"
            )

        text_lines.append("\n【メンバー別稼働状況】")
        for member in report_data.members:
            text_lines.append(f"  - {member.member_name}: {member.total_hours:.2f}h")

        self.report_text.setText("\n".join(text_lines))

    @Slot()
    def _on_export_clicked(self) -> None:
        """エクスポートボタンがクリックされた時の処理."""
        # ディレクトリ選択ダイアログを表示
        output_dir = QFileDialog.getExistingDirectory(
            self, "エクスポート先ディレクトリを選択", ""
        )

        if output_dir:
            export_format = self.export_format_combo.currentText()
            self.view_model.on_export_requested(export_format, output_dir)

    @Slot(dict)
    def show_export_success(self, exported_files: dict) -> None:
        """エクスポート成功ダイアログを表示する.

        Args:
            exported_files: エクスポートされたファイルパスの辞書
        """
        file_list = "\n".join(f"  - {path}" for path in exported_files.values())
        message = f"データのエクスポートが完了しました:\n\n{file_list}"
        QMessageBox.information(self, "エクスポート完了", message)

    @Slot(str)
    def show_error(self, message: str) -> None:
        """エラーダイアログを表示する.

        Args:
            message: エラーメッセージ
        """
        QMessageBox.critical(self, "エラー", message)
