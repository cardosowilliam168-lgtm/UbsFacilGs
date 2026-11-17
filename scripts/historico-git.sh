#!/usr/bin/env bash
# Monta o histórico Git do projeto em branches por entrega, com merges e tag final.
# Usa a identidade configurada na sua máquina (git config user.name / user.email).
# Uso, na raiz do projeto:  bash scripts/historico-git.sh
set -euo pipefail

git config user.name  >/dev/null || { echo "Configure antes: git config --global user.name \"Seu Nome\""; exit 1; }
git config user.email >/dev/null || { echo "Configure antes: git config --global user.email seu@email"; exit 1; }
[ -d .git ] && { echo "Já existe um repositório Git aqui."; exit 1; }

git init -q -b main

entrega() { # branch, mensagem, caminhos...
  local branch="$1" msg="$2"; shift 2
  git switch -q -c "$branch"
  git add "$@"
  git commit -q -m "$msg"
  git switch -q main
  git merge -q --no-ff "$branch" -m "Merge branch '$branch'"
}

# base do repositório direto na main
git add README.md LICENSE .gitignore CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md .github/ISSUE_TEMPLATE
git commit -q -m "chore: estrutura inicial do repositório"

entrega docs/d1-processo   "docs(d1): backlog, roteiro de entrevista e decisões de processo (ADR)" docs/backlog.md docs/roteiro-entrevista.md docs/decisoes
entrega docs/sprints       "docs(sprints): templates de daily e retrospectiva" docs/sprints
entrega feat/d2-bpmn       "feat(d2): diagramas BPMN AS-IS e TO-BE (imagens e modelos)" diagramas bizagi
entrega feat/d3-prototipo  "feat(d3): protótipo com 6 telas (login, início, agendamento, comprovante, fila virtual e painel)" pencil
entrega feat/d4-storyboard "feat(d4): storyboard da jornada do cidadão com 8 quadros" storyboard
entrega feat/entrega-pdf   "docs(entrega): documento único com D1 a D4 e referências" entrega
entrega ci/validacao       "ci: valida modelos BPMN e arquivos obrigatórios da entrega" .github/workflows scripts

git tag -a v1.0.0 -m "Entrega GS 2026.2 — UBS Fácil"
echo
git log --oneline --graph --decorate
echo
echo "Próximos passos:"
echo "  1) Crie um repositório (público ou privado, conforme combinado com o professor) no GitHub chamado UbsFacilGs."
echo "  2) git remote add origin https://github.com/cardosowilliam168-lgtm/UbsFacilGs.git"
echo "  3) git push -u origin main --tags"
echo "  4) bash scripts/criar_issues.sh   (requer gh auth login)"
