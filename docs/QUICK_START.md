# Quick Start - Analisador COCOMO II

## Instalação Rápida

```bash
# Clone o repositório
git clone <repository-url>
cd analiser-cocomo2

# Instale as dependências
uv sync
# ou
pip install -e .
```

## Uso Rápido

### Interface TUI (Recomendado)

```bash
./run_tui.sh
```

**Passo a passo**:
1. Digite os caminhos dos projetos (um por vez)
2. Pressione Enter vazio para finalizar
3. Configure o salário (ex: 18000)
4. Escolha o tipo de análise
5. Confirme exportação JSON
6. Aguarde os resultados

**Relatórios gerados**: `./reports/relatorio_{projeto}_{data}.json`

### Linha de Comando

#### COCOMO II simples
```bash
uv run python main.py /caminho/do/projeto
```

#### COCOMO II + Git
```bash
uv run python git_analyzer.py /caminho/do/projeto
```

#### Com exportação JSON
```bash
uv run python git_analyzer.py /caminho/do/projeto --export relatorio.json
```

## Estrutura de Arquivos

```
analiser-cocomo2/
├── tui_analyzer.py          # Interface TUI ⭐
├── main.py                  # Análise COCOMO II
├── git_analyzer.py          # Análise integrada
├── run_tui.sh              # Script auxiliar
├── reports/                # Relatórios gerados
├── TUI_GUIDE.md            # Guia completo da TUI
├── EXEMPLO_USO_TUI.md      # Exemplos práticos
└── README.md               # Documentação completa
```

## Principais Métricas

### COCOMO II
- **KLOC**: Milhares de linhas de código
- **Esforço**: Pessoa-meses necessários
- **Tempo**: Meses de desenvolvimento
- **Pessoas**: Equipe necessária
- **Custo**: Estimativa em R$

### Git (Integrado)
- **Commits**: Total e por autor
- **Velocidade**: Linhas por dia (real vs estimado)
- **Eficiência**: % de código útil vs retrabalho
- **Score**: Produtividade (0-100)

## Exemplos Rápidos

### Analisar um projeto
```bash
./run_tui.sh
# Digite: ~/meu-projeto
# Enter vazio para finalizar
# Salário: 15000
# Tipo: COCOMO II + Git
# Exportar: Sim
```

### Analisar múltiplos projetos
```bash
./run_tui.sh
# Digite: /var/www/api
# Digite: /var/www/web
# Digite: /var/www/mobile
# Enter vazio para finalizar
# ... configure e aguarde
```

### Análise rápida sem interface
```bash
uv run python main.py .
```

## Documentação

- **Guia completo da TUI**: [TUI_GUIDE.md](TUI_GUIDE.md)
- **Exemplos práticos**: [EXEMPLO_USO_TUI.md](EXEMPLO_USO_TUI.md)
- **Documentação completa**: [README.md](README.md)

## Solução de Problemas

### Comando não encontrado
```bash
chmod +x run_tui.sh
chmod +x tui_analyzer.py
```

### Módulo não encontrado
```bash
source .venv/bin/activate
uv pip install inquirer
```

### Caminho inválido
Use caminhos absolutos ou relativos válidos:
- ✅ `/var/www/projeto`
- ✅ `~/projetos/app`
- ✅ `./src`
- ❌ `projeto` (se não existir no diretório atual)

## Dicas

1. **Use a TUI**: Mais fácil para múltiplos projetos
2. **Salário customizado**: Configure de acordo com sua realidade
3. **Análise integrada**: Oferece insights muito mais ricos
4. **Relatórios JSON**: Úteis para processamento posterior
5. **Análise periódica**: Compare evolução ao longo do tempo

## Suporte

- Issues: GitHub Issues
- Documentação: README.md
- Exemplos: EXEMPLO_USO_TUI.md
