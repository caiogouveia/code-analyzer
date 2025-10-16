"""Serviço integrado para análise completa de projetos."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Callable

from models import (
    CocomoResults,
    GitMetrics,
    IntegratedMetrics,
    SecurityMetrics,
    CodeMetrics,
)
from services.code_analysis_service import CodeAnalysisService
from services.git_analysis_service import GitAnalysisService
from services.security_analysis_service import SecurityAnalysisService
from services.insights_service import InsightsService
from analysis_config import DEFAULT_MONTHLY_SALARY_BRL, WORKING_DAYS_PER_MONTH
from exceptions import CocomoAnalysisError, GitAnalysisError, SecurityAnalysisError
from utils.logger import get_logger

logger = get_logger(__name__)


class IntegratedAnalysisService:
    """
    Serviço principal que coordena todas as análises.

    Este serviço orquestra as análises de código, Git e segurança,
    calculando métricas integradas e gerando insights.
    """

    def __init__(self, project_path: Path):
        """
        Inicializa o serviço de análise integrada.

        Args:
            project_path: Caminho do projeto a ser analisado
        """
        self.project_path = project_path

        # Serviços especializados
        self.code_service = CodeAnalysisService(project_path)
        self.git_service: Optional[GitAnalysisService] = None
        self.security_service: Optional[SecurityAnalysisService] = None
        self.insights_service = InsightsService()

        # Resultados
        self.code_metrics: Optional[CodeMetrics] = None
        self.cocomo_results: Optional[CocomoResults] = None
        self.git_metrics: Optional[GitMetrics] = None
        self.security_metrics: Optional[SecurityMetrics] = None
        self.integrated_metrics: Optional[IntegratedMetrics] = None

        logger.info(f"IntegratedAnalysisService inicializado para: {project_path}")

    def analyze(
        self,
        avg_salary_month_brl: float = DEFAULT_MONTHLY_SALARY_BRL,
        run_security_analysis: bool = True,
        security_config: str = "auto",
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> tuple[CocomoResults, GitMetrics, IntegratedMetrics, Optional[SecurityMetrics]]:
        """
        Executa análise completa do projeto.

        Args:
            avg_salary_month_brl: Salário médio mensal em BRL por pessoa
            run_security_analysis: Se True, executa análise de segurança
            security_config: Configuração do Semgrep
            progress_callback: Função de callback para progresso (percent, message)

        Returns:
            Tupla com (CocomoResults, GitMetrics, IntegratedMetrics, SecurityMetrics?)

        Raises:
            CocomoAnalysisError: Se ocorrer erro na análise
        """
        logger.info("Iniciando análise integrada")

        try:
            # 1. Análise de código (0-30%)
            self._update_progress(progress_callback, 10, "Analisando código-fonte...")
            self.code_metrics, self.cocomo_results = self.code_service.analyze(
                avg_salary_month_brl
            )
            self._update_progress(progress_callback, 30, "Análise de código concluída")

            # 2. Análise Git (30-60%)
            self._update_progress(progress_callback, 35, "Analisando repositório Git...")
            try:
                self.git_service = GitAnalysisService(self.project_path)
                self.git_metrics = self.git_service.analyze()
                self._update_progress(progress_callback, 60, "Análise Git concluída")
            except GitAnalysisError as e:
                logger.warning(f"Análise Git falhou: {e}")
                # Continua sem métricas Git
                self.git_metrics = None

            # 3. Análise de segurança (60-80%) - opcional
            if run_security_analysis:
                self._update_progress(
                    progress_callback, 62, "Analisando segurança..."
                )
                try:
                    self.security_service = SecurityAnalysisService(self.project_path)
                    if self.security_service.check_semgrep_available():
                        self.security_metrics = self.security_service.analyze(
                            config=security_config
                        )
                        self._update_progress(
                            progress_callback, 80, "Análise de segurança concluída"
                        )
                    else:
                        logger.warning("Semgrep não disponível, pulando análise de segurança")
                        self._update_progress(
                            progress_callback, 80, "Análise de segurança pulada"
                        )
                except SecurityAnalysisError as e:
                    logger.warning(f"Análise de segurança falhou: {e}")
                    self._update_progress(
                        progress_callback, 80, "Análise de segurança falhou"
                    )
            else:
                self._update_progress(progress_callback, 80, "Análise de segurança desabilitada")

            # 4. Métricas integradas (80-100%)
            if self.git_metrics:
                self._update_progress(
                    progress_callback, 85, "Calculando métricas integradas..."
                )
                self.integrated_metrics = self._calculate_integrated_metrics(
                    self.cocomo_results,
                    self.git_metrics,
                    self.code_metrics.code_lines
                )
                self._update_progress(progress_callback, 100, "Análise concluída!")
            else:
                logger.warning("Pulando métricas integradas (sem Git)")
                self._update_progress(progress_callback, 100, "Análise concluída (sem Git)")

            logger.info("Análise integrada concluída com sucesso")
            return (
                self.cocomo_results,
                self.git_metrics,
                self.integrated_metrics,
                self.security_metrics
            )

        except Exception as e:
            logger.error(f"Erro na análise integrada: {e}")
            raise CocomoAnalysisError(f"Erro na análise integrada: {e}")

    def _update_progress(
        self,
        callback: Optional[Callable[[int, str], None]],
        percent: int,
        message: str
    ) -> None:
        """Atualiza o progresso via callback."""
        if callback:
            callback(percent, message)

    def _calculate_integrated_metrics(
        self,
        cocomo: CocomoResults,
        git: GitMetrics,
        total_lines: int
    ) -> IntegratedMetrics:
        """
        Calcula métricas integradas entre COCOMO e Git.

        Args:
            cocomo: Resultados COCOMO II
            git: Métricas Git
            total_lines: Total de linhas de código

        Returns:
            IntegratedMetrics calculadas
        """
        logger.debug("Calculando métricas integradas")

        # Linhas por commit
        lines_per_commit = total_lines / git.total_commits if git.total_commits > 0 else 0

        # Commits necessários para recriar
        commits_needed = (
            cocomo.kloc * 1000 / lines_per_commit if lines_per_commit > 0 else 0
        )

        # Velocidade real (linhas/dia)
        actual_velocity = (
            total_lines / git.repository_age_days if git.repository_age_days > 0 else 0
        )

        # Velocidade estimada COCOMO (linhas/dia)
        estimated_velocity = (
            cocomo.productivity / WORKING_DAYS_PER_MONTH
            if cocomo.productivity > 0 else 0
        )

        # Razão velocidade (real/estimado)
        velocity_ratio = (
            actual_velocity / estimated_velocity if estimated_velocity > 0 else 0
        )

        # Eficiência do commit (linhas úteis vs churn)
        total_changes = git.total_insertions + git.total_deletions
        commit_efficiency = (
            (total_lines / total_changes * 100) if total_changes > 0 else 0
        )

        # % média de mudança por commit
        change_percentage_per_commit = (
            (git.avg_changes_per_commit / total_lines * 100) if total_lines > 0 else 0
        )

        # Score de produtividade do desenvolvedor
        base_score = 50
        velocity_score = min((velocity_ratio * 25), 25)  # Max 25 pontos
        efficiency_score = min((commit_efficiency / 100 * 15), 15)  # Max 15 pontos
        complexity_bonus = (
            10 if cocomo.complexity_level == "Alta"
            else 5 if cocomo.complexity_level == "Média"
            else 0
        )

        developer_productivity_score = (
            base_score + velocity_score + efficiency_score + complexity_bonus
        )

        # Commits por mês
        commits_per_month = (
            git.total_commits / (git.repository_age_days / 30)
            if git.repository_age_days > 0 else 0
        )

        return IntegratedMetrics(
            cocomo_kloc=cocomo.kloc,
            cocomo_effort=cocomo.effort_person_months,
            cocomo_time_months=cocomo.time_months,
            cocomo_people=cocomo.people_required,
            cocomo_cost_brl=cocomo.cost_estimate_brl,
            total_commits=git.total_commits,
            avg_changes_per_commit=git.avg_changes_per_commit,
            commits_per_month=commits_per_month,
            lines_per_commit=lines_per_commit,
            commits_needed_to_rebuild=commits_needed,
            actual_velocity=actual_velocity,
            estimated_velocity=estimated_velocity,
            velocity_ratio=velocity_ratio,
            commit_efficiency=commit_efficiency,
            change_percentage_per_commit=change_percentage_per_commit,
            developer_productivity_score=developer_productivity_score
        )

    def get_insights(self) -> str:
        """
        Gera insights consolidados de todas as análises.

        Returns:
            String formatada com os insights

        Raises:
            ValueError: Se a análise não foi executada
        """
        if not self.cocomo_results:
            raise ValueError("Análise não foi executada")

        all_insights = []

        # Insights integrados
        if self.integrated_metrics and self.git_metrics:
            integrated_insights = self.insights_service.generate_integrated_insights(
                self.integrated_metrics,
                self.git_metrics
            )
            all_insights.extend(integrated_insights)

        # Insights de segurança
        if self.security_metrics:
            security_insights = self.insights_service.generate_security_insights(
                self.security_metrics
            )
            all_insights.extend(security_insights)

        # Insights de equipe
        if self.git_metrics:
            team_insights = self.insights_service.generate_team_insights(
                self.git_metrics
            )
            all_insights.extend(team_insights)

        return self.insights_service.format_insights(all_insights)

    def get_code_analyzer(self):
        """Retorna o analisador de código interno."""
        return self.code_service.get_analyzer()
