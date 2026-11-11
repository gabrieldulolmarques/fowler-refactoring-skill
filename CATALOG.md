# Especificação do catálogo

A especificação a partir da qual a skill foi escrita e contra a qual é conferida: uma skill,
`fowler-refactoring`, com um arquivo de referência por refatoração, os smells (cheiros de código) e a disciplina,
e o formato dos arquivos.

Fontes: Fowler, *Refactoring*, 2ª ed. (2018), capítulos 2–4 e 6–12, e o catálogo online
([refactoring.com/catalog](https://refactoring.com/catalog/), conferido em 2026-10-31), que
lista **66 refatorações**: as **61 do livro** mais **5 que só existem na edição
web** (marcadas como "web" na coluna Página).

A skill é genérica: ela ensina as refatorações, não o processo de nenhum projeto. Os exemplos
são C# simples com um domínio neutro (pedidos, clientes, faturas, contas), e nada faz referência
a um projeto, framework, engine ou fluxo de trabalho de equipe específico.

---

## 1. A skill

Uma skill, `fowler-refactoring`. Só a sua `description` fica no contexto do agente; o corpo de
`SKILL.md` é carregado quando a skill é usada, e cada arquivo de referência só quando o agente
o abre. O agente parte de um problema (um smell), não do nome de uma refatoração, então
um único ponto de entrada que roteia smell → refatoração → arquivo funciona melhor que 66
descrições concorrentes.

| Arquivo | Fonte | Conteúdo |
|---|---|---|
| `SKILL.md` | esta especificação | o fluxo smell → refatoração → arquivo, um índice rápido de smells e uma tabela das 66 refatorações (nome, quando, arquivo), agrupadas por capítulo (seção 4.1) |
| `references/smells.md` | cap. 3 | os 24 smells, sintomas e refatorações sugeridas (seção 3) |
| `references/discipline.md` | cap. 2 e 4 | testes primeiro, passos pequenos, commit após cada refatoração verde |
| `references/<chapter>/<slug>.md` (66 arquivos) | cap. 6–12, ou refactoring.com para as exclusivas da web | uma refatoração em cada: quando usar, mecânica, exemplo em C#, verificação (seção 4.2) |

O slug é o nome da refatoração em kebab-case. Exemplo: Extrair Função (Extract Function) →
`references/first-set/extract-function.md`. Os arquivos são agrupados em uma pasta por capítulo:
`first-set` (cap. 6), `encapsulation` (7), `moving-features` (8), `organizing-data` (9),
`conditional-logic` (10), `refactoring-apis` (11) e `inheritance` (12); uma refatoração exclusiva da web fica
no capítulo sob o qual a seção 2 a lista. A página do refactoring.com usa o nome em camelCase:
`https://refactoring.com/catalog/extractFunction.html`.

```
skills/
└── fowler-refactoring/
    ├── SKILL.md
    └── references/
        ├── smells.md
        ├── discipline.md
        ├── first-set/
        │   ├── extract-function.md
        │   └── ...
        ├── encapsulation/
        └── ... # 7 pastas de capítulo, 66 arquivos de refatoração no total
```

---

## 2. As 66 refatorações

Conferido com o livro em 2026-10-31, de forma mecânica a partir do texto do PDF: cada uma das 61 refatorações
do livro começa na **Página** indicada (edição impressa), as colunas **Antes / também** e
**Inversa** são o próprio cabeçalho de seção do livro (`formerly:`, `aka:`, `subsumes:`,
`inverse of:`), e todas as 575 referências cruzadas "Nome (página)" nos cap. 3–12 batem com a coluna
Página. Para as 5 refatorações exclusivas da web, nomes e apelidos vêm do refactoring.com.

**Nota de C#** é o que o arquivo de referência deve acrescentar porque os exemplos do livro são em JavaScript:
somente pontos genéricos de C#. Onde consta "—", o arquivo não tem seção de notas de C#.

### Capítulo 6: Um primeiro conjunto de refatorações

| # | Refatoração | Página | Antes / também | Inversa | Nota de C# |
|---|---|---|---|---|---|
| 1 | Extrair Função (Extract Function) | 106 | antes Extract Method | Internalizar Função | em C#, funções locais são uma opção para auxiliares usados em um só lugar |
| 2 | Internalizar Função (Inline Function) | 115 | antes Inline Method | Extrair Função | não internalize um método `virtual`/`override` nem uma implementação de interface sem verificar as outras implementações |
| 3 | Extrair Variável (Extract Variable) | 119 | antes Introduce Explaining Variable | Internalizar Variável | — |
| 4 | Internalizar Variável (Inline Variable) | 123 | antes Inline Temp | Extrair Variável | — |
| 5 | Mudar Declaração de Função (Change Function Declaration) | 124 | também Rename Function, Change Signature; antes Rename Method, Add Parameter, Remove Parameter | — | o compilador encontra chamadores diretos, não reflexão, buscas baseadas em string nem nomes serializados; em uma API pública, mantenha a assinatura antiga como um encaminhador `[Obsolete]` durante a migração |
| 6 | Encapsular Variável (Encapsulate Variable) | 132 | antes Encapsulate Field, Self-Encapsulate Field | — | campo público → campo privado + propriedade; um campo estático → propriedade estática |
| 7 | Renomear Variável (Rename Variable) | 137 | — | — | — |
| 8 | Introduzir Objeto de Parâmetros (Introduce Parameter Object) | 140 | — | — | uma classe, `record` ou `record struct` |
| 9 | Combinar Funções em Classe (Combine Functions into Class) | 144 | — | — | — |
| 10 | Combinar Funções em Transformação (Combine Functions into Transform) | 149 | — | — | idiomático em JavaScript; em C# costuma ser uma função que devolve um novo `record` enriquecido (expressões `with`), ou vira Combinar Funções em Classe |
| 11 | Dividir em Fases (Split Phase) | 154 | — | — | a estrutura de dados intermediária costuma ser um `record` |

### Capítulo 7: Encapsulamento

| # | Refatoração | Página | Antes / também | Inversa | Nota de C# |
|---|---|---|---|---|---|
| 12 | Encapsular Registro (Encapsulate Record) | 162 | antes Replace Record with Data Class | — | dados em dicionário, tupla, anônimos ou `dynamic` → uma classe ou `record` com propriedades |
| 13 | Encapsular Coleção (Encapsulate Collection) | 170 | — | — | exponha `IReadOnlyList<T>` / `IReadOnlyCollection<T>`, com métodos `Add`/`Remove`; uma interface somente leitura não impede o chamador de fazer cast de volta, então devolva uma cópia onde isso importar |
| 14 | Substituir Primitivo por Objeto (Replace Primitive with Object) | 174 | antes Replace Data Value with Object, Replace Type Code with Class | — | `string`/`int` com significado → tipo próprio (`record`, `readonly record struct`) ou `enum` |
| 15 | Substituir Variável Temporária por Consulta (Replace Temp with Query) | 178 | — | — | uma propriedade somente leitura ou um método; mantenha consultas caras como métodos |
| 16 | Extrair Classe (Extract Class) | 182 | — | Internalizar Classe | — |
| 17 | Internalizar Classe (Inline Class) | 186 | — | Extrair Classe | — |
| 18 | Ocultar Delegação (Hide Delegate) | 189 | — | Remover Intermediário | — |
| 19 | Remover Intermediário (Remove Middle Man) | 192 | — | Ocultar Delegação | — |
| 20 | Substituir Algoritmo (Substitute Algorithm) | 195 | — | — | — |

### Capítulo 8: Movendo recursos

| # | Refatoração | Página | Antes / também | Inversa | Nota de C# |
|---|---|---|---|---|---|
| 21 | Mover Função (Move Function) | 198 | antes Move Method | — | o destino pode ser outra classe, uma classe estática ou um método de extensão |
| 22 | Mover Campo (Move Field) | 207 | — | — | um campo persistido ou serializado só mantém o nome armazenado se o mapeamento também for atualizado |
| 23 | Mover Instruções para Função (Move Statements into Function) | 213 | — | Mover Instruções para os Chamadores | — |
| 24 | Mover Instruções para os Chamadores (Move Statements to Callers) | 217 | — | Mover Instruções para Função | — |
| 25 | Substituir Código Internalizado por Chamada de Função (Replace Inline Code with Function Call) | 222 | — | — | — |
| 26 | Deslocar Instruções (Slide Statements) | 223 | antes Consolidate Duplicate Conditional Fragments | — | — |
| 27 | Dividir Laço (Split Loop) | 227 | — | — | — |
| 28 | Substituir Laço por Pipeline (Replace Loop with Pipeline) | 231 | — | — | LINQ; atenção à execução adiada (enumere uma vez) e à alocação em caminhos críticos |
| 29 | Remover Código Morto (Remove Dead Code) | 237 | — | — | código sem chamadores estáticos ainda pode ser alcançado por reflexão, injeção de dependência ou serialização |

### Capítulo 9: Organizando dados

| # | Refatoração | Página | Antes / também | Inversa | Nota de C# |
|---|---|---|---|---|---|
| 30 | Dividir Variável (Split Variable) | 240 | antes Remove Assignments to Parameters, Split Temp | — | não há locais imutáveis (`const` só serve para constantes de tempo de compilação), então atribua cada nova variável uma única vez; renomear um parâmetro quebra chamadores que usam argumentos nomeados |
| 31 | Renomear Campo (Rename Field) | 244 | — | — | um campo serializado ou persistido só mantém o nome de transmissão com um atributo de mapeamento (p. ex. `[JsonPropertyName("oldName")]`) ou uma migração |
| 32 | Substituir Variável Derivada por Consulta (Replace Derived Variable with Query) | 248 | — | — | uma propriedade calculada somente leitura |
| 33 | Mudar Referência para Valor (Change Reference to Value) | 252 | — | Mudar Valor para Referência | `record`, `readonly record struct` ou uma classe imutável com igualdade por valor (`Equals`/`GetHashCode`) |
| 34 | Mudar Valor para Referência (Change Value to Reference) | 256 | — | Mudar Referência para Valor | um repositório ou registro que entrega a instância compartilhada |
| 35 | Substituir Literal Mágico (Replace Magic Literal) | web | Replace Magic Number with Symbolic Constant | — | `const` para valores de tempo de compilação, `static readonly` para o resto |

### Capítulo 10: Simplificando a lógica condicional

| # | Refatoração | Página | Antes / também | Inversa | Nota de C# |
|---|---|---|---|---|---|
| 36 | Decompor Condicional (Decompose Conditional) | 260 | — | — | — |
| 37 | Consolidar Expressão Condicional (Consolidate Conditional Expression) | 263 | — | — | — |
| 38 | Substituir Condicional Aninhada por Cláusulas de Guarda (Replace Nested Conditional with Guard Clauses) | 266 | — | — | — |
| 39 | Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism) | 272 | — | — | um `switch` sobre um código de tipo → membros `abstract`/`virtual` ou uma interface |
| 40 | Introduzir Caso Especial (Introduce Special Case) | 289 | antes Introduce Null Object | — | com tipos de referência anuláveis habilitados, o caso especial elimina as verificações de `?`/null nos pontos de chamada |
| 41 | Introduzir Asserção (Introduce Assertion) | 302 | — | — | `Debug.Assert` (removido dos builds de Release) |
| 42 | Substituir Flag de Controle por Break (Replace Control Flag with Break) | web | Remove Control Flag | — | — |

### Capítulo 11: Refatorando APIs

| # | Refatoração | Página | Antes / também | Inversa | Nota de C# |
|---|---|---|---|---|---|
| 43 | Separar Consulta de Modificador (Separate Query from Modifier) | 306 | — | — | — |
| 44 | Parametrizar Função (Parameterize Function) | 310 | antes Parameterize Method | — | — |
| 45 | Remover Argumento de Flag (Remove Flag Argument) | 314 | antes Replace Parameter with Explicit Methods | — | — |
| 46 | Preservar Objeto Inteiro (Preserve Whole Object) | 319 | — | — | — |
| 47 | Substituir Parâmetro por Consulta (Replace Parameter with Query) | 324 | antes Replace Parameter with Method | Substituir Consulta por Parâmetro | — |
| 48 | Substituir Consulta por Parâmetro (Replace Query with Parameter) | 327 | — | Substituir Parâmetro por Consulta | útil para remover a dependência de um estático ou singleton e tornar o código testável |
| 49 | Remover Método de Escrita (Remove Setting Method) | 331 | — | — | `{ get; }` ou `{ get; init; }` |
| 50 | Substituir Construtor por Função de Fábrica (Replace Constructor with Factory Function) | 334 | antes Replace Constructor with Factory Method | — | um método de fábrica estático; torne o construtor `private` ou `protected` |
| 51 | Substituir Função por Comando (Replace Function with Command) | 337 | antes Replace Method with Method Object | Substituir Comando por Função | — |
| 52 | Substituir Comando por Função (Replace Command with Function) | 344 | — | Substituir Função por Comando | — |
| 53 | Retornar Valor Modificado (Return Modified Value) | web | — | — | — |
| 54 | Substituir Código de Erro por Exceção (Replace Error Code with Exception) | web | — | — | não use exceções para fluxo de controle esperado |
| 55 | Substituir Exceção por Verificação Prévia (Replace Exception with Precheck) | web | Replace Exception with Test | — | o padrão `TryParse`/`TryGetValue` |

### Capítulo 12: Lidando com herança

| # | Refatoração | Página | Antes / também | Inversa | Nota de C# |
|---|---|---|---|---|---|
| 56 | Subir Método (Pull Up Method) | 350 | — | Descer Método | — |
| 57 | Subir Campo (Pull Up Field) | 353 | — | Descer Campo | — |
| 58 | Subir Corpo do Construtor (Pull Up Constructor Body) | 355 | — | — | encadeamento de construtores com `: base(...)` |
| 59 | Descer Método (Push Down Method) | 359 | — | Subir Método | — |
| 60 | Descer Campo (Push Down Field) | 361 | — | Subir Campo | — |
| 61 | Substituir Código de Tipo por Subclasses (Replace Type Code with Subclasses) | 362 | engloba Replace Type Code with State/Strategy, Extract Subclass | Remover Subclasse | — |
| 62 | Remover Subclasse (Remove Subclass) | 369 | antes Replace Subclass with Fields | Substituir Código de Tipo por Subclasses | — |
| 63 | Extrair Superclasse (Extract Superclass) | 375 | — | — | uma classe base `abstract`, ou uma interface se só as assinaturas forem compartilhadas |
| 64 | Colapsar Hierarquia (Collapse Hierarchy) | 380 | — | — | — |
| 65 | Substituir Subclasse por Delegação (Replace Subclass with Delegate) | 381 | — | — | — |
| 66 | Substituir Superclasse por Delegação (Replace Superclass with Delegate) | 399 | antes Replace Inheritance with Delegation | — | — |

---

## 3. `references/smells.md`: os 24 smells e para onde levam

Resumo do cap. 3: o índice que o agente consulta antes de escolher uma refatoração. Cada refatoração
citada aqui é o arquivo `references/<chapter>/<slug>.md`.

| Smell | Página | Refatorações sugeridas |
|---|---|---|
| Nome Misterioso (Mysterious Name) | 72 | Mudar Declaração de Função, Renomear Variável, Renomear Campo |
| Código Duplicado (Duplicated Code) | 72 | Extrair Função, Deslocar Instruções, Subir Método |
| Função Longa (Long Function) | 73 | Extrair Função, Substituir Variável Temporária por Consulta, Introduzir Objeto de Parâmetros, Preservar Objeto Inteiro, Substituir Função por Comando, Decompor Condicional, Substituir Condicional por Polimorfismo, Dividir Laço |
| Lista Longa de Parâmetros (Long Parameter List) | 74 | Substituir Parâmetro por Consulta, Preservar Objeto Inteiro, Introduzir Objeto de Parâmetros, Remover Argumento de Flag, Combinar Funções em Classe |
| Dados Globais (Global Data) | 74 | Encapsular Variável |
| Dados Mutáveis (Mutable Data) | 75 | Encapsular Variável, Dividir Variável, Deslocar Instruções, Extrair Função, Separar Consulta de Modificador, Remover Método de Escrita, Substituir Variável Derivada por Consulta, Combinar Funções em Classe, Combinar Funções em Transformação, Mudar Referência para Valor |
| Alteração Divergente (Divergent Change) | 76 | Dividir em Fases, Mover Função, Extrair Função, Extrair Classe |
| Cirurgia com Espingarda (Shotgun Surgery) | 76 | Mover Função, Mover Campo, Combinar Funções em Classe, Combinar Funções em Transformação, Dividir em Fases, Internalizar Função, Internalizar Classe |
| Inveja de Recursos (Feature Envy) | 77 | Mover Função, Extrair Função |
| Agrupamentos de Dados (Data Clumps) | 78 | Extrair Classe, Introduzir Objeto de Parâmetros, Preservar Objeto Inteiro |
| Obsessão por Primitivos (Primitive Obsession) | 78 | Substituir Primitivo por Objeto, Substituir Código de Tipo por Subclasses, Substituir Condicional por Polimorfismo, Extrair Classe, Introduzir Objeto de Parâmetros |
| Switches Repetidos (Repeated Switches) | 79 | Substituir Condicional por Polimorfismo |
| Laços (Loops) | 79 | Substituir Laço por Pipeline |
| Elemento Ocioso (Lazy Element) | 80 | Internalizar Função, Internalizar Classe, Colapsar Hierarquia |
| Generalidade Especulativa (Speculative Generality) | 80 | Colapsar Hierarquia, Internalizar Função, Internalizar Classe, Mudar Declaração de Função, Remover Código Morto |
| Campo Temporário (Temporary Field) | 80 | Extrair Classe, Mover Função, Introduzir Caso Especial |
| Cadeias de Mensagens (Message Chains) | 81 | Ocultar Delegação, Extrair Função, Mover Função |
| Intermediário (Middle Man) | 81 | Remover Intermediário, Internalizar Função, Substituir Superclasse por Delegação, Substituir Subclasse por Delegação |
| Troca de Informações Privilegiadas (Insider Trading) | 82 | Mover Função, Mover Campo, Ocultar Delegação, Substituir Subclasse por Delegação, Substituir Superclasse por Delegação |
| Classe Grande (Large Class) | 82 | Extrair Classe, Extrair Superclasse, Substituir Código de Tipo por Subclasses |
| Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces) | 83 | Mudar Declaração de Função, Mover Função, Extrair Superclasse |
| Classe de Dados (Data Class) | 83 | Encapsular Registro, Remover Método de Escrita, Mover Função, Extrair Função |
| Herança Recusada (Refused Bequest) | 83 | Descer Método, Descer Campo, Substituir Subclasse por Delegação, Substituir Superclasse por Delegação |
| Comentários (Comments) | 84 | Extrair Função, Mudar Declaração de Função, Introduzir Asserção |

