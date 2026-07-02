# Roteiro de Análise de Código Legado: Do Fluxo ao Código Morto
## Fase 1: Preparação do Ambiente no Ubuntu 26 LTS
Como o Python 2 e seu respectivo `pip` foram descontinuados das fontes oficiais do Ubuntu, o primeiro passo é garantir que as dependências do sistema e o ambiente isolado estejam corretos.

### Passo 1.1: Instalar dependências do sistema (Graphviz)
O `pycallgraph` precisa do Graphviz para renderizar os diagramas em formato PNG. Abra o terminal e instale:
```bash
sudo apt update
sudo apt install -y graphviz graphviz-dev
```
### Passo 1.2: Validar o interpretador Python 2 e criar um ambiente virtual
Para não poluir o sistema e garantir que as versões antigas das ferramentas não conflitem com o Python 3 do Ubuntu 26, use um ambiente isolado (recomenda-se o virtualenv compatível com Python 2).

1. Navegue até a pasta raiz do seu projeto (onde fica a pasta API/):
```bash
cd /caminho/para/seu/projeto/raiz
```
2. Crie e ative o ambiente virtual para Python 2:
```bash
# Instale o virtualenv globalmente se necessário (via python2 se disponível ou pip2)
virtualenv -p python2 venv_legado

# Ative o ambiente
source venv_legado/bin/activate
```
> (Você saberá que deu certo se o prefixo (venv_legado) aparecer no seu terminal).

### Passo 1.3: Instalar as ferramentas nas versões corretas
Com o ambiente ativado, instale o `pycallgraph` e a versão específica do vulture que ainda suporta a sintaxe do Python 2:
```bash
pip install pycallgraph vulture==0.26 radon<4.5.0 pylint pydocstyle
```
## Fase 2: Análise Dinâmica (Mapeamento do Fluxo com PyCallGraph)
Nesta fase, você vai envelopar o ponto de entrada original do seu Gateway (geralmente onde fica o `if __name__ == '__main__':` do seu arquivo principal).


### Passo 2.1: Modificar o Arquivo Principal do seu Gateway

Abra o arquivo principal que você executa para ligar o Gateway. Vamos modificar o bloco de inicialização dele.

No topo do arquivo, adicione os imports do `pycallgraph`:
```python

# -*- coding: utf-8 -*-
# (Mantenha seus imports originais aqui...)

# Adicione estes para o mapeamento:
from pycallgraph import PyCallGraph, Config, GlobbingFilter
from pycallgraph.output import GraphvizOutput
import os
```

Agora, vá até o final do arquivo e substitua o bloco de execução padrão por este formato "envelopado":

```python
# ... todo o seu código original, classes e funções continuam aqui em cima ...

def iniciar_tudo():
    """
    Encapsule aqui a chamada da sua função original que liga o gateway.
    Ex: Seu daemon do Pyro4, loops de socket, etc.
    """
    # SEU CÓDIGO ORIGINAL DE INICIALIZAÇÃO ENTRA AQUI
    pass

if __name__ == '__main__':
    # 1. Configuração estrita dos filtros do PyCallGraph
    config = Config()
    
    # Rastreia apenas as suas subpastas dentro de API/src/
    config.trace_filter = GlobbingFilter(
        include=[
            '*pasta1.*',
            '*pasta2.*',
            # Adicione outras subpastas do seu projeto se houver
        ],
        exclude=['*']  # Ignora Pyro4, sockets, bibliotecas padrão do Python
    )

    # 2. Configuração do arquivo de saída PNG
    # Ele será salvo na mesma pasta de onde você disparar o terminal
    output = GraphvizOutput()
    output.output_file = os.path.abspath('fluxo_execucao_gateway.png')

    print("================================================================")
    print(" INICIANDO GATEWAY COM MAPEAMENTO DINÂMICO ATIVADO")
    print(" Execute seus testes. Para gerar o gráfico, pare este terminal com CTRL+C.")
    print("================================================================")

    # 3. Execução protegida
    try:
        with PyCallGraph(output=output, config=config):
            iniciar_tudo()
    except KeyboardInterrupt:
        print("\n[INFO] Sinal de parada recebido. Renderizando gráfico...")
        print("[SUCESSO] Gráfico salvo em: {}".format(output.output_file))
```

