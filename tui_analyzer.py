#!/usr/bin/env python3
"""
App TUI Integrado para Análise COCOMO II + Git
Usando Textual (textualize.io)
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import asdict
from dotenv import load_dotenv

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Static, Input, Label,
    DataTable, TabbedContent, TabPane, ProgressBar, Markdown, DirectoryTree
)
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.worker import Worker
from textual import work
from textual import on

# Importa os módulos existentes
from main import CodeAnalyzer, CocomoResults
from git_analyzer import GitAnalyzer, GitMetrics, IntegratedAnalyzer, IntegratedMetrics
from generate_pdf_report import generate_pdf_report
from security_analyzer import SecurityAnalyzer, SecurityMetrics, SecurityFinding

load_dotenv()  # Carrega variáveis de ambiente do .env

class DirectoryBrowserScreen(ModalScreen):
    """Tela de navegação de diretórios"""

    BINDINGS = [
        Binding("escape", "cancel", "Cancelar"),
    ]

    CSS = """
    DirectoryBrowserScreen {
        align: center middle;
    }

    #browser-container {
        width: 90;
        height: auto;
        max-height: 95%;
        border: heavy $primary;
        background: $surface;
        padding: 1;
    }

    #browser-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #current-path {
        color: $text-muted;
        margin-bottom: 1;
    }

    #path-input {
        width: 100%;
        margin-bottom: 1;
    }

    .nav-buttons {
        height: auto;
        margin-bottom: 1;
    }

    #directory-tree {
        height: 12;
        border: solid $primary;
        margin: 1 0;
    }

    #git-indicator {
        text-align: center;
        margin: 1 0;
        height: auto;
    }

    #validation-indicator {
        text-align: center;
        margin: 1 0;
        padding: 1;
        border: solid $primary;
        height: auto;
    }

    .browser-buttons {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    """

    def __init__(self, initial_path: Optional[Path] = None):
        super().__init__()
        self.selected_path = initial_path or Path.cwd()
        self.is_valid_directory = False

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="browser-container"):
            yield Static("📂 Selecionar Diretório do Projeto", id="browser-title")

            with Horizontal(classes="nav-buttons"):
                yield Button("⬆️ Diretório Superior", variant="default", id="btn-parent")
                yield Button("🏠 Diretório Home", variant="default", id="btn-home")

            yield Static("Caminho:", id="current-path")
            yield Input(
                value=str(self.selected_path),
                placeholder="Digite o caminho ou navegue abaixo",
                id="path-input"
            )

            yield DirectoryTree(str(self.selected_path), id="directory-tree")
            yield Static("Verificando Git...", id="git-indicator")
            yield Static("Validando diretório...", id="validation-indicator")

            with Horizontal(classes="browser-buttons"):
                yield Button("✓ OK - Confirmar Seleção", variant="success", id="btn-ok", disabled=True)
                yield Button("✗ Cancelar", variant="error", id="btn-cancel")

    def on_mount(self) -> None:
        """Inicializa o navegador"""
        tree = self.query_one(DirectoryTree)
        tree.focus()
        # Executa validação após um pequeno delay para garantir que tudo esteja renderizado
        self.set_timer(0.1, self.validate_directory)

    @on(DirectoryTree.DirectorySelected)
    def on_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Atualiza o caminho selecionado quando um diretório é escolhido"""
        self.selected_path = Path(event.path)
        self.update_path_display()
        self.validate_directory()

    def update_path_display(self) -> None:
        """Atualiza a exibição do caminho"""
        path_input = self.query_one("#path-input", Input)
        path_input.value = str(self.selected_path)

    def update_git_indicator(self) -> None:
        """Atualiza o indicador de repositório Git"""
        indicator = self.query_one("#git-indicator", Static)

        if (self.selected_path / '.git').exists():
            indicator.update("✓ Este é um repositório Git válido")
            indicator.styles.color = "green"
        else:
            indicator.update("⚠ Este diretório NÃO é um repositório Git")
            indicator.styles.color = "yellow"

    def validate_directory(self) -> None:
        """Valida se o diretório é adequado para análise"""
        self.update_git_indicator()
        
        validation_indicator = self.query_one("#validation-indicator", Static)
        ok_button = self.query_one("#btn-ok", Button)
        
        # Verifica se é um diretório válido
        if not self.selected_path.exists():
            validation_indicator.update("❌ ERRO: Caminho não existe")
            validation_indicator.styles.color = "red"
            validation_indicator.styles.background = "darkred"
            ok_button.disabled = True
            self.is_valid_directory = False
            return
        
        if not self.selected_path.is_dir():
            validation_indicator.update("❌ ERRO: Não é um diretório")
            validation_indicator.styles.color = "red"
            validation_indicator.styles.background = "darkred"
            ok_button.disabled = True
            self.is_valid_directory = False
            return
        
        # Verifica se tem arquivos de código analisáveis
        from main import LANGUAGE_EXTENSIONS
        code_files_found = []
        extensions_found = set()
        
        try:
            # Busca arquivos de código de forma mais eficiente
            # Limita a busca em profundidade para evitar travamentos
            max_depth = 5
            max_files_to_check = 50
            
            def scan_directory(path: Path, depth: int = 0) -> None:
                if depth > max_depth or len(code_files_found) >= max_files_to_check:
                    return
                
                try:
                    # Ignora diretórios comuns que não devem ser analisados
                    exclude_dirs = {
                        'node_modules', '.git', '__pycache__', '.venv', 'venv',
                        '.mypy_cache', '.pytest_cache', 'dist', 'build', '.tox'
                    }
                    
                    for item in path.iterdir():
                        if len(code_files_found) >= max_files_to_check:
                            break
                        
                        if item.is_file():
                            # Verifica se a extensão é suportada
                            suffix = item.suffix
                            for ext_list in LANGUAGE_EXTENSIONS.values():
                                if suffix in ext_list:
                                    code_files_found.append(str(item))
                                    extensions_found.add(suffix)
                                    break
                        elif item.is_dir() and item.name not in exclude_dirs:
                            scan_directory(item, depth + 1)
                
                except PermissionError:
                    pass  # Ignora diretórios sem permissão
            
            scan_directory(self.selected_path)
            
            if not code_files_found:
                validation_indicator.update("⚠️ AVISO: Nenhum arquivo de código detectado neste diretório")
                validation_indicator.styles.color = "yellow"
                validation_indicator.styles.background = "darkgoldenrod"
                ok_button.disabled = True
                self.is_valid_directory = False
                return
            
            # Diretório válido!
            count = len(code_files_found)
            more_indicator = "+" if count >= max_files_to_check else ""
            langs_text = ", ".join(sorted(extensions_found)[:5])
            validation_indicator.update(
                f"✅ Diretório válido! ({count}{more_indicator} arquivos: {langs_text})"
            )
            validation_indicator.styles.color = "green"
            validation_indicator.styles.background = "darkgreen"
            ok_button.disabled = False
            self.is_valid_directory = True
            
        except Exception as e:
            validation_indicator.update(f"⚠️ ERRO ao validar: {str(e)[:50]}")
            validation_indicator.styles.color = "red"
            validation_indicator.styles.background = "darkred"
            ok_button.disabled = True
            self.is_valid_directory = False

    def reload_tree(self) -> None:
        """Recarrega a árvore de diretórios para o caminho atual"""
        tree = self.query_one("#directory-tree", DirectoryTree)
        tree.path = str(self.selected_path)
        tree.reload()
        self.update_path_display()
        self.validate_directory()

    @on(Input.Submitted, "#path-input")
    def on_path_input_submitted(self, event: Input.Submitted) -> None:
        """Quando o usuário digita um caminho e pressiona Enter"""
        new_path_str = event.value.strip()

        if not new_path_str:
            return

        try:
            new_path = Path(new_path_str).expanduser().resolve()

            if not new_path.exists():
                event.input.value = str(self.selected_path)
                return

            if not new_path.is_dir():
                event.input.value = str(self.selected_path)
                return

            self.selected_path = new_path
            self.reload_tree()

        except Exception:
            event.input.value = str(self.selected_path)

    @on(Button.Pressed, "#btn-parent")
    def on_parent_button_pressed(self) -> None:
        """Navega para o diretório pai"""
        parent = self.selected_path.parent

        if parent != self.selected_path:  # Verifica se não está na raiz
            self.selected_path = parent
            self.reload_tree()

    @on(Button.Pressed, "#btn-home")
    def on_home_button_pressed(self) -> None:
        """Navega para o diretório home do usuário"""
        self.selected_path = Path.home()
        self.reload_tree()

    @on(Button.Pressed, "#btn-ok")
    def action_select_directory(self) -> None:
        """Confirma seleção do diretório"""
        if not self.is_valid_directory:
            return  # Não permite seleção se não for válido
        
        self.dismiss(self.selected_path)

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        """Cancela a seleção"""
        self.dismiss(None)


class WelcomeScreen(Screen):
    """Tela de boas-vindas e configuração"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Voltar"),
    ]

    CSS = """
    WelcomeScreen {
        align: center middle;
    }

    #welcome-container {
        width: 80;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    .info-text {
        margin: 1 0;
        color: $text;
    }

    #path-input {
        width: 70%;
        margin: 1 0;
    }

    #browse-btn {
        width: 25%;
        margin: 1 0;
    }

    .path-container {
        width: 100%;
        height: auto;
    }

    #analyze-btn {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="welcome-container"):
            yield Static("🚀 COCOMO II + Git Analyzer", id="title")
            yield Static("Análise Integrada de Código e Repositório", id="subtitle")

            yield Static("📁 Caminho do Projeto:", classes="info-text")
            with Horizontal(classes="path-container"):
                yield Input(
                    placeholder="./path/to/project ou deixe vazio para usar diretório atual",
                    id="path-input"
                )
                yield Button("📂 Navegar...", variant="default", id="browse-btn")

            yield Static("\n💰 Salário Mensal (BRL/pessoa-mês):", classes="info-text")
            yield Input(
                placeholder="15000",
                value="15000",
                id="salary-input"
            )

            yield Button("🔍 Iniciar Análise", variant="primary", id="analyze-btn")

            yield Static("\n💡 Dicas:", classes="info-text")
            yield Static(
                "• O projeto deve ser um repositório Git\n"
                "• Salário padrão: R$ 15.000/mês por pessoa\n"
                "• Pressione TAB para navegar entre campos\n"
                "• Pressione ESC para voltar",
                classes="info-text"
            )

    @on(Button.Pressed, "#browse-btn")
    def browse_directory(self) -> None:
        """Abre o navegador de diretórios"""
        path_input = self.query_one("#path-input", Input)
        current_path = path_input.value.strip() or "."

        try:
            initial_path = Path(current_path).resolve()
            if not initial_path.exists() or not initial_path.is_dir():
                initial_path = Path.cwd()
        except Exception:
            initial_path = Path.cwd()

        def on_directory_selected(selected_path: Optional[Path]) -> None:
            """Callback quando um diretório é selecionado"""
            if selected_path:
                path_input.value = str(selected_path)

        self.app.push_screen(DirectoryBrowserScreen(initial_path), on_directory_selected)

    @on(Button.Pressed, "#analyze-btn")
    def start_analysis(self) -> None:
        """Inicia a análise"""
        path_input = self.query_one("#path-input", Input)
        project_path = path_input.value.strip() or "."

        # Valida o caminho
        path = Path(project_path).resolve()

        if not path.exists():
            self.app.push_screen(ErrorScreen(f"Caminho não encontrado: {path}"))
            return

        if not path.is_dir():
            self.app.push_screen(ErrorScreen(f"Caminho não é um diretório: {path}"))
            return

        if not (path / '.git').exists():
            self.app.push_screen(ErrorScreen(f"Não é um repositório Git: {path}"))
            return

        # Captura o salário customizado
        salary_input = self.query_one("#salary-input", Input)
        try:
            salary = float(salary_input.value.strip().replace(',', '.'))
            if salary <= 0:
                self.app.push_screen(ErrorScreen("Salário deve ser um valor positivo"))
                return
            self.app.custom_salary = salary
        except ValueError:
            self.app.push_screen(ErrorScreen("Valor de salário inválido. Use apenas números."))
            return

        # Fecha a tela de boas-vindas e inicia análise
        self.app.pop_screen()
        self.app.start_analysis(path)


