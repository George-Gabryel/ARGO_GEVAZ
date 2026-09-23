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
