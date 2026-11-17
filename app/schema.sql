-- Modelo de dados do UBS Fácil (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ubs (
    id      INTEGER PRIMARY KEY,
    nome    TEXT NOT NULL,
    bairro  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS atendimento (
    id      INTEGER PRIMARY KEY,
    nome    TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cidadao (
    id          INTEGER PRIMARY KEY,
    nome        TEXT NOT NULL,
    cpf         TEXT NOT NULL UNIQUE,
    cartao_sus  TEXT,
    aceite_lgpd INTEGER NOT NULL DEFAULT 0,
    perfil      TEXT NOT NULL DEFAULT 'cidadao' CHECK (perfil IN ('cidadao','recepcao'))
);

-- Cada linha é uma vaga (horário de um atendimento em uma UBS).
CREATE TABLE IF NOT EXISTS vaga (
    id              INTEGER PRIMARY KEY,
    ubs_id          INTEGER NOT NULL REFERENCES ubs(id),
    atendimento_id  INTEGER NOT NULL REFERENCES atendimento(id),
    data            TEXT NOT NULL,      -- AAAA-MM-DD
    hora            TEXT NOT NULL,      -- HH:MM
    UNIQUE (ubs_id, atendimento_id, data, hora)
);

CREATE TABLE IF NOT EXISTS agendamento (
    id          INTEGER PRIMARY KEY,
    cidadao_id  INTEGER NOT NULL REFERENCES cidadao(id),
    vaga_id     INTEGER NOT NULL REFERENCES vaga(id),
    codigo      TEXT NOT NULL UNIQUE,   -- vai no QR Code
    status      TEXT NOT NULL DEFAULT 'agendado'
                CHECK (status IN ('agendado','confirmado','em_fila','atendido','cancelado','faltou')),
    assistido   INTEGER NOT NULL DEFAULT 0,
    checkin_em  TEXT,
    criado_em   TEXT NOT NULL
);
-- Uma vaga só pode ter um agendamento ativo.
CREATE UNIQUE INDEX IF NOT EXISTS ux_vaga_ativa
    ON agendamento(vaga_id) WHERE status NOT IN ('cancelado','faltou');

CREATE TABLE IF NOT EXISTS lista_espera (
    id              INTEGER PRIMARY KEY,
    cidadao_id      INTEGER NOT NULL REFERENCES cidadao(id),
    ubs_id          INTEGER NOT NULL REFERENCES ubs(id),
    atendimento_id  INTEGER NOT NULL REFERENCES atendimento(id),
    data            TEXT NOT NULL,
    criado_em       TEXT NOT NULL,
    notificado      INTEGER NOT NULL DEFAULT 0
);
