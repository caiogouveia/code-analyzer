#!/usr/bin/env python3
"""
Analisador de Código baseado em COCOMO II
Analisa complexidade, esforço, tempo e recursos necessários para desenvolvimento
"""

import os
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Set
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box
from rich.text import Text


# Extensões de arquivo por linguagem
LANGUAGE_EXTENSIONS = {
    'Python': {'.py', '.pyw', '.pyx'},
    'JavaScript': {'.js', '.jsx', '.mjs', '.cjs'},
    'TypeScript': {'.ts', '.tsx'},
    'Java': {'.java'},
    'C': {'.c', '.h'},
    'C++': {'.cpp', '.hpp', '.cc', '.cxx', '.hxx'},
    'C#': {'.cs'},
    'Go': {'.go'},
    'Rust': {'.rs'},
    'PHP': {'.php', '.phtml'},
    'Ruby': {'.rb'},
    'Swift': {'.swift'},
    'Kotlin': {'.kt', '.kts'},
    'Scala': {'.scala'},
    'R': {'.r', '.R'},
    'Shell': {'.sh', '.bash', '.zsh'},
    'SQL': {'.sql'},
    'HTML': {'.html', '.htm'},
    'CSS': {'.css', '.scss', '.sass', '.less'},
    'Vue': {'.vue'},
    'Dart': {'.dart'},
}

# Diretórios e arquivos a serem excluídos
EXCLUDED_DIRS = {
    'node_modules', '.venv', 'venv', 'env', 'vendor', '__pycache__',
    '.git', '.svn', '.hg', 'dist', 'build', 'target', 'out',
    '.idea', '.vscode', '.vs', 'bin', 'obj', '.gradle', '.next',
    'coverage', '.nyc_output', '.pytest_cache', '.mypy_cache',
    '.tox', '.eggs', '*.egg-info', '.cache'
}

EXCLUDED_FILES = {
    '.pyc', '.pyo', '.so', '.dll', '.dylib', '.exe', '.o',
    '.class', '.jar', '.war', '.min.js', '.min.css', '.map',
    '.lock', 'package-lock.json', 'yarn.lock', 'poetry.lock',
    'Pipfile.lock', 'composer.lock', 'Gemfile.lock'
}


@dataclass
class CodeMetrics:
    """Métricas de código coletadas"""
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    files_count: int = 0
    languages: Dict[str, int] = None

    def __post_init__(self):
        if self.languages is None:
            self.languages = {}


@dataclass
class CocomoResults:
    """Resultados dos cálculos COCOMO II"""
    kloc: float  # Milhares de linhas de código
    effort_person_months: float  # Esforço em pessoa-mês
    time_months: float  # Tempo de desenvolvimento em meses
    people_required: float  # Pessoas necessárias
    maintenance_people: float  # Pessoas para manutenção
    expansion_people: float  # Pessoas para expansão
    productivity: float  # Linhas por pessoa-mês
    cost_estimate_brl: float  # Estimativa de custo (BRL)
    complexity_level: str  # Nível de complexidade


