# Modelos BPMN

- `as-is.bpmn` e `to-be.bpmn`: modelos em BPMN 2.0 (XML), com as coordenadas do diagrama.
- `as-is.bpm` e `to-be.bpm`: arquivos nativos do Bizagi Modeler, gerados a partir dos `.bpmn`.

## Como gerar os arquivos .bpm no Bizagi Modeler

1. Abra o Bizagi Modeler e crie um modelo em branco.
2. Na aba **Exportar/Importar** (Export/Import), no grupo **Importar**, clique em **BPMN**.
3. Selecione `as-is.bpmn` e clique em **Abrir**. O diagrama aparece pronto para edição.
4. Confira lanes, gateways e o data object. Ajuste o que estiver desalinhado.
5. Salve com **Arquivo > Salvar como**, com o nome `as-is.bpm`, nesta pasta.
6. Repita os passos com `to-be.bpmn`, salvando como `to-be.bpm`.

Se a importação falhar, redesenhe a partir das imagens em `../diagramas/`.
