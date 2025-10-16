# Analisador COCOMO II

Analisador de código baseado na metodologia COCOMO II (Constructive Cost Model) que calcula complexidade, esforço, tempo e recursos necessários para desenvolvimento de software.

## Scripts Disponíveis

### 1. tui_analyzer.py - Interface TUI Interativa (RECOMENDADO)
Interface TUI (Text User Interface) interativa para análise de múltiplos projetos com configuração personalizada de salário e geração automática de relatórios.

**Características**:
- Análise de múltiplos projetos em uma única execução
- Configuração de salário personalizada
- Geração automática de relatórios JSON com nome do projeto e data
- Suporte para análise COCOMO II simples ou integrada com Git
- Interface amigável com validação de entrada

### 2. main.py - Análise COCOMO II
Analisador de código que calcula métricas baseadas em COCOMO II.

### 3. git_analyzer.py - Análise Integrada Git + COCOMO II
Análise completa que cruza dados COCOMO II com histórico de commits Git.

## Funcionalidades

### 🤖 Insights com Inteligência Artificial (NOVO!)
- **Análise profunda com IA da OpenAI**:
  - Avaliação do valor do código e qualidade
  - Comparação com métricas de mercado
  - Estimativa de valor de mercado do projeto
  - Recomendações estratégicas (curto, médio e longo prazo)
  - Indicadores chave (ROI, Time to Market, Risco Técnico)
  - Oportunidades de monetização, expansão e otimização
- Disponível via:
  - Interface TUI (aba "🤖 Insights IA")
  - Linha de comando (`--ai-insights` flag)
  - Uso programático (módulo `ai_insights.py`)

📚 **[Ver documentação completa de Insights IA →](AI_INSIGHTS.md)**

### Análise COCOMO II (main.py)
- Análise recursiva de diretórios e subdiretórios
- Exclusão automática de arquivos gerados por frameworks
- Exclusão de pastas de bibliotecas (.venv, node_modules, vendor)
- Suporte a múltiplas linguagens de programação
- Cálculo de métricas COCOMO II:
  - Complexidade do código
  - Tempo para recriar a codebase
  - Quantidade de desenvolvedores necessários
  - Equipe para manutenção
  - Equipe para expansão
  - Produtividade (LOC/pessoa-mês)
  - Estimativa de custo em BRL
- Saída formatada e elegante com Rich

### Análise Integrada Git (git_analyzer.py)
- **Métricas Git**:
  - Total de commits e autores
  - Inserções e deleções
  - Commits por dia/mês
  - Ranking de contribuidores

- **Indicadores de Commits**:
  - Linhas por commit
  - Commits necessários para recriar codebase
  - Percentual médio de mudança por commit
  - Eficiência de commit (código útil vs retrabalho)

- **Análise de Velocidade**:
  - Velocidade real vs estimada COCOMO
  - Razão de velocidade (real/estimado)
  - Score de produtividade dos desenvolvedores (0-100)

- **Insights Automáticos**:
  - Avaliação de velocidade da equipe
  - Análise de eficiência de commits
  - Recomendações de tamanho de commits
  - Avaliação geral de produtividade

- **Exportação**:
  - Exportar resultados em JSON

## Metodologia COCOMO II

O script utiliza a metodologia COCOMO II para estimar:

### Níveis de Complexidade
- **Orgânico (Baixa)**: Projetos até 50 KLOC
- **Semi-Destacado (Média)**: Projetos entre 50-300 KLOC
- **Embarcado (Alta)**: Projetos acima de 300 KLOC

### Fórmulas Utilizadas
- **Esforço**: E = a × (KLOC)^b pessoa-meses
- **Tempo**: T = c × (E)^d meses
- **Pessoas**: P = E / T

## Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd analiser-cocomo2

# Instale as dependências usando uv
uv sync

# Ou usando pip
pip install -e .
```

## Uso

### Interface TUI Interativa (Recomendado)

#### Método 1: Script auxiliar
```bash
./run_tui.sh
```

#### Método 2: Execução direta
```bash
uv run python tui_analyzer.py
# ou
source .venv/bin/activate && python tui_analyzer.py
```

**Fluxo de uso**:
1. Digite os caminhos dos projetos (um por vez)
2. Pressione Enter sem digitar nada para finalizar a lista de projetos
3. Configure o salário mensal (em R$)
4. Escolha o tipo de análise (COCOMO II ou Integrado)
5. Decida se deseja exportar relatórios JSON
6. A análise será executada para todos os projetos
7. Relatórios individuais serão gerados em `./reports/` com formato: `relatorio_{projeto}_{data}_{hora}.json`

**Veja o guia completo**: [TUI_GUIDE.md](TUI_GUIDE.md)

### Análise COCOMO II Básica (Linha de Comando)

#### Análise do diretório atual
```bash
uv run python main.py
```

#### Análise de um diretório específico
```bash
uv run python main.py /caminho/para/projeto
```

#### Análise com Insights de IA (NOVO!)
```bash
# Configure primeiro sua chave da OpenAI
export OPENAI_API_KEY="sk-proj-..."

