#!/usr/bin/env python3
"""
Script de demonstração do navegador de diretórios
Mostra como o DirectoryBrowserScreen funciona
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Container, Vertical
from textual.binding import Binding

# Importa o navegador
from tui_analyzer import DirectoryBrowserScreen


class DemoApp(App):
    """App de demonstração"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #demo-container {
        width: 80;
        height: auto;
        border: heavy green;
        padding: 2;
    }
    
    .demo-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
    }
    
    .demo-text {
        margin: 1 0;
    }
    
    Button {
        width: 100%;
        margin: 1 0;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Sair"),
    ]
    
    TITLE = "Demonstração do Navegador de Diretórios"
    
    def __init__(self):
        super().__init__()
        self.selected_path = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="demo-container"):
            yield Static("🧪 TESTE DO NAVEGADOR DE DIRETÓRIOS", classes="demo-title")
            
            yield Static(
                "Este teste demonstra o novo navegador de diretórios com:\n\n"
                "✅ Botão 'OK - Confirmar Seleção'\n"
                "✅ Validação automática de diretórios\n"
                "✅ Indicador de Git\n"
                "✅ Indicador de arquivos de código\n"
                "✅ Botão OK desabilitado para diretórios inválidos",
                classes="demo-text"
            )
            
            yield Button("📂 Abrir Navegador de Diretórios", variant="primary", id="btn-open")
            yield Static("", id="result-text", classes="demo-text")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Abre o navegador"""
        if event.button.id == "btn-open":
            self.push_screen(DirectoryBrowserScreen(), self.on_directory_selected)
    
    def on_directory_selected(self, selected_path: Path | None) -> None:
        """Callback quando um diretório é selecionado"""
        result_text = self.query_one("#result-text", Static)
        
        if selected_path:
            self.selected_path = selected_path
            result_text.update(
                f"✅ Diretório selecionado:\n{selected_path}\n\n"
                f"Você pode abrir novamente para testar outros diretórios."
            )
            result_text.styles.color = "green"
        else:
            result_text.update("❌ Seleção cancelada")
            result_text.styles.color = "yellow"


def main():
    """Executa o app de demonstração"""
    print("\n" + "="*70)
    print("TESTE DO NAVEGADOR DE DIRETÓRIOS - ANALISER COCOMO II")
    print("="*70)
    print("\nInstruções:")
    print("1. Clique em 'Abrir Navegador de Diretórios'")
    print("2. Navegue pelos diretórios usando a árvore")
    print("3. Observe os indicadores:")
    print("   - Status Git (verde ou amarelo)")
    print("   - Validação de arquivos de código (verde, amarelo ou vermelho)")
    print("4. O botão 'OK' só fica habilitado se o diretório for válido")
    print("5. Clique em 'OK' para confirmar ou 'Cancelar' para voltar")
    print("6. Pressione 'q' para sair a qualquer momento")
    print("="*70 + "\n")
    
    app = DemoApp()
    app.run()


if __name__ == "__main__":
    main()
