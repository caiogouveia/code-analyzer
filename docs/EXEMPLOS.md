# Exemplos de Uso

Este documento contém exemplos práticos de como usar os scripts do Analisador COCOMO II.

## 1. Análise COCOMO II Básica (main.py)

### Exemplo 1: Analisar o diretório atual
```bash
uv run python main.py
```

**Quando usar**: Quando você está dentro do diretório do projeto que deseja analisar.

### Exemplo 2: Analisar um diretório específico
```bash
uv run python main.py /caminho/para/projeto
```

**Exemplo prático**:
```bash
# Analisar projeto em outro local
uv run python main.py ~/Projetos/meu-app

# Analisar projeto no diretório pai
uv run python main.py ..

# Analisar projeto com caminho absoluto
uv run python main.py /Users/usuario/workspace/projeto-xyz
```

### Exemplo 3: Ver ajuda e opções
```bash
uv run python main.py --help
```

**Saída**:
```
usage: main.py [-h] [path]

Analisador de código baseado em COCOMO II

positional arguments:
  path        Caminho do diretório a ser analisado (padrão: diretório atual)

options:
  -h, --help  show this help message and exit
```

## 2. Análise Integrada Git + COCOMO II (git_analyzer.py)

### Exemplo 1: Análise completa do repositório atual
```bash
uv run python git_analyzer.py
```

**Quando usar**: Para análise completa do repositório em que você está trabalhando.

### Exemplo 2: Analisar outro repositório
```bash
uv run python git_analyzer.py /caminho/para/repositorio
```

**Exemplo prático**:
```bash
# Analisar outro projeto
uv run python git_analyzer.py ~/Projetos/api-backend

# Analisar repositório clonado
uv run python git_analyzer.py /tmp/projeto-clonado

# Analisar múltiplos projetos (em sequência)
uv run python git_analyzer.py ~/Projetos/projeto1
uv run python git_analyzer.py ~/Projetos/projeto2
uv run python git_analyzer.py ~/Projetos/projeto3
```

### Exemplo 3: Exportar resultados para JSON
```bash
uv run python git_analyzer.py . --export resultado.json
```

**Exemplo prático**:
```bash
# Exportar com nome personalizado
uv run python git_analyzer.py . --export analise-sprint-15.json

# Exportar para outro diretório
uv run python git_analyzer.py . --export ~/Relatorios/analise-$(date +%Y%m%d).json

# Exportar de outro projeto
uv run python git_analyzer.py ~/Projetos/api --export api-analise.json
```

### Exemplo 4: Ver ajuda e opções
```bash
uv run python git_analyzer.py --help
```

**Saída**:
```
usage: git_analyzer.py [-h] [--export EXPORT] [path]

Análise integrada de código (COCOMO II) e commits Git

positional arguments:
  path                 Caminho do repositório a ser analisado (padrão:
                       diretório atual)

options:
  -h, --help           show this help message and exit
  --export, -e EXPORT  Exportar resultados para arquivo JSON
```

## 3. Casos de Uso Práticos

### Caso 1: Análise de Sprint
Analisar a evolução do projeto ao final de cada sprint:

```bash
# Sprint 1
uv run python git_analyzer.py . --export sprint-01.json

# Sprint 2
uv run python git_analyzer.py . --export sprint-02.json

# Sprint 3
uv run python git_analyzer.py . --export sprint-03.json
```

Depois você pode comparar os JSONs para ver a evolução das métricas.

### Caso 2: Análise de Múltiplos Projetos
Analisar vários projetos para comparação:

```bash
#!/bin/bash
# Script para analisar múltiplos projetos

PROJETOS=(
    "~/Projetos/frontend"
    "~/Projetos/backend"
    "~/Projetos/mobile"
)

for projeto in "${PROJETOS[@]}"; do
    nome=$(basename "$projeto")
    echo "Analisando $nome..."
    uv run python git_analyzer.py "$projeto" --export "analise-$nome.json"
done
```

### Caso 3: Análise Antes do Code Review
Antes de fazer um code review, analyze o projeto:

```bash
# Analisar branch atual
uv run python git_analyzer.py .

# Ver métricas de qualidade:
# - Score de produtividade
# - Eficiência de commits
# - Tamanho médio de commits
```

### Caso 4: Estimativa de Projeto Novo
Para estimar um projeto existente similar:

```bash
# Analisar projeto similar
uv run python main.py ~/Projetos/projeto-similar

# Usar métricas COCOMO II como baseline:
# - Tempo estimado
# - Pessoas necessárias
# - Custo estimado
```

### Caso 5: Monitoramento Contínuo
Criar um script para monitoramento diário:

```bash
#!/bin/bash
# monitorar.sh

DATA=$(date +%Y-%m-%d)
ARQUIVO="relatorios/analise-$DATA.json"

mkdir -p relatorios

uv run python git_analyzer.py . --export "$ARQUIVO"

echo "Análise gerada: $ARQUIVO"

# Opcional: enviar para S3, Slack, etc.
```

### Caso 6: Integração com CI/CD
Adicionar ao seu pipeline:

```yaml
# .github/workflows/analise-codigo.yml
name: Análise de Código

on:
  push:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0  # Importante para análise Git completa

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: pip install rich pathspec

      - name: Análise COCOMO II + Git
        run: python git_analyzer.py . --export analise.json

      - name: Upload resultados
        uses: actions/upload-artifact@v2
        with:
          name: analise-codigo
          path: analise.json
```

