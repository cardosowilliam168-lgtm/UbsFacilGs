# ADR-001 — Ciclo de vida incremental

- **Status:** aceita
- **Contexto:** o núcleo do sistema (agendar, confirmar, cancelar) é conhecido, mas a rotina de cada UBS e o formato da fila só se confirmam com o uso. Prazo de 2 semanas e equipe de 3 pessoas.
- **Decisão:** adotar o ciclo de vida incremental, com três incrementos: I1 núcleo de agendamento, I2 fila virtual e lembretes, I3 evolução (histórico e integração).
- **Alternativas descartadas:** cascata (validação só no fim e pouca tolerância a mudança), espiral (custo de gestão de risco desproporcional) e prototipação pura (não gera produto evolutivo; usada como técnica dentro dos incrementos).
- **Consequências:** valor entregue cedo e risco reduzido; exige disciplina de priorização do Backlog.
