#!/bin/bash
# Script para executar o Analisador TUI COCOMO II

echo "🚀 Iniciando COCOMO II + Git Analyzer TUI..."
echo ""

# Verifica se o ambiente virtual existe
if [ -d ".venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source .venv/bin/activate
fi

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

# Verifica se textual está instalado
if ! python3 -c "import textual" &> /dev/null 2>&1; then
    echo "⚠️  Textual não está instalado."
    echo "📦 Instalando dependências..."
    pip install textual
fi

# Executa o app TUI
python3 tui_analyzer.py "$@"
