from pathlib import Path
import src.extract as ex
import src.load as load
import src.sqlite_schema as SCHEMA


CAMINHO_XLSX = "dados/Total Ovtrampas.xlsx"
ABA = "CICLO 1"
CAMINHO_DB = Path("saida/total_ovt.db")
TABELA = "ovt"
criar_tabela = SCHEMA.criar_tabela()

CAMINHO_XLSX_EDL = "dados/TOTAL DE EDL POR DS.xlsx"
ABA_RESUMO_EDL = "TOTAL DE PE E EDL"
CAMINHO_DB_EDL = Path("saida/edl_por_ds.db")

CAMINHO_XLSX_GEO = "dados/Georreferenciamento OVT 2026 ATUALIZAÇÃO.xlsx"
LINHA_CABECALHO_GEO = 2  # as duas primeiras linhas são título
CAMINHO_DB_GEO = Path("saida/georreferenciamento_ovt.db")
TABELA_GEO = "georef_ovt"


def ovitrampas() -> None:
    dado_bruto = ex.extrair(CAMINHO_XLSX, ABA)
    print(f"Lidas {len(dado_bruto)} linhas da aba '{ABA}' de {CAMINHO_XLSX}")

    tratado = load.transformar(dado_bruto)
    print(f"Restaram {len(tratado)} linhas após a limpeza")

    total = load.carregar(tratado, CAMINHO_DB, TABELA, criar_tabela)
    print(f"Tabela '{TABELA}' agora tem {total} registros em {CAMINHO_DB}")


def edl_por_ds() -> None:
    abas = ex.extrair(CAMINHO_XLSX_EDL, None, header=None)
    print(f"Lidas {len(abas)} abas de {CAMINHO_XLSX_EDL}")

    tabelas = {
        "edl": (load.transformar_edl(abas), SCHEMA.criar_tabela_edl()),
    }
    resumo_ds, resumo_bairro = load.transformar_resumo_edl(abas[ABA_RESUMO_EDL])
    tabelas["resumo_ds"] = (resumo_ds, SCHEMA.criar_tabela_resumo_ds())
    tabelas["resumo_bairro"] = (resumo_bairro, SCHEMA.criar_tabela_resumo_bairro())

    for tabela, (tratado, schema) in tabelas.items():
        total = load.carregar(tratado, CAMINHO_DB_EDL, tabela, schema)
        print(f"Tabela '{tabela}' agora tem {total} registros em {CAMINHO_DB_EDL}")


def georreferenciamento() -> None:
    abas = ex.extrair(CAMINHO_XLSX_GEO, None, header=LINHA_CABECALHO_GEO)
    print(f"Lidas {sum(len(df) for df in abas.values())} linhas de {len(abas)} abas de {CAMINHO_XLSX_GEO}")

    tratado = load.transformar_georef(abas)
    print(f"Restaram {len(tratado)} linhas após a limpeza")

    total = load.carregar(tratado, CAMINHO_DB_GEO, TABELA_GEO, SCHEMA.criar_tabela_georef())
    print(f"Tabela '{TABELA_GEO}' agora tem {total} registros em {CAMINHO_DB_GEO}")


def main() -> None:
    ovitrampas()
    edl_por_ds()
    georreferenciamento()

if __name__ == "__main__":
    main()
