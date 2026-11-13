---
name: refactoring
description: Catálogos de refatoração de Martin Fowler (Refactoring, 2ª ed.) e Joshua Kerievsky (Refactoring to Patterns): 29 code smells, 66 refatorações e 27 refatorações para padrões (Strategy, State, Command, Observer, Composite, Factory, Template Method...), cada uma com mecânica, exemplo em C# e verificação. Use para refatorar ou limpar código sem mudar o comportamento, quando o código estiver difícil de ler ou alterar, quando condicionais ou switches não param de crescer, ou quando uma refatoração, code smell ou padrão de projeto for citado.
---

# Catálogos de refatoração: Fowler e Kerievsky

Fowler (2018), cap. 2-4 (smells e disciplina) e cap. 6-12 (o catálogo), mais cinco
refatorações que só existem na edição web do livro. Kerievsky (2004), cap. 4 (smells) e
cap. 6-11 (refatorações para padrões), que se apoiam nas refatorações de Fowler.

Fluxo: **smell -> refatoração -> seu arquivo em `references/`.**

1. Nomeie o smell. Use o índice rápido abaixo, ou os sintomas em
   [references/smells.md](references/smells.md) para a lista completa dos 29.
2. Escolha uma refatoração para esse smell e abra o arquivo dela nas tabelas mais adiante.
   Comece pela mais simples. Só recorra a uma refatoração para padrão quando o smell pedir, e
   pare assim que o smell sumir: ir *rumo a* um padrão muitas vezes basta.
3. Antes de alterar qualquer coisa, confira a rede de segurança em
   [references/discipline.md](references/discipline.md): testes passando, passos pequenos, um commit
   após cada refatoração verde. Se o código não tem testes, escreva-os primeiro.
4. Siga a mecânica um passo de cada vez. Compile e execute os testes após cada passo; se
   algo falhar, desfaça o passo.

Se o pedido nomear uma refatoração, pule para o passo 3 e abra o arquivo dela diretamente.

## Índice rápido de smells

