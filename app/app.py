"""UBS Fácil — MVP (Flask + SQLite).

Rodar:  pip install -r requirements.txt  &&  python app.py
Abrir:  http://127.0.0.1:5000
"""
import io
import os
import secrets
import sqlite3
from datetime import date, datetime, timedelta

import segno
from flask import (Flask, Response, abort, flash, g, redirect, render_template,
                   request, session, url_for)

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("UBS_DB", os.path.join(BASE, "ubsfacil.db"))
MIN_POR_PACIENTE = 5  # tempo médio estimado por atendimento

app = Flask(__name__)
app.secret_key = os.environ.get("UBS_SECRET", "dev-only-troque-em-producao")


# ---------------------------------------------------------------- banco
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db(seed=True):
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(open(os.path.join(BASE, "schema.sql"), encoding="utf-8").read())
    if seed and conn.execute("SELECT COUNT(*) FROM ubs").fetchone()[0] == 0:
        conn.execute("INSERT INTO ubs(id,nome,bairro) VALUES (1,'UBS Modelo','Vila Mariana'),(2,'UBS Jardim Paulista','Jardim Paulista')")
        conn.executemany("INSERT INTO atendimento(nome) VALUES (?)",
                         [("Clínica Geral",), ("Enfermagem",), ("Vacinação",), ("Pediatria",)])
        conn.executemany("INSERT INTO cidadao(nome,cpf,cartao_sus,aceite_lgpd,perfil) VALUES (?,?,?,?,?)", [
            ("Maria Souza", "52998224725", "898001234567890", 1, "cidadao"),
            ("José Lima", "11144477735", "898009876543210", 1, "cidadao"),
            ("Ana Recepção", "39053344705", None, 1, "recepcao"),
        ])
        hoje = date.today()
        horas = [f"{h:02d}:{m:02d}" for h in range(7, 18) for m in (0, 30)]
        vagas = [(u, a, (hoje + timedelta(days=d)).isoformat(), h)
                 for u in (1, 2) for a in (1, 2, 3, 4) for d in range(0, 6) for h in horas]
        conn.executemany("INSERT INTO vaga(ubs_id,atendimento_id,data,hora) VALUES (?,?,?,?)", vagas)
        conn.commit()
    conn.commit()
    conn.close()


# ---------------------------------------------------------------- regras
def cpf_valido(cpf: str) -> bool:
    n = "".join(c for c in cpf if c.isdigit())
    if len(n) != 11 or n == n[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(n[k]) * (i + 1 - k) for k in range(i))
        if (soma * 10 % 11) % 10 != int(n[i]):
            return False
    return True


def agora():
    return datetime.now().isoformat(timespec="seconds")


def vagas_livres(ubs_id, atend_id, dia):
    return db().execute("""
        SELECT v.id, v.hora FROM vaga v
        WHERE v.ubs_id=? AND v.atendimento_id=? AND v.data=?
          AND NOT EXISTS (SELECT 1 FROM agendamento a WHERE a.vaga_id=v.id
                          AND a.status NOT IN ('cancelado','faltou'))
          AND (v.data > date('now','localtime') OR v.hora > strftime('%H:%M','now','localtime'))
        ORDER BY v.hora""", (ubs_id, atend_id, dia)).fetchall()


def criar_agendamento(cidadao_id, vaga_id, assistido=False):
    codigo = "UBS-" + secrets.token_hex(4).upper()
    try:
        db().execute("""INSERT INTO agendamento(cidadao_id,vaga_id,codigo,assistido,criado_em)
                        VALUES (?,?,?,?,?)""", (cidadao_id, vaga_id, codigo, int(assistido), agora()))
        db().commit()
    except sqlite3.IntegrityError:
        db().rollback()
        return None  # vaga tomada por outra pessoa
    return codigo


