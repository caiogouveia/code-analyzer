# Teste do Navegador de Diretórios

## Como testar:

1. Execute a TUI:
```bash
./run_tui.sh
```

2. Pressione `n` ou clique em "Nova Análise"

3. Clique em "📂 Navegar..."

4. Você deverá ver:
   - ✅ **Caminho** com input editável
   - ✅ **Árvore de diretórios** (altura 12)
   - ✅ **Indicador Git** (linha com status Git)
   - ✅ **Indicador de Validação** (caixa com borda mostrando status)
   - ✅ **Botões:**
     - "✓ OK - Confirmar Seleção" (verde, pode estar desabilitado)
     - "✗ Cancelar" (vermelho)

## O que foi implementado:

### CSS Ajustado:
- Container: `height: auto` com `max-height: 95%`
- Árvore: `height: 12` (reduzida para dar espaço)
- Indicadores: `height: auto`
- Botões: margin-top adicionado

### Validação:
- Executada com delay de 0.1s após montagem
- Verifica:
  1. Se path existe
  2. Se é diretório  
  3. Se tem arquivos de código (.py, .js, etc.)
- Busca até 50 arquivos em 5 níveis de profundidade
- Ignora: node_modules, .git, __pycache__, etc.

### Estados do Botão OK:
- 🔴 **Desabilitado** quando:
  - Path não existe
  - Não é diretório
  - Sem arquivos de código
- 🟢 **Habilitado** quando:
  - Diretório válido
  - Tem arquivos de código

## Debug:

Se os botões não aparecerem:

1. Verifique o tamanho do terminal (precisa ser grande o suficiente)
2. A validação inicial mostra: "Validando diretório..."
3. Depois mostra o resultado com cores:
   - Verde: válido
   - Amarelo: sem código
   - Vermelho: erro

## Teste rápido:
```bash
uv run python test_browser.py
```
Deve abrir o navegador e permitir seleção.
