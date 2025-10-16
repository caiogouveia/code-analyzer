# 🤖 Insights com Inteligência Artificial

## Visão Geral

O Analisador COCOMO II agora inclui integração com a API da OpenAI para gerar insights inteligentes e acionáveis sobre o valor do código e métricas de mercado relevantes. Esta funcionalidade analisa profundamente as métricas do seu projeto e fornece recomendações estratégicas baseadas em padrões da indústria de software.

## O que os Insights de IA fornecem?

Os insights gerados pela IA incluem:

### 💎 Valor do Código
- **Avaliação Geral**: Análise completa do valor e qualidade do código
- **Pontos Fortes**: Identificação dos aspectos mais positivos do projeto
- **Áreas de Melhoria**: Recomendações de melhorias prioritárias
- **Valor de Mercado**: Estimativa do valor do projeto no mercado

### 📊 Métricas de Mercado
- **Comparação com Indústria**: Como seu projeto se compara com padrões do mercado
- **Maturidade do Projeto**: Nível de maturidade técnica e organizacional
- **Qualidade do Código**: Avaliação baseada em métricas objetivas
- **Velocidade de Desenvolvimento**: Análise de produtividade comparativa
- **Custo-Benefício**: Avaliação do retorno sobre investimento

### 🎯 Recomendações Estratégicas
- **Curto Prazo (1-3 meses)**: Ações imediatas e impactantes
- **Médio Prazo (3-6 meses)**: Melhorias estruturais
- **Longo Prazo (6+ meses)**: Investimentos estratégicos

### 📈 Indicadores Chave
- **ROI Estimado**: Retorno sobre investimento
- **Time to Market**: Tempo de chegada ao mercado
- **Risco Técnico**: Avaliação de riscos
- **Escalabilidade**: Potencial de crescimento
- **Sustentabilidade**: Viabilidade de longo prazo

### 💡 Oportunidades
- **Monetização**: Formas de gerar receita
- **Expansão**: Áreas de crescimento
- **Otimização**: Melhorias de maior impacto

## Pré-requisitos

### 1. Chave de API da OpenAI

Você precisa de uma chave de API válida da OpenAI. Para obtê-la:

1. Acesse [platform.openai.com](https://platform.openai.com/)
2. Crie uma conta ou faça login
3. Navegue até [API Keys](https://platform.openai.com/api-keys)
4. Crie uma nova chave de API (Secret Key)
5. Copie a chave gerada (você não poderá vê-la novamente!)

### 2. Configurar a Variável de Ambiente

Configure a variável de ambiente `OPENAI_API_KEY` com sua chave:

**Linux/macOS:**
```bash
export OPENAI_API_KEY="sk-proj-..."
```

Para tornar permanente, adicione ao seu `~/.bashrc`, `~/.zshrc` ou `~/.profile`:
```bash
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-proj-..."
```

Para tornar permanente:
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-...', 'User')
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-proj-...
```

### 3. Instalar Dependências

Certifique-se de que todas as dependências estão instaladas:

```bash
pip install -e .
```

ou

```bash
uv pip install -e .
```

## Como Usar

### Opção 1: Interface TUI (Recomendada)

Execute a interface TUI:

```bash
python tui_analyzer.py
```

ou

```bash
./run_tui.sh
```

**Passos:**

1. Na tela inicial, escolha "Nova Análise" ou "Analisar Diretório Atual"
2. Aguarde a análise do código e Git ser concluída
3. Navegue até a aba "🤖 Insights IA" (use Tab ou clique)
4. Clique no botão "🤖 Gerar Insights com IA" ou pressione `i`
5. Aguarde enquanto a IA processa (geralmente 10-30 segundos)
6. Visualize os insights detalhados!

**Atalhos de Teclado:**
- `i` - Gerar insights de IA
- `Tab` - Navegar entre abas
- `q` - Sair
- `n` - Nova análise

### Opção 2: Linha de Comando (CLI)

Para análise básica COCOMO II com insights de IA:

```bash
python main.py --ai-insights
```

ou

```bash
python main.py /caminho/do/projeto --ai-insights
```

Para análise integrada COCOMO + Git com insights de IA:

```bash
python git_analyzer.py /caminho/do/repositorio
# Depois use a interface TUI ou programe manualmente
```

### Opção 3: Uso Programático

Você pode usar a funcionalidade de insights de IA em seus próprios scripts:

```python
from pathlib import Path
from main import CodeAnalyzer
from insights import build_ai_insights

# Analisar código
analyzer = CodeAnalyzer(Path("./meu-projeto"))
analyzer.analyze_directory()
cocomo_results = analyzer.calculate_cocomo2()

# Gerar insights de IA
insights_text = build_ai_insights(
    cocomo=cocomo_results,
    code_metrics=analyzer.metrics,
    project_name="Meu Projeto",
    project_description="Descrição opcional do projeto"
)

print(insights_text)
```

Com análise Git integrada:

```python
from pathlib import Path
from git_analyzer import IntegratedAnalyzer
from insights import build_ai_insights

# Análise integrada
analyzer = IntegratedAnalyzer(Path("./meu-repositorio"))
cocomo, git, integrated = analyzer.analyze()

# Gerar insights de IA
insights_text = build_ai_insights(
    cocomo=cocomo,
    git=git,
    integrated=integrated,
    project_name="Meu Repositório"
)

print(insights_text)
```

## Custos

A funcionalidade utiliza o modelo **GPT-4o-mini** da OpenAI, que é otimizado para custo-benefício:

- **Custo aproximado por análise**: $0.01 - $0.05 USD
- **Tokens típicos utilizados**: 1000-2000 tokens
- **Preço (out/2024)**:
  - Input: $0.150 / 1M tokens
  - Output: $0.600 / 1M tokens

💡 **Dica**: Uma análise típica custa menos de 5 centavos de dólar!

## Solução de Problemas

### Erro: "API Key da OpenAI não fornecida"

**Solução**: Configure a variável de ambiente `OPENAI_API_KEY`:
```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

### Erro: "Rate limit exceeded"

**Causa**: Você excedeu o limite de requisições da OpenAI.

**Solução**:
- Aguarde alguns minutos antes de tentar novamente
- Verifique seus limites em [platform.openai.com/account/limits](https://platform.openai.com/account/limits)
- Considere fazer upgrade do seu plano OpenAI

### Erro: "Insufficient quota"

**Causa**: Seu crédito/saldo da OpenAI acabou.

**Solução**:
- Adicione créditos em [platform.openai.com/account/billing](https://platform.openai.com/account/billing)
- Configure um método de pagamento

### Timeout ou lentidão

**Causa**: Conexão lenta ou sobrecarga da API.

**Solução**:
- Verifique sua conexão com a internet
- Tente novamente em alguns minutos
- Verifique o status da API em [status.openai.com](https://status.openai.com)

### Insights genéricos ou pouco úteis

**Causa**: Projeto muito pequeno ou com poucos dados.

**Solução**:
- Certifique-se de analisar um projeto com código substancial (>1000 linhas)
- Use análise integrada com Git para obter métricas mais ricas
- Forneça uma descrição do projeto para contexto adicional

## Privacidade e Segurança

⚠️ **IMPORTANTE**: Ao usar esta funcionalidade, as seguintes informações são enviadas para a API da OpenAI:

- Métricas numéricas do código (linhas, arquivos, complexidade)
- Estatísticas Git (commits, autores, frequência)
- Nome do projeto
- Descrição do projeto (se fornecida)

**NÃO são enviados**:
- Código-fonte
- Comentários
- Nomes de variáveis ou funções
- Credenciais ou segredos
- Conteúdo de arquivos

A OpenAI pode usar os dados enviados de acordo com sua [política de privacidade](https://openai.com/policies/privacy-policy). Para projetos sensíveis, considere:

1. Revisar as métricas antes de enviar
2. Usar nomes genéricos para o projeto
3. Não fornecer descrições detalhadas
4. Avaliar se os insights justificam o compartilhamento de métricas

## Exemplos de Insights Gerados

### Exemplo 1: Projeto de Alta Complexidade

```
💎 VALOR DO CÓDIGO

Este projeto demonstra alta complexidade técnica com 50 KLOC e uma estrutura
bem organizada em Python. A qualidade do código indica maturidade técnica.

✓ Pontos Fortes:
  • Alta cobertura de comentários (15%), indicando documentação adequada
  • Uso de múltiplas linguagens (Python, TypeScript) mostra stack moderna
  • Histórico Git ativo com 500+ commits demonstra desenvolvimento contínuo
  • Baixo churn (alta eficiência de commits) indica código estável

⚡ Áreas de Melhoria:
  • Commits muito grandes (5% de mudança média) - considere commits menores
  • Velocidade abaixo do estimado - pode haver impedimentos técnicos
  • Considere aumentar automação de testes baseado na complexidade

💰 Valor de Mercado: R$ 450.000 - R$ 750.000 baseado em esforço de desenvolvimento

📊 MÉTRICAS DE MERCADO

Comparação com Indústria:
O projeto está acima da média em termos de qualidade de código e documentação...
```

### Exemplo 2: Startup MVP

```
💎 VALOR DO CÓDIGO

Projeto em fase inicial (5 KLOC) com desenvolvimento ágil e foco em MVP.
Demonstra velocidade de execução apropriada para startup.

✓ Pontos Fortes:
  • Alta velocidade de commits - desenvolvimento ágil
  • Stack moderna (JavaScript/TypeScript)
  • Tamanho adequado para MVP - scope bem definido

💡 OPORTUNIDADES

Monetização:
  • SaaS subscription model com tier gratuito limitado
  • Freemium com features premium pagas
  • API as a Service para desenvolvedores

Expansão:
  • Integração com plataformas existentes (Slack, Teams)
  • Marketplace de plugins/extensões
  • Versão mobile/PWA
```

## Integração com CI/CD

Você pode integrar a geração de insights em seus pipelines de CI/CD:

### GitHub Actions

```yaml
name: COCOMO Analysis with AI

on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -e .

      - name: Run COCOMO Analysis with AI Insights
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python main.py --ai-insights > analysis_report.txt

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: cocomo-report
          path: analysis_report.txt
```

### GitLab CI

```yaml
cocomo-analysis:
  image: python:3.13
  script:
    - pip install -e .
    - python main.py --ai-insights > analysis_report.txt
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY
  artifacts:
    paths:
      - analysis_report.txt
```

## Suporte e Contribuições

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/analiser-cocomo2/issues)
- **Discussões**: Use a aba de Discussions no GitHub
- **Pull Requests**: Contribuições são bem-vindas!

## Licença

Esta funcionalidade está incluída no projeto sob a mesma licença do analisador COCOMO II.

---

**Desenvolvido com ❤️ para ajudar desenvolvedores a entender melhor seus projetos**
