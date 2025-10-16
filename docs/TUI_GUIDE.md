# Guia de Uso - Interface TUI do Analisador COCOMO II

## Descrição

Interface TUI (Text User Interface) interativa para análise de múltiplos projetos usando a metodologia COCOMO II, com suporte opcional para integração com histórico Git.

## Características

- **Análise de Múltiplos Projetos**: Analise vários projetos em uma única execução
- **Configuração de Salário**: Defina o salário mensal para cálculo de custos personalizado
- **Dois Modos de Análise**:
  - COCOMO II (apenas análise de código)
  - COCOMO II + Git (análise integrada com histórico de commits)
- **Relatórios Individuais**: Gera relatórios JSON separados para cada projeto
- **Nomenclatura Automática**: Arquivos nomeados com nome do projeto e data/hora

## Instalação

```bash
# Instalar dependências
source .venv/bin/activate
uv pip install inquirer

# Ou usando pip
pip install inquirer
```

## Como Usar

### Método 1: Execução Direta

```bash
python tui_analyzer.py
```

### Método 2: Como Executável

```bash
./tui_analyzer.py
```

## Fluxo de Uso

### 1. Adicionar Projetos

A interface pedirá os caminhos dos projetos, um por vez:

```
Projeto 1 (ou Enter para finalizar): /caminho/para/projeto1
✓ Projeto adicionado: /caminho/para/projeto1

Projeto 2 (ou Enter para finalizar): /caminho/para/projeto2
✓ Projeto adicionado: /caminho/para/projeto2

Projeto 3 (ou Enter para finalizar): [Enter para finalizar]
```

**Dicas:**
- Use caminhos absolutos ou relativos
- Suporta `~` para diretório home
- Pressione Enter sem digitar nada para finalizar

### 2. Configurar Análise

Após adicionar os projetos, você configurará:

- **Salário Mensal**: Valor em R$ para cálculo de custos (padrão: R$ 15.000)
- **Tipo de Análise**:
  - `Apenas COCOMO II`: Analisa apenas o código
  - `COCOMO II + Git`: Inclui análise de commits (requer repositório Git)
- **Exportar JSON**: Gera relatórios em formato JSON

### 3. Visualizar Resultados

A interface exibirá:

- **Métricas de Código**: Linhas totais, por linguagem, arquivos, etc.
- **Resultados COCOMO II**: Esforço, tempo, pessoas necessárias, custos
- **Métricas Git** (se habilitado): Commits, autores, velocidade
- **Indicadores Integrados** (se habilitado): Produtividade, eficiência
- **Insights e Recomendações**: Análise inteligente dos resultados

## Relatórios Gerados

### Localização

Os relatórios são salvos em: `./reports/`

### Nomenclatura

Formato: `relatorio_{nome_projeto}_{data}_{hora}.json`

Exemplo: `relatorio_meu_projeto_20251014_153045.json`

### Estrutura do JSON

#### Relatório COCOMO II

```json
{
  "analysis_type": "cocomo",
  "project_name": "meu_projeto",
  "project_path": "/caminho/completo/projeto",
  "generated_at": "2025-10-14T15:30:45.123456",
  "metrics": {
    "total_lines": 5000,
    "code_lines": 3500,
    "comment_lines": 800,
    "blank_lines": 700,
    "files_count": 45,
    "languages": {
      "Python": 2500,
      "JavaScript": 1000
    }
  },
  "cocomo": {
    "kloc": 3.5,
    "effort_person_months": 8.5,
    "time_months": 4.2,
    "people_required": 2.0,
    "cost_estimate_brl": 127500.00,
    "complexity_level": "Baixa"
  }
}
```

#### Relatório Integrado (COCOMO II + Git)

```json
{
  "analysis_type": "integrated",
  "project_name": "meu_projeto",
  "project_path": "/caminho/completo/projeto",
  "generated_at": "2025-10-14T15:30:45.123456",
  "cocomo": { ... },
  "git": {
    "total_commits": 150,
    "total_authors": 3,
    "repository_age_days": 90,
    "commits_per_day": 1.67,
    "authors_commits": {
      "João Silva": 80,
      "Maria Santos": 50,
      "Pedro Oliveira": 20
    }
  },
  "integrated": {
    "lines_per_commit": 23.3,
    "actual_velocity": 38.9,
    "estimated_velocity": 35.2,
    "velocity_ratio": 1.10,
    "commit_efficiency": 65.5,
    "developer_productivity_score": 78.5
  }
}
```

## Exemplos de Uso

### Exemplo 1: Analisar Projeto Único com Salário Personalizado

```bash
./tui_analyzer.py

# Entrada:
Projeto 1: ~/meu-projeto
Projeto 2: [Enter]

Salário: 20000
Tipo de análise: COCOMO II + Git
Exportar JSON: Sim
```

### Exemplo 2: Analisar Múltiplos Projetos

```bash
./tui_analyzer.py

# Entrada:
Projeto 1: /var/www/site-principal
Projeto 2: /var/www/api-backend
Projeto 3: /var/www/painel-admin
Projeto 4: [Enter]

Salário: 15000
Tipo de análise: COCOMO II + Git
Exportar JSON: Sim
```

### Exemplo 3: Análise Rápida sem Git

```bash
./tui_analyzer.py

# Entrada:
Projeto 1: ./src
Projeto 2: [Enter]

Salário: 18000
Tipo de análise: Apenas COCOMO II
Exportar JSON: Não
```

## Validações

A interface valida automaticamente:

- **Caminhos**: Verifica se o diretório existe
- **Salário**: Deve ser número positivo
- **Duplicatas**: Impede adicionar o mesmo projeto duas vezes
- **Repositório Git**: Alerta se Git não disponível quando selecionado

## Tratamento de Erros

### Projeto sem Código

```
⚠️  Nenhum arquivo de código encontrado
```

O projeto é pulado e a análise continua com os próximos.

### Não é Repositório Git

```
⚠️  Não é um repositório Git. Usando apenas COCOMO II.
```

A análise continua apenas com COCOMO II.

### Erro na Análise

```
Erro ao analisar projeto: [detalhes do erro]
```

O erro é exibido e a análise continua com os próximos projetos.

## Dicas e Boas Práticas

1. **Organize seus projetos**: Mantenha os projetos em diretórios bem estruturados
2. **Use salário realista**: Configure o salário de acordo com sua região/realidade
3. **Ative Git quando possível**: A análise integrada oferece insights muito mais ricos
4. **Revise os relatórios**: Os arquivos JSON podem ser processados por outras ferramentas
5. **Backup dos relatórios**: O diretório `reports/` contém histórico valioso

## Arquivos Gerados

```
analiser-cocomo2/
├── tui_analyzer.py          # Interface TUI
├── main.py                  # Analisador COCOMO II
├── git_analyzer.py          # Analisador Git
└── reports/                 # Relatórios gerados
    ├── relatorio_projeto1_20251014_153045.json
    ├── relatorio_projeto2_20251014_153120.json
    └── ...
```

## Cancelamento

Pressione `Ctrl+C` a qualquer momento para cancelar a operação.

## Suporte

Para reportar problemas ou sugerir melhorias, consulte o arquivo README.md principal do projeto.

## Próximos Passos

Após gerar os relatórios, você pode:

1. Analisar os arquivos JSON para comparar projetos
2. Importar os dados em planilhas ou ferramentas de BI
3. Criar scripts de processamento batch
4. Integrar com sistemas de gestão de projetos
