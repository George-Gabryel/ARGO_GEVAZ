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