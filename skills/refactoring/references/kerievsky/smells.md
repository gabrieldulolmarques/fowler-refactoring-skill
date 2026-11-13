# Os 12 code smells

Kerievsky (2004), cap. 4, pp. 37-45 (a página de cada smell está no título), e a tabela de smells do livro (na contracapa interna). Os sintomas são parafraseados; cada refatoração aponta para o seu arquivo nesta pasta.

Um smell é uma pista, não um veredito. A maioria aponta para uma refatoração para um padrão, e o padrão só vale a pena se remover o smell de forma mais simples do que as alternativas (veja [discipline.md](discipline.md)).

---

## Código Duplicado (Duplicated Code, p. 39)
**Sintomas:** o mesmo código, ou quase o mesmo, em vários lugares, às vezes escondido: métodos parecidos em subclasses irmãs, construtores que se repetem, código separado para um objeto e para muitos, a mesma checagem de null em todo lugar.
**Tente:**
- Formar Template Method (Form Template Method) ([form-template-method.md](generalization/form-template-method.md)), para métodos parecidos em subclasses irmãs
- Introduzir Criação Polimórfica com Factory Method (Introduce Polymorphic Creation with Factory Method) ([introduce-polymorphic-creation-with-factory-method.md](creation/introduce-polymorphic-creation-with-factory-method.md)), quando esses métodos diferem apenas no objeto que criam
- Encadear Construtores (Chain Constructors) ([chain-constructors.md](utilities/chain-constructors.md)), para código duplicado entre os construtores de uma classe
- Substituir Distinções Um/Muitos por Composite (Replace One/Many Distinctions with Composite) ([replace-one-many-distinctions-with-composite.md](generalization/replace-one-many-distinctions-with-composite.md)), para código separado que trata um objeto e uma coleção deles
- Extrair Composite (Extract Composite) ([extract-composite.md](generalization/extract-composite.md)), para a mesma lógica de Composite em várias classes de uma hierarquia
- Unificar Interfaces com Adapter (Unify Interfaces with Adapter) ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), quando objetos são tratados de forma diferente só porque suas interfaces diferem
- Introduzir Null Object (Introduce Null Object) ([introduce-null-object.md](protection/introduce-null-object.md)), para a mesma checagem de null e o mesmo fallback repetidos pelo código

## Método Longo (Long Method, p. 40)
**Sintomas:** um método longo demais para entender de relance; ele mistura níveis de detalhe, constrói um resultado peça por peça ou guarda várias versões de um algoritmo.
**Tente:**
- Compor Método (Compose Method) ([compose-method.md](simplification/compose-method.md)), para transformar o método em algumas chamadas em um único nível de detalhe
- Mover Acumulação para Collecting Parameter (Move Accumulation to Collecting Parameter) ([move-accumulation-to-collecting-parameter.md](accumulation/move-accumulation-to-collecting-parameter.md)), quando o método constrói um resultado peça por peça
- Substituir Despachante Condicional por Command (Replace Conditional Dispatcher with Command) ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), quando o método é um grande despachante por nome de requisição
- Mover Acumulação para Visitor (Move Accumulation to Visitor) ([move-accumulation-to-visitor.md](accumulation/move-accumulation-to-visitor.md)), quando um switch reúne dados de classes com interfaces diferentes
- Substituir Lógica Condicional por Strategy (Replace Conditional Logic with Strategy) ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), quando o método guarda várias variantes de um algoritmo e escolhe uma em tempo de execução

## Complexidade Condicional (Conditional Complexity, p. 41)
**Sintomas:** lógica condicional que começou pequena e cresceu a cada funcionalidade, até ficar difícil de seguir.
**Tente:**
- Substituir Lógica Condicional por Strategy ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), quando os condicionais escolhem uma entre várias variantes de um cálculo
- Mover Embelezamento para Decorator (Move Embellishment to Decorator) ([move-embellishment-to-decorator.md](simplification/move-embellishment-to-decorator.md)), quando eles ligam comportamento opcional por cima do trabalho principal da classe
- Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State) ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), quando eles decidem como o objeto passa de um estado a outro
- Introduzir Null Object ([introduce-null-object.md](protection/introduce-null-object.md)), quando a mesma checagem de null e o mesmo fallback se repetem pelo código

