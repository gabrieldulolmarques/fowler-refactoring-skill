# fowler-refactoring-skill

O catálogo de refatorações de Martin Fowler (*Refactoring*, 2ª ed., 2018) empacotado como
[Agent Skills](https://agentskills.io) para agentes de código: uma skill, `fowler-refactoring`,
que relaciona os 24 code smells às refatorações que os corrigem, com um arquivo de referência por
refatoração (mecânica, um exemplo em C# e passos de verificação).

## Estrutura

```
.claude-plugin/plugin.json # transforma o pacote em um plugin do Claude Code
LICENSE # CC BY 4.0
NOTICE # crédito a Fowler e à Addison-Wesley; o que a licença cobre
CATALOG.md # a especificação: 66 refatorações, 24 smells, formato dos arquivos
agents/
├── fowler-analyst.md # somente leitura: encontra smells e devolve um plano curto
└── fowler-implementer.md # aplica uma refatoração, testando após cada passo
skills/fowler-refactoring/
├── SKILL.md # fluxo smell → refatoração → arquivo, índice de smells, tabela das 66
└── references/ # smells.md, discipline.md e um <slug>.md por refatoração, em uma pasta por capítulo
```

Só a descrição da skill fica no contexto do agente. O corpo é carregado quando a skill é
usada, e o arquivo de cada refatoração só quando o agente o abre.

## Agentes

Dois subagentes que usam a skill:

- `fowler-analyst` lê o código indicado na chamada, nomeia os smells e devolve um plano
  curto: onde, qual smell, qual refatoração, se há testes cobrindo e o risco. Nunca
  edita.
- `fowler-implementer` aplica um item desse plano (ou uma refatoração nomeada), seguindo
  a mecânica com um build e uma execução dos testes após cada passo.

Revise o plano antes de entregar um item ao implementador. Os comandos de build e de teste
vêm da chamada ou das instruções do próprio projeto, não deste pacote.

## Como usar

- **Qualquer cliente de Agent Skills** (Claude Code, Codex, OpenCode): crie um link da pasta
  `skills/fowler-refactoring` na pasta de skills do projeto (no Windows, uma junção:
  `New-Item -ItemType Junction`).
- **Plugin do Claude Code**: `claude --plugin-dir <caminho-deste-repositório>`. A skill e os agentes
  ficam então com o prefixo `fowler-refactoring:<name>`.

Use uma só via por projeto, ou o Claude Code verá a skill duas vezes.

## Licença e crédito

[CC BY 4.0](LICENSE): livre para compartilhar e adaptar para qualquer finalidade, desde que você dê crédito a este
pacote **e** ao livro em que ele se baseia:

> Martin Fowler. *Refactoring: Improving the Design of Existing Code*. 2nd ed. Boston:
> Addison-Wesley (Pearson Education), 2018. ISBN 978-0-13-475759-9.

A licença cobre apenas o conteúdo próprio deste pacote, não o livro (veja [NOTICE](NOTICE)).
A motivação e a mecânica na skill são parafraseadas, com capítulo e página citados;
nada é copiado do livro, de refactoring.com, do *Dive Into
Refactoring* da Refactoring.Guru, nem do pacote de replicação de Chen Kuang Piao et al. Os nomes das refatorações, os nomes
antigos e as inversas vêm dos cabeçalhos de seção do livro e da edição web do livro para as cinco
refatorações só da web. Os exemplos em C# são originais.