| Smell | Primeira coisa a tentar |
|---|---|
| Nome Misterioso (Mysterious Name) | [change-function-declaration](references/first-set/change-function-declaration.md), [rename-variable](references/first-set/rename-variable.md), [rename-field](references/organizing-data/rename-field.md) |
| Código Duplicado (Duplicated Code) | [extract-function](references/first-set/extract-function.md), [pull-up-method](references/inheritance/pull-up-method.md) (mesmo código em subclasses irmãs) |
| Função Longa (Long Function) | [extract-function](references/first-set/extract-function.md) |
| Lista Longa de Parâmetros (Long Parameter List) | [introduce-parameter-object](references/first-set/introduce-parameter-object.md), [preserve-whole-object](references/refactoring-apis/preserve-whole-object.md) |
| Dados Globais (Global Data) | [encapsulate-variable](references/first-set/encapsulate-variable.md) |
| Dados Mutáveis (Mutable Data) | [encapsulate-variable](references/first-set/encapsulate-variable.md), [split-variable](references/organizing-data/split-variable.md) |
| Alteração Divergente (Divergent Change) | [split-phase](references/first-set/split-phase.md), [extract-class](references/encapsulation/extract-class.md) |
| Cirurgia com Espingarda (Shotgun Surgery) | [move-function](references/moving-features/move-function.md), [move-field](references/moving-features/move-field.md) |
| Inveja de Recursos (Feature Envy) | [move-function](references/moving-features/move-function.md) |
| Agrupamentos de Dados (Data Clumps) | [extract-class](references/encapsulation/extract-class.md) |
| Obsessão por Primitivos (Primitive Obsession) | [replace-primitive-with-object](references/encapsulation/replace-primitive-with-object.md) |
| Switches Repetidos (Repeated Switches) | [replace-conditional-with-polymorphism](references/conditional-logic/replace-conditional-with-polymorphism.md) |
| Laços (Loops) | [replace-loop-with-pipeline](references/moving-features/replace-loop-with-pipeline.md) |
| Elemento Ocioso (Lazy Element) | [inline-function](references/first-set/inline-function.md), [inline-class](references/encapsulation/inline-class.md) |
| Generalidade Especulativa (Speculative Generality) | [collapse-hierarchy](references/inheritance/collapse-hierarchy.md), [remove-dead-code](references/moving-features/remove-dead-code.md) |
| Campo Temporário (Temporary Field) | [extract-class](references/encapsulation/extract-class.md) |
| Cadeias de Mensagens (Message Chains) | [hide-delegate](references/encapsulation/hide-delegate.md) |
| Intermediário (Middle Man) | [remove-middle-man](references/encapsulation/remove-middle-man.md) |
| Troca de Informações Privilegiadas (Insider Trading) | [move-function](references/moving-features/move-function.md), [move-field](references/moving-features/move-field.md) |
| Classe Grande (Large Class) | [extract-class](references/encapsulation/extract-class.md) |
| Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces) | [change-function-declaration](references/first-set/change-function-declaration.md) |
| Classe de Dados (Data Class) | [encapsulate-record](references/encapsulation/encapsulate-record.md), [move-function](references/moving-features/move-function.md) |
| Herança Recusada (Refused Bequest) | [push-down-method](references/inheritance/push-down-method.md), [push-down-field](references/inheritance/push-down-field.md), [replace-subclass-with-delegate](references/inheritance/replace-subclass-with-delegate.md), [replace-superclass-with-delegate](references/inheritance/replace-superclass-with-delegate.md) |
| Comentários (Comments) | [extract-function](references/first-set/extract-function.md) |
| Complexidade Condicional (Conditional Complexity) | [replace-conditional-logic-with-strategy](references/simplification/replace-conditional-logic-with-strategy.md), [replace-state-altering-conditionals-with-state](references/simplification/replace-state-altering-conditionals-with-state.md), [move-embellishment-to-decorator](references/simplification/move-embellishment-to-decorator.md), [introduce-null-object](references/protection/introduce-null-object.md) |
| Exposição Indecente (Indecent Exposure) | [encapsulate-classes-with-factory](references/creation/encapsulate-classes-with-factory.md) |
| Solução Espalhada (Solution Sprawl) | [move-creation-knowledge-to-factory](references/creation/move-creation-knowledge-to-factory.md) |
| Explosão Combinatória (Combinatorial Explosion) | [replace-implicit-language-with-interpreter](references/generalization/replace-implicit-language-with-interpreter.md) |
| Solução Destoante (Oddball Solution) | [substitute-algorithm](references/encapsulation/substitute-algorithm.md), [unify-interfaces-with-adapter](references/generalization/unify-interfaces-with-adapter.md) |

Os cinco últimos são de Kerievsky. Para os demais smells, o `smells.md` também lista as
refatorações para padrões que Kerievsky acrescenta.

## As refatorações