## 4. Dicas e Truques

### Dica 1: Análise Rápida vs Completa
```bash
# Análise rápida (apenas COCOMO II)
uv run python main.py

# Análise completa (COCOMO II + Git)
uv run python git_analyzer.py
```

### Dica 2: Caminhos Relativos vs Absolutos
```bash
# Caminho relativo (a partir do diretório atual)
uv run python main.py ../outro-projeto

# Caminho absoluto (caminho completo)
uv run python main.py /home/usuario/projetos/app

# Usando ~ para home directory
uv run python main.py ~/Projetos/aplicacao
```

### Dica 3: Verificar se é Repositório Git
```bash
# Verificar antes de executar git_analyzer.py
if [ -d ".git" ]; then
    uv run python git_analyzer.py .
else
    echo "Não é um repositório Git, usando análise básica..."
    uv run python main.py .
fi
```

### Dica 4: Processar JSON com jq
```bash
# Exportar e processar com jq
uv run python git_analyzer.py . --export analise.json

# Ver apenas score de produtividade
jq '.integrated.developer_productivity_score' analise.json

# Ver custo estimado
jq '.cocomo.cost_estimate_brl' analise.json

# Ver top 3 contribuidores
jq '.git.authors_commits | to_entries | sort_by(.value) | reverse | .[0:3]' analise.json
```

### Dica 5: Comparar Duas Análises
```bash
# Análise inicial
uv run python git_analyzer.py . --export inicial.json

# ... fazer mudanças no código ...

# Análise final
uv run python git_analyzer.py . --export final.json

# Comparar métricas
echo "Score inicial: $(jq '.integrated.developer_productivity_score' inicial.json)"
echo "Score final: $(jq '.integrated.developer_productivity_score' final.json)"
```

## 5. Troubleshooting

### Erro: "não é um repositório Git"
**Solução**: Use `main.py` ao invés de `git_analyzer.py`, ou inicialize um repositório Git:
```bash
git init
git add .
git commit -m "Initial commit"
uv run python git_analyzer.py .
```

### Erro: "Caminho não encontrado"
**Solução**: Verifique se o caminho existe e está correto:
```bash
# Verificar se o caminho existe
ls -la /caminho/para/projeto

# Usar caminho absoluto
uv run python main.py "$(pwd)/projeto"
```

### Aviso: "Nenhum arquivo de código encontrado"
**Solução**: O diretório não tem arquivos de código suportados. Verifique:
- Se há arquivos .py, .js, .java, etc.
- Se os arquivos não estão sendo excluídos (ex: dentro de node_modules)

### Performance lenta
**Solução**: Para projetos muito grandes:
- Garanta que pastas como `node_modules`, `.venv` estão sendo excluídas
- Use uma versão mais recente do Python
- Considere analisar apenas subdiretórios específicos

## 6. Scripts Úteis

### Script: Análise de Todos os Projetos
```bash
#!/bin/bash
# analisar-todos.sh

PROJETOS_DIR=~/Projetos
OUTPUT_DIR=./analises

mkdir -p "$OUTPUT_DIR"

for projeto in "$PROJETOS_DIR"/*; do
    if [ -d "$projeto/.git" ]; then
        nome=$(basename "$projeto")
        echo "Analisando: $nome"
        uv run python git_analyzer.py "$projeto" \
            --export "$OUTPUT_DIR/$nome-$(date +%Y%m%d).json"
    fi
done

echo "Análises completas em: $OUTPUT_DIR"
```

### Script: Relatório Semanal
```bash
#!/bin/bash
# relatorio-semanal.sh

SEMANA=$(date +%Y-W%V)
ARQUIVO="relatorios/semana-$SEMANA.json"

mkdir -p relatorios

uv run python git_analyzer.py . --export "$ARQUIVO"

# Extrair métricas principais
echo "=== Relatório da Semana $SEMANA ==="
echo "Commits: $(jq '.git.total_commits' "$ARQUIVO")"
echo "Score: $(jq '.integrated.developer_productivity_score' "$ARQUIVO")"
echo "Custo: R$ $(jq '.cocomo.cost_estimate_brl' "$ARQUIVO")"
```

### Script: Notificação Slack
```bash
#!/bin/bash
# notificar-slack.sh

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

uv run python git_analyzer.py . --export temp.json

SCORE=$(jq '.integrated.developer_productivity_score' temp.json)
COMMITS=$(jq '.git.total_commits' temp.json)

curl -X POST "$WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"📊 Análise COCOMO II\n Score: $SCORE\n Commits: $COMMITS\"}"

rm temp.json
```

## 7. Perguntas Frequentes

**P: Posso analisar projetos em outras linguagens além de Python?**
R: Sim! O analisador suporta 20+ linguagens incluindo JavaScript, TypeScript, Java, Go, etc.

**P: O git_analyzer.py funciona em repositórios sem commits?**
R: Não, é necessário pelo menos 1 commit. Use `main.py` para projetos sem Git.

**P: Posso analisar apenas um subdiretório?**
R: Sim, passe o caminho do subdiretório como argumento.

**P: Os resultados JSON são compatíveis com outras ferramentas?**
R: Sim, é JSON padrão e pode ser processado com jq, Python, JavaScript, etc.

**P: Como interpretar o score de produtividade?**
R: 75-100 = Excelente, 50-74 = Bom, <50 = Precisa melhorar.