def cancelar_agendamento(ag_id):
    """Cancela e libera a vaga; o primeiro da lista de espera é promovido (RF05)."""
    ag = db().execute("""SELECT a.*, v.ubs_id, v.atendimento_id, v.data FROM agendamento a
                         JOIN vaga v ON v.id=a.vaga_id WHERE a.id=?""", (ag_id,)).fetchone()
    if not ag or ag["status"] in ("cancelado", "atendido"):
        return None
    db().execute("UPDATE agendamento SET status='cancelado' WHERE id=?", (ag_id,))
    prox = db().execute("""SELECT * FROM lista_espera WHERE ubs_id=? AND atendimento_id=? AND data=?
                           ORDER BY id LIMIT 1""", (ag["ubs_id"], ag["atendimento_id"], ag["data"])).fetchone()
    promovido = None
    if prox:
        cod = "UBS-" + secrets.token_hex(4).upper()
        db().execute("""INSERT INTO agendamento(cidadao_id,vaga_id,codigo,criado_em) VALUES (?,?,?,?)""",
                     (prox["cidadao_id"], ag["vaga_id"], cod, agora()))
        db().execute("DELETE FROM lista_espera WHERE id=?", (prox["id"],))
        promovido = prox["cidadao_id"]
    db().commit()
    return promovido


def posicao_na_fila(ag):
    """Posição = quantos já fizeram check-in antes na mesma UBS/atendimento/dia + 1."""
    r = db().execute("""
        SELECT COUNT(*) FROM agendamento a JOIN vaga v ON v.id=a.vaga_id
        WHERE a.status='em_fila' AND (a.checkin_em < ? OR (a.checkin_em = ? AND a.id < ?))
          AND v.ubs_id=(SELECT ubs_id FROM vaga WHERE id=?) AND v.data=?""",
        (ag["checkin_em"], ag["checkin_em"], ag["id"], ag["vaga_id"], date.today().isoformat())).fetchone()[0]
    return r + 1


BASE_SQL = """SELECT a.*, v.data, v.hora, u.nome AS ubs, u.bairro, t.nome AS atendimento
              FROM agendamento a JOIN vaga v ON v.id=a.vaga_id
              JOIN ubs u ON u.id=v.ubs_id JOIN atendimento t ON t.id=v.atendimento_id"""


def usuario():
    uid = session.get("uid")
    return db().execute("SELECT * FROM cidadao WHERE id=?", (uid,)).fetchone() if uid else None


def exige_login(perfil=None):
    u = usuario()
    if not u:
        abort(redirect(url_for("login")))
    if perfil and u["perfil"] != perfil:
        abort(403)
    return u


# ---------------------------------------------------------------- rotas: cidadão
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cpf = "".join(c for c in request.form.get("cpf", "") if c.isdigit())
        if not cpf_valido(cpf):
            flash("CPF inválido. Confira os 11 números.", "erro")
            return render_template("login.html")
        u = db().execute("SELECT * FROM cidadao WHERE cpf=?", (cpf,)).fetchone()
        if not u:
            if not request.form.get("lgpd"):
                flash("Para criar sua conta, aceite o termo de uso dos dados (LGPD).", "erro")
                return render_template("login.html", cpf=cpf, novo=True)
            nome = request.form.get("nome", "").strip()
            if not nome:
                flash("Informe seu nome para criar a conta.", "erro")
                return render_template("login.html", cpf=cpf, novo=True)
            cur = db().execute("INSERT INTO cidadao(nome,cpf,cartao_sus,aceite_lgpd) VALUES (?,?,?,1)",
                               (nome, cpf, request.form.get("sus") or None))
            db().commit()
            u = db().execute("SELECT * FROM cidadao WHERE id=?", (cur.lastrowid,)).fetchone()
        session["uid"] = u["id"]
        return redirect(url_for("recepcao") if u["perfil"] == "recepcao" else url_for("inicio"))
    if "novo" in request.args:
        return render_template("login.html", novo=True)
    return render_template("login.html")


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


