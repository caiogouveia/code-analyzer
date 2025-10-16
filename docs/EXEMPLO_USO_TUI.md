# Exemplo Prático de Uso da Interface TUI

## Cenário: Analisar 3 Projetos

Vamos analisar três projetos diferentes com um salário customizado de R$ 18.000,00.

### Passo 1: Iniciar a Interface

```bash
./run_tui.sh
```

### Passo 2: Adicionar os Projetos

A interface irá solicitar os caminhos dos projetos:

```
┌────────────────────────────────────────────────────────────┐
│         ANALISADOR COCOMO II                               │
│         Análise de Projetos de Software                    │
└────────────────────────────────────────────────────────────┘

Digite os caminhos dos projetos para análise.
Deixe em branco e pressione Enter quando terminar.

[?] Projeto 1 (ou Enter para finalizar): /var/www/ecommerce-api
✓ Projeto adicionado: /var/www/ecommerce-api

[?] Projeto 2 (ou Enter para finalizar): /var/www/admin-dashboard
✓ Projeto adicionado: /var/www/admin-dashboard

[?] Projeto 3 (ou Enter para finalizar): ~/projetos/mobile-app
✓ Projeto adicionado: /home/user/projetos/mobile-app

[?] Projeto 4 (ou Enter para finalizar): [ENTER]

Total de projetos: 3
```

### Passo 3: Configurar a Análise

```
Configurações da Análise

[?] Salário mensal do desenvolvedor (R$): 18000

[?] Tipo de análise:
   Apenas COCOMO II (código)
 > COCOMO II + Git (integrado)

[?] Exportar relatórios em JSON? (Y/n): Y

Iniciando análise dos projetos...
```

### Passo 4: Visualizar os Resultados

A interface irá processar cada projeto e exibir:

```
================================================================================

PROJETO 1/3
================================================================================

Analisando: /var/www/ecommerce-api

┌────────────────────────────────────────────────────────────┐
│         ANÁLISE INTEGRADA: COCOMO II + GIT                 │
└────────────────────────────────────────────────────────────┘

📊 Resumo COCOMO II
┌────────────────────────────┬────────────────┐
│ Métrica                    │          Valor │
├────────────────────────────┼────────────────┤
│ KLOC                       │          12.50 │
│ Complexidade               │          Baixa │
│ Esforço (pessoa-mês)       │          28.45 │
│ Tempo (meses)              │           7.82 │
│ Pessoas Necessárias        │           3.64 │
│ Custo Estimado             │ R$ 512,100.00  │
└────────────────────────────┴────────────────┘

📈 Métricas do Repositório Git
┌────────────────────────────┬────────────────┐
│ Métrica                    │          Valor │
├────────────────────────────┼────────────────┤
│ Total de Commits           │            245 │
│ Total de Autores           │              4 │
│ Idade do Repositório (dias)│            180 │
│ Commits por Dia            │           1.36 │
└────────────────────────────┴────────────────┘

👥 Top 10 Contribuidores
┌────────────────────────────┬─────────┬────────────┐
│ Autor                      │ Commits │ % do Total │
├────────────────────────────┼─────────┼────────────┤
│ João Silva                 │     150 │      61.2% │
│ Maria Santos               │      65 │      26.5% │
│ Pedro Costa                │      20 │       8.2% │
│ Ana Oliveira               │      10 │       4.1% │
└────────────────────────────┴─────────┴────────────┘

🎯 Indicadores Integrados
┌────────────────────────────────────────┬────────────┐
│ Indicador                              │      Valor │
├────────────────────────────────────────┼────────────┤
│ Linhas por Commit                      │       51.0 │
│ Commits p/ Recriar Codebase            │        245 │
│ Velocidade Real (linhas/dia)           │       69.4 │
│ Velocidade COCOMO (linhas/dia)         │       58.2 │
│ Razão Velocidade (real/estimado)       │      1.19x │
│ Eficiência de Commit                   │      62.5% │
└────────────────────────────────────────┴────────────┘

⭐ Score de Produtividade dos Desenvolvedores
┌────────────────────────────────────────────────────────────┐
│                           82.5/100                         │
│                                                            │
│ Score baseado em velocidade, eficiência e complexidade    │
└────────────────────────────────────────────────────────────┘

💡 Insights e Recomendações
┌────────────────────────────────────────────────────────────┐
│ 🚀 Velocidade acima do esperado - Equipe muito produtiva! │
│ ✓ Alta eficiência de commits - Baixo retrabalho           │
│ ✓ Commits pequenos e incrementais - Boa prática           │
│ ✓ Alta frequência de commits - Desenvolvimento ativo      │
│ 🌟 Excelente produtividade da equipe!                      │
└────────────────────────────────────────────────────────────┘

✓ Relatório exportado: ./reports/relatorio_ecommerce-api_20251014_103045.json

================================================================================
```

## Arquivos Gerados

Após a análise, você terá os seguintes relatórios:

