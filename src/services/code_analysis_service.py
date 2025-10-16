"""Serviço para análise de código usando COCOMO II."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from main import CodeAnalyzer
from models import CodeMetrics, CocomoResults
from analysis_config import DEFAULT_MONTHLY_SALARY_BRL
from utils.logger import get_logger

logger = get_logger(__name__)


class CodeAnalysisService:
    """
    Serviço responsável pela análise de código e cálculo de métricas COCOMO II.

    Este serviço encapsula a lógica de análise de código, fornecendo uma interface
    limpa para contagem de linhas, detecção de linguagens e cálculos COCOMO II.
    """

    def __init__(self, project_path: Path):
        """
        Inicializa o serviço de análise de código.

        Args:
            project_path: Caminho do projeto a ser analisado
        """
        self.project_path = project_path
        self.analyzer: Optional[CodeAnalyzer] = None
        self.metrics: Optional[CodeMetrics] = None
        self.cocomo_results: Optional[CocomoResults] = None

        logger.info(f"CodeAnalysisService inicializado para: {project_path}")

    def analyze(self, avg_salary_month_brl: float = DEFAULT_MONTHLY_SALARY_BRL) -> tuple[CodeMetrics, CocomoResults]:
        """
        Executa a análise completa de código.

        Args:
            avg_salary_month_brl: Salário médio mensal em BRL por pessoa

        Returns:
            Tupla com (CodeMetrics, CocomoResults)

        Raises:
            ValueError: Se nenhum arquivo de código for encontrado
        """
        logger.info("Iniciando análise de código")

        # Cria o analisador
        self.analyzer = CodeAnalyzer(self.project_path)

        # Analisa o diretório
        self.analyzer.analyze_directory()

        # Verifica se encontrou arquivos
        if self.analyzer.metrics.files_count == 0:
            logger.error("Nenhum arquivo de código encontrado")
            raise ValueError("Nenhum arquivo de código encontrado")

        self.metrics = self.analyzer.metrics

        # Calcula COCOMO II
        self.cocomo_results = self.analyzer.calculate_cocomo2(avg_salary_month_brl)

        logger.info(
            f"Análise concluída: {self.metrics.files_count} arquivos, "
            f"{self.metrics.code_lines} linhas de código"
        )

        return self.metrics, self.cocomo_results

    def get_metrics(self) -> Optional[CodeMetrics]:
        """
        Retorna as métricas de código calculadas.

        Returns:
            CodeMetrics ou None se análise não foi executada
        """
        return self.metrics

    def get_cocomo_results(self) -> Optional[CocomoResults]:
        """
        Retorna os resultados COCOMO II calculados.

        Returns:
            CocomoResults ou None se análise não foi executada
        """
        return self.cocomo_results

    def get_analyzer(self) -> Optional[CodeAnalyzer]:
        """
        Retorna o analisador interno (para casos de uso avançados).

        Returns:
            CodeAnalyzer ou None se análise não foi executada
        """
        return self.analyzer
