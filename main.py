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

