#!/usr/bin/env python3
"""Teste do DirectoryBrowserScreen"""

from pathlib import Path
from textual.app import App
from textual.screen import Screen

# Importa apenas o DirectoryBrowserScreen
import sys
sys.path.insert(0, str(Path(__file__).parent))

from tui_analyzer import DirectoryBrowserScreen


class TestApp(App):
    """App de teste"""
    
    def on_mount(self) -> None:
        """Abre o navegador ao iniciar"""
        def on_selected(path):
            self.exit(message=f"Selecionado: {path}")
        
        self.push_screen(DirectoryBrowserScreen(), on_selected)


if __name__ == "__main__":
    app = TestApp()
    result = app.run()
    print(result)
