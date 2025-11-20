"""Get factor analysis use case."""

from src.application.dtos.factor_analysis_dto import Factor, FactorAnalysisDTO
from src.domain.repositories.project_repository import ProjectRepository
from src.domain.repositories.work_record_repository import WorkRecordRepository
from src.domain.repositories.workday_calendar_repository import (
    WorkdayCalendarRepository,
)
from src.domain.services.factor_estimator import FactorEstimator


class GetFactorAnalysisUseCase:
    """工数余剰要因分析取得ユースケース."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        work_record_repo: WorkRecordRepository,
        calendar_repo: WorkdayCalendarRepository,
        estimator: FactorEstimator | None = None,
    ) -> None:
        """初期化.

        Args:
            project_repo: プロジェクトリポジトリ
            work_record_repo: 工数実績リポジトリ
            calendar_repo: 営業日カレンダーリポジトリ
            estimator: 要因推定サービス（省略時は新規インスタンス）
        """
        self.project_repo = project_repo
        self.work_record_repo = work_record_repo
        self.calendar_repo = calendar_repo
        self.estimator = estimator or FactorEstimator()

    def execute(self, project_name: str) -> FactorAnalysisDTO:
        """工数余剰要因分析を取得する.

        Args:
            project_name: プロジェクト名

        Returns:
            要因分析 DTO

        Raises:
            ValueError: プロジェクトが見つからない場合
        """
        # プロジェクト取得
        project = self.project_repo.find_by_name(project_name)
        if project is None:
            raise ValueError(f"Project not found: {project_name}")

        # 工数実績取得
        work_records = self.work_record_repo.find_all()

        # 要因推定
        domain_factors = self.estimator.estimate_factors(
            project, work_records, self.calendar_repo
        )

        # ドメイン層の Factor を DTO の Factor に変換
        factors: list[Factor] = []
        for domain_factor in domain_factors:
            # factor_type を category にマッピング
            category = self._map_factor_type_to_category(domain_factor.factor_type)

            # confidence を factor_type に基づいて設定
            confidence = self._calculate_confidence(domain_factor.factor_type)

            factors.append(
                Factor(
                    category=category,
                    description=domain_factor.description,
                    impact_hours=domain_factor.impact_hours,
                    confidence=confidence,
                )
            )

        # 全体的な確信度を計算（各要因の確信度の平均）
        confidence_level = (
            sum(factor.confidence for factor in factors) / len(factors)
            if factors
            else 0.0
        )

        # DTO 生成
        return FactorAnalysisDTO(
            project_name=project_name,
            factors=factors,
            confidence_level=confidence_level,
        )

    def _map_factor_type_to_category(self, factor_type: str) -> str:
        """factor_type を category にマッピングする.

        Args:
            factor_type: ドメイン層の要因タイプ

        Returns:
            カテゴリ名
        """
        # factor_type から category へのマッピング
        mapping = {
            "early_completion": "その他",
            "low_workload": "複数PJ掛け持ち",
            "holidays": "休日出勤",
        }
        return mapping.get(factor_type, "その他")

    def _calculate_confidence(self, factor_type: str) -> float:
        """要因タイプに基づいて確信度を計算する.

        Args:
            factor_type: ドメイン層の要因タイプ

        Returns:
            確信度（0.0 ~ 1.0）
        """
        # 要因タイプごとの確信度
        confidence_map = {
            "early_completion": 0.8,  # 早期完了は比較的確信度が高い
            "low_workload": 0.6,  # 低稼働率は中程度
            "holidays": 0.7,  # 休日・休暇は比較的高い
        }
        return confidence_map.get(factor_type, 0.5)
