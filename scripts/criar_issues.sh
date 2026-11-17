#!/usr/bin/env bash
# Cria labels e uma issue por requisito do Backlog. Requer GitHub CLI autenticado (gh auth login).
set -euo pipefail

gh label create requisito   --color 0F4C81 --description "Item do Product Backlog" --force
gh label create funcional   --color 17A398 --force
gh label create nao-funcional --color 6B7785 --force
gh label create must   --color D93025 --force
gh label create should --color E8A317 --force
gh label create could  --color 9AA5B1 --force
gh label create sprint-1 --color 2E7D32 --force
gh label create sprint-2 --color 1565C0 --force
gh label create futuro   --color 7B1FA2 --force

issue() { # id, titulo, labels, corpo
  gh issue create --title "$1 — $2" --label "requisito,$3" --body "$4"
}

issue RF01 "Cadastro e login" "funcional,must,sprint-1" "Como cidadão, quero me cadastrar e entrar com CPF e Cartão SUS para acessar meus agendamentos."
issue RF02 "Agendar consulta" "funcional,must,sprint-1" "Como cidadão, quero escolher UBS, atendimento, dia e horário disponíveis para marcar minha consulta sem ir à unidade."
issue RF03 "Confirmação com comprovante e QR Code" "funcional,must,sprint-1" "Como cidadão, quero receber a confirmação com comprovante e QR Code para ter segurança de que a vaga é minha."
issue RF04 "Lembrete 24 h antes" "funcional,must,sprint-2" "Como cidadão, quero receber lembrete 24 h antes e poder confirmar ou cancelar a presença com um toque."
issue RF05 "Cancelar, remarcar e lista de espera" "funcional,must,sprint-2" "Como cidadão, quero cancelar ou remarcar e ver a vaga liberada para outra pessoa da lista de espera."
issue RF06 "Check-in e fila virtual" "funcional,must,sprint-2" "Como cidadão, quero fazer check-in por QR Code e acompanhar minha posição e o tempo estimado na fila virtual."
issue RF07 "Painel da recepção e agendamento assistido" "funcional,should,sprint-2" "Como recepcionista, quero um painel com a fila do dia e o agendamento assistido para quem não usa smartphone."
issue RF08 "Histórico de consultas e faltas" "funcional,could,futuro" "Como cidadão, quero consultar o histórico de consultas e faltas."
issue RNF01 "Proteção de dados (LGPD)" "nao-funcional,must,sprint-1" "Proteção de dados pessoais conforme a LGPD, com consentimento explícito e acesso restrito por perfil."
issue RNF02 "Usabilidade e acessibilidade" "nao-funcional,must,sprint-1" "Fonte ampliada, alto contraste, botões grandes e linguagem simples para público idoso."
issue RNF03 "Desempenho" "nao-funcional,should,sprint-2" "Consulta de horários disponíveis em até 3 segundos em uso normal."
issue RNF04 "Compatibilidade" "nao-funcional,should,sprint-2" "Aplicativo Android e iOS e painel web responsivo."
issue RNF05 "Integração com o e-SUS APS" "nao-funcional,could,futuro" "Integração com o e-SUS APS por padrões abertos."
echo "Issues criadas."