class ErrorScreen(Screen):
    """Tela de erro"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Voltar"),
        Binding("enter", "app.pop_screen", "Voltar"),
    ]

    CSS = """
    ErrorScreen {
        align: center middle;
    }

    #error-container {
        width: 60;
        height: auto;
        border: heavy $error;
        background: $surface;
        padding: 2;
    }

    #error-title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }

    #error-message {
        text-align: center;
        margin: 1 0;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="error-container"):
            yield Static("❌ ERRO", id="error-title")
            yield Static(self.message, id="error-message")
            yield Static("\nPressione ESC ou ENTER para voltar", id="error-hint")


class CocomoIIAnalyzerApp(App):
    """App principal TUI"""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    TabPane {
        padding: 1;
    }

    .metrics-table {
        height: auto;
        margin: 1 0;
    }

    .action-buttons {
        height: auto;
        align: center middle;
        margin: 1 0;
    }

    Button {
        margin: 0 1;
    }

    .status-text {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }

    ProgressBar {
        margin: 1 0;
    }

    #analysis-progress {
        display: none;
        margin: 1 2;
    }

    #progress-label {
        display: none;
        text-align: center;
        margin-top: 1;
    }

    .info-text {
        margin: 1 0;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Sair"),
        Binding("r", "reload", "Recarregar"),
        Binding("e", "export_json", "Exportar JSON"),
        Binding("p", "export_pdf", "Exportar PDF"),
        Binding("n", "new_analysis", "Nova Análise"),
        Binding("i", "generate_ai_insights", "Gerar Insights IA"),
    ]

    TITLE = "COCOMO II + Git Analyzer"
    SUB_TITLE = "Análise Integrada de Código e Repositório"

    def __init__(self):
        super().__init__()
        self.project_path: Optional[Path] = None
        self.cocomo_results: Optional[CocomoResults] = None
        self.git_metrics: Optional[GitMetrics] = None
        self.integrated_metrics: Optional[IntegratedMetrics] = None
        self.security_metrics: Optional[SecurityMetrics] = None
        self.code_analyzer: Optional[CodeAnalyzer] = None
        self.ai_insights_generated: bool = False
        self.ai_insights_data: Optional[dict] = None
        self.custom_salary: float = 15000.0  # Salário padrão em BRL/mês

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="main-container"):
            # Barra de progresso global (inicialmente oculta)
            yield Static("", id="progress-label", classes="status-text")
            yield ProgressBar(id="analysis-progress", total=100, show_eta=False)

            with TabbedContent(initial="tab-welcome"):
                with TabPane("🏠 Início", id="tab-welcome"):
                    yield Static("Bem-vindo ao COCOMO II + Git Analyzer!", classes="section-title")
                    yield Static(
                        "Selecione 'Nova Análise' abaixo para começar ou pressione 'n' para nova análise.",
                        classes="status-text"
                    )
                    with Horizontal(classes="action-buttons"):
                        yield Button("🔍 Nova Análise", variant="primary", id="btn-new-analysis")
                        yield Button("📂 Analisar Diretório Atual", variant="success", id="btn-analyze-current")

                with TabPane("📊 COCOMO II", id="tab-cocomo"):
                    yield Static("Análise COCOMO II", classes="section-title")
                    yield DataTable(id="cocomo-table", classes="metrics-table")
                    yield Static("Aguardando análise...", id="cocomo-status", classes="status-text")

                with TabPane("📈 Git", id="tab-git"):
                    yield Static("Análise do Repositório Git", classes="section-title")
                    yield DataTable(id="git-table", classes="metrics-table")
                    yield Static("\nTop 10 Contribuidores", classes="section-title")
                    yield DataTable(id="authors-table", classes="metrics-table")
                    yield Static("Aguardando análise...", id="git-status", classes="status-text")

                with TabPane("🎯 Integrado", id="tab-integrated"):
                    yield Static("Análise Integrada", classes="section-title")
                    yield DataTable(id="integrated-table", classes="metrics-table")
                    yield Static("\n💡 Insights e Recomendações", classes="section-title")
                    yield Static("", id="insights-text", classes="info-text")
                    yield Static("Aguardando análise...", id="integrated-status", classes="status-text")

                with TabPane("🔒 Segurança", id="tab-security"):
                    yield Static("Análise de Segurança (Semgrep)", classes="section-title")
                    yield Static(
                        "Análise automatizada de vulnerabilidades e problemas de segurança no código.\n"
                        "Requer o Semgrep instalado no sistema.",
                        classes="info-text"
                    )

                    with Horizontal(classes="action-buttons"):
                        yield Button("🔍 Executar Análise de Segurança", variant="primary", id="btn-run-security")

                    yield Static("", id="security-status", classes="status-text")

                    yield Static("\n📊 Métricas de Segurança", classes="section-title")
                    yield DataTable(id="security-metrics-table", classes="metrics-table")

                    yield Static("\n⚠️ Top 10 Arquivos com Problemas", classes="section-title")
                    yield DataTable(id="vulnerable-files-table", classes="metrics-table")

                    yield Static("\n🚨 Descobertas Críticas e Altas", classes="section-title")
                    yield DataTable(id="critical-findings-table", classes="metrics-table")

                with TabPane("🤖 Insights IA", id="tab-ai-insights"):
                    yield Static("Insights Gerados por Inteligência Artificial", classes="section-title")
                    yield Static(
                        "Use IA para obter análises avançadas sobre valor do código e métricas de mercado.\n"
                        "Requer uma chave de API da OpenAI configurada (variável OPENAI_API_KEY).",
                        classes="info-text"
                    )

                    with Horizontal(classes="action-buttons"):
                        yield Button("🤖 Gerar Insights com IA", variant="primary", id="btn-generate-ai")

                    yield Static("", id="ai-insights-status", classes="status-text")
                    yield ScrollableContainer(
                        Static("Aguardando geração de insights...", id="ai-insights-content", classes="info-text")
                    )

                with TabPane("💾 Exportar", id="tab-export"):
                    yield Static("Exportar Resultados", classes="section-title")
                    yield Static("Escolha o formato de exportação:", classes="status-text")

                    with Vertical():
                        yield Static("", id="export-config-info", classes="info-text")

                        yield Static("📄 Nome do arquivo (sem extensão):", classes="info-text")
                        yield Input(
                            placeholder="relatorio_cocomo",
                            value="relatorio_cocomo",
                            id="export-filename"
                        )

                        with Horizontal(classes="action-buttons"):
                            yield Button("💾 Exportar JSON", variant="primary", id="btn-export-json")
                            yield Button("📄 Exportar PDF", variant="success", id="btn-export-pdf")

                        yield Static("", id="export-status", classes="status-text")

        yield Footer()

    def on_mount(self) -> None:
        """Inicializa as tabelas"""
        # Tabela COCOMO
        cocomo_table = self.query_one("#cocomo-table", DataTable)
        cocomo_table.add_columns("Métrica", "Valor")
        cocomo_table.cursor_type = "row"

        # Tabela Git
        git_table = self.query_one("#git-table", DataTable)
        git_table.add_columns("Métrica", "Valor")
        git_table.cursor_type = "row"

        # Tabela de autores
        authors_table = self.query_one("#authors-table", DataTable)
        authors_table.add_columns("Autor", "Commits", "% do Total")
        authors_table.cursor_type = "row"

        # Tabela integrada
        integrated_table = self.query_one("#integrated-table", DataTable)
        integrated_table.add_columns("Indicador", "Valor")
        integrated_table.cursor_type = "row"

        # Tabelas de segurança
        security_metrics_table = self.query_one("#security-metrics-table", DataTable)
        security_metrics_table.add_columns("Métrica", "Valor")
        security_metrics_table.cursor_type = "row"

        vulnerable_files_table = self.query_one("#vulnerable-files-table", DataTable)
        vulnerable_files_table.add_columns("Arquivo", "Problemas")
        vulnerable_files_table.cursor_type = "row"

        critical_findings_table = self.query_one("#critical-findings-table", DataTable)
        critical_findings_table.add_columns("Severidade", "Arquivo", "Linha", "Mensagem")
        critical_findings_table.cursor_type = "row"

    @on(Button.Pressed, "#btn-new-analysis")
    def action_new_analysis(self) -> None:
        """Abre tela de nova análise"""
        self.push_screen(WelcomeScreen())

    @on(Button.Pressed, "#btn-analyze-current")
    def action_analyze_current(self) -> None:
        """Analisa o diretório atual"""
        current_path = Path.cwd()

        if not (current_path / '.git').exists():
            self.push_screen(ErrorScreen(f"Diretório atual não é um repositório Git: {current_path}"))
            return

        self.start_analysis(current_path)

    def start_analysis(self, path: Path) -> None:
        """Inicia a análise em background"""
        self.project_path = path

        # Mostra a barra de progresso
        progress_bar = self.query_one("#analysis-progress", ProgressBar)
        progress_label = self.query_one("#progress-label", Static)
        progress_bar.styles.display = "block"
        progress_label.styles.display = "block"
        progress_bar.update(progress=0)
        progress_label.update("🔍 Iniciando análise...")

        # Atualiza status
        self.query_one("#cocomo-status", Static).update("⏳ Analisando código...")
        self.query_one("#git-status", Static).update("⏳ Analisando repositório Git...")
        self.query_one("#integrated-status", Static).update("⏳ Calculando métricas integradas...")

        # Executa análise em worker (o @work decorator já cria o worker)
        self.perform_analysis(path)

    @work(thread=True)
    def perform_analysis(self, path: Path) -> None:
        """Executa a análise em background"""
        try:
            # Etapa 1: Análise COCOMO (0-40%)
            self.call_from_thread(self.update_progress, 10, "📊 Analisando código-fonte...")

            self.code_analyzer = CodeAnalyzer(path)
            self.code_analyzer.analyze_directory()

            self.call_from_thread(self.update_progress, 30, "📊 Calculando métricas COCOMO...")

            # Etapa 2: Análise Git (40-70%)
            self.call_from_thread(self.update_progress, 45, "📈 Analisando repositório Git...")

            analyzer = IntegratedAnalyzer(path)
            cocomo, git, integrated, security = analyzer.analyze(
                self.custom_salary,
                run_security_analysis=False  # Desativa análise de segurança no TUI por enquanto
            )

            self.call_from_thread(self.update_progress, 70, "📈 Processando histórico de commits...")

            self.cocomo_results = cocomo
            self.git_metrics = git

            # Etapa 3: Métricas Integradas (70-95%)
            self.call_from_thread(self.update_progress, 85, "🎯 Calculando métricas integradas...")

            self.integrated_metrics = integrated

            self.call_from_thread(self.update_progress, 95, "✨ Finalizando análise...")

            # Atualiza a UI
            self.call_from_thread(self.update_results)

            # Completa o progresso
            self.call_from_thread(self.update_progress, 100, "✅ Análise concluída!")

        except Exception as e:
            self.call_from_thread(self.show_error, str(e))

    def update_progress(self, progress: int, message: str) -> None:
        """Atualiza a barra de progresso"""
        progress_bar = self.query_one("#analysis-progress", ProgressBar)
        progress_label = self.query_one("#progress-label", Static)

        progress_bar.update(progress=progress)
        progress_label.update(message)

        # Esconde a barra quando completa
        if progress >= 100:
            # Aguarda um pouco para o usuário ver a conclusão
            self.set_timer(2.0, self.hide_progress_bar)

    def hide_progress_bar(self) -> None:
        """Esconde a barra de progresso"""
        progress_bar = self.query_one("#analysis-progress", ProgressBar)
        progress_label = self.query_one("#progress-label", Static)
        progress_bar.styles.display = "none"
        progress_label.styles.display = "none"

    def update_results(self) -> None:
        """Atualiza os resultados na UI"""
        if not all([self.cocomo_results, self.git_metrics, self.integrated_metrics]):
            return

        self.update_cocomo_tab()
        self.update_git_tab()
        self.update_integrated_tab()
        self.update_export_info()

    def update_cocomo_tab(self) -> None:
        """Atualiza aba COCOMO II"""
        if not self.cocomo_results:
            return

        cocomo = self.cocomo_results
        table = self.query_one("#cocomo-table", DataTable)
        table.clear()

        table.add_row("💰 Salário Base (BRL/pessoa-mês)", f"R$ {self.custom_salary:,.2f}")
        table.add_row("", "")
        table.add_row("KLOC (Milhares de LOC)", f"{cocomo.kloc:.2f}")
        table.add_row("Complexidade", cocomo.complexity_level)
        table.add_row("Esforço (pessoa-mês)", f"{cocomo.effort_person_months:.2f}")
        table.add_row("Tempo (meses)", f"{cocomo.time_months:.2f}")
        table.add_row("Anos de Desenvolvimento", f"{cocomo.time_months / 12:.2f}")
        table.add_row("Pessoas Necessárias", f"{cocomo.people_required:.2f}")
        table.add_row("Pessoas para Manutenção", f"{cocomo.maintenance_people:.2f}")
        table.add_row("Pessoas para Expansão", f"{cocomo.expansion_people:.2f}")
        table.add_row("Produtividade (LOC/pessoa-mês)", f"{cocomo.productivity:.0f}")
        table.add_row("Custo Estimado (BRL)", f"R$ {cocomo.cost_estimate_brl:,.2f}")

        self.query_one("#cocomo-status", Static).update("✅ Análise COCOMO II concluída!")

    def update_git_tab(self) -> None:
        """Atualiza aba Git"""
        if not self.git_metrics:
            return

        git = self.git_metrics

        # Tabela principal
        table = self.query_one("#git-table", DataTable)
        table.clear()

        table.add_row("Total de Commits", f"{git.total_commits:,}")
        table.add_row("Total de Autores", f"{git.total_authors}")
        table.add_row("Idade do Repositório (dias)", f"{git.repository_age_days}")
        table.add_row("Commits por Dia", f"{git.commits_per_day:.2f}")
        table.add_row("Inserções Totais", f"{git.total_insertions:,}")
        table.add_row("Deleções Totais", f"{git.total_deletions:,}")
        table.add_row("Mudanças/Commit (média)", f"{git.avg_changes_per_commit:.1f}")
        table.add_row("Arquivos/Commit (média)", f"{git.avg_files_per_commit:.1f}")

        # Tabela de autores
        authors_table = self.query_one("#authors-table", DataTable)
        authors_table.clear()

        if git.authors_commits:
            sorted_authors = sorted(
                git.authors_commits.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            for author, count in sorted_authors:
                percentage = (count / git.total_commits * 100)
                authors_table.add_row(author, f"{count:,}", f"{percentage:.1f}%")

        self.query_one("#git-status", Static).update("✅ Análise Git concluída!")

    def update_integrated_tab(self) -> None:
        """Atualiza aba Integrada"""
        if not self.integrated_metrics:
            return

        integrated = self.integrated_metrics

        # Tabela
        table = self.query_one("#integrated-table", DataTable)
        table.clear()

        table.add_row("KLOC (COCOMO)", f"{integrated.cocomo_kloc:.2f}")
        table.add_row("Esforço (pessoa-mês)", f"{integrated.cocomo_effort:.2f}")
        table.add_row("Tempo (meses)", f"{integrated.cocomo_time_months:.2f}")
        table.add_row("Pessoas", f"{integrated.cocomo_people:.2f}")
        table.add_row("Custo (BRL)", f"R$ {integrated.cocomo_cost_brl:,.2f}")
        table.add_row("", "")
        table.add_row("Total de Commits", f"{integrated.total_commits:,}")
        table.add_row("Commits por Mês", f"{integrated.commits_per_month:.1f}")
        table.add_row("Linhas por Commit", f"{integrated.lines_per_commit:.1f}")
        table.add_row("Commits p/ Recriar Codebase", f"{integrated.commits_needed_to_rebuild:.0f}")
        table.add_row("", "")
        table.add_row("Velocidade Real (linhas/dia)", f"{integrated.actual_velocity:.1f}")
        table.add_row("Velocidade COCOMO (linhas/dia)", f"{integrated.estimated_velocity:.1f}")
        table.add_row("Razão Velocidade (real/estimado)", f"{integrated.velocity_ratio:.2f}x")
        table.add_row("Eficiência de Commit", f"{integrated.commit_efficiency:.1f}%")
        table.add_row("% Mudança Média/Commit", f"{integrated.change_percentage_per_commit:.2f}%")
        table.add_row("", "")
        table.add_row("⭐ Score de Produtividade", f"{integrated.developer_productivity_score:.1f}/100")

        # Insights
        insights = self.generate_insights(integrated, self.git_metrics)
        self.query_one("#insights-text", Static).update(insights)

        self.query_one("#integrated-status", Static).update("✅ Análise integrada concluída!")

    def generate_insights(self, integrated: IntegratedMetrics, git: GitMetrics) -> str:
        """Gera insights"""
        insights = []

        # Velocidade
        if integrated.velocity_ratio > 1.2:
            insights.append("🚀 Velocidade acima do esperado - Equipe muito produtiva!")
        elif integrated.velocity_ratio > 0.8:
            insights.append("✓ Velocidade dentro do esperado")
        else:
            insights.append("⚠️  Velocidade abaixo do esperado - Revisar impedimentos")

        # Eficiência
        if integrated.commit_efficiency > 50:
            insights.append("✓ Alta eficiência de commits - Baixo retrabalho")
        elif integrated.commit_efficiency > 30:
            insights.append("⚡ Eficiência moderada - Algum retrabalho presente")
        else:
            insights.append("⚠️  Baixa eficiência - Alto retrabalho (churn)")

        # Tamanho de commits
        if integrated.change_percentage_per_commit < 1:
            insights.append("✓ Commits pequenos e incrementais - Boa prática")
        elif integrated.change_percentage_per_commit < 5:
            insights.append("⚡ Tamanho de commit moderado")
        else:
            insights.append("⚠️  Commits muito grandes - Considere commits menores")

        # Frequência
        if integrated.commits_per_month > 40:
            insights.append("✓ Alta frequência de commits - Desenvolvimento ativo")
        elif integrated.commits_per_month > 20:
            insights.append("⚡ Frequência moderada de commits")
        else:
            insights.append("📊 Baixa frequência de commits")

        # Score
        if integrated.developer_productivity_score >= 75:
            insights.append("🌟 Excelente produtividade da equipe!")
        elif integrated.developer_productivity_score >= 50:
            insights.append("👍 Boa produtividade geral")
        else:
            insights.append("📈 Oportunidade de melhoria na produtividade")

        return "\n".join(insights)

    def update_export_info(self) -> None:
        """Atualiza informações de exportação"""
        info_text = f"💰 Salário usado nos cálculos: R$ {self.custom_salary:,.2f}/pessoa-mês\n" \
                    f"📁 Projeto: {self.project_path.name if self.project_path else 'N/A'}"
        self.query_one("#export-config-info", Static).update(info_text)

    @on(Button.Pressed, "#btn-export-json")
    def action_export_json(self) -> None:
        """Exporta para JSON"""
        if not all([self.cocomo_results, self.git_metrics, self.integrated_metrics]):
            self.query_one("#export-status", Static).update("❌ Execute uma análise primeiro!")
            return

        filename = self.query_one("#export-filename", Input).value.strip()
        if not filename:
            filename = "relatorio_cocomo"

        output_path = Path(f"{filename}.json")

        try:
            data = {
                'project_name': self.project_path.name if self.project_path else "Projeto",
                'project_path': str(self.project_path) if self.project_path else "",
                'analysis_type': 'integrated',
                'generated_at': datetime.now().isoformat(),
                'custom_salary_brl': self.custom_salary,
                'cocomo': asdict(self.cocomo_results),
                'git': self.git_metrics.to_dict(),
                'integrated': asdict(self.integrated_metrics),
            }

            # Inclui insights de IA se foram gerados
            if self.ai_insights_generated and self.ai_insights_data:
                data['ai_insights'] = self.ai_insights_data

            # Inclui análise de segurança se foi executada
            if self.security_metrics:
                data['security'] = self.security_metrics.to_dict()
                data['security_score'] = self.get_security_score(self.security_metrics)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.query_one("#export-status", Static).update(f"✅ JSON exportado: {output_path}")

        except Exception as e:
            self.query_one("#export-status", Static).update(f"❌ Erro ao exportar: {e}")

    @on(Button.Pressed, "#btn-export-pdf")
    def action_export_pdf(self) -> None:
        """Exporta para PDF"""
        if not all([self.cocomo_results, self.git_metrics, self.integrated_metrics]):
            self.query_one("#export-status", Static).update("❌ Execute uma análise primeiro!")
            return

        filename = self.query_one("#export-filename", Input).value.strip()
        if not filename:
            filename = "relatorio_cocomo"

        # Primeiro exporta JSON temporário
        temp_json = Path(f"{filename}_temp.json")
        output_pdf = Path(f"{filename}.pdf")

        try:
            self.query_one("#export-status", Static).update("⏳ Gerando PDF...")

            # Cria JSON temporário
            data = {
                'project_name': self.project_path.name if self.project_path else "Projeto",
                'project_path': str(self.project_path) if self.project_path else "",
                'analysis_type': 'integrated',
                'generated_at': datetime.now().isoformat(),
                'custom_salary_brl': self.custom_salary,
                'cocomo': asdict(self.cocomo_results),
                'git': self.git_metrics.to_dict(),
                'integrated': asdict(self.integrated_metrics),
            }

            # Inclui insights de IA se foram gerados
            if self.ai_insights_generated and self.ai_insights_data:
                data['ai_insights'] = self.ai_insights_data

            # Inclui análise de segurança se foi executada
            if self.security_metrics:
                data['security'] = self.security_metrics.to_dict()
                data['security_score'] = self.get_security_score(self.security_metrics)

            with open(temp_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Gera PDF
            generate_pdf_report(str(temp_json), str(output_pdf))

            # Remove JSON temporário
            temp_json.unlink()

            self.query_one("#export-status", Static).update(f"✅ PDF exportado: {output_pdf}")

        except Exception as e:
            self.query_one("#export-status", Static).update(f"❌ Erro ao exportar: {e}")
            if temp_json.exists():
                temp_json.unlink()

    def show_error(self, message: str) -> None:
        """Mostra erro"""
        # Esconde a barra de progresso
        self.hide_progress_bar()

        self.push_screen(ErrorScreen(message))
        self.query_one("#cocomo-status", Static).update(f"❌ Erro: {message}")
        self.query_one("#git-status", Static).update(f"❌ Erro: {message}")
        self.query_one("#integrated-status", Static).update(f"❌ Erro: {message}")

    def action_reload(self) -> None:
        """Recarrega análise"""
        if self.project_path:
            self.start_analysis(self.project_path)
        else:
            self.push_screen(WelcomeScreen())

    def action_quit(self) -> None:
        """Sai do app"""
        self.exit()

    @on(Button.Pressed, "#btn-generate-ai")
    def action_generate_ai_insights(self) -> None:
        """Gera insights usando IA da OpenAI"""
        if not all([self.cocomo_results, self.code_analyzer]):
            self.query_one("#ai-insights-status", Static).update(
                "❌ Execute uma análise primeiro antes de gerar insights com IA!"
            )
            return

        # Verifica se a chave API está disponível
        import os
        if not os.getenv("OPENAI_API_KEY"):
            self.query_one("#ai-insights-status", Static).update(
                "❌ Configure a variável de ambiente OPENAI_API_KEY com sua chave da OpenAI"
            )
            return

        self.query_one("#ai-insights-status", Static).update("⏳ Gerando insights com IA...")
        self.query_one("#ai-insights-content", Static).update("Processando...")

        # Executa geração em worker
        self.generate_ai_insights_worker()

    @work(thread=True)
    def generate_ai_insights_worker(self) -> None:
        """Gera insights de IA em background"""
        try:
            from ai_insights import generate_ai_insights

            project_name = self.project_path.name if self.project_path else "Projeto"

            insights_result = generate_ai_insights(
                cocomo=self.cocomo_results,
                git=self.git_metrics,
                integrated=self.integrated_metrics,
                code_metrics=self.code_analyzer.metrics if self.code_analyzer else None,
                project_name=project_name
            )

            self.call_from_thread(self.update_ai_insights, insights_result)

        except Exception as e:
            error_msg = f"❌ Erro ao gerar insights: {str(e)}"
            self.call_from_thread(self.show_ai_error, error_msg)

    def update_ai_insights(self, insights_result: dict) -> None:
        """Atualiza os insights de IA na UI"""
        from insights import build_ai_insights
        from ai_insights import AIInsightsGenerator

        self.ai_insights_generated = True
        self.ai_insights_data = insights_result  # Armazena os dados estruturados

        # Formata para exibição
        generator = AIInsightsGenerator()
        insights_text = generator.format_insights_for_display(insights_result)

        self.query_one("#ai-insights-status", Static).update("✅ Insights gerados com sucesso!")
        self.query_one("#ai-insights-content", Static).update(insights_text)

    def show_ai_error(self, error_msg: str) -> None:
        """Mostra erro na geração de insights"""
        self.query_one("#ai-insights-status", Static).update(error_msg)
        self.query_one("#ai-insights-content", Static).update(
            "[red]Não foi possível gerar insights. Verifique sua chave API e tente novamente.[/red]"
        )

    @on(Button.Pressed, "#btn-run-security")
    def action_run_security_analysis(self) -> None:
        """Executa a análise de segurança"""
        if not self.project_path:
            self.query_one("#security-status", Static).update(
                "❌ Execute uma análise do projeto primeiro!"
            )
            return

        self.query_one("#security-status", Static).update("⏳ Executando análise de segurança...")

        # Executa análise em worker
        self.run_security_analysis_worker()

    @work(thread=True)
    def run_security_analysis_worker(self) -> None:
        """Executa a análise de segurança em background"""
        try:
            analyzer = SecurityAnalyzer(self.project_path)

            # Verifica se o Semgrep está disponível
            if not analyzer.check_semgrep_available():
                error_msg = "❌ Semgrep não está instalado. Instale com: pip install semgrep"
                self.call_from_thread(self.show_security_error, error_msg)
                return

            # Executa a análise
            metrics = analyzer.analyze(config='auto', max_findings=100)

            self.call_from_thread(self.update_security_results, metrics)

        except Exception as e:
            error_msg = f"❌ Erro ao executar análise de segurança: {str(e)}"
            self.call_from_thread(self.show_security_error, error_msg)

    def update_security_results(self, metrics: SecurityMetrics) -> None:
        """Atualiza os resultados da análise de segurança na UI"""
        self.security_metrics = metrics

        # Atualiza status
        security_score = self.get_security_score(metrics)
        self.query_one("#security-status", Static).update(
            f"✅ Análise concluída! Score de Segurança: {security_score:.1f}/100"
        )

        # Atualiza tabela de métricas
        metrics_table = self.query_one("#security-metrics-table", DataTable)
        metrics_table.clear()

        metrics_table.add_row("🎯 Score de Segurança", f"{security_score:.1f}/100")
        metrics_table.add_row("", "")
        metrics_table.add_row("Total de Descobertas", f"{metrics.total_findings:,}")
        metrics_table.add_row("  • Críticas", f"{metrics.critical_findings}")
        metrics_table.add_row("  • Altas", f"{metrics.high_findings}")
        metrics_table.add_row("  • Médias", f"{metrics.medium_findings}")
        metrics_table.add_row("  • Baixas", f"{metrics.low_findings}")
        metrics_table.add_row("  • Informativas", f"{metrics.info_findings}")
        metrics_table.add_row("", "")
        metrics_table.add_row("Problemas de Segurança", f"{metrics.security_issues}")
        metrics_table.add_row("Problemas de Best Practice", f"{metrics.best_practice_issues}")
        metrics_table.add_row("Problemas de Performance", f"{metrics.performance_issues}")
        metrics_table.add_row("", "")
        metrics_table.add_row("Arquivos Escaneados", f"{metrics.files_scanned}")
        metrics_table.add_row("Tempo de Scan", f"{metrics.scan_duration_seconds:.2f}s")

        # Atualiza tabela de arquivos vulneráveis
        vulnerable_files_table = self.query_one("#vulnerable-files-table", DataTable)
        vulnerable_files_table.clear()

        sorted_files = sorted(
            metrics.files_with_issues.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        for file_path, count in sorted_files:
            # Encurta o caminho se for muito longo
            display_path = file_path
            if len(display_path) > 60:
                display_path = "..." + display_path[-57:]
            vulnerable_files_table.add_row(display_path, f"{count}")

        # Atualiza tabela de descobertas críticas e altas
        critical_findings_table = self.query_one("#critical-findings-table", DataTable)
        critical_findings_table.clear()

        critical_and_high = [
            f for f in metrics.findings
            if f.severity in ['CRITICAL', 'HIGH']
        ][:15]  # Limita a 15 descobertas

        for finding in critical_and_high:
            # Encurta o caminho do arquivo
            display_path = finding.file_path
            if len(display_path) > 40:
                display_path = "..." + display_path[-37:]

            # Encurta a mensagem
            message = finding.message
            if len(message) > 50:
                message = message[:47] + "..."

            critical_findings_table.add_row(
                finding.severity,
                display_path,
                f"{finding.line}",
                message
            )

    def get_security_score(self, metrics: SecurityMetrics) -> float:
        """Calcula o score de segurança"""
        if metrics.total_findings == 0:
            return 100.0

        # Pesos por severidade
        critical_weight = 10
        high_weight = 5
        medium_weight = 2
        low_weight = 1

        # Calcula pontuação negativa
        negative_score = (
            metrics.critical_findings * critical_weight +
            metrics.high_findings * high_weight +
            metrics.medium_findings * medium_weight +
            metrics.low_findings * low_weight
        )

        # Normaliza para 0-100
        import math
        if negative_score == 0:
            return 100.0

        score = max(0, 100 - (math.log1p(negative_score) * 10))
        return round(score, 2)

    def show_security_error(self, error_msg: str) -> None:
        """Mostra erro na análise de segurança"""
        self.query_one("#security-status", Static).update(error_msg)


def main():
    """Função principal"""
    app = CocomoIIAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()
