# Analisador COCOMO II

Analisador de código baseado na metodologia COCOMO II (Constructive Cost Model) que calcula complexidade, esforço, tempo e recursos necessários para desenvolvimento de software.

## Funcionalidades

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
  - Estimativa de custo
- Saída formatada e elegante com Rich

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

### Análise do diretório atual
```bash
python main.py
```

### Análise de um diretório específico
```bash
python main.py /caminho/para/projeto
```

### Usando com ambiente virtual
```bash
# Ative o ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Execute o script
python main.py
```

## Exemplos de Saída

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
   - Custo total estimado em USD

5. **Insights e Recomendações**
   - Análise automática dos resultados
   - Sugestões baseadas nas métricas

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

## Dependências

- Python >= 3.13
- rich >= 13.7.0
- pathspec >= 0.12.1

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

Desenvolvido para análise de projetos de software usando metodologia COCOMO II.

## Referências

- [COCOMO II Model Definition Manual](http://csse.usc.edu/csse/research/COCOMOII/cocomo_main.html)
- Barry W. Boehm et al., "Software Cost Estimation with COCOMO II"