Cada arquivo tem: Quando usar, Mecânica, Exemplo (C#), Notas (C#) onde o catálogo tem uma, e
Verificação. "(web)" marca uma refatoração que existe só na edição web do livro, sem página
no impresso. Um arquivo de Kerievsky também dá o padrão (com a página no GoF) e a direção:
*até* o padrão, *rumo a* ele, ou para *longe* dele.

### Um primeiro conjunto (cap. 6)

| Refatoração | Quando | Arquivo |
|---|---|---|
| Extrair Função (Extract Function) | um trecho precisa de um comentário para dizer o que faz, ou uma função é longa demais | [extract-function.md](references/first-set/extract-function.md) |
| Internalizar Função (Inline Function) | o corpo de uma função diz tanto quanto o nome dela, ou ela só delega | [inline-function.md](references/first-set/inline-function.md) |
| Extrair Variável (Extract Variable) | uma expressão é longa ou difícil de ler | [extract-variable.md](references/first-set/extract-variable.md) |
| Internalizar Variável (Inline Variable) | o nome de uma variável não diz mais que a expressão dela | [inline-variable.md](references/first-set/inline-variable.md) |
| Mudar Declaração de Função (Change Function Declaration) | renomear uma função, ou adicionar, remover ou alterar um parâmetro | [change-function-declaration.md](references/first-set/change-function-declaration.md) |
| Encapsular Variável (Encapsulate Variable) | um campo ou global é lido e escrito em muitos lugares | [encapsulate-variable.md](references/first-set/encapsulate-variable.md) |
| Renomear Variável (Rename Variable) | o nome de uma variável é enigmático, enganoso ou desatualizado | [rename-variable.md](references/first-set/rename-variable.md) |
| Introduzir Objeto de Parâmetros (Introduce Parameter Object) | o mesmo grupo de valores viaja junto por várias assinaturas | [introduce-parameter-object.md](references/first-set/introduce-parameter-object.md) |
| Combinar Funções em Classe (Combine Functions into Class) | várias funções trabalham sobre os mesmos dados | [combine-functions-into-class.md](references/first-set/combine-functions-into-class.md) |
| Combinar Funções em Transformação (Combine Functions into Transform) | os mesmos valores derivados são calculados em vários lugares a partir de dados somente leitura | [combine-functions-into-transform.md](references/first-set/combine-functions-into-transform.md) |
| Dividir em Fases (Split Phase) | um trecho de código faz duas coisas em sequência (interpretar e depois calcular, calcular e depois formatar) | [split-phase.md](references/first-set/split-phase.md) |

### Encapsulamento (cap. 7)

| Refatoração | Quando | Arquivo |
|---|---|---|
| Encapsular Registro (Encapsulate Record) | dados soltos (dicionário, tupla) são lidos e escritos pelo programa inteiro | [encapsulate-record.md](references/encapsulation/encapsulate-record.md) |
| Encapsular Coleção (Encapsulate Collection) | os chamadores podem alterar uma coleção que o dono deveria controlar | [encapsulate-collection.md](references/encapsulation/encapsulate-collection.md) |
| Substituir Primitivo por Objeto (Replace Primitive with Object) | uma string ou um número carrega significado e regras próprios | [replace-primitive-with-object.md](references/encapsulation/replace-primitive-with-object.md) |
| Substituir Variável Temporária por Consulta (Replace Temp with Query) | uma variável temporária guarda um cálculo que impede a extração ou se repete em outro lugar | [replace-temp-with-query.md](references/encapsulation/replace-temp-with-query.md) |
| Extrair Classe (Extract Class) | uma classe faz coisas demais ou muda por motivos não relacionados | [extract-class.md](references/encapsulation/extract-class.md) |
| Internalizar Classe (Inline Class) | uma classe já não faz o bastante para se justificar | [inline-class.md](references/encapsulation/inline-class.md) |
| Ocultar Delegação (Hide Delegate) | os clientes passam por um objeto para chamar outro (`a.B.C()`) | [hide-delegate.md](references/encapsulation/hide-delegate.md) |
| Remover Intermediário (Remove Middle Man) | uma classe é feita quase só de métodos de uma linha que repassam para outra | [remove-middle-man.md](references/encapsulation/remove-middle-man.md) |
| Substituir Algoritmo (Substitute Algorithm) | um jeito mais simples, ou uma chamada de biblioteca, faz o mesmo trabalho | [substitute-algorithm.md](references/encapsulation/substitute-algorithm.md) |

### Movendo recursos (cap. 8)

| Refatoração | Quando | Arquivo |
|---|---|---|
| Mover Função (Move Function) | uma função usa mais os dados de outra classe do que os da própria | [move-function.md](references/moving-features/move-function.md) |
| Mover Campo (Move Field) | um campo é sempre usado ou alterado junto com outro objeto | [move-field.md](references/moving-features/move-field.md) |
| Mover Instruções para Função (Move Statements into Function) | as mesmas linhas rodam antes ou depois de toda chamada a uma função | [move-statements-into-function.md](references/moving-features/move-statements-into-function.md) |
| Mover Instruções para os Chamadores (Move Statements to Callers) | parte de uma função precisa passar a variar entre os chamadores | [move-statements-to-callers.md](references/moving-features/move-statements-to-callers.md) |
| Substituir Código Internalizado por Chamada de Função (Replace Inline Code with Function Call) | o código inline repete o que uma função existente já faz | [replace-inline-code-with-function-call.md](references/moving-features/replace-inline-code-with-function-call.md) |
| Deslocar Instruções (Slide Statements) | instruções relacionadas estão separadas, ou uma declaração está longe do seu uso | [slide-statements.md](references/moving-features/slide-statements.md) |
| Dividir Laço (Split Loop) | um laço calcula duas ou mais coisas não relacionadas | [split-loop.md](references/moving-features/split-loop.md) |
| Substituir Laço por Pipeline (Replace Loop with Pipeline) | um laço filtra, mapeia ou acumula de um jeito que um pipeline (LINQ) expressa com mais clareza | [replace-loop-with-pipeline.md](references/moving-features/replace-loop-with-pipeline.md) |
| Remover Código Morto (Remove Dead Code) | o código nunca é chamado ou uma condição é sempre falsa | [remove-dead-code.md](references/moving-features/remove-dead-code.md) |

### Organizando dados (cap. 9)

| Refatoração | Quando | Arquivo |
|---|---|---|
| Dividir Variável (Split Variable) | uma variável é atribuída mais de uma vez para finalidades diferentes | [split-variable.md](references/organizing-data/split-variable.md) |
| Renomear Campo (Rename Field) | o nome de um campo é enganoso ou desatualizado | [rename-field.md](references/organizing-data/rename-field.md) |
| Substituir Variável Derivada por Consulta (Replace Derived Variable with Query) | um valor armazenado pode ser calculado a partir de outros dados e pode divergir deles | [replace-derived-variable-with-query.md](references/organizing-data/replace-derived-variable-with-query.md) |
| Mudar Referência para Valor (Change Reference to Value) | um objeto pequeno é alterado no lugar, mas deveria ser copiado e comparado por valor | [change-reference-to-value.md](references/organizing-data/change-reference-to-value.md) |
| Mudar Valor para Referência (Change Value to Reference) | cópias da mesma entidade precisam todas ver uma atualização | [change-value-to-reference.md](references/organizing-data/change-value-to-reference.md) |
| Substituir Literal Mágico (Replace Magic Literal) (web) | um número ou string aparece inline e o leitor precisa adivinhar o significado | [replace-magic-literal.md](references/organizing-data/replace-magic-literal.md) |

### Simplificando a lógica condicional (cap. 10)

| Refatoração | Quando | Arquivo |
|---|---|---|
| Decompor Condicional (Decompose Conditional) | uma condição ou seus ramos são longos e precisam de um comentário | [decompose-conditional.md](references/conditional-logic/decompose-conditional.md) |
| Consolidar Expressão Condicional (Consolidate Conditional Expression) | várias verificações levam ao mesmo resultado | [consolidate-conditional-expression.md](references/conditional-logic/consolidate-conditional-expression.md) |
| Substituir Condicional Aninhada por Cláusulas de Guarda (Replace Nested Conditional with Guard Clauses) | ifs aninhados escondem o caminho normal entre os casos especiais | [replace-nested-conditional-with-guard-clauses.md](references/conditional-logic/replace-nested-conditional-with-guard-clauses.md) |
| Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism) | o mesmo switch sobre um tipo aparece em vários lugares | [replace-conditional-with-polymorphism.md](references/conditional-logic/replace-conditional-with-polymorphism.md) |
| Introduzir Caso Especial (Introduce Special Case) | muitos chamadores verificam o mesmo valor especial (geralmente null) e reagem do mesmo jeito | [introduce-special-case.md](references/conditional-logic/introduce-special-case.md) |
| Introduzir Asserção (Introduce Assertion) | o código só funciona se uma condição valer, e nada diz isso | [introduce-assertion.md](references/conditional-logic/introduce-assertion.md) |
| Substituir Flag de Controle por Break (Replace Control Flag with Break) (web) | uma variável de flag controla quando um laço para | [replace-control-flag-with-break.md](references/conditional-logic/replace-control-flag-with-break.md) |