@app.route("/inicio")
def inicio():
    u = exige_login()
    prox = db().execute(BASE_SQL + """ WHERE a.cidadao_id=? AND a.status IN ('agendado','confirmado','em_fila')
                        AND (v.data > date('now','localtime') OR v.data = date('now','localtime'))
                        ORDER BY v.data, v.hora LIMIT 1""", (u["id"],)).fetchone()
    espera = db().execute("""SELECT le.*, u.nome AS ubs, t.nome AS atendimento FROM lista_espera le
                             JOIN ubs u ON u.id=le.ubs_id JOIN atendimento t ON t.id=le.atendimento_id
                             WHERE le.cidadao_id=?""", (u["id"],)).fetchall()
    return render_template("inicio.html", u=u, prox=prox, espera=espera, hoje=date.today().isoformat())


@app.route("/agendar", methods=["GET", "POST"])
def agendar():
    u = exige_login()
    ubs = db().execute("SELECT * FROM ubs ORDER BY nome").fetchall()
    ats = db().execute("SELECT * FROM atendimento ORDER BY nome").fetchall()
    hoje = date.today()
    dias = [(hoje + timedelta(days=i)).isoformat() for i in range(6)]
    f = request.values
    livres = None
    if f.get("ubs") and f.get("atendimento") and f.get("dia"):
        livres = vagas_livres(int(f["ubs"]), int(f["atendimento"]), f["dia"])
    if request.method == "POST" and f.get("vaga"):
        cod = criar_agendamento(u["id"], int(f["vaga"]))
        if not cod:
            flash("Esse horário acabou de ser ocupado. Escolha outro.", "erro")
            return redirect(url_for("agendar", ubs=f["ubs"], atendimento=f["atendimento"], dia=f["dia"]))
        return redirect(url_for("comprovante", codigo=cod))
    return render_template("agendar.html", u=u, ubs=ubs, ats=ats, dias=dias, livres=livres, f=f)


@app.route("/lista-espera", methods=["POST"])
def entrar_lista():
    u = exige_login()
    f = request.form
    db().execute("INSERT INTO lista_espera(cidadao_id,ubs_id,atendimento_id,data,criado_em) VALUES (?,?,?,?,?)",
                 (u["id"], int(f["ubs"]), int(f["atendimento"]), f["dia"], agora()))
    db().commit()
    flash("Você entrou na lista de espera. Avisamos assim que abrir uma vaga.", "ok")
    return redirect(url_for("inicio"))


def meu_agendamento(codigo, u):
    ag = db().execute(BASE_SQL + " WHERE a.codigo=?", (codigo,)).fetchone()
    if not ag or (ag["cidadao_id"] != u["id"] and u["perfil"] != "recepcao"):
        abort(404)
    return ag


@app.route("/comprovante/<codigo>")
def comprovante(codigo):
    u = exige_login()
    return render_template("comprovante.html", u=u, ag=meu_agendamento(codigo, u))


@app.route("/qr/<codigo>.svg")
def qr(codigo):
    buf = io.BytesIO()
    segno.make(codigo, error="m").save(buf, kind="svg", scale=8, border=2, dark="#0f2a4a")
    return Response(buf.getvalue(), mimetype="image/svg+xml")


@app.route("/confirmar/<codigo>", methods=["POST"])
def confirmar(codigo):
    u = exige_login()
    ag = meu_agendamento(codigo, u)
    acao = request.form.get("acao")
    if acao == "confirmar":
        db().execute("UPDATE agendamento SET status='confirmado' WHERE id=? AND status='agendado'", (ag["id"],))
        db().commit()
        flash("Presença confirmada. Até lá!", "ok")
    elif acao == "cancelar":
        cancelar_agendamento(ag["id"])
        flash("Consulta cancelada. A vaga foi liberada para outra pessoa.", "ok")
    return redirect(url_for("inicio"))


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    u = exige_login()
    if request.method == "POST":
        cod = request.form.get("codigo", "").strip().upper()
        ag = db().execute(BASE_SQL + " WHERE a.codigo=? AND a.cidadao_id=?", (cod, u["id"])).fetchone()
        if not ag:
            flash("Código não encontrado.", "erro")
        elif ag["data"] != date.today().isoformat():
            flash("O check-in só vale no dia da consulta.", "erro")
        elif ag["status"] not in ("agendado", "confirmado"):
            flash("Este agendamento não aceita check-in.", "erro")
        else:
            db().execute("UPDATE agendamento SET status='em_fila', checkin_em=? WHERE id=?", (agora(), ag["id"]))
            db().commit()
            return redirect(url_for("fila"))
    return render_template("checkin.html", u=u)