# Execute com insights de IA
uv run python main.py --ai-insights

# Ou para um projeto específico
uv run python main.py /caminho/para/projeto --ai-insights
```

📚 **[Ver guia completo de Insights IA →](AI_INSIGHTS.md)**

### Análise Integrada Git + COCOMO II (Linha de Comando)

#### Análise completa do diretório atual
```bash
uv run python git_analyzer.py
```

#### Análise de um repositório específico
```bash
uv run python git_analyzer.py /caminho/para/repositorio
```

#### Análise com exportação JSON
```bash
uv run python git_analyzer.py . --export resultados.json
```

#### Ajuda e opções
```bash
uv run python git_analyzer.py --help
```

## Exemplos de Saída

### Análise COCOMO II (main.py)

O script gera relatórios com:

1. **Métricas de Código**
   - Total de arquivos
   - Total de linhas
   - Linhas de código
   - Linhas de comentários
   - Linhas em branco

2. **Distribuição por Linguagem**
   - Quantidade de linhas por linguagem
   - Porcentagem de cada linguagem

3. **Resultados COCOMO II**
   - Nível de complexidade
   - Esforço total (pessoa-mês)
   - Tempo de desenvolvimento
   - Pessoas necessárias
   - Equipe de manutenção
   - Equipe de expansão
   - Produtividade

4. **Estimativa de Custo**
   - Custo total estimado em BRL
   - Baseado em R$15.000/pessoa-mês

5. **Insights e Recomendações**
   - Análise automática dos resultados
   - Sugestões baseadas nas métricas

### Análise Integrada Git (git_analyzer.py)

O script gera relatórios expandidos com:

1. **Resumo COCOMO II**
   - KLOC, complexidade, esforço, tempo, custo

2. **Métricas do Repositório Git**
   - Total de commits, autores
   - Idade do repositório
   - Commits por dia
   - Inserções e deleções totais
   - Médias por commit

3. **Top Contribuidores**
   - Ranking dos 10 principais autores
   - Número de commits e porcentagem

4. **Indicadores Integrados**
   - Linhas por commit
   - Commits necessários para recriar
   - Commits por mês
   - Velocidade real vs estimada
   - Razão de velocidade
   - Eficiência de commit
   - % média de mudança por commit

5. **Score de Produtividade**
   - Pontuação de 0-100
   - Baseado em velocidade, eficiência e complexidade

6. **Insights Personalizados**
   - Avaliação de velocidade
   - Análise de eficiência
   - Recomendações de tamanho de commits
   - Frequência de commits
   - Avaliação geral

## Indicadores Calculados

### Linhas por Commit
Total de linhas de código dividido pelo número de commits.

**Interpretação**:
- < 100 linhas: Commits pequenos e incrementais (ideal)
- 100-500 linhas: Commits de tamanho moderado
- > 500 linhas: Commits grandes (considere dividir)

### Commits Necessários para Recriar
Estimativa de quantos commits seriam necessários para recriar a codebase.

### Percentual Médio de Mudança por Commit
Porcentagem média do código que é modificada em cada commit.

**Interpretação**:
- < 1%: Mudanças incrementais pequenas (ótimo)
- 1-5%: Mudanças moderadas (bom)
- > 5%: Mudanças grandes (avaliar necessidade)

### Eficiência de Commit
Relação entre código útil e churn (retrabalho).

**Cálculo**: (Linhas atuais / Total de mudanças) × 100

**Interpretação**:
- > 50%: Alta eficiência, baixo retrabalho
- 30-50%: Eficiência moderada
- < 30%: Baixa eficiência, muito retrabalho

### Razão de Velocidade
Velocidade real dividida pela velocidade estimada pelo COCOMO II.

**Interpretação**:
- > 1.2: Equipe muito produtiva
- 0.8-1.2: Velocidade dentro do esperado
- < 0.8: Velocidade abaixo do esperado

### Score de Produtividade
Pontuação composta de 0-100 baseada em:
- Velocidade de desenvolvimento (até 25 pontos)
- Eficiência de commits (até 15 pontos)
- Complexidade do projeto (até 10 pontos)
- Base de 50 pontos

**Interpretação**:
- 75-100: Excelente produtividade
- 50-74: Boa produtividade
- < 50: Oportunidade de melhoria

## Linguagens Suportadas

- Python
- JavaScript/TypeScript
- Java
- C/C++/C#
- Go
- Rust
- PHP
- Ruby
- Swift
- Kotlin
- Scala
- R
- Shell
- SQL
- HTML/CSS
- Vue
- Dart

## Diretórios e Arquivos Excluídos

O analisador exclui automaticamente:

### Diretórios
- node_modules
- .venv, venv, env
- vendor
- __pycache__
- .git, .svn, .hg
- dist, build, target, out
- .idea, .vscode, .vs
- bin, obj
- .gradle, .next
- coverage, .nyc_output
- .pytest_cache, .mypy_cache
- .tox, .eggs

### Arquivos
- Arquivos compilados (.pyc, .class, .jar, .o)
- Arquivos minificados (.min.js, .min.css)
- Arquivos de lock (package-lock.json, yarn.lock, etc.)
- Bibliotecas compiladas (.so, .dll, .dylib)

## Exportação JSON

O script git_analyzer.py pode exportar resultados em JSON com a flag `--export`:

```bash
uv run python git_analyzer.py . --export resultados.json
```

Estrutura do JSON:
```json
{
  "cocomo": {
    "kloc": 0.74,
    "effort_person_months": 1.75,
    "time_months": 3.09,
    "people_required": 0.57,
    "cost_estimate_brl": 26204.70,
    "complexity_level": "Baixa"
  },
  "git": {
    "total_commits": 100,
    "total_authors": 5,
    "authors_commits": {...},
    "total_insertions": 10000,
    "total_deletions": 2000,
    ...
  },
  "integrated": {
    "lines_per_commit": 100.0,
    "commits_needed_to_rebuild": 74,
    "velocity_ratio": 1.2,
    "commit_efficiency": 61.1,
    "change_percentage_per_commit": 1.5,
    "developer_productivity_score": 84.2
  },
  "generated_at": "2025-10-13T18:19:23.117434"
}
```

## Dependências

- Python >= 3.13
- rich >= 13.7.0
- pathspec >= 0.12.1
- inquirer >= 3.1.3 (para interface TUI)
- textual >= 0.47.0 (para interface TUI avançada)
- reportlab >= 4.0.0 (para geração de PDF)
- matplotlib >= 3.8.0 (para gráficos)
- openai >= 1.0.0 (para insights com IA - opcional)

## Casos de Uso

### 1. Estimativa de Projeto
Use o `main.py` para estimar custo, tempo e recursos necessários para um projeto novo ou existente.

### 2. Acompanhamento de Progresso
Use o `git_analyzer.py` regularmente para:
- Monitorar velocidade da equipe
- Avaliar eficiência de commits
- Identificar gargalos de produtividade

### 3. Code Review
Use os indicadores para:
- Identificar commits muito grandes
- Avaliar qualidade do código (eficiência)
- Comparar produtividade entre sprints

### 4. Planejamento de Sprint
Use as métricas para:
- Estimar capacidade da equipe
- Prever tempo de entrega
- Alocar recursos adequadamente

### 5. Relatórios para Stakeholders
Exporte os resultados em JSON para:
- Criar dashboards personalizados
- Integrar com ferramentas de BI
- Gerar relatórios periódicos

### 6. 🤖 Análise Estratégica com IA (NOVO!)
Use os insights de IA para:
- Avaliar o valor de mercado do projeto
- Obter recomendações estratégicas personalizadas
- Identificar oportunidades de monetização e expansão
- Comparar com benchmarks da indústria
- Avaliar riscos técnicos e ROI

📚 **[Ver guia completo de Insights IA →](AI_INSIGHTS.md)**

## Limitações

- A análise Git requer que o diretório seja um repositório Git válido
- Estimativas COCOMO II são baseadas em modelos estatísticos e podem variar
- Detecção de comentários é simplificada e pode não capturar todos os casos
- Valores de salário são médias e podem variar por região e senioridade

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abrir um Pull Request

## Licença

MIT License

## Autor

Desenvolvido para análise de projetos de software usando metodologia COCOMO II integrada com análise de commits Git.

## Referências

- [COCOMO II Model Definition Manual](http://csse.usc.edu/csse/research/COCOMOII/cocomo_main.html)
- Barry W. Boehm et al., "Software Cost Estimation with COCOMO II"
- [Git Documentation](https://git-scm.com/doc)
