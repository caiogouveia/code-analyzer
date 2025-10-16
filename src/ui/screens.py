"""Telas modais para a interface TUI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from textual.screen import Screen, ModalScreen
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Button, Static, Input, DirectoryTree
from textual.app import ComposeResult
from textual.binding import Binding
from textual import on


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
            max_depth = 5
            max_files_to_check = 50

            def scan_directory(path: Path, depth: int = 0) -> None:
                if depth > max_depth or len(code_files_found) >= max_files_to_check:
                    return

                try:
                    exclude_dirs = {
                        'node_modules', '.git', '__pycache__', '.venv', 'venv',
                        '.mypy_cache', '.pytest_cache', 'dist', 'build', '.tox'
                    }

                    for item in path.iterdir():
                        if len(code_files_found) >= max_files_to_check:
                            break

                        if item.is_file():
                            suffix = item.suffix
                            for ext_list in LANGUAGE_EXTENSIONS.values():
                                if suffix in ext_list:
                                    code_files_found.append(str(item))
                                    extensions_found.add(suffix)
                                    break
                        elif item.is_dir() and item.name not in exclude_dirs:
                            scan_directory(item, depth + 1)

                except PermissionError:
                    pass

            scan_directory(self.selected_path)

            if not code_files_found:
                validation_indicator.update("⚠️ AVISO: Nenhum arquivo de código detectado")
                validation_indicator.styles.color = "yellow"
                validation_indicator.styles.background = "darkgoldenrod"
                ok_button.disabled = True
                self.is_valid_directory = False
                return

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

        if parent != self.selected_path:
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
            return

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
            if selected_path:
                path_input.value = str(selected_path)

        self.app.push_screen(DirectoryBrowserScreen(initial_path), on_directory_selected)

    @on(Button.Pressed, "#analyze-btn")
    def start_analysis(self) -> None:
        """Inicia a análise"""
        path_input = self.query_one("#path-input", Input)
        project_path = path_input.value.strip() or "."

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

        # Fecha a tela e inicia análise
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