@app.route("/fila")
def fila():
    u = exige_login()
    ag = db().execute(BASE_SQL + """ WHERE a.cidadao_id=? AND a.status='em_fila'
                       ORDER BY a.checkin_em DESC LIMIT 1""", (u["id"],)).fetchone()
    if not ag:
        flash("Você ainda não fez check-in hoje.", "erro")
        return redirect(url_for("inicio"))
    pos = posicao_na_fila(ag)
    return render_template("fila.html", u=u, ag=ag, pos=pos, tempo=pos * MIN_POR_PACIENTE)


# ---------------------------------------------------------------- rotas: recepção
@app.route("/recepcao", methods=["GET", "POST"])
def recepcao():
    u = exige_login("recepcao")
    hoje = date.today().isoformat()
    if request.method == "POST":
        ac = request.form.get("acao")
        ag_id = request.form.get("id")
        if ac == "chamar":
            db().execute("UPDATE agendamento SET status='atendido' WHERE id=?", (ag_id,))
        elif ac == "faltou":
            db().execute("UPDATE agendamento SET status='faltou' WHERE id=?", (ag_id,))
        elif ac == "cancelar":
            cancelar_agendamento(int(ag_id))
        db().commit()
        return redirect(url_for("recepcao"))
    q = BASE_SQL + " WHERE v.data=? AND a.status NOT IN ('cancelado') ORDER BY (a.status='em_fila') DESC, a.checkin_em, a.id, v.hora"
    itens = db().execute(q, (hoje,)).fetchall()
    nomes = {r["id"]: r["nome"] for r in db().execute("SELECT id,nome FROM cidadao")}
    resumo = {s: sum(1 for i in itens if i["status"] == s) for s in ("agendado", "confirmado", "em_fila", "atendido", "faltou")}
    return render_template("recepcao.html", u=u, itens=itens, nomes=nomes, resumo=resumo, hoje=hoje)


@app.route("/recepcao/assistido", methods=["GET", "POST"])
def assistido():
    u = exige_login("recepcao")
    ubs = db().execute("SELECT * FROM ubs ORDER BY nome").fetchall()
    ats = db().execute("SELECT * FROM atendimento ORDER BY nome").fetchall()
    hoje = date.today()
    dias = [(hoje + timedelta(days=i)).isoformat() for i in range(6)]
    f = request.values
    livres = None
    if f.get("ubs") and f.get("atendimento") and f.get("dia"):
        livres = vagas_livres(int(f["ubs"]), int(f["atendimento"]), f["dia"])
    if request.method == "POST" and f.get("vaga"):
        cpf = "".join(c for c in f.get("cpf", "") if c.isdigit())
        if not cpf_valido(cpf) or not f.get("nome", "").strip():
            flash("Informe nome e CPF válido do cidadão.", "erro")
        else:
            c = db().execute("SELECT id FROM cidadao WHERE cpf=?", (cpf,)).fetchone()
            if not c:
                cur = db().execute("INSERT INTO cidadao(nome,cpf,aceite_lgpd) VALUES (?,?,1)", (f["nome"].strip(), cpf))
                db().commit()
                cid = cur.lastrowid
            else:
                cid = c["id"]
            cod = criar_agendamento(cid, int(f["vaga"]), assistido=True)
            if cod:
                flash(f"Agendamento assistido criado. Código {cod}.", "ok")
                return redirect(url_for("recepcao"))
            flash("Horário ocupado. Escolha outro.", "erro")
    return render_template("assistido.html", u=u, ubs=ubs, ats=ats, dias=dias, livres=livres, f=f)


@app.errorhandler(403)
def proibido(_e):
    return render_template("erro.html", msg="Acesso restrito à recepção."), 403


@app.errorhandler(404)
def nao_achou(_e):
    return render_template("erro.html", msg="Página não encontrada."), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=False)
