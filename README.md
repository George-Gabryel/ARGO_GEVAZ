# Gevaz — Planilha de Ovitrampas para Banco de Dados

Este projeto lê a planilha **"Total Ovtrampas.xlsx"** (registros de coleta das ovitrampas — armadilhas usadas para monitorar ovos do mosquito *Aedes aegypti*), **limpa e padroniza** os dados e **salva tudo em um banco de dados SQLite** (`saida/total_ovt.db`), pronto para ser consultado com SQL, Power BI, Excel ou outra ferramenta.

Esse tipo de processo tem um nome na área de dados: **ETL**, sigla em inglês para:

| Etapa | Em português | O que faz aqui |
|---|---|---|
| **E**xtract | Extrair | Ler a planilha Excel |
| **T**ransform | Transformar | Arrumar nomes de colunas, datas, números, espaços em branco etc. |
| **L**oad | Carregar | Gravar os dados limpos no banco SQLite |

O documento tem duas partes:

1. **[Parte 1 — Como replicar o projeto, passo a passo](#parte-1--como-replicar-o-projeto-passo-a-passo)**: do zero até rodar o código, explicando cada trecho.
2. **[Parte 2 — Como o código funciona](#parte-2--como-o-código-funciona)**: o caminho que os dados percorrem, do Excel até o banco.

---

## Glossário rápido

Se você não é da área, estes termos aparecem bastante:

- **Python**: a linguagem de programação usada no projeto.
- **Biblioteca (ou pacote)**: código pronto, escrito por outras pessoas, que instalamos para não reinventar a roda. Aqui usamos o **pandas** (manipular tabelas) e o **openpyxl** (ler arquivos `.xlsx`).
- **DataFrame**: é como o pandas guarda uma tabela na memória. Pense numa aba do Excel: tem linhas, colunas e nomes de colunas.
- **Função**: um bloco de código com nome que recebe algo, faz um trabalho e devolve um resultado. Ex.: `extrair(...)` recebe o caminho da planilha e devolve a tabela.
- **Módulo**: um arquivo `.py` que agrupa funções. Ex.: `src/extract.py`.
- **SQLite**: um banco de dados que fica inteiro dentro de **um único arquivo** (`.db`). Não precisa instalar servidor; o Python já sabe usá-lo.
- **Tabela / Schema**: no banco, os dados ficam em tabelas. O *schema* é a "planta" da tabela: quais colunas existem, de que tipo são e quais regras seguem.
- **Ambiente virtual (venv)**: uma pasta isolada onde ficam as bibliotecas deste projeto, para não misturar com outros projetos do computador.
- **Terminal**: a janela onde digitamos comandos (no Windows: PowerShell ou Prompt de Comando).

---

## Parte 1 — Como replicar o projeto, passo a passo

### Passo 1 — Instalar as ferramentas

1. **Python 3.12 ou mais recente** (o projeto foi feito com o Python 3.14).
   Baixe em <https://www.python.org/downloads/>. No Windows, na primeira tela do instalador, **marque a opção "Add python.exe to PATH"**. Sem isso, o terminal não encontra o Python.
2. **Um editor de código** — recomendado o [Visual Studio Code](https://code.visualstudio.com/), com a extensão "Python" da Microsoft.
3. *(Opcional)* **Git**, se quiser baixar o projeto do GitHub em vez de criar os arquivos à mão.

Para conferir se o Python foi instalado, abra o terminal e digite:

```powershell
python --version
```

Deve aparecer algo como `Python 3.14.4`.

### Passo 2 — Criar a estrutura de pastas

Crie uma pasta para o projeto (ex.: `Gevaz`) com esta organização:

```
Gevaz/
├── main.py                 ← ponto de partida: executa as 3 etapas em ordem
├── transform.ipynb         ← caderno Jupyter usado para testar a limpeza (opcional)
├── dados/
│   └── Total Ovtrampas.xlsx   ← planilha de entrada
├── saida/                  ← onde o banco total_ovt.db será criado
└── src/                    ← "source" (código-fonte): as peças do ETL
    ├── extract.py          ← etapa E: lê a planilha
    ├── load.py             ← etapas T e L: limpa e grava no banco
    └── sqlite_schema.py    ← a "planta" da tabela no banco
```

Por que separar em arquivos? Cada arquivo tem **uma responsabilidade**. Se um dia a planilha mudar de formato, você mexe só no `extract.py`; se o banco mudar, só no `sqlite_schema.py`. Fica mais fácil de entender e de consertar.

> A pasta `saida/` é criada automaticamente pelo código se não existir, mas não há problema em criá-la antes.

Se você for usar o Git, **clone** o repositório em vez de criar as pastas:

```powershell
git clone https://github.com/George-Gabryel/Gevaz.git
cd Gevaz
```

### Passo 3 — Criar o ambiente virtual e instalar as bibliotecas

Abra o terminal **dentro da pasta do projeto** e rode:

```powershell
python -m venv .venv
```

Isso cria a pasta `.venv` com um Python "particular" do projeto. Agora **ative** o ambiente:

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Prompt de Comando / cmd)
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

Quando ativado, aparece `(.venv)` no começo da linha do terminal.

> **Erro no PowerShell dizendo que a execução de scripts está desabilitada?** Rode uma vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e tente ativar de novo.

Instale as bibliotecas:

```powershell
pip install pandas openpyxl
```

- **pandas**: lê a planilha, guarda como tabela (DataFrame) e faz a limpeza.
- **openpyxl**: é o "leitor" de arquivos `.xlsx` que o pandas usa por baixo dos panos.

Se quiser usar o caderno `transform.ipynb`, instale também:

```powershell
pip install ipykernel
```

As bibliotecas `sqlite3`, `pathlib`, `contextlib` e `unicodedata` **já vêm com o Python**, não precisam ser instaladas.

### Passo 4 — Colocar a planilha na pasta `dados/`

Copie o arquivo `Total Ovtrampas.xlsx` para dentro de `dados/`. O código espera:

- uma aba chamada **`CICLO 1`**;
- na **primeira linha**, os cabeçalhos abaixo (maiúsculas/minúsculas e acentos não importam, o código padroniza):

| Cabeçalho na planilha | Significado |
|---|---|
| `Ano` | Ano da coleta |
| `CICLOS` | Número do ciclo de coleta |
| `DS` | Distrito Sanitário (ex.: I, II, III…) |
| `BAIRRO` | Bairro |
| `BAIRRO_AREA` | Bairro/área de atuação |
| `AGENTE / MATRICULA` | Nome do agente e matrícula juntos, separados por `/` (ex.: `FULANO DE TAL/00.000-0`) |
| `QT` | Quantidade |
| `ID_OVT` | Código da ovitrampa (ex.: `REC1001`) |
| `DT_COLETA` | Data da coleta |
| `DT_ENTREGA_APOIO` | Data de entrega ao apoio |
| `DT_ENTREGA_LAB` | Data de entrega ao laboratório |
| `DT_LEITURA` | Data de leitura no laboratório |
| `NM_TEC_LAB` | Nome do técnico do laboratório |
| `DT_DIG` | Data de digitação |
| `DT_ENVIO_DS` | Data de envio ao Distrito Sanitário |
| `N_OVOS` | Número de ovos contados |
| `OBS…` | Observações. O cabeçalho pode ser longo (ex.: `OBS F (Fechado); E (Extraviado)…`); qualquer coluna que comece com "OBS" é tratada como observação |

> **Feche a planilha no Excel/LibreOffice antes de rodar o código.** Arquivos como `.~lock.Total Ovtrampas.xlsx#` são criados enquanto a planilha está aberta e indicam que ela está em uso.

### Passo 5 — Escrever o código

A seguir, cada arquivo com a explicação de **o que cada parte faz**.

---

#### 5.1 `src/extract.py` — Extrair (ler a planilha)

```python
from pathlib import Path
import pandas as pd

def extrair(caminho, ABA) -> pd.DataFrame:
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {caminho}")
    df = pd.read_excel(
        caminho,
        sheet_name=ABA,
        header=0,
        dtype=str,
        na_values=["", "-", "N/A", "#DIV/0!", "#N/D"],
        engine="openpyxl",
    )

    return df
```

Linha a linha:

- `from pathlib import Path` — traz a ferramenta `Path`, que representa caminhos de arquivo de um jeito que funciona igual no Windows e no Linux.
- `import pandas as pd` — carrega o pandas e dá a ele o apelido `pd` (convenção de mercado).
- `def extrair(caminho, ABA) -> pd.DataFrame:` — cria a função `extrair`, que recebe **o caminho do arquivo** e **o nome da aba**, e devolve (`->`) um DataFrame.
- `caminho = Path(caminho)` — transforma o texto do caminho em um objeto `Path`.
- `if not caminho.exists(): raise FileNotFoundError(...)` — **verificação de segurança**: se o arquivo não existe, o programa para imediatamente com uma mensagem clara, em vez de um erro confuso mais adiante.
- `pd.read_excel(...)` — lê a planilha. Os parâmetros:
  - `sheet_name=ABA` — qual aba ler (`"CICLO 1"`).
  - `header=0` — a linha 0 (a primeira) contém os nomes das colunas.
  - `dtype=str` — **lê tudo como texto**. Isso é proposital: evita que o pandas "adivinhe" tipos errado (por exemplo, transformar uma matrícula `077` em número `77`). A conversão para número e data é feita depois, de forma controlada, na etapa de transformação.
  - `na_values=[...]` — lista de valores que devem ser entendidos como **"vazio"** (em pandas, vazio = `NaN`): célula em branco, traço, `N/A` e erros comuns do Excel (`#DIV/0!`, `#N/D`).
  - `engine="openpyxl"` — usa o openpyxl para ler o `.xlsx`.
- `return df` — devolve a tabela lida.

---

#### 5.2 `src/sqlite_schema.py` — A "planta" da tabela

```python
def criar_tabela():
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS ovt (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ano                 INTEGER NOT NULL,
    ciclos              INTEGER NOT NULL,
    ds                  TEXT NOT NULL,
    bairro              TEXT NOT NULL,
    bairro_area         TEXT NOT NULL,
    agente              TEXT NOT NULL,
    matricula           TEXT,
    qt                  INTEGER NOT NULL,
    id_ovt              TEXT NOT NULL,
    dt_coleta           TEXT,
    dt_entrega_apoio    TEXT,
    dt_entrega_lab      TEXT,
    dt_leitura          TEXT,
    nm_tec_lab          TEXT,
    dt_dig              TEXT,
    dt_envio_ds         TEXT,
    n_ovos              INTEGER,
    obs                 TEXT,
    UNIQUE (ds, id_ovt, ciclos, dt_coleta)
    );
    CREATE INDEX IF NOT EXISTS idx_dt_coleta ON ovt (dt_coleta);
    CREATE INDEX IF NOT EXISTS idx_ds ON ovt (ds);
    CREATE INDEX IF NOT EXISTS idx_bairro_area ON ovt (bairro_area);
    """

    return SCHEMA
```

Este arquivo **não executa nada sozinho**: ele só devolve um texto com comandos **SQL** (a linguagem dos bancos de dados). Quem executa esse texto é a função `carregar`, em `load.py`.

O que cada parte do SQL significa:

- `CREATE TABLE IF NOT EXISTS ovt (...)` — cria a tabela `ovt`, se ela ainda não existir.
- `id INTEGER PRIMARY KEY AUTOINCREMENT` — cada linha ganha um número de identificação único, gerado automaticamente (1, 2, 3…). Esse campo não vem da planilha.
- **Tipos**:
  - `INTEGER` — número inteiro (ano, ciclo, quantidade, número de ovos).
  - `TEXT` — texto. **As datas são gravadas como texto** no formato `AAAA-MM-DD` (ex.: `2026-01-29`), que é o padrão recomendado para SQLite: fica legível e ordena corretamente.
- `NOT NULL` — o campo é **obrigatório**. Se alguma linha vier sem `ano`, `ciclos`, `ds`, `bairro`, `bairro_area`, `agente`, `qt` ou `id_ovt`, o banco recusa a gravação.
- `UNIQUE (ds, id_ovt, ciclos, dt_coleta)` — **proíbe duplicatas**: não pode existir duas linhas com o mesmo distrito + mesma ovitrampa + mesmo ciclo + mesma data de coleta. É uma proteção contra registros repetidos na planilha.
- `CREATE INDEX ...` — cria **índices**, que funcionam como o índice de um livro: deixam as buscas e filtros por `dt_coleta`, `ds` e `bairro_area` muito mais rápidos.

> Os nomes das colunas aqui **precisam ser iguais** aos nomes que a etapa de transformação produz (tudo minúsculo, sem acento, com `_`). É isso que permite ao pandas encaixar cada coluna do DataFrame na coluna certa do banco.

---

#### 5.3 `src/load.py` — Transformar e Carregar

Este é o arquivo mais importante. Ele tem três funções.

**Importações:**

```python
import pandas as pd
from contextlib import closing
from pathlib import Path
import sqlite3
import unicodedata as uni
```

- `pandas` — manipular a tabela.
- `closing` — garante que a conexão com o banco seja **fechada** no final, mesmo se der erro.
- `Path` — caminhos de arquivo.
- `sqlite3` — conversar com o banco SQLite (já vem com o Python).
- `unicodedata` — ferramentas para lidar com acentos e caracteres especiais.

##### Função 1: `normalizar_nome` — padronizar nomes de colunas

```python
def normalizar_nome(coluna:str) -> str:
    """'Agente / Matricula' -> 'Agente_Matricula'"""
    texto = uni.normalize('NFKD', str(coluna))
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.strip().lower()
    for caractere in "-/().$ ":
        texto = texto.replace(caractere, "_")
    while "__" in texto:
        texto = texto.replace("__","_")
    return texto.strip("_")
```

Nomes de colunas vindos do Excel costumam ter acentos, espaços, barras e letras maiúsculas — o que atrapalha no banco e no código. Esta função transforma, por exemplo, `"AGENTE / MATRICULA"` em `"agente_matricula"`:

| Linha | O que faz | Exemplo |
|---|---|---|
| `uni.normalize('NFKD', ...)` | Separa a letra do acento (`ç` vira `c` + `¸`) | `"Ação"` → `"Ac¸a~o"` (internamente) |
| `.encode("ascii", "ignore").decode("ascii")` | Joga fora tudo que não é letra/número "simples", ou seja, os acentos | → `"Acao"` |
| `.strip().lower()` | Remove espaços nas pontas e deixa tudo minúsculo | `" AGENTE / MATRICULA "` → `"agente / matricula"` |
| `for caractere in "-/().$ ":` | Troca `-`, `/`, `(`, `)`, `.`, `$` e espaço por `_` | → `"agente___matricula"` |
| `while "__" in texto:` | Junta vários `_` seguidos em um só | → `"agente_matricula"` |
| `texto.strip("_")` | Remove `_` que tenham sobrado nas pontas | → `"agente_matricula"` |

##### Função 2: `transformar` — limpar os dados

```python
def transformar (df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
```

- `df.copy()` — trabalha numa **cópia** da tabela, para não alterar a original sem querer.

```python
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
```

- Quando uma coluna da planilha não tem cabeçalho (coluna "fantasma", às vezes com formatação), o pandas a chama de `Unnamed: 17`, `Unnamed: 18` etc. Esta linha **remove essas colunas**. O `~` significa "NÃO": fique com as colunas que **não** começam com "Unnamed".

```python
    df.columns = [normalizar_nome(c) for c in df.columns]
```

- Aplica a função `normalizar_nome` em **todos** os cabeçalhos.

```python
    df = df.rename(columns=lambda c: "obs" if c.startswith("obs") else c)
```

- O cabeçalho de observações na planilha é bem longo (tem a legenda `F (Fechado); E (Extraviado)…`). Aqui ele é renomeado simplesmente para `obs`. O `lambda` é uma "mini função" de uma linha: para cada nome `c`, se começar com `"obs"`, vira `"obs"`; senão, continua igual.

```python
    for coluna in df.select_dtypes(include=["object", "str"]).columns:
        df[coluna] = df[coluna].str.strip()
```

- Para **cada coluna de texto**, remove espaços em branco sobrando no começo e no fim das células (ex.: `"RECIFE  "` → `"RECIFE"`). Espaços invisíveis fazem o computador achar que `"RECIFE"` e `"RECIFE "` são coisas diferentes.

```python
    agen_matri = df["agente_matricula"].str.split("/", n=1, expand=True)
    df = df.drop(columns=["agente_matricula"])
```

- A coluna `agente_matricula` junta duas informações: `"NOME DO AGENTE/00.000-0"`. Aqui ela é **dividida na primeira barra** (`n=1`) em duas partes: `agen_matri[0]` (nome) e `agen_matri[1]` (matrícula). Depois a coluna original é descartada (`drop`).

Em seguida, cada coluna é convertida para o **tipo certo**:

```python
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    df["ciclos"] = pd.to_numeric(df["ciclos"], errors="coerce")
    ...
    df["agente"] = agen_matri[0].str.strip()
    df["matricula"] = agen_matri[1].str.strip()
    df["qt"] = pd.to_numeric(df["qt"], errors="coerce")
    ...
    df["dt_coleta"] = pd.to_datetime(df["dt_coleta"], errors="coerce", format="ISO8601").dt.strftime("%Y-%m-%d")
    ...
    df["n_ovos"] = pd.to_numeric(df["n_ovos"], errors="coerce")
    df["obs"] = df["obs"].str.strip()
```

- `pd.to_numeric(..., errors="coerce")` — converte texto em **número**. O `errors="coerce"` diz: "se não der para converter (ex.: alguém digitou `abc`), deixe vazio em vez de travar o programa".
  Aplicado em: `ano`, `ciclos`, `qt`, `n_ovos`.
- `pd.to_datetime(..., errors="coerce", format="ISO8601")` — converte texto em **data**. `ISO8601` é o formato padrão `AAAA-MM-DD HH:MM:SS`, que é como o Excel entrega as datas lidas pelo pandas. Datas inválidas viram vazio.
- `.dt.strftime("%Y-%m-%d")` — transforma a data de volta em texto, mas **padronizado** como `2026-01-29` (sem horário). É o formato que será gravado no banco.
  Aplicado em: `dt_coleta`, `dt_entrega_apoio`, `dt_entrega_lab`, `dt_leitura`, `dt_dig`, `dt_envio_ds`.
- `.str.strip()` — nas colunas de texto (`ds`, `bairro`, `bairro_area`, `id_ovt`, `nm_tec_lab`, `obs`, `agente`, `matricula`), remove espaços nas pontas.
- As colunas novas `agente` e `matricula` são criadas a partir da divisão feita antes.

```python
    df = df.dropna(how='all')
    df = df.drop_duplicates()

    return df
```

- `dropna(how='all')` — remove linhas **completamente vazias** (muito comum no fim de planilhas).
- `drop_duplicates()` — remove linhas **exatamente iguais** (repetidas).
- `return df` — devolve a tabela limpa.

##### Função 3: `carregar` — gravar no banco

```python
def carregar(df: pd.DataFrame, caminho_db: Path, tabela: str, SCHEMA) -> int:
    caminho_db.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(caminho_db)) as conexao:
        with conexao:
            conexao.executescript(f"BEGIN; DROP TABLE IF EXISTS {tabela}; {SCHEMA}")
            df.to_sql(tabela, conexao, if_exists="append", index=False)
        return conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
```

Recebe a tabela limpa (`df`), o caminho do arquivo do banco, o nome da tabela e o texto do schema. Devolve quantas linhas ficaram gravadas.

- `caminho_db.parent.mkdir(parents=True, exist_ok=True)` — cria a pasta `saida/` se ela não existir (e não reclama se já existir).
- `sqlite3.connect(caminho_db)` — abre (ou cria) o arquivo `total_ovt.db`.
- `with closing(...) as conexao:` — garante que a conexão será **fechada** ao final.
- `with conexao:` — abre uma **transação**. Transação é um "tudo ou nada": se tudo correr bem, as mudanças são salvas (*commit*); se qualquer coisa der erro, **tudo é desfeito** (*rollback*) e o banco volta a ser como estava antes.
- `executescript("BEGIN; DROP TABLE IF EXISTS ovt; <SCHEMA>")`:
  - `BEGIN` — inicia a transação.
  - `DROP TABLE IF EXISTS ovt` — **apaga a tabela antiga**, se existir.
  - `<SCHEMA>` — recria a tabela vazia com a estrutura definida em `sqlite_schema.py`.
- `df.to_sql(tabela, conexao, if_exists="append", index=False)` — insere todas as linhas do DataFrame na tabela recém-criada. `append` = "adicionar à tabela que já existe" (a que acabamos de criar, respeitando o schema). `index=False` = não gravar a numeração interna do pandas.
- `SELECT COUNT(*) FROM ovt` — conta quantas linhas ficaram na tabela e devolve esse número.

> **Por que apagar e recriar a tabela a cada execução?** Porque a **planilha é a fonte da verdade**. Se você rodar o programa duas vezes, os dados não ficam duplicados: o banco sempre reflete exatamente o conteúdo atual da planilha. E como tudo acontece dentro de uma transação, se a gravação falhar no meio, a tabela anterior é preservada.

---

#### 5.4 `main.py` — O maestro

```python
from pathlib import Path
import src.extract as ex
import src.load as load
import src.sqlite_schema as SCHEMA


CAMINHO_XLSX = "dados/Total Ovtrampas.xlsx"
ABA = "CICLO 1"
CAMINHO_DB = Path("saida/total_ovt.db")
TABELA = "ovt"
criar_tabela = SCHEMA.criar_tabela()


def main() -> None:
    dado_bruto = ex.extrair(CAMINHO_XLSX, ABA)
    print(f"Lidas {len(dado_bruto)} linhas da aba '{ABA}' de {CAMINHO_XLSX}")

    tratado = load.transformar(dado_bruto)
    print(f"Restaram {len(tratado)} linhas após a limpeza")

    total = load.carregar(tratado, CAMINHO_DB, TABELA, criar_tabela)
    print(f"Tabela '{TABELA}' agora tem {total} registros em {CAMINHO_DB}")

if __name__ == "__main__":
    main()
```

- **Importações**: traz os três módulos da pasta `src/`, com apelidos curtos (`ex`, `load`, `SCHEMA`).
- **Configurações** (em MAIÚSCULAS, por convenção, indicando valores fixos):
  - `CAMINHO_XLSX` — onde está a planilha.
  - `ABA` — qual aba ler.
  - `CAMINHO_DB` — onde o banco será salvo.
  - `TABELA` — nome da tabela no banco. **Deve ser igual ao nome usado no `CREATE TABLE` de `sqlite_schema.py`** (`ovt`).
  - `criar_tabela` — guarda o texto SQL do schema.
- **`main()`** — executa as 3 etapas em ordem, mostrando no terminal quantas linhas passaram por cada uma:
  1. `extrair` → dados brutos;
  2. `transformar` → dados limpos;
  3. `carregar` → grava no banco e informa o total.
- `if __name__ == "__main__": main()` — significa "só execute `main()` se este arquivo for rodado diretamente". Assim, se outro código importar o `main.py`, ele não dispara o ETL sem querer.

> Para processar outra aba ou outra planilha, basta mudar `CAMINHO_XLSX` e/ou `ABA` aqui.

---

#### 5.5 `transform.ipynb` — O caderno de testes (opcional)

É um **caderno Jupyter**: um arquivo onde o código é dividido em células que você roda uma de cada vez, vendo o resultado de cada passo. Ele foi usado como "rascunho" para desenvolver a limpeza que depois virou a função `transformar` em `load.py`. Ele **não é necessário** para o projeto funcionar, mas é útil para investigar a planilha ou testar novas regras de limpeza antes de passá-las para o código definitivo.

Para abri-lo no VS Code, instale a extensão "Jupyter", abra o arquivo e escolha o Python da pasta `.venv` como *kernel*.

### Passo 6 — Rodar

Com o ambiente virtual ativado e dentro da pasta do projeto:

```powershell
python main.py
```

A saída será parecida com:

```
Lidas 31455 linhas da aba 'CICLO 1' de dados/Total Ovtrampas.xlsx
Restaram N linhas após a limpeza
Tabela 'ovt' agora tem N registros em saida\total_ovt.db
```

(Os números exatos dependem do conteúdo atual da planilha.)

> **Importante:** rode sempre a partir da pasta raiz do projeto. Os caminhos `dados/...` e `saida/...` são relativos à pasta onde o terminal está.

### Passo 7 — Conferir o resultado

O arquivo `saida/total_ovt.db` pode ser aberto com:

- **[DB Browser for SQLite](https://sqlitebrowser.org/)** (gratuito, visual — recomendado para quem não programa);
- a extensão **"SQLite Viewer"** do VS Code;
- o próprio Python:

```python
import sqlite3
import pandas as pd

con = sqlite3.connect("saida/total_ovt.db")
print(pd.read_sql("SELECT ds, SUM(n_ovos) AS total_ovos FROM ovt GROUP BY ds", con))
con.close()
```

Esse exemplo soma o número de ovos por Distrito Sanitário.

### Problemas comuns

| Mensagem / sintoma | Causa provável | Solução |
|---|---|---|
| `'python' não é reconhecido...` | Python não está no PATH | Reinstale marcando "Add python.exe to PATH" |
| `ModuleNotFoundError: No module named 'pandas'` | Bibliotecas não instaladas ou venv não ativado | Ative o `.venv` e rode `pip install pandas openpyxl` |
| `ModuleNotFoundError: No module named 'src'` | Rodou o comando fora da pasta do projeto | Entre na pasta raiz (`cd Gevaz`) e rode de novo |
| `FileNotFoundError: Planilha não encontrada` | Arquivo com outro nome ou em outra pasta | Confira `dados/Total Ovtrampas.xlsx` (nome exato, com espaço) |
| `ValueError: Worksheet named 'CICLO 1' not found` | A aba tem outro nome | Ajuste a variável `ABA` no `main.py` |
| `PermissionError` ao ler a planilha | Planilha aberta no Excel | Feche a planilha e rode de novo |
| `KeyError: 'agente_matricula'` (ou outra coluna) | Um cabeçalho da planilha mudou | Confira os cabeçalhos com a tabela do Passo 4 |
| `sqlite3.IntegrityError: NOT NULL constraint failed: ovt.<coluna>` | Alguma linha tem um campo obrigatório vazio (ou inválido, que virou vazio na conversão) | Corrija a linha na planilha. O banco anterior continua intacto |
| `sqlite3.IntegrityError: UNIQUE constraint failed` | Duas linhas com mesmo DS + ID_OVT + ciclo + data de coleta | Localize e corrija a duplicata na planilha |

---

## Parte 2 — Como o código funciona

### Visão geral do fluxo

```
┌──────────────────────────┐
│ dados/Total Ovtrampas.xlsx│   planilha original (aba "CICLO 1")
└────────────┬─────────────┘
             │  1. EXTRAIR  — src/extract.py → extrair()
             ▼
   DataFrame "bruto" (tudo como texto, vazios marcados)
             │
             │  2. TRANSFORMAR — src/load.py → transformar()
             ▼
   DataFrame "tratado" (nomes padronizados, tipos corretos, sem lixo)
             │
             │  3. CARREGAR — src/load.py → carregar()
             │     usando a planta de src/sqlite_schema.py
             ▼
┌──────────────────────────┐
│ saida/total_ovt.db       │   banco SQLite, tabela "ovt"
└──────────────────────────┘
```

Quem comanda tudo é o `main.py`: ele chama as três funções, uma depois da outra, passando o resultado de uma como entrada da próxima — como uma linha de montagem.

### O que acontece quando você digita `python main.py`

1. **O Python carrega os módulos** de `src/` e prepara as configurações (caminhos, nome da aba, nome da tabela e o texto do schema).

2. **Extração.** `extrair()` confere se a planilha existe e a lê inteira para a memória. Todas as células chegam como **texto**, e valores como `-`, `N/A` ou `#N/D` são marcados como **vazios**. Nada é alterado ainda: é uma cópia fiel da aba. O terminal mostra quantas linhas foram lidas.

3. **Transformação.** `transformar()` faz a faxina, nesta ordem:
   1. descarta colunas sem cabeçalho (`Unnamed…`);
   2. padroniza os cabeçalhos (`AGENTE / MATRICULA` → `agente_matricula`, `OBS F (Fechado)…` → `obs`);
   3. remove espaços sobrando em todas as células de texto;
   4. divide `agente_matricula` em `agente` e `matricula`;
   5. converte `ano`, `ciclos`, `qt` e `n_ovos` em números;
   6. converte as seis colunas de data para o formato `AAAA-MM-DD`;
   7. apaga linhas totalmente vazias e linhas repetidas.

   Valores que não puderem ser convertidos (um número digitado errado, uma data impossível) **viram vazio** em vez de interromper o programa. O terminal mostra quantas linhas restaram.

   **Exemplo de uma linha antes e depois** (dados fictícios):

   | | Antes (planilha) | Depois (banco) |
   |---|---|---|
   | Coluna | `AGENTE / MATRICULA` = `FULANO DE TAL/00.000-0` | `agente` = `FULANO DE TAL`, `matricula` = `00.000-0` |
   | Data | `DT_COLETA` = `2026-01-29 00:00:00` | `dt_coleta` = `2026-01-29` |
   | Número | `N_OVOS` = `"16"` (texto) | `n_ovos` = `16` (número) |
   | Texto | `BAIRRO` = `" RECIFE ANTIGO "` | `bairro` = `RECIFE ANTIGO` |

4. **Carga.** `carregar()`:
   1. cria a pasta `saida/` se necessário e abre o banco `total_ovt.db`;
   2. inicia uma **transação** (tudo ou nada);
   3. apaga a tabela `ovt` antiga e cria uma nova, vazia, seguindo o schema — com campos obrigatórios, a regra contra duplicatas e os índices;
   4. insere todas as linhas limpas;
   5. se tudo deu certo, confirma a transação; se algo falhou (ex.: uma linha sem `ano`), **desfaz tudo** e o banco continua com os dados da execução anterior;
   6. conta os registros gravados e devolve esse número, que o `main.py` mostra no terminal.

### Duas camadas de proteção de qualidade

O projeto verifica os dados em dois momentos diferentes:

| Onde | Como | Comportamento |
|---|---|---|
| **pandas** (`transformar`) | Converte tipos com `errors="coerce"`, remove vazios e duplicatas exatas | **Tolerante**: corrige o que dá e marca como vazio o que não dá |
| **SQLite** (schema) | `NOT NULL`, `UNIQUE`, tipos das colunas | **Rigoroso**: se uma linha violar as regras, recusa a carga inteira |

Essa combinação significa que problemas pequenos de digitação são absorvidos, mas problemas que comprometeriam a análise (linha sem distrito, sem ano, ou a mesma coleta registrada duas vezes) **não passam despercebidos** — o programa avisa com um erro e o banco não é corrompido.

### Resumo de responsabilidades

| Arquivo | Responsabilidade | Recebe | Devolve |
|---|---|---|---|
| `main.py` | Orquestrar as etapas e guardar as configurações | — | Mensagens no terminal |
| `src/extract.py` → `extrair()` | Ler a planilha | Caminho + nome da aba | DataFrame bruto |
| `src/load.py` → `normalizar_nome()` | Padronizar um nome de coluna | Um texto | Texto padronizado |
| `src/load.py` → `transformar()` | Limpar e tipar os dados | DataFrame bruto | DataFrame limpo |
| `src/sqlite_schema.py` → `criar_tabela()` | Definir a estrutura da tabela | — | Texto SQL |
| `src/load.py` → `carregar()` | Gravar no banco com segurança | DataFrame limpo + caminho + tabela + schema | Nº de registros gravados |
