# Analisador COCOMO II

Analisador de c�digo baseado na metodologia COCOMO II (Constructive Cost Model) que calcula complexidade, esfor�o, tempo e recursos necess�rios para desenvolvimento de software.

## Funcionalidades

- An�lise recursiva de diret�rios e subdiret�rios
- Exclus�o autom�tica de arquivos gerados por frameworks
- Exclus�o de pastas de bibliotecas (.venv, node_modules, vendor)
- Suporte a m�ltiplas linguagens de programa��o
- C�lculo de m�tricas COCOMO II:
  - Complexidade do c�digo
  - Tempo para recriar a codebase
  - Quantidade de desenvolvedores necess�rios
  - Equipe para manuten��o
  - Equipe para expans�o
  - Produtividade (LOC/pessoa-m�s)
  - Estimativa de custo
- Sa�da formatada e elegante com Rich

## Metodologia COCOMO II

O script utiliza a metodologia COCOMO II para estimar:

### N�veis de Complexidade
- **Org�nico (Baixa)**: Projetos at� 50 KLOC
- **Semi-Destacado (M�dia)**: Projetos entre 50-300 KLOC
- **Embarcado (Alta)**: Projetos acima de 300 KLOC

### F�rmulas Utilizadas
- **Esfor�o**: E = a � (KLOC)^b pessoa-meses
- **Tempo**: T = c � (E)^d meses
- **Pessoas**: P = E / T

## Instala��o

```bash
# Clone o reposit�rio
git clone <repository-url>
cd analiser-cocomo2

# Instale as depend�ncias usando uv
uv sync

# Ou usando pip
pip install -e .
```

## Uso

### An�lise do diret�rio atual
```bash
python main.py
```

### An�lise de um diret�rio espec�fico
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

## Exemplos de Sa�da

O script gera relat�rios com:

1. **M�tricas de C�digo**
   - Total de arquivos
   - Total de linhas
   - Linhas de c�digo
   - Linhas de coment�rios
   - Linhas em branco

2. **Distribui��o por Linguagem**
   - Quantidade de linhas por linguagem
   - Porcentagem de cada linguagem

3. **Resultados COCOMO II**
   - N�vel de complexidade
   - Esfor�o total (pessoa-m�s)
   - Tempo de desenvolvimento
   - Pessoas necess�rias
   - Equipe de manuten��o
   - Equipe de expans�o
   - Produtividade

4. **Estimativa de Custo**
   - Custo total estimado em USD

5. **Insights e Recomenda��es**
   - An�lise autom�tica dos resultados
   - Sugest�es baseadas nas m�tricas

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

## Diret�rios e Arquivos Exclu�dos

O analisador exclui automaticamente:

### Diret�rios
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

## Depend�ncias

- Python >= 3.13
- rich >= 13.7.0
- pathspec >= 0.12.1

## Contribuindo

Contribui��es s�o bem-vindas! Sinta-se � vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature
3. Commit suas mudan�as
4. Push para a branch
5. Abrir um Pull Request

## Licen�a

MIT License

## Autor

Desenvolvido para an�lise de projetos de software usando metodologia COCOMO II.

## Refer�ncias

- [COCOMO II Model Definition Manual](http://csse.usc.edu/csse/research/COCOMOII/cocomo_main.html)
- Barry W. Boehm et al., "Software Cost Estimation with COCOMO II"
