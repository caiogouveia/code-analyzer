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
# Importa o analisador de segurança
from security_analyzer import SecurityAnalyzer, SecurityMetrics
# Importa os modelos consolidados
from models import CommitInfo, GitMetrics, IntegratedMetrics
# Importa constantes
from analysis_config import WORKING_DAYS_PER_MONTH


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
    """
    Análise integrada entre COCOMO II e Git.

    Facade que delega para IntegratedAnalysisService.
    Mantido para compatibilidade com código existente.
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.console = Console()
        # Delega para o serviço
        from services.integrated_analysis_service import IntegratedAnalysisService
        self._service = IntegratedAnalysisService(repo_path)

    def analyze(self, avg_salary_month_brl: float = 15000.0,
                run_security_analysis: bool = True,
                security_config: str = "auto") -> tuple[CocomoResults, GitMetrics, IntegratedMetrics, Optional[SecurityMetrics]]:
        """Executa análise completa

        Args:
            avg_salary_month_brl: Salário médio mensal em BRL por pessoa (padrão: R$15.000)
            run_security_analysis: Se True, executa análise de segurança com Semgrep (padrão: True)
            security_config: Configuração do Semgrep (padrão: 'auto')
        """

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:

            def progress_callback(percent: int, message: str):
                """Callback para atualizar progresso."""
                # Mapeia porcentagens para tarefas do Progress
                if percent <= 30:
                    if not hasattr(progress_callback, 'task1'):
                        progress_callback.task1 = progress.add_task(f"[cyan]{message}", total=None)
                    else:
                        progress.update(progress_callback.task1, description=f"[cyan]{message}")
                elif percent <= 60:
                    if hasattr(progress_callback, 'task1'):
                        progress.update(progress_callback.task1, completed=True)
                    if not hasattr(progress_callback, 'task2'):
                        progress_callback.task2 = progress.add_task(f"[cyan]{message}", total=None)
                    else:
                        progress.update(progress_callback.task2, description=f"[cyan]{message}")
                elif percent <= 80:
                    if hasattr(progress_callback, 'task2'):
                        progress.update(progress_callback.task2, completed=True)
                    if not hasattr(progress_callback, 'task3'):
                        progress_callback.task3 = progress.add_task(f"[cyan]{message}", total=None)
                    else:
                        progress.update(progress_callback.task3, description=f"[cyan]{message}")
                else:
                    if hasattr(progress_callback, 'task3'):
                        progress.update(progress_callback.task3, completed=True)
                    if not hasattr(progress_callback, 'task4'):
                        progress_callback.task4 = progress.add_task(f"[cyan]{message}", total=None)
                    else:
                        progress.update(progress_callback.task4, description=f"[cyan]{message}")
                        progress.update(progress_callback.task4, completed=True)

            # Delega para o serviço
            return self._service.analyze(
                avg_salary_month_brl=avg_salary_month_brl,
                run_security_analysis=run_security_analysis,
                security_config=security_config,
                progress_callback=progress_callback
            )

    def _calculate_integrated_metrics(
        self,
        cocomo: CocomoResults,
        git: GitMetrics,
        total_lines: int
    ) -> IntegratedMetrics:
        """
        Calcula métricas integradas.

        Deprecated: Use IntegratedAnalysisService diretamente.
        Mantido para compatibilidade.
        """
        return self._service._calculate_integrated_metrics(cocomo, git, total_lines)

    def display_results(
        self,
        cocomo: CocomoResults,
        git: Optional[GitMetrics],
        integrated: Optional[IntegratedMetrics],
        security: Optional[SecurityMetrics] = None
    ):
        """Exibe resultados da análise integrada"""

        # Título
        if security:
            title_text = "ANÁLISE INTEGRADA: COCOMO II + GIT + SEGURANÇA"
        elif git:
            title_text = "ANÁLISE INTEGRADA: COCOMO II + GIT"
        else:
            title_text = "ANÁLISE COCOMO II"
        title = Text(title_text, style="bold magenta")
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

        # Métricas Git (se disponível)
        if git:
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

        # Top contribuidores (se Git disponível)
        if git and git.authors_commits:
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

        # Indicadores Integrados (se disponível)
        if integrated:
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
            if git:
                self.console.print("\n")
                insights = Panel(
                    self._generate_insights(integrated, git),
                    title="💡 Insights e Recomendações",
                    box=box.ROUNDED,
                    style="cyan"
                )
                self.console.print(insights)

        # Análise de Segurança
        if security:
            self.console.print("\n")
            security_table = Table(
                title="🔒 Análise de Segurança (Semgrep)",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )
            security_table.add_column("Métrica", style="yellow", width=30)
            security_table.add_column("Valor", justify="right", style="green")

            from security_analyzer import SecurityAnalyzer
            sa = SecurityAnalyzer(self.repo_path)
            sa.metrics = security
            score = sa.get_security_score()

            score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"

            security_table.add_row("Score de Segurança", f"[{score_color}]{score:.1f}/100[/{score_color}]")
            security_table.add_row("Total de Descobertas", f"{security.total_findings:,}")
            security_table.add_row("Críticas", f"[red]{security.critical_findings}[/red]" if security.critical_findings > 0 else "0")
            security_table.add_row("Altas", f"[orange1]{security.high_findings}[/orange1]" if security.high_findings > 0 else "0")
            security_table.add_row("Médias", f"[yellow]{security.medium_findings}[/yellow]" if security.medium_findings > 0 else "0")
            security_table.add_row("Baixas", f"{security.low_findings}")
            security_table.add_row("Informativas", f"{security.info_findings}")
            security_table.add_row("", "")
            security_table.add_row("Problemas de Segurança", f"{security.security_issues}")
            security_table.add_row("Best Practices", f"{security.best_practice_issues}")
            security_table.add_row("Performance", f"{security.performance_issues}")
            security_table.add_row("", "")
            security_table.add_row("Arquivos Escaneados", f"{security.files_scanned:,}")
            security_table.add_row("Tempo de Scan", f"{security.scan_duration_seconds:.2f}s")

            self.console.print(security_table)

            # Top arquivos vulneráveis
            if security.files_with_issues:
                top_files = sa.get_top_vulnerable_files(5)
                if top_files:
                    files_table = Table(
                        title="📁 Top 5 Arquivos Mais Vulneráveis",
                        box=box.ROUNDED,
                        show_header=True,
                        header_style="bold cyan"
                    )
                    files_table.add_column("Arquivo", style="yellow", width=50)
                    files_table.add_column("Problemas", justify="right", style="red")

                    for file_path, count in top_files:
                        # Encurta o caminho para exibição
                        display_path = file_path if len(file_path) <= 50 else "..." + file_path[-47:]
                        files_table.add_row(display_path, str(count))

                    self.console.print("\n")
                    self.console.print(files_table)

    def _generate_insights(self, integrated: IntegratedMetrics, git: GitMetrics) -> str:
        """
        Gera insights baseados nas métricas integradas.

        Deprecated: Use InsightsService diretamente.
        Mantido para compatibilidade.
        """
        from services.insights_service import InsightsService
        insights_service = InsightsService()
        insights = insights_service.generate_integrated_insights(integrated, git)
        return insights_service.format_insights(insights)

    def export_json(
        self,
        cocomo: CocomoResults,
        git: GitMetrics,
        integrated: IntegratedMetrics,
        output_path: Path,
        security: Optional[SecurityMetrics] = None
    ):
        """Exporta resultados para JSON"""
        data = {
            'project_name': self.repo_path.name,
            'project_path': str(self.repo_path),
            'analysis_type': 'integrated',
            'cocomo': asdict(cocomo),
            'git': git.to_dict(),
            'integrated': asdict(integrated),
            'generated_at': datetime.now().isoformat()
        }

        if security:
            data['security'] = security.to_dict()

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
        cocomo_results, git_metrics, integrated_metrics, security_metrics = analyzer.analyze()

        # Exibe resultados
        analyzer.display_results(cocomo_results, git_metrics, integrated_metrics, security_metrics)

        # Exporta se solicitado
        if args.export:
            export_path = Path(args.export)
            analyzer.export_json(cocomo_results, git_metrics, integrated_metrics, export_path, security_metrics)

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
