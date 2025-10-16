"""Serviço para geração de insights a partir de métricas."""

from __future__ import annotations

from typing import List

from models import IntegratedMetrics, GitMetrics, SecurityMetrics
from utils.logger import get_logger
from utils.score_calculator import calculate_security_score

logger = get_logger(__name__)


class InsightsService:
    """
    Serviço responsável pela geração de insights e recomendações.

    Este serviço analisa métricas integradas e gera insights acionáveis
    sobre a produtividade, qualidade e segurança do código.
    """

    def __init__(self):
        """Inicializa o serviço de insights."""
        logger.info("InsightsService inicializado")

    def generate_integrated_insights(
        self,
        integrated: IntegratedMetrics,
        git: GitMetrics
    ) -> List[str]:
        """
        Gera insights baseados nas métricas integradas.

        Args:
            integrated: Métricas integradas COCOMO + Git
            git: Métricas do repositório Git

        Returns:
            Lista de strings com os insights
        """
        insights = []

        # Análise de velocidade
        if integrated.velocity_ratio > 1.2:
            insights.append("🚀 Velocidade acima do esperado - Equipe muito produtiva!")
        elif integrated.velocity_ratio > 0.8:
            insights.append("✓ Velocidade dentro do esperado")
        else:
            insights.append("⚠️  Velocidade abaixo do esperado - Revisar impedimentos")

        # Análise de eficiência
        if integrated.commit_efficiency > 50:
            insights.append("✓ Alta eficiência de commits - Baixo retrabalho")
        elif integrated.commit_efficiency > 30:
            insights.append("⚡ Eficiência moderada - Algum retrabalho presente")
        else:
            insights.append("⚠️  Baixa eficiência - Alto retrabalho (churn)")

        # Análise de mudança por commit
        if integrated.change_percentage_per_commit < 1:
            insights.append("✓ Commits pequenos e incrementais - Boa prática")
        elif integrated.change_percentage_per_commit < 5:
            insights.append("⚡ Tamanho de commit moderado")
        else:
            insights.append("⚠️  Commits muito grandes - Considere commits menores")

        # Análise de frequência
        if integrated.commits_per_month > 40:
            insights.append("✓ Alta frequência de commits - Desenvolvimento ativo")
        elif integrated.commits_per_month > 20:
            insights.append("⚡ Frequência moderada de commits")
        else:
            insights.append("📊 Baixa frequência de commits")

        # Análise de score
        if integrated.developer_productivity_score >= 75:
            insights.append("🌟 Excelente produtividade da equipe!")
        elif integrated.developer_productivity_score >= 50:
            insights.append("👍 Boa produtividade geral")
        else:
            insights.append("📈 Oportunidade de melhoria na produtividade")

        logger.info(f"Gerados {len(insights)} insights integrados")
        return insights

    def generate_security_insights(self, security: SecurityMetrics) -> List[str]:
        """
        Gera insights baseados nas métricas de segurança.

        Args:
            security: Métricas de segurança

        Returns:
            Lista de strings com os insights
        """
        insights = []
        score = calculate_security_score(security)

        # Análise do score geral
        if score >= 90:
            insights.append("🛡️ Excelente postura de segurança!")
        elif score >= 75:
            insights.append("✓ Boa segurança geral")
        elif score >= 60:
            insights.append("⚠️  Segurança moderada - Atenção necessária")
        else:
            insights.append("🚨 Problemas de segurança significativos detectados")

        # Análise de descobertas críticas
        if security.critical_findings > 0:
            insights.append(
                f"🔴 URGENTE: {security.critical_findings} vulnerabilidade(s) crítica(s) "
                "devem ser corrigidas imediatamente!"
            )

        if security.high_findings > 5:
            insights.append(
                f"🟠 {security.high_findings} problemas de alta severidade "
                "requerem atenção prioritária"
            )

        # Análise por categoria
        if security.security_issues > security.total_findings * 0.5:
            insights.append("⚠️  Maioria dos problemas são relacionados a segurança")

        if security.best_practice_issues > security.total_findings * 0.3:
            insights.append("📋 Muitas violações de boas práticas - revisar guidelines")

        logger.info(f"Gerados {len(insights)} insights de segurança")
        return insights

    def generate_team_insights(self, git: GitMetrics) -> List[str]:
        """
        Gera insights sobre a equipe baseados nas métricas Git.

        Args:
            git: Métricas do repositório Git

        Returns:
            Lista de strings com os insights
        """
        insights = []

        # Análise de concentração de commits
        if git.authors_commits:
            sorted_authors = sorted(
                git.authors_commits.items(),
                key=lambda x: x[1],
                reverse=True
            )

            top_author_commits = sorted_authors[0][1] if sorted_authors else 0
            top_author_percentage = (
                (top_author_commits / git.total_commits * 100)
                if git.total_commits > 0 else 0
            )

            if top_author_percentage > 70:
                insights.append(
                    "⚠️  Concentração muito alta de commits em um único autor "
                    "- risco de dependência"
                )
            elif top_author_percentage > 50:
                insights.append(
                    "⚡ Concentração moderada de commits - "
                    "considere distribuir mais o conhecimento"
                )
            else:
                insights.append("✓ Boa distribuição de contribuições entre a equipe")

        # Análise de tamanho da equipe
        if git.total_authors == 1:
            insights.append("👤 Projeto individual - considere envolver mais colaboradores")
        elif git.total_authors <= 3:
            insights.append("👥 Equipe pequena - desenvolvimento focado")
        elif git.total_authors <= 10:
            insights.append("👥 Equipe de tamanho médio - boa escala")
        else:
            insights.append(
                "👥 Equipe grande - certifique-se de ter processos bem definidos"
            )

        # Análise de atividade
        if git.commits_per_day >= 5:
            insights.append("🔥 Repositório muito ativo - desenvolvimento intenso")
        elif git.commits_per_day >= 1:
            insights.append("✓ Atividade de desenvolvimento regular")
        else:
            insights.append("📊 Atividade de desenvolvimento moderada")

        logger.info(f"Gerados {len(insights)} insights de equipe")
        return insights

    def format_insights(self, insights: List[str]) -> str:
        """
        Formata lista de insights para exibição.

        Args:
            insights: Lista de insights

        Returns:
            String formatada com os insights
        """
        return "\n".join(insights)
