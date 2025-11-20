"""Main entry point for Profit Trace application."""

import logging
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication

from src.application.usecases.export_data_usecase import ExportDataUseCase
from src.application.usecases.generate_report_usecase import GenerateReportUseCase
from src.application.usecases.get_burndown_chart_usecase import (
    GetBurndownChartUseCase,
)
from src.application.usecases.get_factor_analysis_usecase import (
    GetFactorAnalysisUseCase,
)
from src.application.usecases.get_member_workload_usecase import (
    GetMemberWorkloadUseCase,
)
from src.application.usecases.get_project_list_usecase import GetProjectListUseCase
from src.application.usecases.import_project_usecase import ImportProjectUseCase
from src.application.usecases.import_work_record_usecase import (
    ImportWorkRecordUseCase,
)
from src.application.usecases.import_workday_calendar_usecase import (
    ImportWorkdayCalendarUseCase,
)
from src.domain.services.burndown_calculator import BurndownCalculator
from src.domain.services.consumption_rate_calculator import ConsumptionRateCalculator
from src.domain.services.factor_estimator import FactorEstimator
from src.infrastructure.database.initializer import DatabaseInitializer
from src.infrastructure.repositories.member_repository_impl import (
    MemberRepositoryImpl,
)
from src.infrastructure.repositories.project_repository_impl import (
    ProjectRepositoryImpl,
)
from src.infrastructure.repositories.work_record_repository_impl import (
    WorkRecordRepositoryImpl,
)
from src.infrastructure.repositories.workday_calendar_repository_impl import (
    WorkdayCalendarRepositoryImpl,
)
from src.presentation.viewmodels.import_viewmodel import ImportViewModel
from src.presentation.viewmodels.main_viewmodel import MainViewModel
from src.presentation.viewmodels.member_workload_viewmodel import (
    MemberWorkloadViewModel,
)
from src.presentation.viewmodels.project_detail_viewmodel import (
    ProjectDetailViewModel,
)
from src.presentation.viewmodels.project_list_viewmodel import ProjectListViewModel
from src.presentation.viewmodels.report_viewmodel import ReportViewModel
from src.presentation.views.main_window import MainWindow


def setup_logging() -> logging.Logger:
    """ロギング設定を初期化.

    Returns:
        ロガーインスタンス
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("profit_trace.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def initialize_database(db_path: str, logger: logging.Logger) -> None:
    """データベースを初期化.

    Args:
        db_path: データベースファイルパス
        logger: ロガー
    """
    DatabaseInitializer.initialize_database(db_path)
    logger.info(f"Database initialized: {db_path}")


def create_application(logger: logging.Logger) -> MainWindow:
    """アプリケーションを作成.

    Args:
        logger: ロガー

    Returns:
        MainWindow インスタンス
    """
    # データベースパス
    db_path = "profit_trace.db"

    # データベース初期化
    initialize_database(db_path, logger)

    # Repository の初期化
    project_repo = ProjectRepositoryImpl(db_path)
    work_record_repo = WorkRecordRepositoryImpl(db_path)
    calendar_repo = WorkdayCalendarRepositoryImpl(db_path)
    member_repo = MemberRepositoryImpl(db_path)

    # Domain Services の初期化
    burndown_calc = BurndownCalculator()
    consumption_rate_calc = ConsumptionRateCalculator()
    factor_estimator = FactorEstimator()

    # Use Cases の初期化
    import_project_uc = ImportProjectUseCase(project_repo, logger)
    import_work_record_uc = ImportWorkRecordUseCase(
        work_record_repo, member_repo, logger
    )
    import_calendar_uc = ImportWorkdayCalendarUseCase(calendar_repo, logger)
    get_project_list_uc = GetProjectListUseCase(
        project_repo, work_record_repo, consumption_rate_calc
    )
    get_burndown_chart_uc = GetBurndownChartUseCase(
        project_repo, work_record_repo, calendar_repo, burndown_calc
    )
    get_member_workload_uc = GetMemberWorkloadUseCase(work_record_repo, calendar_repo)
    get_factor_analysis_uc = GetFactorAnalysisUseCase(
        project_repo, work_record_repo, calendar_repo, factor_estimator
    )
    generate_report_uc = GenerateReportUseCase(
        project_repo, work_record_repo, member_repo, consumption_rate_calc
    )
    export_data_uc = ExportDataUseCase(
        project_repo, work_record_repo, calendar_repo, logger=logger
    )

    # ViewModels の初期化
    main_vm = MainViewModel()
    project_list_vm = ProjectListViewModel(get_project_list_uc, logger)
    project_detail_vm = ProjectDetailViewModel(
        get_burndown_chart_uc, get_factor_analysis_uc, logger
    )
    member_workload_vm = MemberWorkloadViewModel(get_member_workload_uc, logger)
    report_vm = ReportViewModel(generate_report_uc, export_data_uc, logger)
    import_vm = ImportViewModel(
        import_project_uc, import_work_record_uc, import_calendar_uc, logger
    )

    # MainWindow の初期化
    main_window = MainWindow(
        main_vm,
        project_list_vm,
        project_detail_vm,
        member_workload_vm,
        report_vm,
        import_vm,
        logger,
    )

    return main_window


def main():
    """アプリケーションのエントリーポイント."""
    # ロギング設定
    logger = setup_logging()
    logger.info("Starting Profit Trace application")

    # Qt アプリケーション初期化
    app = QApplication(sys.argv)

    # メインウィンドウ作成
    main_window = create_application(logger)
    main_window.show()

    # イベントループ実行
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