class CodeAnalyzer:
    """Analisador de código com metodologia COCOMO II"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.console = Console()
        self.metrics = CodeMetrics()

    def should_exclude(self, path: Path) -> bool:
        """Verifica se um arquivo ou diretório deve ser excluído"""
        # Verifica diretórios excluídos
        for part in path.parts:
            if part in EXCLUDED_DIRS or part.startswith('.'):
                return True

        # Verifica extensões excluídas
        if path.is_file():
            if any(path.name.endswith(ext) for ext in EXCLUDED_FILES):
                return True

        return False

    def detect_language(self, file_path: Path) -> str:
        """Detecta a linguagem de programação do arquivo"""
        suffix = file_path.suffix.lower()
        for language, extensions in LANGUAGE_EXTENSIONS.items():
            if suffix in extensions:
                return language
        return 'Other'

    def count_lines(self, file_path: Path) -> tuple:
        """Conta linhas de código, comentários e em branco"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            total = len(lines)
            blank = sum(1 for line in lines if line.strip() == '')
            comment = 0
            code = 0

            # Detecção simples de comentários (pode ser melhorada)
            for line in lines:
                stripped = line.strip()
                if stripped == '':
                    continue
                elif stripped.startswith(('#', '//', '/*', '*', '--', '<!--')):
                    comment += 1
                else:
                    code += 1

            return total, code, comment, blank
        except Exception as e:
            return 0, 0, 0, 0

    def analyze_directory(self):
        """Analisa recursivamente o diretório"""
        self.console.print(f"\n[cyan]Analisando:[/cyan] {self.root_path}\n")

        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)

            # Remove diretórios excluídos da busca
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]

            for file in files:
                file_path = root_path / file

                if self.should_exclude(file_path):
                    continue

                language = self.detect_language(file_path)
                if language == 'Other':
                    continue

                total, code, comment, blank = self.count_lines(file_path)

                self.metrics.total_lines += total
                self.metrics.code_lines += code
                self.metrics.comment_lines += comment
                self.metrics.blank_lines += blank
                self.metrics.files_count += 1

                if language in self.metrics.languages:
                    self.metrics.languages[language] += code
                else:
                    self.metrics.languages[language] = code

    def calculate_cocomo2(self, mode: str = 'organic') -> CocomoResults:
        """
        Calcula métricas usando COCOMO II

        Modos:
        - organic: Projetos pequenos e simples (até 50 KLOC)
        - semi-detached: Projetos médios (50-300 KLOC)
        - embedded: Projetos grandes e complexos (>300 KLOC)
        """
        kloc = self.metrics.code_lines / 1000.0

        # Coeficientes COCOMO II baseados no modo
        coefficients = {
            'organic': {'a': 2.4, 'b': 1.05, 'c': 2.5, 'd': 0.38},
            'semi-detached': {'a': 3.0, 'b': 1.12, 'c': 2.5, 'd': 0.35},
            'embedded': {'a': 3.6, 'b': 1.20, 'c': 2.5, 'd': 0.32}
        }

        # Determina modo automaticamente baseado em KLOC
        if kloc <= 50:
            mode = 'organic'
            complexity = 'Baixa'
        elif kloc <= 300:
            mode = 'semi-detached'
            complexity = 'Média'
        else:
            mode = 'embedded'
            complexity = 'Alta'

        coef = coefficients[mode]

        # Esforço em pessoa-mês: E = a * (KLOC)^b
        effort = coef['a'] * (kloc ** coef['b'])

        # Tempo de desenvolvimento em meses: T = c * (E)^d
        time = coef['c'] * (effort ** coef['d'])

        # Pessoas necessárias: P = E / T
        people = effort / time if time > 0 else 0

        # Manutenção: tipicamente 15-20% da equipe de desenvolvimento
        maintenance = people * 0.18

        # Expansão: tipicamente 25-35% da equipe de desenvolvimento
        expansion = people * 0.30

        # Produtividade: LOC por pessoa-mês
        productivity = (self.metrics.code_lines / effort) if effort > 0 else 0

        # Estimativa de custo
        # BRL: R$15,000/pessoa-mês (média Brasil para desenvolvedores)
        avg_salary_month_brl = 15000
        cost_brl = effort * avg_salary_month_brl

        return CocomoResults(
            kloc=kloc,
            effort_person_months=effort,
            time_months=time,
            people_required=people,
            maintenance_people=maintenance,
            expansion_people=expansion,
            productivity=productivity,
            cost_estimate_brl=cost_brl,
            complexity_level=complexity
        )

    def display_results(self, cocomo: CocomoResults):
        """Exibe os resultados de forma elegante usando Rich"""

        # Painel principal
        title = Text("ANÁLISE COCOMO II", style="bold magenta")
        self.console.print(Panel(title, box=box.DOUBLE, expand=False))

        # Tabela de métricas básicas
        metrics_table = Table(title="📊 Métricas de Código", box=box.ROUNDED, show_header=True, header_style="bold cyan")
        metrics_table.add_column("Métrica", style="yellow", width=30)
        metrics_table.add_column("Valor", justify="right", style="green")

        metrics_table.add_row("Total de Arquivos", f"{self.metrics.files_count:,}")
        metrics_table.add_row("Total de Linhas", f"{self.metrics.total_lines:,}")
        metrics_table.add_row("Linhas de Código", f"{self.metrics.code_lines:,}")
        metrics_table.add_row("Linhas de Comentários", f"{self.metrics.comment_lines:,}")
        metrics_table.add_row("Linhas em Branco", f"{self.metrics.blank_lines:,}")
        metrics_table.add_row("KLOC (Milhares de LOC)", f"{cocomo.kloc:.2f}")

        self.console.print("\n")
        self.console.print(metrics_table)

        # Tabela de linguagens
        if self.metrics.languages:
            lang_table = Table(title="💻 Distribuição por Linguagem", box=box.ROUNDED, show_header=True, header_style="bold cyan")
            lang_table.add_column("Linguagem", style="yellow", width=20)
            lang_table.add_column("Linhas de Código", justify="right", style="green")
            lang_table.add_column("Porcentagem", justify="right", style="blue")

            sorted_langs = sorted(self.metrics.languages.items(), key=lambda x: x[1], reverse=True)
            for lang, lines in sorted_langs:
                percentage = (lines / self.metrics.code_lines * 100) if self.metrics.code_lines > 0 else 0
                lang_table.add_row(lang, f"{lines:,}", f"{percentage:.1f}%")

            self.console.print("\n")
            self.console.print(lang_table)

        # Tabela de resultados COCOMO II
        cocomo_table = Table(title="🎯 Resultados COCOMO II", box=box.ROUNDED, show_header=True, header_style="bold cyan")
        cocomo_table.add_column("Métrica", style="yellow", width=35)
        cocomo_table.add_column("Valor", justify="right", style="green")

        cocomo_table.add_row("Nível de Complexidade", f"{cocomo.complexity_level}")
        cocomo_table.add_row("Esforço Total (pessoa-mês)", f"{cocomo.effort_person_months:.2f}")
        cocomo_table.add_row("Tempo de Desenvolvimento (meses)", f"{cocomo.time_months:.2f}")
        cocomo_table.add_row("Anos de Desenvolvimento", f"{cocomo.time_months / 12:.2f}")
        cocomo_table.add_row("Pessoas Necessárias (Desenvolvimento)", f"{cocomo.people_required:.2f}")
        cocomo_table.add_row("Pessoas para Manutenção", f"{cocomo.maintenance_people:.2f}")
        cocomo_table.add_row("Pessoas para Expansão", f"{cocomo.expansion_people:.2f}")
        cocomo_table.add_row("Produtividade (LOC/pessoa-mês)", f"{cocomo.productivity:.0f}")

        self.console.print("\n")
        self.console.print(cocomo_table)

        # Painel de estimativa de custo
        cost_panel = Panel(
            f"[bold green]R$ {cocomo.cost_estimate_brl:,.2f}[/bold green]\n\n"
            f"[dim]Baseado em R$15.000/pessoa-mês[/dim]\n"
            f"[dim](média salarial para desenvolvedores no Brasil)[/dim]",
            title="💰 Estimativa de Custo Total",
            box=box.DOUBLE,
            style="bold blue"
        )
        self.console.print("\n")
        self.console.print(cost_panel)

        # Insights e recomendações
        self.console.print("\n")
        insights = Panel(
            self._generate_insights(cocomo),
            title="💡 Insights e Recomendações",
            box=box.ROUNDED,
            style="cyan"
        )
        self.console.print(insights)

    def _generate_insights(self, cocomo: CocomoResults) -> str:
        """Gera insights baseados nos resultados"""
        insights = []

        if cocomo.complexity_level == "Baixa":
            insights.append("✓ Projeto de baixa complexidade - Ideal para equipes pequenas")
        elif cocomo.complexity_level == "Média":
            insights.append("⚡ Projeto de complexidade média - Requer gestão adequada")
        else:
            insights.append("⚠️  Projeto de alta complexidade - Requer gestão rigorosa")

        if cocomo.people_required < 5:
            insights.append("✓ Equipe pequena suficiente para desenvolvimento")
        elif cocomo.people_required < 15:
            insights.append("⚡ Equipe média necessária - Considere divisão em squads")
        else:
            insights.append("⚠️  Equipe grande necessária - Estrutura organizacional complexa")

        if cocomo.time_months < 6:
            insights.append("✓ Tempo de desenvolvimento curto")
        elif cocomo.time_months < 18:
            insights.append("⚡ Tempo de desenvolvimento médio - Planejamento de releases importante")
        else:
            insights.append("⚠️  Desenvolvimento de longo prazo - Risco de mudanças tecnológicas")

        # Recomendações de produtividade
        if cocomo.productivity < 300:
            insights.append("📉 Produtividade baixa - Considere refatoração ou automação")
        elif cocomo.productivity < 600:
            insights.append("📊 Produtividade adequada")
        else:
            insights.append("📈 Alta produtividade - Boas práticas aplicadas")

        return "\n".join(insights)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Analisador de código baseado em COCOMO II',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Caminho do diretório a ser analisado (padrão: diretório atual)'
    )

    args = parser.parse_args()

    path = Path(args.path).resolve()

    if not path.exists():
        Console().print(f"[bold red]Erro:[/bold red] Caminho '{path}' não encontrado")
        sys.exit(1)

    if not path.is_dir():
        Console().print(f"[bold red]Erro:[/bold red] '{path}' não é um diretório")
        sys.exit(1)

    # Executa análise
    analyzer = CodeAnalyzer(path)
    analyzer.analyze_directory()

    if analyzer.metrics.files_count == 0:
        Console().print("[bold yellow]Aviso:[/bold yellow] Nenhum arquivo de código encontrado")
        sys.exit(0)

    # Calcula COCOMO II
    cocomo_results = analyzer.calculate_cocomo2()

    # Exibe resultados
    analyzer.display_results(cocomo_results)


if __name__ == "__main__":
    main()
