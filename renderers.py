"""Funções utilitárias para montar componentes Rich reutilizáveis."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Optional

from models import CodeMetrics, CocomoResults, GitMetrics, IntegratedMetrics


def _new_table(title: str) -> Any:
    table_module = import_module("rich.table")
    box_module = import_module("rich.box")
    Table = table_module.Table
    box = box_module
    return Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )


def build_code_metrics_table(metrics: CodeMetrics, kloc: float) -> Any:
    table = _new_table("📊 Métricas de Código")
    table.add_column("Métrica", style="yellow", width=30)
    table.add_column("Valor", justify="right", style="green")

    table.add_row("Total de Arquivos", f"{metrics.files_count:,}")
    table.add_row("Total de Linhas", f"{metrics.total_lines:,}")
    table.add_row("Linhas de Código", f"{metrics.code_lines:,}")
    table.add_row("Linhas de Comentários", f"{metrics.comment_lines:,}")
    table.add_row("Linhas em Branco", f"{metrics.blank_lines:,}")
    table.add_row("KLOC (Milhares de LOC)", f"{kloc:.2f}")

    return table


def build_language_distribution_table(metrics: CodeMetrics) -> Optional[Any]:
    if not metrics.languages:
        return None

    table = _new_table("💻 Distribuição por Linguagem")
    table.add_column("Linguagem", style="yellow", width=20)
    table.add_column("Linhas de Código", justify="right", style="green")
    table.add_column("Porcentagem", justify="right", style="blue")

    total = max(metrics.code_lines, 1)
    for language, lines in sorted(metrics.languages.items(), key=lambda item: item[1], reverse=True):
        percentage = (lines / total) * 100
        table.add_row(language, f"{lines:,}", f"{percentage:.1f}%")

    return table


def build_cocomo_table(cocomo: CocomoResults) -> Any:
    table = _new_table("🎯 Resultados COCOMO II")
    table.add_column("Métrica", style="yellow", width=35)
    table.add_column("Valor", justify="right", style="green")

    table.add_row("Nível de Complexidade", cocomo.complexity_level)
    table.add_row("Esforço Total (pessoa-mês)", f"{cocomo.effort_person_months:.2f}")
    table.add_row("Tempo de Desenvolvimento (meses)", f"{cocomo.time_months:.2f}")
    table.add_row("Anos de Desenvolvimento", f"{cocomo.time_months / 12:.2f}")
    table.add_row("Pessoas Necessárias (Desenvolvimento)", f"{cocomo.people_required:.2f}")
    table.add_row("Pessoas para Manutenção", f"{cocomo.maintenance_people:.2f}")
    table.add_row("Pessoas para Expansão", f"{cocomo.expansion_people:.2f}")
    table.add_row("Produtividade (LOC/pessoa-mês)", f"{cocomo.productivity:.0f}")

    return table


def build_cost_panel(cocomo: CocomoResults) -> Any:
    box_module = import_module("rich.box")
    panel_module = import_module("rich.panel")
    Panel = panel_module.Panel
    box = box_module
    return Panel(
        f"[bold green]R$ {cocomo.cost_estimate_brl:,.2f}[/bold green]\n\n"
        "[dim]Baseado em R$15.000/pessoa-mês[/dim]\n"
        "[dim](média salarial para desenvolvedores no Brasil)[/dim]",
        title="💰 Estimativa de Custo Total",
        box=box.DOUBLE,
        style="bold blue",
    )


def build_git_metrics_table(git: GitMetrics) -> Any:
    table = _new_table("📈 Métricas do Repositório Git")
    table.add_column("Métrica", style="yellow", width=30)
    table.add_column("Valor", justify="right", style="green")

    table.add_row("Total de Commits", f"{git.total_commits:,}")
    table.add_row("Total de Autores", f"{git.total_authors}")
    table.add_row("Idade do Repositório (dias)", f"{git.repository_age_days}")
    table.add_row("Commits por Dia", f"{git.commits_per_day:.2f}")
    table.add_row("Inserções Totais", f"{git.total_insertions:,}")
    table.add_row("Deleções Totais", f"{git.total_deletions:,}")
    table.add_row("Mudanças/Commit (média)", f"{git.avg_changes_per_commit:.1f}")
    table.add_row("Arquivos/Commit (média)", f"{git.avg_files_per_commit:.1f}")

    return table


def build_git_authors_table(git: GitMetrics, top: int = 10) -> Optional[Any]:
    if not git.authors_commits:
        return None

    table = _new_table("👥 Top Contribuidores")
    table.add_column("Autor", style="yellow", width=30)
    table.add_column("Commits", justify="right", style="green")
    table.add_column("% do Total", justify="right", style="blue")

    sorted_authors = sorted(git.authors_commits.items(), key=lambda item: item[1], reverse=True)[:top]
    for author, count in sorted_authors:
        percentage = (count / git.total_commits * 100) if git.total_commits else 0
        table.add_row(author, f"{count:,}", f"{percentage:.1f}%")

    return table


def build_integrated_table(integrated: IntegratedMetrics) -> Any:
    table = _new_table("🎯 Indicadores Integrados")
    table.add_column("Indicador", style="yellow", width=40)
    table.add_column("Valor", justify="right", style="green")

    table.add_row("Linhas por Commit", f"{integrated.lines_per_commit:.1f}")
    table.add_row("Commits p/ Recriar Codebase", f"{integrated.commits_needed_to_rebuild:.0f}")
    table.add_row("Commits por Mês", f"{integrated.commits_per_month:.1f}")
    table.add_row("Velocidade Real (linhas/dia)", f"{integrated.actual_velocity:.1f}")
    table.add_row("Velocidade COCOMO (linhas/dia)", f"{integrated.estimated_velocity:.1f}")
    table.add_row("Razão Velocidade (real/estimado)", f"{integrated.velocity_ratio:.2f}x")
    table.add_row("Eficiência de Commit", f"{integrated.commit_efficiency:.1f}%")
    table.add_row("% Mudança Média/Commit", f"{integrated.change_percentage_per_commit:.2f}%")

    return table


def build_score_panel(score: float) -> Any:
    score_color = "green" if score >= 75 else "yellow" if score >= 50 else "red"
    box_module = import_module("rich.box")
    panel_module = import_module("rich.panel")
    Panel = panel_module.Panel
    box = box_module
    return Panel(
        f"[bold {score_color}]{score:.1f}/100[/bold {score_color}]\n\n"
        "[dim]Score baseado em velocidade, eficiência e complexidade[/dim]",
        title="⭐ Score de Produtividade dos Desenvolvedores",
        box=box.DOUBLE,
        style=f"bold {score_color}",
    )
