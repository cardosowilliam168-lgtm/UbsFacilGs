# MVP do UBS Fácil

Sistema funcional que implementa os requisitos essenciais do Backlog: cadastro com LGPD, agendamento, comprovante com QR Code, cancelamento com lista de espera, check-in, fila virtual e painel da recepção.

| Camada | Tecnologia |
|---|---|
| Aplicação | Python 3 + Flask (HTML responsivo, acessível, fonte grande) |
| Banco de dados | SQLite ([`schema.sql`](schema.sql): 6 tabelas, chaves estrangeiras e índice que impede duas reservas na mesma vaga) |
| QR Code | biblioteca `segno` (SVG gerado no servidor) |
| Testes | `pytest` (10 testes automatizados) |
| Infraestrutura | execução local; testes rodam no GitHub Actions a cada push |

## Como rodar

```bash
cd app
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000. O banco `ubsfacil.db` é criado sozinho, com 2 UBS, 4 atendimentos e vagas dos próximos 6 dias.

| Perfil | CPF para entrar |
|---|---|
| Cidadã (Maria) | 529.982.247-25 |
| Cidadão (José) | 111.444.777-35 |
| Recepção | 390.533.447-05 |

## Testes

```bash
python -m pytest -q tests
```

## Roteiro de demonstração (2 minutos)

1. Entrar como Maria, **Agendar**, escolher UBS, atendimento, dia e horário.
2. Ver o **comprovante com QR Code**.
3. **Check-in** com o código e ver a **posição na fila**.
4. Entrar como recepção e mostrar o **painel** com a fila do dia, **Chamar** o paciente.
5. Mostrar o banco: `sqlite3 ubsfacil.db "select * from agendamento;"`.
6. Rodar `python -m pytest -q tests` e mostrar os testes passando.

## Mapa de requisitos

| Requisito | Onde |
|---|---|
| RF01 cadastro/login com CPF e LGPD | `/` |
| RF02 escolher UBS, atendimento, dia e horário | `/agendar` |
| RF03 comprovante com QR Code | `/comprovante/<código>` |
| RF04 confirmar ou cancelar com um toque | `/confirmar/<código>` (o envio do lembrete 24 h não está no MVP) |
| RF05 cancelar libera vaga e promove a lista de espera | `cancelar_agendamento()` |
| RF06 check-in e fila virtual | `/checkin`, `/fila` |
| RF07 painel e agendamento assistido | `/recepcao`, `/recepcao/assistido` |
| RNF01 LGPD, acesso por perfil | aceite no cadastro, painel restrito à recepção |
| RNF02 acessibilidade | fonte 18 px, alto contraste, botões grandes |

Limitações do MVP: sem envio real de notificações (lembrete e aviso da fila), sem integração com o e-SUS (RNF05, fora do escopo) e autenticação simplificada por CPF, adequada só para demonstração.
