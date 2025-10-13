#!/usr/bin/env python3
"""
Analisador de Commits Git com integração COCOMO II
Cruza dados de análise de código com histórico de commits
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.text import Text

# Importa o analisador COCOMO
from main import CodeAnalyzer, CocomoResults


@dataclass
class CommitInfo:
    """Informações de um commit"""
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int
    total_changes: int

    def to_dict(self):
        return {
            **asdict(self),
            'date': self.date.isoformat()
        }


@dataclass
class GitMetrics:
    """Métricas do repositório Git"""
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

    def to_dict(self):
        return {
            **asdict(self),
            'first_commit_date': self.first_commit_date.isoformat(),
            'last_commit_date': self.last_commit_date.isoformat()
        }


@dataclass
class IntegratedMetrics:
    """Métricas integradas entre COCOMO II e Git"""
    # COCOMO II
    cocomo_kloc: float
    cocomo_effort: float
    cocomo_time_months: float
    cocomo_people: float
    cocomo_cost_brl: float

    # Git
    total_commits: int
    avg_changes_per_commit: float
    commits_per_month: float

    # Indicadores calculados
    lines_per_commit: float
    commits_needed_to_rebuild: float
    actual_velocity: float  # linhas/dia baseado no histórico
    estimated_velocity: float  # linhas/dia baseado no COCOMO
    velocity_ratio: float  # real/estimado
    commit_efficiency: float  # % de código útil vs churn
    change_percentage_per_commit: float  # % média de mudança por commit
    developer_productivity_score: float  # score de produtividade


class GitAnalyzer:
    """Analisador de repositório Git"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.console = Console()

        # Verifica se é um repositório Git
        if not (repo_path / '.git').exists():
            raise ValueError(f"'{repo_path}' não é um repositório Git")

    def run_git_command(self, args: List[str]) -> str:
        """Executa um comando git"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]Erro ao executar git {' '.join(args)}:[/red] {e}")
            return ""

    def get_commits(self) -> List[CommitInfo]:
        """Obtém lista de commits com estatísticas"""
        commits = []

        # Formato: hash|author|date|message
        log_output = self.run_git_command([
            'log',
            '--pretty=format:%H|%an|%ai|%s',
            '--shortstat'
        ])

        lines = log_output.split('\n')
        i = 0

        while i < len(lines):
            if '|' in lines[i]:
                parts = lines[i].split('|')
                if len(parts) >= 4:
                    commit_hash = parts[0]
                    author = parts[1]
                    date_str = parts[2]
                    message = parts[3]

                    # Parse da data
                    date = datetime.fromisoformat(date_str.replace(' ', 'T', 1).rsplit(' ', 1)[0])

                    # Stats na próxima linha (se existir)
                    files_changed = 0
                    insertions = 0
                    deletions = 0

                    if i + 1 < len(lines) and 'changed' in lines[i + 1]:
                        stats_line = lines[i + 1]

                        # Parse: "X files changed, Y insertions(+), Z deletions(-)"
                        if 'file' in stats_line:
                            files_changed = int(stats_line.split()[0])
                        if 'insertion' in stats_line:
                            parts = stats_line.split('insertion')
                            insertions = int(parts[0].split(',')[-1].strip())
                        if 'deletion' in stats_line:
                            parts = stats_line.split('deletion')
                            deletions = int(parts[0].split(',')[-1].strip())

                        i += 1  # Pula a linha de stats

                    total_changes = insertions + deletions

                    commits.append(CommitInfo(
                        hash=commit_hash,
                        author=author,
                        date=date,
                        message=message,
                        files_changed=files_changed,
                        insertions=insertions,
                        deletions=deletions,
                        total_changes=total_changes
                    ))

            i += 1

        return commits

    def calculate_metrics(self, commits: List[CommitInfo]) -> GitMetrics:
        """Calcula métricas do repositório"""
        if not commits:
            raise ValueError("Nenhum commit encontrado")

        # Contadores
        total_commits = len(commits)
        authors = defaultdict(int)
        total_insertions = 0
        total_deletions = 0
        total_files = 0
        total_changes = 0

        for commit in commits:
            authors[commit.author] += 1
            total_insertions += commit.insertions
            total_deletions += commit.deletions
            total_files += commit.files_changed
            total_changes += commit.total_changes

        # Datas
        first_commit = min(commits, key=lambda c: c.date)
        last_commit = max(commits, key=lambda c: c.date)

        repo_age_days = (last_commit.date - first_commit.date).days
        if repo_age_days == 0:
            repo_age_days = 1  # Evita divisão por zero

        return GitMetrics(
            total_commits=total_commits,
            total_authors=len(authors),
            authors_commits=dict(authors),
            total_insertions=total_insertions,
            total_deletions=total_deletions,
            avg_changes_per_commit=total_changes / total_commits if total_commits > 0 else 0,
            avg_files_per_commit=total_files / total_commits if total_commits > 0 else 0,
            commits_per_day=total_commits / repo_age_days if repo_age_days > 0 else 0,
            first_commit_date=first_commit.date,
            last_commit_date=last_commit.date,
            repository_age_days=repo_age_days
        )


class IntegratedAnalyzer:
    """Análise integrada entre COCOMO II e Git"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.console = Console()

    def analyze(self) -> tuple[CocomoResults, GitMetrics, IntegratedMetrics]:
        """Executa análise completa"""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:

            # Análise COCOMO II
            task1 = progress.add_task("[cyan]Analisando código (COCOMO II)...", total=None)
            code_analyzer = CodeAnalyzer(self.repo_path)
            code_analyzer.analyze_directory()

            if code_analyzer.metrics.files_count == 0:
                raise ValueError("Nenhum arquivo de código encontrado")

            cocomo_results = code_analyzer.calculate_cocomo2()
            progress.update(task1, completed=True)

            # Análise Git
            task2 = progress.add_task("[cyan]Analisando commits Git...", total=None)
            git_analyzer = GitAnalyzer(self.repo_path)
            commits = git_analyzer.get_commits()
            git_metrics = git_analyzer.calculate_metrics(commits)
            progress.update(task2, completed=True)

            # Cálculo de métricas integradas
            task3 = progress.add_task("[cyan]Calculando indicadores integrados...", total=None)
            integrated = self._calculate_integrated_metrics(
                cocomo_results,
                git_metrics,
                code_analyzer.metrics.code_lines
            )
            progress.update(task3, completed=True)

        return cocomo_results, git_metrics, integrated

    def _calculate_integrated_metrics(
        self,
        cocomo: CocomoResults,
        git: GitMetrics,
        total_lines: int
    ) -> IntegratedMetrics:
        """Calcula métricas integradas"""

        # Linhas por commit
        lines_per_commit = total_lines / git.total_commits if git.total_commits > 0 else 0

        # Commits necessários para recriar
        commits_needed = cocomo.kloc * 1000 / lines_per_commit if lines_per_commit > 0 else 0

        # Velocidade real (linhas/dia)
        actual_velocity = total_lines / git.repository_age_days if git.repository_age_days > 0 else 0

        # Velocidade estimada COCOMO (linhas/dia)
        # COCOMO: produtividade em LOC/pessoa-mês, convertendo para LOC/dia
        estimated_velocity = cocomo.productivity / 22 if cocomo.productivity > 0 else 0  # ~22 dias úteis/mês

        # Razão velocidade (real/estimado)
        velocity_ratio = actual_velocity / estimated_velocity if estimated_velocity > 0 else 0

        # Eficiência do commit (linhas úteis vs churn)
        total_changes = git.total_insertions + git.total_deletions
        commit_efficiency = (total_lines / total_changes * 100) if total_changes > 0 else 0

        # % média de mudança por commit
        change_percentage_per_commit = (git.avg_changes_per_commit / total_lines * 100) if total_lines > 0 else 0

        # Score de produtividade do desenvolvedor
        # Baseado em: velocidade, eficiência e complexidade
        base_score = 50
        velocity_score = min((velocity_ratio * 25), 25)  # Max 25 pontos
        efficiency_score = min((commit_efficiency / 100 * 15), 15)  # Max 15 pontos
        complexity_bonus = 10 if cocomo.complexity_level == "Alta" else 5 if cocomo.complexity_level == "Média" else 0

        developer_productivity_score = base_score + velocity_score + efficiency_score + complexity_bonus

        # Commits por mês
        commits_per_month = git.total_commits / (git.repository_age_days / 30) if git.repository_age_days > 0 else 0

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

    def display_results(
        self,
        cocomo: CocomoResults,
        git: GitMetrics,
        integrated: IntegratedMetrics
    ):
        """Exibe resultados da análise integrada"""

        # Título
        title = Text("ANÁLISE INTEGRADA: COCOMO II + GIT", style="bold magenta")
        self.console.print("\n")
        self.console.print(Panel(title, box=box.DOUBLE, expand=False))

        # Resumo COCOMO II
        cocomo_table = Table(
            title="📊 Resumo COCOMO II",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        cocomo_table.add_column("Métrica", style="yellow", width=30)
        cocomo_table.add_column("Valor", justify="right", style="green")

        cocomo_table.add_row("KLOC", f"{cocomo.kloc:.2f}")
        cocomo_table.add_row("Complexidade", cocomo.complexity_level)
        cocomo_table.add_row("Esforço (pessoa-mês)", f"{cocomo.effort_person_months:.2f}")
        cocomo_table.add_row("Tempo (meses)", f"{cocomo.time_months:.2f}")
        cocomo_table.add_row("Pessoas Necessárias", f"{cocomo.people_required:.2f}")
        cocomo_table.add_row("Custo Estimado", f"R$ {cocomo.cost_estimate_brl:,.2f}")

        self.console.print("\n")
        self.console.print(cocomo_table)

        # Métricas Git
        git_table = Table(
            title="📈 Métricas do Repositório Git",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        git_table.add_column("Métrica", style="yellow", width=30)
        git_table.add_column("Valor", justify="right", style="green")

        git_table.add_row("Total de Commits", f"{git.total_commits:,}")
        git_table.add_row("Total de Autores", f"{git.total_authors}")
        git_table.add_row("Idade do Repositório (dias)", f"{git.repository_age_days}")
        git_table.add_row("Commits por Dia", f"{git.commits_per_day:.2f}")
        git_table.add_row("Inserções Totais", f"{git.total_insertions:,}")
        git_table.add_row("Deleções Totais", f"{git.total_deletions:,}")
        git_table.add_row("Mudanças/Commit (média)", f"{git.avg_changes_per_commit:.1f}")
        git_table.add_row("Arquivos/Commit (média)", f"{git.avg_files_per_commit:.1f}")

        self.console.print("\n")
        self.console.print(git_table)

        # Top contribuidores
        if git.authors_commits:
            authors_table = Table(
                title="👥 Top 10 Contribuidores",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )
            authors_table.add_column("Autor", style="yellow", width=30)
            authors_table.add_column("Commits", justify="right", style="green")
            authors_table.add_column("% do Total", justify="right", style="blue")

            sorted_authors = sorted(
                git.authors_commits.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            for author, count in sorted_authors:
                percentage = (count / git.total_commits * 100)
                authors_table.add_row(author, f"{count:,}", f"{percentage:.1f}%")

            self.console.print("\n")
            self.console.print(authors_table)

        # Indicadores Integrados
        integrated_table = Table(
            title="🎯 Indicadores Integrados",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        integrated_table.add_column("Indicador", style="yellow", width=40)
        integrated_table.add_column("Valor", justify="right", style="green")

        integrated_table.add_row("Linhas por Commit", f"{integrated.lines_per_commit:.1f}")
        integrated_table.add_row("Commits p/ Recriar Codebase", f"{integrated.commits_needed_to_rebuild:.0f}")
        integrated_table.add_row("Commits por Mês", f"{integrated.commits_per_month:.1f}")
        integrated_table.add_row("Velocidade Real (linhas/dia)", f"{integrated.actual_velocity:.1f}")
        integrated_table.add_row("Velocidade COCOMO (linhas/dia)", f"{integrated.estimated_velocity:.1f}")
        integrated_table.add_row("Razão Velocidade (real/estimado)", f"{integrated.velocity_ratio:.2f}x")
        integrated_table.add_row("Eficiência de Commit", f"{integrated.commit_efficiency:.1f}%")
        integrated_table.add_row("% Mudança Média/Commit", f"{integrated.change_percentage_per_commit:.2f}%")

        self.console.print("\n")
        self.console.print(integrated_table)

        # Score de Produtividade
        score_color = "green" if integrated.developer_productivity_score >= 75 else \
                      "yellow" if integrated.developer_productivity_score >= 50 else "red"

        score_panel = Panel(
            f"[bold {score_color}]{integrated.developer_productivity_score:.1f}/100[/bold {score_color}]\n\n"
            f"[dim]Score baseado em velocidade, eficiência e complexidade[/dim]",
            title="⭐ Score de Produtividade dos Desenvolvedores",
            box=box.DOUBLE,
            style=f"bold {score_color}"
        )
        self.console.print("\n")
        self.console.print(score_panel)

        # Insights
        self.console.print("\n")
        insights = Panel(
            self._generate_insights(integrated, git),
            title="💡 Insights e Recomendações",
            box=box.ROUNDED,
            style="cyan"
        )
        self.console.print(insights)

    def _generate_insights(self, integrated: IntegratedMetrics, git: GitMetrics) -> str:
        """Gera insights baseados nas métricas integradas"""
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

        return "\n".join(insights)

    def export_json(
        self,
        cocomo: CocomoResults,
        git: GitMetrics,
        integrated: IntegratedMetrics,
        output_path: Path
    ):
        """Exporta resultados para JSON"""
        data = {
            'cocomo': asdict(cocomo),
            'git': git.to_dict(),
            'integrated': asdict(integrated),
            'generated_at': datetime.now().isoformat()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.console.print(f"\n[green]✓[/green] Resultados exportados para: {output_path}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Análise integrada de código (COCOMO II) e commits Git',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Caminho do repositório a ser analisado (padrão: diretório atual)'
    )
    parser.add_argument(
        '--export',
        '-e',
        type=str,
        help='Exportar resultados para arquivo JSON'
    )

    args = parser.parse_args()

    path = Path(args.path).resolve()

    if not path.exists():
        Console().print(f"[bold red]Erro:[/bold red] Caminho '{path}' não encontrado")
        sys.exit(1)

    if not path.is_dir():
        Console().print(f"[bold red]Erro:[/bold red] '{path}' não é um diretório")
        sys.exit(1)

    try:
        # Executa análise integrada
        analyzer = IntegratedAnalyzer(path)
        cocomo_results, git_metrics, integrated_metrics = analyzer.analyze()

        # Exibe resultados
        analyzer.display_results(cocomo_results, git_metrics, integrated_metrics)

        # Exporta se solicitado
        if args.export:
            export_path = Path(args.export)
            analyzer.export_json(cocomo_results, git_metrics, integrated_metrics, export_path)

    except ValueError as e:
        Console().print(f"[bold red]Erro:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        Console().print(f"[bold red]Erro inesperado:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
