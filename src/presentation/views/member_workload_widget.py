"""Member workload widget."""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.presentation.viewmodels.member_workload_viewmodel import (
    MemberWorkloadViewModel,
)


class MemberWorkloadWidget(QWidget):
    """メンバー稼働状況画面."""

    def __init__(self, view_model: MemberWorkloadViewModel) -> None:
        """初期化.

        Args:
            view_model: メンバー稼働状況 ViewModel
        """
        super().__init__()
        self.view_model = view_model

        # UI コンポーネント
        self.member_info = QLabel("メンバー情報")
        self.workload_text = QTextEdit()
        self.workload_text.setReadOnly(True)
        self.refresh_button = QPushButton("更新")
        self.back_button = QPushButton("戻る")

        # レイアウト
        layout = QVBoxLayout()
        layout.addWidget(self.member_info)
        layout.addWidget(self.workload_text)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        # Signal/Slot 接続
        self.refresh_button.clicked.connect(self.view_model.on_refresh_requested)
        self.view_model.workload_updated.connect(self.update_workload)
        self.view_model.error_occurred.connect(self.show_error)

    @Slot(object)
    def update_workload(self, workload_data) -> None:
        """稼働状況を更新する.

        Args:
            workload_data: メンバー稼働状況 DTO
        """
        # メンバー情報の表示
        self.member_info.setText(f"メンバー: {workload_data.member_name}")

        # 稼働状況の表示
        text_lines = [
            f"総工数: {workload_data.total_hours:.2f}時間\n",
            "プロジェクト別工数配分:",
        ]

        for dist in workload_data.project_distribution:
            text_lines.append(
                f"  - {dist.project_name}: {dist.hours:.2f}h ({dist.percentage * 100:.1f}%)"
            )

        if workload_data.idle_periods:
            text_lines.append("\n稼働していない期間:")
            for period in workload_data.idle_periods:
                text_lines.append(
                    f"  - {period.start_date.isoformat()} 〜 {period.end_date.isoformat()} ({period.days}日)"
                )
        else:
            text_lines.append("\n稼働していない期間はありません。")

        self.workload_text.setText("\n".join(text_lines))

    @Slot(str)
    def show_error(self, message: str) -> None:
        """エラーダイアログを表示する.

        Args:
            message: エラーメッセージ
        """
        QMessageBox.critical(self, "エラー", message)