## Obsessão por Primitivos (Primitive Obsession, p. 41)
**Sintomas:** números, strings e outros primitivos onde uma classe modelaria a ideia de forma mais simples e atrairia o código que lhe pertence.
**Tente:**
- Substituir Código de Tipo por Classe (Replace Type Code with Class) ([replace-type-code-with-class.md](protection/replace-type-code-with-class.md)), quando um código de tipo primitivo dirige a lógica e pode assumir valores inválidos
- Substituir Condicionais que Alteram Estado por State ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), quando campos primitivos e condicionais controlam as transições de estado
- Substituir Lógica Condicional por Strategy ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), quando primitivos escolhem qual algoritmo roda
- Substituir Árvore Implícita por Composite (Replace Implicit Tree with Composite) ([replace-implicit-tree-with-composite.md](simplification/replace-implicit-tree-with-composite.md)), quando uma árvore é montada implicitamente em strings ou outros primitivos
- Substituir Linguagem Implícita por Interpreter (Replace Implicit Language with Interpreter) ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), quando existem muitos métodos para combinações de valores primitivos
- Mover Embelezamento para Decorator ([move-embellishment-to-decorator.md](simplification/move-embellishment-to-decorator.md)), quando primitivos existem só para ligar e desligar embelezamentos
- Encapsular Composite com Builder (Encapsulate Composite with Builder) ([encapsulate-composite-with-builder.md](creation/encapsulate-composite-with-builder.md)), quando um Composite é complicado demais para os clientes montarem

## Exposição Indecente (Indecent Exposure, p. 42)
**Sintomas:** classes ou métodos que os clientes não precisam são públicos, então os clientes dependem de detalhes (falta de ocultação de informação).
**Tente:**
- Encapsular Classes com Factory (Encapsulate Classes with Factory) ([encapsulate-classes-with-factory.md](creation/encapsulate-classes-with-factory.md)), quando os clientes devem alcançar um conjunto de classes só pela interface comum

## Solução Espalhada (Solution Sprawl, p. 43)
**Sintomas:** o código e os dados de uma responsabilidade estão espalhados por muitas classes, geralmente depois que uma funcionalidade foi adicionada às pressas. Você percebe lendo o código, antes que uma mudança obrigue a editar todos esses lugares.
**Tente:**
- Mover Conhecimento de Criação para Factory (Move Creation Knowledge to Factory) ([move-creation-knowledge-to-factory.md](creation/move-creation-knowledge-to-factory.md)), quando a responsabilidade espalhada é a criação de objetos

## Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces, p. 43)
**Sintomas:** duas classes fazem o mesmo trabalho por meio de interfaces diferentes, e uma delas não pode ser alterada (código de terceiros).
**Tente:**
- Unificar Interfaces com Adapter ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md))

## Classe Preguiçosa (Lazy Class, p. 43)
**Sintomas:** uma classe que não faz o bastante para se justificar; muitas vezes um Singleton que só acrescenta acesso global.
**Tente:**
- Internalizar Singleton (Inline Singleton) ([inline-singleton.md](creation/inline-singleton.md))

## Classe Grande (Large Class, p. 44)
**Sintomas:** uma classe com responsabilidades demais, muitas vezes porque guarda um grande despachante, uma máquina de estados ou uma linguagem implícita.
**Tente:**
- Substituir Despachante Condicional por Command ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), quando grande parte da classe é lógica de despacho
- Substituir Condicionais que Alteram Estado por State ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), quando grande parte da classe é lógica de transição de estado
- Substituir Linguagem Implícita por Interpreter ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), quando a classe tem um método para cada combinação de uma linguagem implícita

## Comandos Switch (Switch Statements, p. 44)
**Sintomas:** um switch (ou uma cadeia de `if`/`else if`) que torna o design mais complicado ou rígido do que precisa. Um switch não é ruim em si.
**Tente:**
- Substituir Despachante Condicional por Command ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), para quebrar um switch grande em objetos Command buscados por chave
- Mover Acumulação para Visitor ([move-accumulation-to-visitor.md](accumulation/move-accumulation-to-visitor.md)), quando um switch existe só para ler dados de classes com interfaces diferentes

## Explosão Combinatória (Combinatorial Explosion, p. 45)
**Sintomas:** muitos trechos de código fazem a mesma coisa com tipos ou quantidades diferentes de dados, como um método de consulta para cada combinação de critérios.
**Tente:**
- Substituir Linguagem Implícita por Interpreter ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), para substituir os métodos por uma pequena linguagem que combina os critérios

## Solução Destoante (Oddball Solution, p. 45)
**Sintomas:** o mesmo problema é resolvido de um jeito na maior parte do sistema e de outro jeito em algum outro lugar; geralmente é uma duplicação escondida.
**Tente:**
- Substituir Algoritmo (Substitute Algorithm, de Fowler), para que todo lugar use a solução preferida e depois mover essa solução para um único lugar
- Unificar Interfaces com Adapter ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), quando as classes envolvidas têm interfaces diferentes e por isso não podem ser usadas da mesma forma
