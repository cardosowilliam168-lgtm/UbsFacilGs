import os, sys, tempfile
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import app as ubs


@pytest.fixture()
def c(tmp_path, monkeypatch):
    monkeypatch.setattr(ubs, "DB_PATH", str(tmp_path / "t.db"))
    ubs.init_db()
    ubs.app.config["TESTING"] = True
    return ubs.app.test_client()


def entrar(c, cpf):
    return c.post("/", data={"cpf": cpf}, follow_redirects=True)


def vaga_hoje_livre():
    with ubs.app.app_context():
        # Usa um dia futuro para não depender do horário do teste
        from datetime import date, timedelta
        d = (date.today() + timedelta(days=2)).isoformat()
        return [v["id"] for v in ubs.vagas_livres(1, 1, d)], d


def test_cpf_valido():
    assert ubs.cpf_valido("529.982.247-25")
    assert not ubs.cpf_valido("111.111.111-11")
    assert not ubs.cpf_valido("123")


def test_login_cpf_invalido(c):
    r = entrar(c, "12345678900")
    assert "CPF inválido" in r.get_data(as_text=True)


def test_cadastro_exige_lgpd(c):
    r = c.post("/", data={"cpf": "16899535009", "nome": "Novo"}, follow_redirects=True)
    assert "LGPD" in r.get_data(as_text=True)
    r = c.post("/", data={"cpf": "16899535009", "nome": "Novo", "lgpd": "1"}, follow_redirects=True)
    assert "Olá, Novo" in r.get_data(as_text=True)


def test_agendar_gera_comprovante_e_qr(c):
    entrar(c, "52998224725")
    vagas, dia = vaga_hoje_livre()
    r = c.post("/agendar", data={"ubs": 1, "atendimento": 1, "dia": dia, "vaga": vagas[0]}, follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "Consulta agendada" in html and "UBS-" in html
    cod = html.split("UBS-")[1][:8]
    qr = c.get(f"/qr/UBS-{cod}.svg")
    assert qr.status_code == 200 and b"<svg" in qr.data


def test_vaga_nao_pode_ter_dois_agendamentos(c):
    vagas, dia = vaga_hoje_livre()
    entrar(c, "52998224725")
    c.post("/agendar", data={"ubs": 1, "atendimento": 1, "dia": dia, "vaga": vagas[0]})
    c.get("/sair"); entrar(c, "11144477735")
    r = c.post("/agendar", data={"ubs": 1, "atendimento": 1, "dia": dia, "vaga": vagas[0]}, follow_redirects=True)
    assert "acabou de ser ocupado" in r.get_data(as_text=True)


def test_cancelar_libera_vaga_e_promove_lista_de_espera(c):
    vagas, dia = vaga_hoje_livre()
    entrar(c, "52998224725")
    r = c.post("/agendar", data={"ubs": 1, "atendimento": 1, "dia": dia, "vaga": vagas[0]}, follow_redirects=True)
    cod = "UBS-" + r.get_data(as_text=True).split("UBS-")[1][:8]
    c.get("/sair"); entrar(c, "11144477735")
    c.post("/lista-espera", data={"ubs": 1, "atendimento": 1, "dia": dia})
    c.get("/sair"); entrar(c, "52998224725")
    r = c.post(f"/confirmar/{cod}", data={"acao": "cancelar"}, follow_redirects=True)
    assert "vaga foi liberada" in r.get_data(as_text=True)
    with ubs.app.app_context():
        ativo = ubs.db().execute("SELECT c.nome FROM agendamento a JOIN cidadao c ON c.id=a.cidadao_id WHERE a.vaga_id=? AND a.status!='cancelado'", (vagas[0],)).fetchone()
        assert ativo["nome"] == "José Lima"
        assert ubs.db().execute("SELECT COUNT(*) FROM lista_espera").fetchone()[0] == 0


def test_checkin_so_no_dia(c):
    vagas, dia = vaga_hoje_livre()
    entrar(c, "52998224725")
    r = c.post("/agendar", data={"ubs": 1, "atendimento": 1, "dia": dia, "vaga": vagas[0]}, follow_redirects=True)
    cod = "UBS-" + r.get_data(as_text=True).split("UBS-")[1][:8]
    r = c.post("/checkin", data={"codigo": cod}, follow_redirects=True)
    assert "só vale no dia da consulta" in r.get_data(as_text=True)


def test_checkin_fila_e_posicao(c):
    from datetime import date
    with ubs.app.app_context():
        v = ubs.db().execute("SELECT id FROM vaga WHERE data=? AND ubs_id=1 AND atendimento_id=1 ORDER BY hora LIMIT 2", (date.today().isoformat(),)).fetchall()
        ubs.criar_agendamento(1, v[0]["id"]); ubs.criar_agendamento(2, v[1]["id"])
        cods = [r["codigo"] for r in ubs.db().execute("SELECT codigo FROM agendamento ORDER BY id")]
    entrar(c, "52998224725")
    c.post("/checkin", data={"codigo": cods[0]})
    c.get("/sair"); entrar(c, "11144477735")
    r = c.post("/checkin", data={"codigo": cods[1]}, follow_redirects=True)
    assert "2º" in r.get_data(as_text=True)


def test_painel_restrito_a_recepcao(c):
    entrar(c, "52998224725")
    assert c.get("/recepcao").status_code == 403
    c.get("/sair"); entrar(c, "39053344705")
    assert c.get("/recepcao").status_code == 200


def test_agendamento_assistido(c):
    vagas, dia = vaga_hoje_livre()
    entrar(c, "39053344705")
    r = c.post("/recepcao/assistido", data={"ubs": 1, "atendimento": 1, "dia": dia, "vaga": vagas[1], "nome": "Dona Lurdes", "cpf": "168.995.350-09"}, follow_redirects=True)
    assert "Agendamento assistido criado" in r.get_data(as_text=True)