### Passo 2.2: Executar o teste de fluxo diretamente

1. No terminal com o ambiente `venv_legado` ativo, ligue o seu gateway normalmente:
```bash
python nome_do_seu_arquivo_principal.py
```
2. No segundo terminal, rode o seu gerador de testes.

3. Assim que os testes terminarem de estressar o Gateway, volte ao terminal do Gateway e pressione `CTRL + C`.

4. O `pycallgraph` vai interceptar o encerramento e salvar o arquivo `fluxo_execucao_gateway.png` exatamente no diretório onde você estava no terminal.


## Fase 3: Análise Estática (Caça ao Código Morto com Vulture)
Agora que você já tem o mapa de quem roda de verdade, vamos extrair a lista textual de tudo o que está teoricamente abandonado no código.

### Passo 3.1: Executar o scanner de forma segura

O Vulture não altera arquivos, apenas lê. Vamos rodar o comando direcionando a saída para um arquivo de texto para que você possa analisar com calma no VS Code.

Na raiz do projeto, execute o seguinte comando no terminal:
```bash
vulture API/src/ > relatorio_codigo_morto.txt
```

### Passo 3.2: Filtrar falsos positivos no relatório
O arquivo `relatorio_codigo_morto.txt` será gerado. Abra-o no VS Code. Você verá linhas como esta:
> API/src/pasta1/arquivo.py:50: unused function 'metodo_antigo'

**Atenção aos detalhes metodológicos para o seu Mestrado:**

Como você usa **Pyro4**, os métodos que são expostos remotamente para outros gateways (geralmente decorados com `@Pyro4.expose`) podem ser listados pelo Vulture como "não utilizados" (unused). Isso acontece porque nenhuma parte do código local chama eles, a chamada vem da rede.

Para validar se o método é código morto real ou uma opção legítima que o Vulture não enxergou:

1. Pegue o nome do método suspeito no relatório do Vulture.
2. Procure por ele no gráfico `fluxo_execucao_gateway.png` gerado na Fase 2.
3. Se ele não está no gráfico dinâmico (não foi rodado nos testes) e o Vulture acusou como não utilizado, há $99\%$ de chance de ser código depreciado que pode ser limpo ou comentado.

## Fase 4: Métricas Estruturais e Complexidade (Radon & Pyreverse)

Nesta fase, coletamos os dados de saúde algorítmica e acoplamento arquitetural para cruzar com o fluxo gerado pelo `pycallgraph`.

### Passo 4.1: Extrair a Complexidade Ciclomática (Radon)

Ainda na raiz do projeto, execute o comando para medir a complexidade de caminhos lógicos de cada método sem tocar nos arquivos:

```bash
radon cc API/src/ -s -a > relatorio_complexidade_radon.txt
```
Abra o arquivo gerado no VS Code. Métodos com notas D, E ou F representam pontos de alto risco para refatoração.

### Passo 4.2: Mapear o Acoplamento de Módulos (Pyreverse)

Execute o Pyreverse para analisar de forma global como os submódulos se interconectam (evite rodar em pastas isoladas para não perder as conexões cruzadas):

```bash
pyreverse -o png -p EstruturaGateway API/src/
```

O arquivo `packages_EstruturaGateway.png` será gerado. Ele ilustra o nível de entrelaçamento ("código espaguete") entre suas subpastas.

## Fase 5: Arqueologia de Comentários e Diagnóstico de Documentação (Qualidade do Texto)

Aqui, buscamos rastrear a poluição de comentários desatualizados (prints de debug desativados, conversas de desenvolvedores) e a integridade das docstrings em relação às assinaturas dos métodos.

### Passo 5.1: Mapear Proporção de Comentários vs Código Real

Execute a análise estatística de linhas brutas para extrair a métrica de linhas de comentários (`COM`) em relação às linhas de código ativo (`SLOC`):

```bash
radon raw API/src/ > relatorio_linhas_brutas.txt
```

### Passo 5.2: Rastrear Prints Desativados e Conversas Legadas via Expressões Regulares

