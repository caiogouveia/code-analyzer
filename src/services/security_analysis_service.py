"""Serviço para análise de segurança com Semgrep."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from security_analyzer import SecurityAnalyzer
from models import SecurityMetrics
from exceptions import SecurityAnalysisError
from utils.logger import get_logger
from utils.score_calculator import calculate_security_score

logger = get_logger(__name__)


class SecurityAnalysisService:
    """
    Serviço responsável pela análise de segurança usando Semgrep.

    Este serviço encapsula a lógica de análise de segurança estática,
    fornecendo detecção de vulnerabilidades e problemas no código.
    """

    def __init__(self, project_path: Path):
        """
        Inicializa o serviço de análise de segurança.

        Args:
            project_path: Caminho do projeto a ser analisado
        """
        self.project_path = project_path
        self.analyzer: Optional[SecurityAnalyzer] = None
        self.metrics: Optional[SecurityMetrics] = None

        logger.info(f"SecurityAnalysisService inicializado para: {project_path}")

    def check_semgrep_available(self) -> bool:
        """
        Verifica se o Semgrep está instalado e disponível.

        Returns:
            True se Semgrep está disponível, False caso contrário
        """
        analyzer = SecurityAnalyzer(self.project_path)
        return analyzer.check_semgrep_available()

    def analyze(
        self,
        config: str = "auto",
        max_findings: int = 1000
    ) -> SecurityMetrics:
        """
        Executa a análise de segurança.

        Args:
            config: Configuração do Semgrep ('auto', 'p/security-audit', etc.)
            max_findings: Número máximo de descobertas a retornar

        Returns:
            SecurityMetrics com as métricas e descobertas

        Raises:
            SecurityAnalysisError: Se ocorrer erro na análise
        """
        logger.info(f"Iniciando análise de segurança (config={config})")

        try:
            # Cria o analisador
            self.analyzer = SecurityAnalyzer(self.project_path)

            # Verifica se Semgrep está disponível
            if not self.analyzer.check_semgrep_available():
                error_msg = "Semgrep não está instalado ou não está no PATH"
                logger.error(error_msg)
                raise SecurityAnalysisError(error_msg)

            # Executa a análise
            self.metrics = self.analyzer.analyze(
                config=config,
                max_findings=max_findings
            )

            logger.info(
                f"Análise de segurança concluída: {self.metrics.total_findings} descobertas, "
                f"{self.metrics.files_scanned} arquivos escaneados"
            )

            return self.metrics

        except Exception as e:
            logger.error(f"Erro ao executar análise de segurança: {e}")
            raise SecurityAnalysisError(f"Erro na análise de segurança: {e}")

    def get_metrics(self) -> Optional[SecurityMetrics]:
        """
        Retorna as métricas de segurança calculadas.

        Returns:
            SecurityMetrics ou None se análise não foi executada
        """
        return self.metrics

    def get_security_score(self) -> float:
        """
        Calcula o score de segurança baseado nas métricas.

        Returns:
            Score de segurança (0-100)

        Raises:
            ValueError: Se a análise não foi executada
        """
        if not self.metrics:
            raise ValueError("Análise de segurança não foi executada")

        return calculate_security_score(self.metrics)

    def get_top_vulnerable_files(self, top: int = 10) -> list[tuple[str, int]]:
        """
        Retorna os arquivos mais vulneráveis.

        Args:
            top: Número de arquivos a retornar

        Returns:
            Lista de tuplas (arquivo, número_de_problemas)

        Raises:
            ValueError: Se a análise não foi executada
        """
        if not self.analyzer:
            raise ValueError("Análise de segurança não foi executada")

        return self.analyzer.get_top_vulnerable_files(top)

    def get_analyzer(self) -> Optional[SecurityAnalyzer]:
        """
        Retorna o analisador interno (para casos de uso avançados).

        Returns:
            SecurityAnalyzer ou None se análise não foi executada
        """
        return self.analyzer
