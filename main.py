#!/usr/bin/env python3
"""
Analisador de Código baseado em COCOMO II
Analisa complexidade, esforço, tempo e recursos necessários para desenvolvimento
"""

import os
import sys
import argparse
from importlib import import_module
from pathlib import Path

from analysis_config import COCOMO_COEFFICIENTS, COMPLEXITY_THRESHOLDS, compile_exclusion_spec
from insights import build_cocomo_insights, build_ai_insights
from models import CodeMetrics, CocomoResults
from renderers import (
    build_code_metrics_table,
    build_language_distribution_table,
    build_cocomo_table,
    build_cost_panel,
)

Console = import_module("rich.console").Console
Panel = import_module("rich.panel").Panel
box = import_module("rich.box")
Text = import_module("rich.text").Text


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

class CodeAnalyzer:
    """Analisador de código com metodologia COCOMO II"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.console = Console()
        self.metrics = CodeMetrics()
        self._exclude_spec = compile_exclusion_spec()

    def should_exclude(self, path: Path) -> bool:
        """Verifica se um arquivo ou diretório deve ser excluído."""
        try:
            relative = path.relative_to(self.root_path)
        except ValueError:
            relative = path

        parts = [part for part in relative.parts if part not in (".", "")]
        if any(part.startswith('.') for part in parts):
            return True

        relative_str = relative.as_posix()
        if not relative_str or relative_str == '.':
            return False

        if path.is_dir():
            relative_str = f"{relative_str.rstrip('/')}/"

        return self._exclude_spec.match_file(relative_str)

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
        except Exception:
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

    def calculate_cocomo2(self, avg_salary_month_brl: float = 15000.0) -> CocomoResults:
        """Calcula métricas usando COCOMO II.

        Args:
            avg_salary_month_brl: Salário médio mensal em BRL por pessoa (padrão: R$15.000)
        """
        kloc = self.metrics.code_lines / 1000.0

        mode = 'organic'
        complexity = 'Baixa'
        for threshold, candidate_mode, label in COMPLEXITY_THRESHOLDS:
            if kloc <= threshold:
                mode = candidate_mode
                complexity = label
                break

        coef = COCOMO_COEFFICIENTS[mode]

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

    def display_results(self, cocomo: CocomoResults, use_ai_insights: bool = False):
        """Exibe os resultados de forma elegante usando Rich"""

        # Painel principal
        title = Text("ANÁLISE COCOMO II", style="bold magenta")
        self.console.print(Panel(title, box=box.DOUBLE, expand=False))

        metrics_table = build_code_metrics_table(self.metrics, cocomo.kloc)
        self.console.print("\n")
        self.console.print(metrics_table)

        language_table = build_language_distribution_table(self.metrics)
        if language_table:
            self.console.print("\n")
            self.console.print(language_table)

        cocomo_table = build_cocomo_table(cocomo)
        self.console.print("\n")
        self.console.print(cocomo_table)

        self.console.print("\n")
        self.console.print(build_cost_panel(cocomo))

        # Insights tradicionais
        insights_content = build_cocomo_insights(cocomo)
        self.console.print("\n")
        self.console.print(
            Panel(
                insights_content,
                title="💡 Insights e Recomendações",
                box=box.ROUNDED,
                style="cyan",
            )
        )

        # Insights com IA (se solicitado)
        if use_ai_insights:
            self.console.print("\n")
            self.console.print("[cyan]Gerando insights com IA...[/cyan]")

            ai_insights_content = build_ai_insights(
                cocomo=cocomo,
                code_metrics=self.metrics,
                project_name=self.root_path.name
            )

            self.console.print("\n")
            self.console.print(
                Panel(
                    ai_insights_content,
                    title="🤖 Insights com Inteligência Artificial",
                    box=box.ROUNDED,
                    style="magenta",
                )
            )

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
    parser.add_argument(
        '--ai-insights',
        '-ai',
        action='store_true',
        help='Gera insights usando IA da OpenAI (requer OPENAI_API_KEY configurada)'
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
    analyzer.display_results(cocomo_results, use_ai_insights=args.ai_insights)


if __name__ == "__main__":
    main()
