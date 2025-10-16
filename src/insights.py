"""Regras compartilhadas para geração de insights a partir das métricas."""

from __future__ import annotations

from typing import Sequence, Optional, Dict, Any

from analysis_config import (
    CHANGE_SIZE_RULES,
    COCOMO_COMPLEXITY_MESSAGES,
    COMMIT_EFFICIENCY_RULES,
    COMMIT_FREQUENCY_RULES,
    PRODUCTIVITY_RULES,
    PRODUCTIVITY_SCORE_RULES,
    TEAM_SIZE_RULES,
    TIME_RULES,
    VELOCITY_RULES,
)
from models import CocomoResults, GitMetrics, IntegratedMetrics, CodeMetrics


def _pick_lt(value: float, rules: Sequence[tuple[float, str]]) -> str:
    for threshold, message in rules:
        if value < threshold:
            return message
    # fallback em caso de lista vazia
    return ""


def _pick_gt(value: float, rules: Sequence[tuple[float, str]]) -> str:
    for threshold, message in rules:
        if value > threshold:
            return message
    return ""


def build_cocomo_insights(cocomo: CocomoResults) -> str:
    """Retorna os insights em formato de string para impressão."""
    insights: list[str] = []

    complexity_message = COCOMO_COMPLEXITY_MESSAGES.get(cocomo.complexity_level)
    if complexity_message:
        insights.append(complexity_message)

    insights.append(_pick_lt(cocomo.people_required, TEAM_SIZE_RULES))
    insights.append(_pick_lt(cocomo.time_months, TIME_RULES))
    insights.append(_pick_lt(cocomo.productivity, PRODUCTIVITY_RULES))

    return "\n".join(filter(None, insights))


def build_integrated_insights(integrated: IntegratedMetrics, git: GitMetrics | None = None) -> str:
    """Gera insights combinando indicadores integrados e métricas Git."""
    insights: list[str] = []

    insights.append(_pick_gt(integrated.velocity_ratio, VELOCITY_RULES))
    insights.append(_pick_gt(integrated.commit_efficiency, COMMIT_EFFICIENCY_RULES))
    insights.append(_pick_lt(integrated.change_percentage_per_commit, CHANGE_SIZE_RULES))
    insights.append(_pick_gt(integrated.commits_per_month, COMMIT_FREQUENCY_RULES))
    insights.append(_pick_gt(integrated.developer_productivity_score, PRODUCTIVITY_SCORE_RULES))

    return "\n".join(filter(None, insights))


def build_ai_insights(
    cocomo: CocomoResults,
    git: Optional[GitMetrics] = None,
    integrated: Optional[IntegratedMetrics] = None,
    code_metrics: Optional[CodeMetrics] = None,
    project_name: str = "Projeto",
    project_description: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Gera insights usando IA da OpenAI.

    Args:
        cocomo: Resultados COCOMO II
        git: Métricas Git (opcional)
        integrated: Métricas integradas (opcional)
        code_metrics: Métricas de código (opcional)
        project_name: Nome do projeto
        project_description: Descrição do projeto
        api_key: Chave API OpenAI (usa variável de ambiente se não fornecida)

    Returns:
        String formatada com insights de IA
    """
    try:
        from ai_insights import AIInsightsGenerator

        generator = AIInsightsGenerator(api_key=api_key)
        insights_result = generator.generate_insights(
            cocomo=cocomo,
            git=git,
            integrated=integrated,
            code_metrics=code_metrics,
            project_name=project_name,
            project_description=project_description
        )

        return generator.format_insights_for_display(insights_result)

    except ImportError:
        return "[red]❌ Módulo ai_insights não encontrado. Instale o pacote openai.[/red]"
    except ValueError as e:
        return f"[red]❌ {str(e)}[/red]"
    except Exception as e:
        return f"[red]❌ Erro ao gerar insights com IA: {str(e)}[/red]"
