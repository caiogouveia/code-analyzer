"""Projeto: configurações compartilhadas para análise COCOMO II."""

from __future__ import annotations

from importlib import import_module
from typing import Iterable, List, Sequence, Tuple, Any


DEFAULT_EXCLUDE_PATTERNS: List[str] = [
    ".git/",
    ".svn/",
    ".hg/",
    "__pycache__/",
    "node_modules/",
    ".venv/",
    "venv/",
    "env/",
    "vendor/",
    "dist/",
    "build/",
    "target/",
    "out/",
    ".idea/",
    ".vscode/",
    ".vs/",
    "bin/",
    "obj/",
    ".gradle/",
    ".next/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".tox/",
    ".eggs/",
    "*.egg-info/",
    ".nyc_output/",
    "coverage/",
    ".cache/",
    "*.pyc",
    "*.pyo",
    "*.so",
    "*.dll",
    "*.dylib",
    "*.exe",
    "*.o",
    "*.class",
    "*.jar",
    "*.war",
    "*.min.js",
    "*.min.css",
    "*.map",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
    "composer.lock",
    "Gemfile.lock",
]


COCOMO_COEFFICIENTS = {
    "organic": {"a": 2.4, "b": 1.05, "c": 2.5, "d": 0.38},
    "semi-detached": {"a": 3.0, "b": 1.12, "c": 2.5, "d": 0.35},
    "embedded": {"a": 3.6, "b": 1.20, "c": 2.5, "d": 0.32},
}

COMPLEXITY_THRESHOLDS: Sequence[Tuple[float, str, str]] = (
    (50.0, "organic", "Baixa"),
    (300.0, "semi-detached", "Média"),
    (float("inf"), "embedded", "Alta"),
)

COCOMO_COMPLEXITY_MESSAGES = {
    "Baixa": "✓ Projeto de baixa complexidade - Ideal para equipes pequenas",
    "Média": "⚡ Projeto de complexidade média - Requer gestão adequada",
    "Alta": "⚠️  Projeto de alta complexidade - Requer gestão rigorosa",
}

TEAM_SIZE_RULES: Sequence[Tuple[float, str]] = (
    (5, "✓ Equipe pequena suficiente para desenvolvimento"),
    (15, "⚡ Equipe média necessária - Considere divisão em squads"),
    (float("inf"), "⚠️  Equipe grande necessária - Estrutura organizacional complexa"),
)

TIME_RULES: Sequence[Tuple[float, str]] = (
    (6, "✓ Tempo de desenvolvimento curto"),
    (18, "⚡ Tempo de desenvolvimento médio - Planejamento de releases importante"),
    (float("inf"), "⚠️  Desenvolvimento de longo prazo - Risco de mudanças tecnológicas"),
)

PRODUCTIVITY_RULES: Sequence[Tuple[float, str]] = (
    (300, "📉 Produtividade baixa - Considere refatoração ou automação"),
    (600, "📊 Produtividade adequada"),
    (float("inf"), "📈 Alta produtividade - Boas práticas aplicadas"),
)

VELOCITY_RULES: Sequence[Tuple[float, str]] = (
    (1.2, "🚀 Velocidade acima do esperado - Equipe muito produtiva!"),
    (0.8, "✓ Velocidade dentro do esperado"),
    (-float("inf"), "⚠️  Velocidade abaixo do esperado - Revisar impedimentos"),
)

COMMIT_EFFICIENCY_RULES: Sequence[Tuple[float, str]] = (
    (50, "✓ Alta eficiência de commits - Baixo retrabalho"),
    (30, "⚡ Eficiência moderada - Algum retrabalho presente"),
    (-float("inf"), "⚠️  Baixa eficiência - Alto retrabalho (churn)"),
)

CHANGE_SIZE_RULES: Sequence[Tuple[float, str]] = (
    (1, "✓ Commits pequenos e incrementais - Boa prática"),
    (5, "⚡ Tamanho de commit moderado"),
    (float("inf"), "⚠️  Commits muito grandes - Considere commits menores"),
)

COMMIT_FREQUENCY_RULES: Sequence[Tuple[float, str]] = (
    (40, "✓ Alta frequência de commits - Desenvolvimento ativo"),
    (20, "⚡ Frequência moderada de commits"),
    (-float("inf"), "📊 Baixa frequência de commits"),
)

PRODUCTIVITY_SCORE_RULES: Sequence[Tuple[float, str]] = (
    (75, "🌟 Excelente produtividade da equipe!"),
    (50, "👍 Boa produtividade geral"),
    (-float("inf"), "📈 Oportunidade de melhoria na produtividade"),
)


def compile_exclusion_spec(patterns: Iterable[str] | None = None) -> Any:
    """Monta um PathSpec para filtros de arquivos/pastas."""
    pathspec_module = import_module("pathspec")
    compiled_patterns = list(DEFAULT_EXCLUDE_PATTERNS)
    if patterns:
        compiled_patterns.extend(patterns)
    return pathspec_module.PathSpec.from_lines("gitwildmatch", compiled_patterns)