### Refatorando APIs (cap. 11)

| Refatoração | Quando | Arquivo |
|---|---|---|
| Separar Consulta de Modificador (Separate Query from Modifier) | uma função devolve um valor e também tem efeitos colaterais | [separate-query-from-modifier.md](references/refactoring-apis/separate-query-from-modifier.md) |
| Parametrizar Função (Parameterize Function) | várias funções diferem apenas em um valor literal | [parameterize-function.md](references/refactoring-apis/parameterize-function.md) |
| Remover Argumento de Flag (Remove Flag Argument) | um argumento booleano ou enum seleciona o que a função faz | [remove-flag-argument.md](references/refactoring-apis/remove-flag-argument.md) |
| Preservar Objeto Inteiro (Preserve Whole Object) | os chamadores desempacotam um objeto só para passar seus campos | [preserve-whole-object.md](references/refactoring-apis/preserve-whole-object.md) |
| Substituir Parâmetro por Consulta (Replace Parameter with Query) | a função consegue descobrir sozinha o valor de um parâmetro | [replace-parameter-with-query.md](references/refactoring-apis/replace-parameter-with-query.md) |
| Substituir Consulta por Parâmetro (Replace Query with Parameter) | uma função depende de estado global ou mutável que os chamadores deveriam fornecer | [replace-query-with-parameter.md](references/refactoring-apis/replace-query-with-parameter.md) |
| Remover Método de Escrita (Remove Setting Method) | um campo não deveria mudar após a construção | [remove-setting-method.md](references/refactoring-apis/remove-setting-method.md) |
| Substituir Construtor por Função de Fábrica (Replace Constructor with Factory Function) | o nome ou o tipo de retorno fixo de um construtor atrapalha | [replace-constructor-with-factory-function.md](references/refactoring-apis/replace-constructor-with-factory-function.md) |
| Substituir Função por Comando (Replace Function with Command) | uma função precisa de desfazer, de preparação em etapas, ou é emaranhada demais para dividir | [replace-function-with-command.md](references/refactoring-apis/replace-function-with-command.md) |
| Substituir Comando por Função (Replace Command with Function) | um objeto de comando não faz nada que uma função simples não faria | [replace-command-with-function.md](references/refactoring-apis/replace-command-with-function.md) |
| Retornar Valor Modificado (Return Modified Value) (web) | uma função altera dados externos e não devolve nada | [return-modified-value.md](references/refactoring-apis/return-modified-value.md) |
| Substituir Código de Erro por Exceção (Replace Error Code with Exception) (web) | os chamadores ignoram ou se enroscam com códigos de erro devolvidos | [replace-error-code-with-exception.md](references/refactoring-apis/replace-error-code-with-exception.md) |
| Substituir Exceção por Verificação Prévia (Replace Exception with Precheck) (web) | uma exceção é usada para uma condição que o chamador poderia testar antes | [replace-exception-with-precheck.md](references/refactoring-apis/replace-exception-with-precheck.md) |

