"""Dataclasses compartilhadas usadas nas análises COCOMO II."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Optional


@dataclass
class CodeMetrics:
    """Métricas de código coletadas durante a varredura."""

    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    files_count: int = 0
    languages: Dict[str, int] = field(default_factory=dict)


@dataclass
class CocomoResults:
    """Resultados dos cálculos COCOMO II."""

    kloc: float
    effort_person_months: float
    time_months: float
    people_required: float
    maintenance_people: float
    expansion_people: float
    productivity: float
    cost_estimate_brl: float
    complexity_level: str


@dataclass
class CommitInfo:
    """Informações essenciais de um commit git."""

    hash: str
    author: str
    date: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int
    total_changes: int

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["date"] = self.date.isoformat()
        return data


@dataclass
class GitMetrics:
    """Métricas agregadas do repositório Git."""

    total_commits: int
    total_authors: int
    authors_commits: Dict[str, int]
    total_insertions: int
    total_deletions: int
    avg_changes_per_commit: float
    avg_files_per_commit: float
    commits_per_day: float
    first_commit_date: datetime
    last_commit_date: datetime
    repository_age_days: int

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["first_commit_date"] = self.first_commit_date.isoformat()
        data["last_commit_date"] = self.last_commit_date.isoformat()
        return data


@dataclass
class IntegratedMetrics:
    """Indicadores integrados COCOMO II + Git."""

    cocomo_kloc: float
    cocomo_effort: float
    cocomo_time_months: float
    cocomo_people: float
    cocomo_cost_brl: float
    total_commits: int
    avg_changes_per_commit: float
    commits_per_month: float
    lines_per_commit: float
    commits_needed_to_rebuild: float
    actual_velocity: float
    estimated_velocity: float
    velocity_ratio: float
    commit_efficiency: float
    change_percentage_per_commit: float
    developer_productivity_score: float


@dataclass
class AnalysisBundle:
    """Pacote com resultados agregados de uma análise integrada."""

    code_metrics: CodeMetrics
    cocomo: CocomoResults
    git: Optional[GitMetrics]
    integrated: Optional[IntegratedMetrics]