Conferido com o cap. 3 em 2026-10-31: toda refatoração que o capítulo cita como "Nome (página)" sob
cada smell está em sua linha. Classe de Dados não lista Dividir em Fases: o livro a menciona apenas como
exemplo de exceção (um record de resultado imutável), não como correção.

---

## 4. Como cada peça vira um arquivo

### 4.1 `SKILL.md`

Frontmatter `name: fowler-refactoring` e uma `description` (no máximo 1024 caracteres) que nomeia
o catálogo, os sintomas comuns e as refatorações mais usadas, de modo que o agente encontre a skill
tanto pelo problema ("esta classe faz coisas demais") quanto pelo nome ("faça um Extrair Classe"). O corpo tem
o fluxo (smell → refatoração → arquivo, com a disciplina antes do primeiro passo), o índice rápido
de smells e uma tabela por capítulo com cada refatoração, um "quando" de uma linha e um link para
o seu arquivo. Termina com a linha de Fonte:

```markdown
Fonte: Martin Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed.,
Addison-Wesley (Pearson Education), 2018, e o catálogo online em
https://refactoring.com/catalog/. Parafraseado; veja o NOTICE do pacote.
```

Quando um arquivo de referência é adicionado, renomeado ou removido, sua linha na tabela de `SKILL.md` muda
junto.