### Lidando com herança (cap. 12)

| Refatoração | Quando | Arquivo |
|---|---|---|
| Subir Método (Pull Up Method) | subclasses irmãs têm o mesmo método | [pull-up-method.md](references/inheritance/pull-up-method.md) |
| Subir Campo (Pull Up Field) | subclasses irmãs guardam o mesmo campo | [pull-up-field.md](references/inheritance/pull-up-field.md) |
| Subir Corpo do Construtor (Pull Up Constructor Body) | os construtores das subclasses repetem a mesma preparação | [pull-up-constructor-body.md](references/inheritance/pull-up-constructor-body.md) |
| Descer Método (Push Down Method) | um método da superclasse importa só para algumas subclasses | [push-down-method.md](references/inheritance/push-down-method.md) |
| Descer Campo (Push Down Field) | um campo da superclasse é usado só por algumas subclasses | [push-down-field.md](references/inheritance/push-down-field.md) |
| Substituir Código de Tipo por Subclasses (Replace Type Code with Subclasses) | comportamento ou dados variam conforme um código de tipo | [replace-type-code-with-subclasses.md](references/inheritance/replace-type-code-with-subclasses.md) |
| Remover Subclasse (Remove Subclass) | as subclasses fazem pouco demais para se justificar | [remove-subclass.md](references/inheritance/remove-subclass.md) |
| Extrair Superclasse (Extract Superclass) | duas classes compartilham dados ou comportamento | [extract-superclass.md](references/inheritance/extract-superclass.md) |
| Colapsar Hierarquia (Collapse Hierarchy) | uma subclasse já não é diferente o bastante da classe pai | [collapse-hierarchy.md](references/inheritance/collapse-hierarchy.md) |
| Substituir Subclasse por Delegação (Replace Subclass with Delegate) | a herança já é usada para outra variação, ou a variante precisa mudar em tempo de execução | [replace-subclass-with-delegate.md](references/inheritance/replace-subclass-with-delegate.md) |
| Substituir Superclasse por Delegação (Replace Superclass with Delegate) | a subclasse não é de fato um tipo da classe pai | [replace-superclass-with-delegate.md](references/inheritance/replace-superclass-with-delegate.md) |


