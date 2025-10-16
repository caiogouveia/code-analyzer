#!/usr/bin/env python3
"""
Entry point for TUI (Textual User Interface) COCOMO II Analyzer.

This module provides a command-line interface for running the TUI application.
The actual application logic is in the ui package.
"""

from dotenv import load_dotenv
from ui.app import CocomoIIAnalyzerApp

# Carrega variáveis de ambiente do .env
load_dotenv()


def main():
    """Função principal que inicia a aplicação TUI."""
    app = CocomoIIAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()
