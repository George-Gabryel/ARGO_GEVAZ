import pandas as pd
from contextlib import closing
from pathlib import Path
import sqlite3
import unicodedata as uni

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


def transformar (df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    df.columns = [normalizar_nome(c) for c in df.columns]

    df = df.rename(columns=lambda c: "obs" if c.startswith("obs") else c)
    for coluna in df.select_dtypes(include=["object", "str"]).columns:
        df[coluna] = df[coluna].str.strip()

    agen_matri = df["agente_matricula"].str.split("/", n=1, expand=True)
    df = df.drop(columns=["agente_matricula"])

    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    df["ciclos"] = pd.to_numeric(df["ciclos"], errors="coerce")
    df["ds"] = df["ds"].str.strip()
    df["bairro"] = df["bairro"].str.strip()
    df["bairro_area"] = df["bairro_area"].str.strip()
    df["agente"] = agen_matri[0].str.strip()
    df["matricula"] = agen_matri[1].str.strip()
    df["qt"] = pd.to_numeric(df["qt"], errors="coerce")
    df["id_ovt"] = df["id_ovt"].str.strip()
    df["dt_coleta"] = pd.to_datetime(df["dt_coleta"], errors="coerce", format="ISO8601").dt.strftime("%Y-%m-%d")
    df["dt_entrega_apoio"] = pd.to_datetime(df["dt_entrega_apoio"], errors="coerce", format="ISO8601").dt.strftime("%Y-%m-%d")
    df["dt_entrega_lab"] = pd.to_datetime(df["dt_entrega_lab"], errors="coerce", format="ISO8601").dt.strftime("%Y-%m-%d")
    df["dt_leitura"] = pd.to_datetime(df["dt_leitura"], errors="coerce", format="ISO8601").dt.strftime("%Y-%m-%d")
    df["nm_tec_lab"] = df["nm_tec_lab"].str.strip()
    df["dt_dig"] = pd.to_datetime(df["dt_dig"], errors="coerce", format="ISO8601").dt.strftime("%Y-%m-%d")
    df["dt_envio_ds"] = pd.to_datetime(df["dt_envio_ds"], errors="coerce", format="ISO8601").dt.strftime("%Y-%m-%d")
    df["n_ovos"] = pd.to_numeric(df["n_ovos"], errors="coerce")
    df["obs"] = df["obs"].str.strip()   

    df = df.dropna(how='all')
    df = df.drop_duplicates()

    return df

def carregar(df: pd.DataFrame, caminho_db: Path, tabela: str, SCHEMA) -> int:
    """Recria a tabela a partir do df. A planilha é a fonte da verdade, então
    rodar de novo substitui os dados em vez de duplicá-los. Tudo acontece numa
    única transação: se a inserção falhar, a tabela anterior é preservada."""
    caminho_db.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(caminho_db)) as conexao:
        with conexao:
            conexao.executescript(f"BEGIN; DROP TABLE IF EXISTS {tabela}; {SCHEMA}")
            df.to_sql(tabela, conexao, if_exists="append", index=False)
        return conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]

