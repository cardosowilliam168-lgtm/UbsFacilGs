# Product Backlog

Prioridade pelo método MoSCoW: **Must** (essencial ao MVP), **Should** (entra se houver capacidade), **Could** (fica para depois). Esforço em story points (escala de Fibonacci).

| ID | Tipo | Requisito | Prioridade | Pontos | Técnica de levantamento | Sprint |
|---|---|---|---|---|---|---|
| RF01 | Funcional | Como cidadão, quero me cadastrar e entrar com CPF e Cartão SUS para acessar meus agendamentos. | Must | 3 | Entrevista | 1 |
| RF02 | Funcional | Como cidadão, quero escolher UBS, atendimento, dia e horário disponíveis para marcar a consulta sem ir à unidade. | Must | 5 | Observação | 1 |
| RF03 | Funcional | Como cidadão, quero receber a confirmação com comprovante e QR Code para ter segurança de que a vaga é minha. | Must | 3 | Observação | 1 |
| RF04 | Funcional | Como cidadão, quero receber lembrete 24 h antes e confirmar ou cancelar a presença com um toque. | Must | 3 | Benchmarking | 2 |
| RF05 | Funcional | Como cidadão, quero cancelar ou remarcar e ver a vaga liberada para a lista de espera. | Must | 5 | Entrevista | 2 |
| RF06 | Funcional | Como cidadão, quero fazer check-in por QR Code e acompanhar posição e tempo estimado na fila virtual. | Must | 5 | Observação | 2 |
| RF07 | Funcional | Como recepcionista, quero um painel com a fila do dia e o agendamento assistido para quem não usa smartphone. | Should | 3 | Entrevista | 2 |
| RF08 | Funcional | Como cidadão, quero consultar meu histórico de consultas e faltas. | Could | 2 | Benchmarking | Futuro |
| RNF01 | Não funcional | Segurança: proteção de dados pessoais conforme a LGPD, com consentimento explícito e acesso por perfil. | Must | 3 | Análise documental | 1 |
| RNF02 | Não funcional | Usabilidade e acessibilidade: fonte ampliada, alto contraste, botões grandes e linguagem simples. | Must | 3 | Observação | 1 |
| RNF03 | Não funcional | Desempenho: consulta de horários disponíveis em até 3 segundos em uso normal. | Should | 2 | Benchmarking | 2 |
| RNF04 | Não funcional | Portabilidade: aplicativo Android e iOS e painel web responsivo. | Should | 2 | Benchmarking | 2 |
| RNF05 | Não funcional | Interoperabilidade: integração com o e-SUS APS por padrões abertos. | Could | 8 | Benchmarking | Futuro |

## Critérios de aceite dos itens essenciais

- **RF01:** o cadastro só é concluído com CPF válido e aceite do termo de dados; após o login, o cidadão vê a tela inicial com a próxima consulta.
- **RF02:** só aparecem horários livres da UBS escolhida; sem horário disponível, o aplicativo oferece a lista de espera.
- **RF03:** o comprovante mostra atendimento, data, hora, unidade e QR Code; o agendamento aparece no painel da recepção.
- **RF04:** o lembrete é enviado 24 horas antes; confirmar ou cancelar exige um único toque.
- **RF05:** ao cancelar, a vaga volta a ficar disponível de imediato; o primeiro da lista de espera é notificado.
- **RF06:** o check-in só é aceito no dia da consulta, com QR Code válido; a posição na fila é atualizada a cada chamada.

## Plano das Sprints do produto

| | Sprint 1 (semana 1) | Sprint 2 (semana 2) |
|---|---|---|
| Meta | O cidadão consegue se cadastrar, agendar e receber o comprovante da consulta. | Reduzir faltas e filas no dia do atendimento. |
| Itens | RF01, RF02, RF03, RNF01, RNF02 | RF04, RF05, RF06, RF07, RNF03, RNF04 |
| Pontos | 17 | 20 (13 Must e 7 Should) |
| Incremento | I1, núcleo de agendamento | I2, fila virtual e lembretes |

Capacidade estimada: 18 pontos por Sprint. Os 7 pontos Should da Sprint 2 saem do escopo se faltar capacidade.
