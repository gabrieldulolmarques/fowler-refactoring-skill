# Especificação do catálogo

A especificação a partir da qual a skill foi escrita e contra a qual é conferida: uma skill,
`refactoring`, com um arquivo de referência por refatoração, os code smells e a disciplina,
e o formato dos arquivos. As seções 1–4 tratam do catálogo de Fowler; a seção 5 trata das
refatorações para padrões de Kerievsky, acrescentadas na 0.4.0.

Fontes: Fowler, *Refactoring*, 2ª ed. (2018), capítulos 2–4 e 6–12, e o catálogo online
([refactoring.com/catalog](https://refactoring.com/catalog/), conferido em 2026-10-31), que
lista **66 refatorações**: as **61 do livro** mais **5 que só existem na edição
web** (marcadas como "web" na coluna Página).

A skill é genérica: ela ensina as refatorações, não o processo de nenhum projeto. Os exemplos
são C# simples com um domínio neutro (pedidos, clientes, faturas, contas), e nada faz referência
a um projeto, framework, engine ou fluxo de trabalho de equipe específico.

---

## 1. A skill

Uma skill, `refactoring`. Só a sua `description` fica no contexto do agente; o corpo de
`SKILL.md` é carregado quando a skill é usada, e cada arquivo de referência só quando o agente
o abre. O agente parte de um problema (um smell), não do nome de uma refatoração, então
um único ponto de entrada que roteia smell → refatoração → arquivo funciona melhor que 66
descrições concorrentes.

| Arquivo | Fonte | Conteúdo |
|---|---|---|
| `SKILL.md` | esta especificação | o fluxo smell → refatoração → arquivo, um índice rápido de smells e uma tabela das 66 refatorações (nome, quando, arquivo), agrupadas por capítulo (seção 4.1) |
| `references/fowler/smells.md` | cap. 3 | os 24 smells, sintomas e refatorações sugeridas (seção 3) |
| `references/fowler/discipline.md` | cap. 2 e 4 | testes primeiro, passos pequenos, commit após cada refatoração verde |
| `references/fowler/<chapter>/<slug>.md` (66 arquivos) | cap. 6–12, ou a edição web para as exclusivas da web | uma refatoração em cada: quando usar, mecânica, exemplo em C#, verificação (seção 4.2) |
| `references/kerievsky/<chapter>/<slug>.md` (27 arquivos) | Kerievsky, cap. 6–11 | uma refatoração para padrão em cada, no mesmo formato, mais padrão e direção (seção 5) |
| `references/kerievsky/smells.md` | Kerievsky, cap. 4 | os 12 smells e as refatorações para padrões a que levam (seção 5.2) |

O slug é o nome da refatoração em kebab-case. Exemplo: Extrair Função (Extract Function) →
`references/fowler/first-set/extract-function.md`. Os arquivos são agrupados por livro (`fowler/`, `kerievsky/`) e, dentro dele, em uma pasta por capítulo. Os de Fowler:
`first-set` (cap. 6), `encapsulation` (7), `moving-features` (8), `organizing-data` (9),
`conditional-logic` (10), `refactoring-apis` (11) e `inheritance` (12); uma refatoração exclusiva da web fica
no capítulo sob o qual a seção 2 a lista. A página do refactoring.com usa o nome em camelCase:
`https://refactoring.com/catalog/extractFunction.html`.

```
skills/
└── refactoring/
    ├── SKILL.md
    └── references/
        ├── fowler/
        │   ├── smells.md
        │   ├── discipline.md
        │   ├── first-set/
        │   │   ├── extract-function.md
        │   │   └── ...
        │   └── ... # 7 pastas de capítulo, 66 arquivos
        └── kerievsky/
            ├── smells.md
            ├── creation/
            └── ... # 6 pastas de capítulo, 27 arquivos
```

---

## 2. As 66 refatorações

Conferido com o livro em 2026-10-31, de forma mecânica a partir do texto do PDF: cada uma das 61 refatorações
do livro começa na **Página** indicada (edição impressa), as colunas **Antes / também** e
**Inversa** são o próprio cabeçalho de seção do livro (`formerly:`, `aka:`, `subsumes:`,
`inverse of:`), e todas as 575 referências cruzadas "Nome (página)" nos cap. 3–12 batem com a coluna
Página. Para as 5 refatorações exclusivas da web, nomes, apelidos e mecânica vêm da edição web do livro (conferida em 2026-11-11).

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

## 3. `references/fowler/smells.md`: os 24 smells e para onde levam

Resumo do cap. 3: o índice que o agente consulta antes de escolher uma refatoração. Cada refatoração
citada aqui é o arquivo `references/fowler/<chapter>/<slug>.md`.

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

Frontmatter `name: refactoring` e uma `description` (no máximo 1024 caracteres) que nomeia
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

## Notas (C#)
- Somente quando a seção 2 tiver uma nota de C#.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
```

Sem frontmatter e sem linha de Fonte: o crédito está em `SKILL.md` e no NOTICE. Um link para
outra refatoração é relativo: `[inline-class.md](inline-class.md)` na mesma pasta de capítulo,
`[move-function.md](../moving-features/move-function.md)` em outra. Para uma refatoração
exclusiva da web, a linha de citação diz "só na edição web" e aponta o resumo do refactoring.com em vez de capítulo e página.

### 4.3 O que vai em cada parte

| Parte | Vem de | Observação |
|---|---|---|
| Nome, antes / também, inversa | o cabeçalho de seção do livro (seção 2); a edição web para as exclusivas da web | curto: pode ser literal |
| Quando usar, mecânica | o livro (a edição web para as exclusivas da web) | **paráfrase**, com capítulo e página; nada copiado |
| Exemplo | escrito para este pacote em C# | domínio neutro (pedidos, clientes, faturas, contas); não o exemplo nem o domínio do livro |
| Notas (C#) | seção 2, coluna "Nota de C#" | só onde houver algo a dizer |
| Verificação | cap. 4 + `references/fowler/discipline.md` | igual em todos os arquivos |
| Linha de Fonte | esta especificação (4.1) | uma vez, no fim de `SKILL.md`; credita o autor e a editora |

Nada na skill nomeia um projeto, framework, engine ou processo de equipe específico.


---

## 5. As refatorações para padrões de Kerievsky

Fonte: Joshua Kerievsky, *Refactoring to Patterns*, Addison-Wesley (Pearson Education), 2004,
capítulos 4 e 6–11. Cada refatoração é uma sequência de refatorações menores, em geral de
Fowler, que termina em um padrão (*até*), avança parte do caminho (*rumo a*) ou remove um
(*longe*). O catálogo online em https://www.industriallogic.com/refactoring-to-patterns/catalog/
tem só um resumo e um diagrama de cada uma; a mecânica vem do livro.

### 5.1 As 27 refatorações

Conferidas com o livro: **Página** é a página impressa da própria lista de refatorações do livro
(segunda capa), e **Direção** vem da tabela "Refactoring Directions" dele. A mecânica do livro
cita as refatorações de Fowler pelos nomes da 1ª edição; os arquivos de referência usam os nomes
da 2ª edição (seção 2) e apontam para os arquivos delas.

**Nota C#** é o que o arquivo de referência precisa acrescentar porque os exemplos do livro são
em Java: só pontos genéricos de C#. Onde está "—", o arquivo não tem seção de notas de C#.

#### Capítulo 6: Criação (`kerievsky/creation`)

| # | Refatoração | Página | Padrão | Direção | Nota C# |
|---|---|---|---|---|---|
| 1 | Substituir Construtores por Métodos de Criação (Replace Constructors with Creation Methods) | 57 | Creation Method | até | parâmetros opcionais e inicializadores de objeto não dão nome à variante; um `record` com construtor privado funciona igual |
| 2 | Mover Conhecimento de Criação para Factory (Move Creation Knowledge to Factory) | 68 | Factory | até | — |
| 3 | Encapsular Classes com Factory (Encapsulate Classes with Factory) | 80 | Factory | até | esconda as classes com tipos e construtores `internal` (ou `private` aninhados); os testes podem usar `InternalsVisibleTo` |
| 4 | Introduzir Criação Polimórfica com Factory Method (Introduce Polymorphic Creation with Factory Method) | 88 | Factory Method | até | o factory method é `protected abstract`, ou `protected virtual` com um padrão |
| 5 | Encapsular Composite com Builder (Encapsulate Composite with Builder) | 96 | Builder | até (Builder); longe (Composite) | — |
| 6 | Internalizar Singleton (Inline Singleton) | 114 | Singleton | longe | uma `static class` conta como Singleton aqui |

#### Capítulo 7: Simplificação (`kerievsky/simplification`)

| # | Refatoração | Página | Padrão | Direção | Nota C# |
|---|---|---|---|---|---|
| 7 | Compor Método (Compose Method) | 123 | Composed Method | até | membros com corpo de expressão e funções locais mantêm as partes curtas |
| 8 | Substituir Lógica Condicional por Strategy (Replace Conditional Logic with Strategy) | 129 | Strategy | até, rumo a | uma interface, ou uma classe abstrata se as estratégias compartilham código; estratégias sem estado podem ser `static readonly` |
| 9 | Mover Embelezamento para Decorator (Move Embellishment to Decorator) | 144 | Decorator | até, rumo a | — |
| 10 | Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State) | 166 | State | até, rumo a | instâncias de estado `static readonly` compartilhadas, subclasses `private sealed` aninhadas; persista um código estável, não o objeto |
| 11 | Substituir Árvore Implícita por Composite (Replace Implicit Tree with Composite) | 178 | Composite | até | uma folha `record`; exponha os filhos como `IReadOnlyList<T>` |
| 12 | Substituir Despachante Condicional por Command (Replace Conditional Dispatcher with Command) | 191 | Command | até, rumo a | um `Dictionary<string, Func<...>>` é um tipo de comando mais leve para handlers pequenos |

#### Capítulo 8: Generalização (`kerievsky/generalization`)

| # | Refatoração | Página | Padrão | Direção | Nota C# |
|---|---|---|---|---|---|
| 13 | Formar Template Method (Form Template Method) | 205 | Template Method | até | um template method não `virtual` é o `final` do C#; passos `protected` `abstract` e `virtual` |
| 14 | Extrair Composite (Extract Composite) | 214 | Composite | até | exponha os filhos como `IReadOnlyList<T>` |
| 15 | Substituir Distinções Um/Muitos por Composite (Replace One/Many Distinctions with Composite) | 224 | Composite | até | uma sobrecarga com `params`/`IEnumerable<T>` pode bastar |
| 16 | Substituir Notificações Fixas no Código por Observer (Replace Hard-Coded Notifications with Observer) | 236 | Observer | até, rumo a | `event EventHandler<T>`; todo `+=` precisa do seu `-=` |
| 17 | Unificar Interfaces com Adapter (Unify Interfaces with Adapter) | 247 | Adapter | até, rumo a | — |
| 18 | Extrair Adapter (Extract Adapter) | 258 | Adapter | até | — |
| 19 | Substituir Linguagem Implícita por Interpreter (Replace Implicit Language with Interpreter) | 269 | Interpreter | até | `Func<T, bool>` ou LINQ podem bastar; `Expression<Func<T, bool>>` quando um provedor traduz os critérios |

#### Capítulo 9: Proteção (`kerievsky/protection`)

| # | Refatoração | Página | Padrão | Direção | Nota C# |
|---|---|---|---|---|---|
| 20 | Substituir Código de Tipo por Classe (Replace Type Code with Class) | 286 | — | — | um `enum` aceita qualquer inteiro; use uma classe selada com construtor privado para um conjunto fechado |
| 21 | Limitar Instanciação com Singleton (Limit Instantiation with Singleton) | 296 | Singleton | até | `static readonly` ou `Lazy<T>`; o tempo de vida singleton de um contêiner de DI muitas vezes substitui o padrão |
| 22 | Introduzir Null Object (Introduce Null Object) | 301 | Null Object | até | com tipos de referência anuláveis o campo deixa de ser anulável; uma instância estática compartilhada |

#### Capítulo 10: Acumulação (`kerievsky/accumulation`)

| # | Refatoração | Página | Padrão | Direção | Nota C# |
|---|---|---|---|---|---|
| 23 | Mover Acumulação para Collecting Parameter (Move Accumulation to Collecting Parameter) | 313 | Collecting Parameter | até | `StringBuilder`, ou um parâmetro `TextWriter` |
| 24 | Mover Acumulação para Visitor (Move Accumulation to Visitor) | 320 | Visitor | até, rumo a (Visitor); longe (Iterator) | uma expressão `switch` com padrões de tipo muitas vezes basta; um visitor genérico devolve valores |

#### Capítulo 11: Utilitários (`kerievsky/utilities`)

| # | Refatoração | Página | Padrão | Direção | Nota C# |
|---|---|---|---|---|---|
| 25 | Encadear Construtores (Chain Constructors) | 340 | — | — | `: this(...)`; parâmetros opcionais como alternativa; construtores primários |
| 26 | Unificar Interfaces (Unify Interfaces) | 343 | — | — | `virtual`/`override`, sem ocultar; métodos padrão de interface |
| 27 | Extrair Parâmetro (Extract Parameter) | 346 | — | — | `ArgumentNullException.ThrowIfNull` |

Sobreposições com a 2ª edição de Fowler, mantidas curtas e apontando para o arquivo de Fowler:
Compor Método (Extrair Função, Deslocar Instruções), Substituir Código de Tipo por Classe
(Substituir Primitivo por Objeto, que a engloba) e Introduzir Null Object (Introduzir Caso
Especial, seu novo nome).

### 5.2 Os 12 smells

Do cap. 4 e da terceira capa, em `references/kerievsky/smells.md`. A coluna "Smell de Fowler" é a
ponte que o índice rápido do `SKILL.md` usa; os dois `smells.md` não citam um ao outro.

| Smell | Página | Smell de Fowler | Refatorações |
|---|---|---|---|
| Código Duplicado (Duplicated Code) | 39 | Código Duplicado | Formar Template Method, Introduzir Criação Polimórfica com Factory Method, Encadear Construtores, Substituir Distinções Um/Muitos por Composite, Extrair Composite, Unificar Interfaces com Adapter, Introduzir Null Object |
| Método Longo (Long Method) | 40 | Função Longa | Compor Método, Mover Acumulação para Collecting Parameter, Substituir Despachante Condicional por Command, Mover Acumulação para Visitor, Substituir Lógica Condicional por Strategy |
| Complexidade Condicional (Conditional Complexity) | 41 | novo | Substituir Lógica Condicional por Strategy, Mover Embelezamento para Decorator, Substituir Condicionais que Alteram Estado por State, Introduzir Null Object |
| Obsessão por Primitivos (Primitive Obsession) | 41 | Obsessão por Primitivos | Substituir Código de Tipo por Classe, Substituir Condicionais que Alteram Estado por State, Substituir Lógica Condicional por Strategy, Substituir Árvore Implícita por Composite, Substituir Linguagem Implícita por Interpreter, Mover Embelezamento para Decorator, Encapsular Composite com Builder |
| Exposição Indecente (Indecent Exposure) | 42 | novo | Encapsular Classes com Factory |
| Solução Espalhada (Solution Sprawl) | 43 | novo (o livro o chama de gêmeo da Cirurgia com Espingarda) | Mover Conhecimento de Criação para Factory |
| Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces) | 43 | o mesmo | Unificar Interfaces com Adapter |
| Classe Preguiçosa (Lazy Class) | 43 | Elemento Ocioso | Internalizar Singleton |
| Classe Grande (Large Class) | 44 | Classe Grande | Substituir Despachante Condicional por Command, Substituir Condicionais que Alteram Estado por State, Substituir Linguagem Implícita por Interpreter |
| Comandos Switch (Switch Statements) | 44 | Switches Repetidos | Substituir Despachante Condicional por Command, Mover Acumulação para Visitor |
| Explosão Combinatória (Combinatorial Explosion) | 45 | novo | Substituir Linguagem Implícita por Interpreter |
| Solução Destoante (Oddball Solution) | 45 | novo | Substituir Algoritmo, Unificar Interfaces com Adapter |

### 5.3 Formato dos arquivos

O mesmo da seção 4.2, com outra linha de citação:

```markdown
# Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State)

Kerievsky (2004), cap. 7, p. 166. Padrão: State. Direção: até, rumo a.
```

Um passo da mecânica que é uma refatoração de Fowler a cita pelo nome da 2ª edição e aponta
para o arquivo dela; uma refatoração sem equivalente na 2ª edição (como Extrair Interface) é
descrita em palavras e marcada "(só na 1ª ed.)". "Quando usar" inclui as desvantagens que o
livro aponta, para o agente saber quando o padrão não compensa. Os exemplos são em C# original,
como na seção 4.3.