### 4.2 O arquivo de referência de uma refatoração

```markdown
# Extrair Classe (Extract Class)

Fowler (2018), cap. 7, p. 182. Antes / também: —. Inversa: Internalizar Classe
([inline-class.md](inline-class.md)).

## Quando usar
Smells: Classe Grande, Alteração Divergente, Agrupamentos de Dados. (paráfrase, 2 a 5 linhas, mais quando
não usar, se o livro disser)

## Mecânica
1. ... (paráfrase dos passos do livro, numerados, um passo testável por item)

## Exemplo
Antes / depois em C#, escrito para este pacote (não copiado do livro).

## Notas de C#
- Somente quando a seção 2 tiver uma nota de C#.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
```

Sem frontmatter e sem linha de Fonte: o crédito está em `SKILL.md` e no NOTICE. Um link para
outra refatoração é relativo: `[inline-class.md](inline-class.md)` na mesma pasta de capítulo,
`[move-function.md](../moving-features/move-function.md)` em outra. Para uma refatoração
exclusiva da web, a linha de citação é a URL do refactoring.com em vez de capítulo e página.

### 4.3 O que vai em cada parte

| Parte | Vem de | Observação |
|---|---|---|
| Nome, antes / também, inversa | o cabeçalho de seção do livro (seção 2); refactoring.com para as exclusivas da web | curto: pode ser literal |
| Quando usar, mecânica | o livro (refactoring.com para as exclusivas da web) | **paráfrase**, com capítulo e página; nada copiado |
| Exemplo | escrito para este pacote em C# | domínio neutro (pedidos, clientes, faturas, contas); não o exemplo nem o domínio do livro |
| Notas de C# | seção 2, coluna "Nota de C#" | só onde houver algo a dizer |
| Verificação | cap. 4 + `references/discipline.md` | igual em todos os arquivos |
| Linha de Fonte | esta especificação (4.1) | uma vez, no fim de `SKILL.md`; credita o autor e a editora |

Nada na skill nomeia um projeto, framework, engine ou processo de equipe específico.

Não usado como fonte: o pacote de replicação de Chen Kuang Piao et al.
(`Fowler_catalog.json`). Ele não tem licença e contém texto do livro.
