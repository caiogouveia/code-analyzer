"""Calculadora de scores para análises."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import SecurityMetrics

from analysis_config import SECURITY_SEVERITY_WEIGHTS


def calculate_security_score(metrics: SecurityMetrics) -> float:
    """
    Calcula um score de segurança de 0-100 baseado nas descobertas.

    O score é calculado usando pesos por severidade e uma escala logarítmica
    para suavizar o impacto de grandes números de descobertas.

    Args:
        metrics: Métricas de segurança contendo as descobertas

    Returns:
        float: Score de 0-100, onde:
            - 100 = sem problemas
            - 80-99 = excelente segurança
            - 60-79 = boa segurança
            - 40-59 = segurança adequada
            - 20-39 = segurança fraca
            - 0-19 = segurança crítica

    Examples:
        >>> from models import SecurityMetrics
        >>> metrics = SecurityMetrics(total_findings=0)
        >>> calculate_security_score(metrics)
        100.0

        >>> metrics = SecurityMetrics(
        ...     total_findings=5,
        ...     critical_findings=1,
        ...     high_findings=2,
        ...     medium_findings=2
        ... )
        >>> score = calculate_security_score(metrics)
        >>> 0 <= score <= 100
        True
    """
    if metrics.total_findings == 0:
        return 100.0

    # Calcula pontuação negativa ponderada usando pesos configurados
    negative_score = (
        metrics.critical_findings * SECURITY_SEVERITY_WEIGHTS['critical'] +
        metrics.high_findings * SECURITY_SEVERITY_WEIGHTS['high'] +
        metrics.medium_findings * SECURITY_SEVERITY_WEIGHTS['medium'] +
        metrics.low_findings * SECURITY_SEVERITY_WEIGHTS['low']
    )

    if negative_score == 0:
        return 100.0

    # Usa escala logarítmica para suavizar grandes números
    # log1p(x) = log(1 + x) evita problemas com log(0)
    score = max(0, 100 - (math.log1p(negative_score) * 10))

    return round(score, 2)
