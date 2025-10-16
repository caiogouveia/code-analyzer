"""Serviço para análise de repositório Git."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List

from git_analyzer import GitAnalyzer
from models import GitMetrics, CommitInfo
from exceptions import GitAnalysisError
from utils.logger import get_logger

logger = get_logger(__name__)


class GitAnalysisService:
    """
    Serviço responsável pela análise de repositório Git.

    Este serviço encapsula a lógica de extração e análise de commits,
    fornecendo métricas sobre o histórico do repositório.
    """

    def __init__(self, repo_path: Path):
        """
        Inicializa o serviço de análise Git.

        Args:
            repo_path: Caminho do repositório Git

        Raises:
            GitAnalysisError: Se o caminho não é um repositório Git válido
        """
        self.repo_path = repo_path

        # Verifica se é um repositório Git
        if not (repo_path / '.git').exists():
            error_msg = f"'{repo_path}' não é um repositório Git"
            logger.error(error_msg)
            raise GitAnalysisError(error_msg)

        self.analyzer: Optional[GitAnalyzer] = None
        self.commits: Optional[List[CommitInfo]] = None
        self.metrics: Optional[GitMetrics] = None

        logger.info(f"GitAnalysisService inicializado para: {repo_path}")

    def analyze(self) -> GitMetrics:
        """
        Executa a análise completa do repositório Git.

        Returns:
            GitMetrics com as métricas calculadas

        Raises:
            GitAnalysisError: Se ocorrer erro na análise
        """
        logger.info("Iniciando análise do repositório Git")

        try:
            # Cria o analisador
            self.analyzer = GitAnalyzer(self.repo_path)

            # Obtém commits
            self.commits = self.analyzer.get_commits()

            if not self.commits:
                error_msg = "Nenhum commit encontrado no repositório"
                logger.error(error_msg)
                raise GitAnalysisError(error_msg)

            # Calcula métricas
            self.metrics = self.analyzer.calculate_metrics(self.commits)

            logger.info(
                f"Análise Git concluída: {self.metrics.total_commits} commits, "
                f"{self.metrics.total_authors} autores"
            )

            return self.metrics

        except ValueError as e:
            logger.error(f"Erro ao analisar repositório: {e}")
            raise GitAnalysisError(f"Erro ao analisar repositório: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao analisar repositório: {e}")
            raise GitAnalysisError(f"Erro inesperado: {e}")

    def get_commits(self) -> Optional[List[CommitInfo]]:
        """
        Retorna a lista de commits analisados.

        Returns:
            Lista de CommitInfo ou None se análise não foi executada
        """
        return self.commits

    def get_metrics(self) -> Optional[GitMetrics]:
        """
        Retorna as métricas Git calculadas.

        Returns:
            GitMetrics ou None se análise não foi executada
        """
        return self.metrics

    def get_analyzer(self) -> Optional[GitAnalyzer]:
        """
        Retorna o analisador interno (para casos de uso avançados).

        Returns:
            GitAnalyzer ou None se análise não foi executada
        """
        return self.analyzer