```
reports/
├── relatorio_ecommerce-api_20251014_103045.json
├── relatorio_admin-dashboard_20251014_103128.json
└── relatorio_mobile-app_20251014_103210.json
```

## Estrutura de um Relatório JSON

```json
{
  "analysis_type": "integrated",
  "project_name": "ecommerce-api",
  "project_path": "/var/www/ecommerce-api",
  "generated_at": "2025-10-14T10:30:45.123456",
  "cocomo": {
    "kloc": 12.5,
    "effort_person_months": 28.45,
    "time_months": 7.82,
    "people_required": 3.64,
    "maintenance_people": 0.66,
    "expansion_people": 1.09,
    "productivity": 439.4,
    "cost_estimate_brl": 512100.0,
    "complexity_level": "Baixa"
  },
  "git": {
    "total_commits": 245,
    "total_authors": 4,
    "authors_commits": {
      "João Silva": 150,
      "Maria Santos": 65,
      "Pedro Costa": 20,
      "Ana Oliveira": 10
    },
    "total_insertions": 18500,
    "total_deletions": 6000,
    "avg_changes_per_commit": 100.0,
    "avg_files_per_commit": 3.2,
    "commits_per_day": 1.36,
    "first_commit_date": "2024-04-17T09:00:00",
    "last_commit_date": "2025-10-14T10:00:00",
    "repository_age_days": 180
  },
  "integrated": {
    "cocomo_kloc": 12.5,
    "cocomo_effort": 28.45,
    "cocomo_time_months": 7.82,
    "cocomo_people": 3.64,
    "cocomo_cost_brl": 512100.0,
    "total_commits": 245,
    "avg_changes_per_commit": 100.0,
    "commits_per_month": 40.8,
    "lines_per_commit": 51.0,
    "commits_needed_to_rebuild": 245,
    "actual_velocity": 69.4,
    "estimated_velocity": 58.2,
    "velocity_ratio": 1.19,
    "commit_efficiency": 62.5,
    "change_percentage_per_commit": 0.8,
    "developer_productivity_score": 82.5
  }
}
```

## Usando os Dados

### Comparar Projetos em Planilha

Você pode importar os arquivos JSON em uma planilha:

| Projeto          | KLOC | Esforço (PM) | Tempo (M) | Custo (R$)   | Produtividade |
|------------------|------|--------------|-----------|--------------|---------------|
| ecommerce-api    | 12.5 | 28.45        | 7.82      | 512,100.00   | 82.5          |
| admin-dashboard  | 8.2  | 18.32        | 6.45      | 329,760.00   | 75.3          |
| mobile-app       | 15.8 | 36.24        | 8.95      | 652,320.00   | 68.9          |

### Script Python para Consolidar Relatórios

```python
import json
from pathlib import Path

reports_dir = Path("./reports")
projects = []

for json_file in reports_dir.glob("*.json"):
    with open(json_file) as f:
        data = json.load(f)
        projects.append({
            "nome": data["project_name"],
            "kloc": data["cocomo"]["kloc"],
            "custo": data["cocomo"]["cost_estimate_brl"],
            "score": data.get("integrated", {}).get("developer_productivity_score", 0)
        })

# Ordenar por custo
projects.sort(key=lambda x: x["custo"], reverse=True)

print("Projetos por custo:")
for p in projects:
    print(f"{p['nome']}: R$ {p['custo']:,.2f} - Score: {p['score']:.1f}")
```

## Dicas Avançadas

### 1. Análise Periódica

Crie um script cron para analisar projetos regularmente:

```bash
#!/bin/bash
# analise_mensal.sh

cd /path/to/analiser-cocomo2
./run_tui.sh <<EOF
/var/www/projeto1
/var/www/projeto2
/var/www/projeto3

18000
COCOMO II + Git (integrado)
Y
EOF
```

### 2. Comparação de Sprints

Analise o mesmo projeto em diferentes datas:

```bash
# Sprint 1 (Jan)
./run_tui.sh # Gera relatorio_projeto_20250115_*.json

# Sprint 2 (Fev)
./run_tui.sh # Gera relatorio_projeto_20250215_*.json

# Compare os scores de produtividade
```

### 3. Análise de Portfólio

Analise todos os projetos da empresa:

```bash
# projects.txt
/srv/app1
/srv/app2
/srv/app3
...

# Use xargs ou loop para processar
```

## Cancelamento

Para cancelar a qualquer momento:
- Pressione `Ctrl+C`

```
^C
Operação cancelada pelo usuário.
```

## Troubleshooting

### Caminho não encontrado

```
[?] Projeto 1: /path/invalido
ValidationError: Caminho '/path/invalido' não encontrado
```

**Solução**: Verifique se o caminho existe e está correto.

### Não é repositório Git

```
⚠️  Não é um repositório Git. Usando apenas COCOMO II.
```

**Solução**: Escolha "Apenas COCOMO II" ou inicialize um repositório Git.

### Nenhum arquivo encontrado

```
⚠️  Nenhum arquivo de código encontrado
```

**Solução**: Verifique se o diretório contém arquivos de código nas linguagens suportadas.