## As refatorações para padrões (Kerievsky)

Cada uma é uma sequência de refatorações menores, muitas delas de Fowler, que termina em um
padrão, avança rumo a ele ou remove um. A coluna Padrão traz a direção.

### Criação (Kerievsky, cap. 6)

| Refatoração | Padrão | Quando | Arquivo |
|---|---|---|---|
| Substituir Construtores por Métodos de Criação (Replace Constructors with Creation Methods) | Creation Method (até) | vários construtores tornam difícil saber qual chamar | [replace-constructors-with-creation-methods.md](references/creation/replace-constructors-with-creation-methods.md) |
| Mover Conhecimento de Criação para Factory (Move Creation Knowledge to Factory) | Factory (até) | os dados e o código usados para criar um objeto estão espalhados por muitas classes | [move-creation-knowledge-to-factory.md](references/creation/move-creation-knowledge-to-factory.md) |
| Encapsular Classes com Factory (Encapsulate Classes with Factory) | Factory (até) | os clientes instanciam classes de um pacote que compartilham uma interface e poderiam ficar ocultas | [encapsulate-classes-with-factory.md](references/creation/encapsulate-classes-with-factory.md) |
| Introduzir Criação Polimórfica com Factory Method (Introduce Polymorphic Creation with Factory Method) | Factory Method (até) | classes irmãs repetem um método, exceto pelo objeto que ele cria | [introduce-polymorphic-creation-with-factory-method.md](references/creation/introduce-polymorphic-creation-with-factory-method.md) |
| Encapsular Composite com Builder (Encapsulate Composite with Builder) | Builder (até) | montar um Composite é repetitivo, complicado ou sujeito a erros | [encapsulate-composite-with-builder.md](references/creation/encapsulate-composite-with-builder.md) |
| Internalizar Singleton (Inline Singleton) | Singleton (longe) | o código precisa de um objeto, mas não de acesso global a ele | [inline-singleton.md](references/creation/inline-singleton.md) |

### Simplificação (Kerievsky, cap. 7)

| Refatoração | Padrão | Quando | Arquivo |
|---|---|---|---|
| Compor Método (Compose Method) | Composed Method (até) | a lógica de um método é difícil de entender de relance | [compose-method.md](references/simplification/compose-method.md) |
| Substituir Lógica Condicional por Strategy (Replace Conditional Logic with Strategy) | Strategy (até, rumo a) | condicionais escolhem qual variante de um cálculo executar | [replace-conditional-logic-with-strategy.md](references/simplification/replace-conditional-logic-with-strategy.md) |
| Mover Embelezamento para Decorator (Move Embellishment to Decorator) | Decorator (até, rumo a) | o código acrescenta comportamento opcional ao trabalho principal de uma classe | [move-embellishment-to-decorator.md](references/simplification/move-embellishment-to-decorator.md) |
| Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State) | State (até, rumo a) | as condicionais que controlam as transições de estado de um objeto são complexas | [replace-state-altering-conditionals-with-state.md](references/simplification/replace-state-altering-conditionals-with-state.md) |
| Substituir Árvore Implícita por Composite (Replace Implicit Tree with Composite) | Composite (até) | uma árvore é montada implicitamente com strings ou outros primitivos | [replace-implicit-tree-with-composite.md](references/simplification/replace-implicit-tree-with-composite.md) |
| Substituir Despachante Condicional por Command (Replace Conditional Dispatcher with Command) | Command (até, rumo a) | condicionais despacham pedidos e executam suas ações | [replace-conditional-dispatcher-with-command.md](references/simplification/replace-conditional-dispatcher-with-command.md) |

### Generalização (Kerievsky, cap. 8)