Use o poder do terminal para indexar onde estão os comentários desnecessários deixados por desenvolvedores anteriores:

```bash
# Localiza códigos e prints comentados
grep -rn "#.*print" API/src/ > relatorio_prints_comentados.txt

# Localiza discussões, lembretes ou notas informais de desenvolvimento
egrep -rn "#.*(TODO|FIXME|OBS|olhar|ajustar|testar)" API/src/ > relatorio_conversas_devs.txt
```

### Passo 5.3: Validar a Cobertura de Documentação (pydocstyle)

Execute a varredura para descobrir quais métodos públicos estão sem documentação ou fora do padrão Pep257:

```bash
pydocstyle API/src/ > relatorio_cobertura_documentacao.txt
```

### Passo 5.4: Validar se a Documentação Condiz com a Assinatura (Pylint)

Rode o Pylint silenciando as validações comuns e ativando estritamente os checadores de documentação ausente e discrepâncias entre parâmetros declarados no texto vs parâmetros reais da função (`useless-param-doc`):

```bash
pylint --disable=all --enable=basic,classes,design --disable=C0103,R0903 --enable=missing-docstring,useless-param-doc API/src/ > validacao_parametros_doc.txt
```

## Fase 6: Limpeza Prática no VS Code
Com as duas ferramentas tendo feito o trabalho pesado, seu fluxo de trabalho de refatoração será:

1. **Garantia de segurança:** Crie uma nova branch no Git antes de mexer em qualquer linha (`git checkout -b refatoracao-legado`).
2. **Métodos duplicados:** Ao encontrar métodos com funções semelhantes, use o atalho `Shift + Alt + F12` no VS Code sobre o nome do método para ver quais arquivos ainda dependem dele.
3. **Desativação segura:** Em vez de deletar imediatamente os métodos depreciados que você confirmou que não são usados, comente-os (`#`) ou adicione um aviso de depreciação no início do escopo:

```python
import warnings

def metodo_legado_duplicado():
    # O aviso só dispara se esta função for de fato invocada
    warnings.warn(
        "O metodo 'metodo_legado_duplicado' foi chamado! Verifique o fluxo.", 
        DeprecationWarning
    )
    
    # Código original do método continua aqui...
    print("Executando a lógica antiga...")
```

## Fase 7: Detecção de Clonagem e Duplicação de Código (PMD CPD)

Nesta fase, buscamos blocos de código que foram copiados e colados entre arquivos diferentes (Copy-Paste Dependency), o que infla o tamanho do legado e gera retrabalho na manutenção.

### Passo 7.1: Instalar o PMD no Ubuntu 26 LTS
O CPD é uma ferramenta multiplataforma baseada em Java. Instale o runtime do Java e baixe o PMD oficial pelo terminal:

```bash
sudo apt update
sudo apt install -y default-jre

# Baixa e extrai o PMD na sua pasta home ou ferramentas
cd ~
wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.0.0/pmd-dist-7.0.0-bin.zip
unzip pmd-dist-7.0.0-bin.zip
```

### Passo 7.2: Executar o Detector de Recortar e Colar (CPD)
Volte para a pasta raiz do seu projeto e execute o scanner apontando para a sua pasta `src`. Vamos configurar o parâmetro `--minimum-tokens` para `50` (o que equivale a mais ou menos 5 a 6 linhas de código idênticas):

```bash
~/pmd-bin-7.0.0/bin/pmd cpd --minimum-tokens 50 --dir API/src/ --language python --format text > relatorio_codigo_duplicado.txt
```

### Passo 7.3: Como ler o Relatório de Duplicações
Abra o arquivo `relatorio_codigo_duplicado.txt` no VS Code. Ele agrupa as duplicidades mostrando os arquivos e as linhas exatas envolvidas:

```text
Found a 12 line (58 tokens) duplication in the following files:
To: /API/src/pasta1/gateway.py:120
To: /API/src/pasta2/comunicacao.py:84
```

Se o mesmo bloco de código aparece na pasta1 e na pasta2, você acabou de mapear candidatos perfeitos para virarem uma função utilitária centralizada na hora de aplicar a comunicação direta.

