# Como trabalhamos neste repositório

## Branches

- `main`: sempre estável; recebe alterações por Pull Request.
- `feat/<assunto>`: nova entrega ou funcionalidade (ex.: `feat/d3-prototipo`).
- `docs/<assunto>`: documentação (ex.: `docs/d1-backlog`).
- `fix/<assunto>`: correções (ex.: `fix/gateway-rotulo`).

## Commits (Conventional Commits)

Formato: `tipo(escopo): descrição no imperativo, em português`.

| Tipo | Uso |
|---|---|
| `feat` | entrega nova (diagrama, tela, quadro) |
| `docs` | texto, backlog, ADR, README |
| `fix` | correção de erro em algo já entregue |
| `chore` | estrutura, arquivos de apoio |
| `ci` | validação automática |

Exemplos: `feat(d2): adiciona diagrama BPMN TO-BE`, `docs(d1): registra decisão pelo ciclo incremental`.

## Pull Requests

1. Abra o PR a partir de uma branch.
2. Preencha o checklist do template.
3. O outro integrante revisa antes do merge (o autor não aprova o próprio PR).

## Issues

Cada requisito do Backlog é uma issue (`RF01`, `RNF02`...), com label de tipo, prioridade (MoSCoW) e Sprint. Os arquivos de apoio estão em `scripts/`.