| Refatoração | Padrão | Quando | Arquivo |
|---|---|---|---|
| Formar Template Method (Form Template Method) | Template Method (até) | duas subclasses fazem passos parecidos na mesma ordem | [form-template-method.md](references/generalization/form-template-method.md) |
| Extrair Composite (Extract Composite) | Composite (até) | subclasses de uma hierarquia implementam o mesmo Composite | [extract-composite.md](references/generalization/extract-composite.md) |
| Substituir Distinções Um/Muitos por Composite (Replace One/Many Distinctions with Composite) | Composite (até) | um trecho trata um único objeto e outro trata uma coleção deles | [replace-one-many-distinctions-with-composite.md](references/generalization/replace-one-many-distinctions-with-composite.md) |
| Substituir Notificações Fixas no Código por Observer (Replace Hard-Coded Notifications with Observer) | Observer (até, rumo a) | classes notificam receptores específicos em chamadas fixas no código | [replace-hard-coded-notifications-with-observer.md](references/generalization/replace-hard-coded-notifications-with-observer.md) |
| Unificar Interfaces com Adapter (Unify Interfaces with Adapter) | Adapter (até, rumo a) | os clientes usam duas classes do mesmo jeito, mas as interfaces delas diferem | [unify-interfaces-with-adapter.md](references/generalization/unify-interfaces-with-adapter.md) |
| Extrair Adapter (Extract Adapter) | Adapter (até) | uma classe adapta várias versões de um componente, biblioteca ou API | [extract-adapter.md](references/generalization/extract-adapter.md) |
| Substituir Linguagem Implícita por Interpreter (Replace Implicit Language with Interpreter) | Interpreter (até) | muitos métodos, ou combinações deles, expressam os elementos de uma linguagem implícita | [replace-implicit-language-with-interpreter.md](references/generalization/replace-implicit-language-with-interpreter.md) |

### Proteção (Kerievsky, cap. 9)

| Refatoração | Padrão | Quando | Arquivo |
|---|---|---|---|
| Substituir Código de Tipo por Classe (Replace Type Code with Class) | — | o tipo de um campo (uma string ou um int) não o protege de valores inválidos | [replace-type-code-with-class.md](references/protection/replace-type-code-with-class.md) |
| Limitar Instanciação com Singleton (Limit Instantiation with Singleton) | Singleton (até) | o código cria muitas instâncias de um objeto quando uma basta, e isso custa memória ou tempo | [limit-instantiation-with-singleton.md](references/protection/limit-instantiation-with-singleton.md) |
| Introduzir Null Object (Introduce Null Object) | Null Object (até) | a mesma verificação de campo ou variável nula se repete pelo código | [introduce-null-object.md](references/protection/introduce-null-object.md) |

### Acumulação (Kerievsky, cap. 10)

| Refatoração | Padrão | Quando | Arquivo |
|---|---|---|---|
| Mover Acumulação para Collecting Parameter (Move Accumulation to Collecting Parameter) | Collecting Parameter (até) | um método grande junta informação em uma variável local | [move-accumulation-to-collecting-parameter.md](references/accumulation/move-accumulation-to-collecting-parameter.md) |
| Mover Acumulação para Visitor (Move Accumulation to Visitor) | Visitor (até, rumo a) | um método junta informação de classes com interfaces diferentes | [move-accumulation-to-visitor.md](references/accumulation/move-accumulation-to-visitor.md) |

### Utilitários (Kerievsky, cap. 11)

| Refatoração | Padrão | Quando | Arquivo |
|---|---|---|---|
| Encadear Construtores (Chain Constructors) | — | vários construtores repetem o mesmo código | [chain-constructors.md](references/utilities/chain-constructors.md) |
| Unificar Interfaces (Unify Interfaces) | — | uma superclasse ou interface precisa da mesma interface de uma subclasse | [unify-interfaces.md](references/utilities/unify-interfaces.md) |
| Extrair Parâmetro (Extract Parameter) | — | um método ou construtor atribui a um campo um valor criado localmente | [extract-parameter.md](references/utilities/extract-parameter.md) |

Fontes: Martin Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed.,
Addison-Wesley (Pearson Education), 2018, e o catálogo online em
https://refactoring.com/catalog/; Joshua Kerievsky, *Refactoring to Patterns*, Addison-Wesley
(Pearson Education), 2004; páginas dos padrões em Gamma, Helm, Johnson e Vlissides, *Design
Patterns*, Addison-Wesley, 1995. Parafraseado; veja o NOTICE do pacote.
