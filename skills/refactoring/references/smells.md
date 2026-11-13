# Os 29 code smells

Fowler (2018), cap. 3, pp. 71-84, traz 24 smells (a página de cada smell está no título). Kerievsky (2004), cap. 4, pp. 39-45, traz 12: sete correspondem a um smell de Fowler e aparecem nele, com as refatorações para padrões que acrescentam; os outros cinco estão no fim deste arquivo. Os sintomas são parafraseados; as listas de refatorações seguem o texto do capítulo. Cada refatoração tem link para o seu arquivo nesta pasta (`<slug>.md`).

Um smell é uma pista, não um veredito. Decida lendo o código; nenhuma métrica substitui o julgamento.

---

## Nome Misterioso (Mysterious Name, p. 72)
**Sintomas:** você precisa ler o corpo para saber para que serve uma função, variável, campo ou classe; nenhum bom nome vem à mente (muitas vezes um sinal de que o design está confuso).
**Tente:**
- Mudar Declaração de Função (Change Function Declaration) ([change-function-declaration.md](first-set/change-function-declaration.md)), para renomear uma função
- Renomear Variável (Rename Variable) ([rename-variable.md](first-set/rename-variable.md))
- Renomear Campo (Rename Field) ([rename-field.md](organizing-data/rename-field.md))

## Código Duplicado (Duplicated Code, p. 72)
**Sintomas:** a mesma estrutura em mais de um lugar, então cada leitor precisa comparar as cópias e cada mudança precisa atingir todas.
**Tente:**
- Extrair Função (Extract Function) ([extract-function.md](first-set/extract-function.md)), para código idêntico na mesma classe
- Deslocar Instruções (Slide Statements) ([slide-statements.md](moving-features/slide-statements.md)), para agrupar fragmentos parecidos, mas não idênticos, antes de extrair
- Subir Método (Pull Up Method) ([pull-up-method.md](inheritance/pull-up-method.md)), para cópias em subclasses irmãs

**Kerievsky (2004), p. 39, acrescenta:**
- Formar Template Method (Form Template Method) ([form-template-method.md](generalization/form-template-method.md)), para métodos parecidos em subclasses irmãs
- Introduzir Criação Polimórfica com Factory Method (Introduce Polymorphic Creation with Factory Method) ([introduce-polymorphic-creation-with-factory-method.md](creation/introduce-polymorphic-creation-with-factory-method.md)), quando esses métodos diferem só no objeto que criam
- Encadear Construtores (Chain Constructors) ([chain-constructors.md](utilities/chain-constructors.md)), para código duplicado entre os construtores de uma classe
- Substituir Distinções Um/Muitos por Composite (Replace One/Many Distinctions with Composite) ([replace-one-many-distinctions-with-composite.md](generalization/replace-one-many-distinctions-with-composite.md)), para trechos separados que tratam um objeto e uma coleção deles
- Extrair Composite (Extract Composite) ([extract-composite.md](generalization/extract-composite.md)), para a mesma lógica de Composite em várias classes de uma hierarquia
- Unificar Interfaces com Adapter (Unify Interfaces with Adapter) ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), quando objetos são tratados de forma diferente só porque suas interfaces diferem
- Introduzir Null Object (Introduce Null Object) ([introduce-null-object.md](protection/introduce-null-object.md)), para a mesma verificação de nulo, com a mesma alternativa, repetida pelo código

## Função Longa (Long Function, p. 73)
**Sintomas:** uma função em que você precisa rolar a tela; blocos que precisam de um comentário para dizer o que fazem; muitas variáveis temporárias e parâmetros; laços ou condicionais que fazem vários trabalhos.
**Tente:**
- Extrair Função ([extract-function.md](first-set/extract-function.md)), a resposta habitual, guiada pela intenção por trás de um comentário
- Extrair Função em cada ramo de um `switch` grande, de modo que cada ramo vire uma única chamada
- Extrair um laço junto com o seu corpo, como uma função, antes de considerar se ele deve ser dividido
- Substituir Variável Temporária por Consulta (Replace Temp with Query) ([replace-temp-with-query.md](encapsulation/replace-temp-with-query.md)), quando variáveis temporárias impedem a extração
- Introduzir Objeto de Parâmetros (Introduce Parameter Object) ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)) e Preservar Objeto Inteiro (Preserve Whole Object) ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), quando os parâmetros impedem a extração
- Substituir Função por Comando (Replace Function with Command) ([replace-function-with-command.md](refactoring-apis/replace-function-with-command.md)), quando variáveis temporárias e parâmetros ainda atrapalham
- Decompor Condicional (Decompose Conditional) ([decompose-conditional.md](conditional-logic/decompose-conditional.md)), para condicionais grandes
- Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism) ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md)), para o mesmo switch repetido
- Dividir Laço (Split Loop) ([split-loop.md](moving-features/split-loop.md)), quando um laço faz duas coisas e o pedaço extraído não tem um bom nome

**Kerievsky (2004), p. 40, como Método Longo (Long Method), acrescenta:**
- Compor Método (Compose Method) ([compose-method.md](simplification/compose-method.md)), para transformar o método em poucas chamadas no mesmo nível de detalhe
- Mover Acumulação para Collecting Parameter (Move Accumulation to Collecting Parameter) ([move-accumulation-to-collecting-parameter.md](accumulation/move-accumulation-to-collecting-parameter.md)), quando o método monta um resultado pedaço por pedaço
- Substituir Despachante Condicional por Command (Replace Conditional Dispatcher with Command) ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), quando o método é um grande despachante sobre o nome de um pedido
- Mover Acumulação para Visitor (Move Accumulation to Visitor) ([move-accumulation-to-visitor.md](accumulation/move-accumulation-to-visitor.md)), quando um switch junta dados de classes com interfaces diferentes
- Substituir Lógica Condicional por Strategy (Replace Conditional Logic with Strategy) ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), quando o método contém várias variantes de um algoritmo e escolhe uma em tempo de execução

## Lista Longa de Parâmetros (Long Parameter List, p. 74)
**Sintomas:** uma assinatura difícil de ler ou de chamar corretamente.
**Tente:**
- Substituir Parâmetro por Consulta (Replace Parameter with Query) ([replace-parameter-with-query.md](refactoring-apis/replace-parameter-with-query.md)), se um argumento puder ser derivado de outro
- Preservar Objeto Inteiro ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), em vez de desempacotar uma estrutura em vários argumentos
- Introduzir Objeto de Parâmetros ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), para argumentos que sempre viajam juntos
- Remover Argumento de Flag (Remove Flag Argument) ([remove-flag-argument.md](refactoring-apis/remove-flag-argument.md)), quando um parâmetro seleciona o comportamento
- Combinar Funções em Classe (Combine Functions into Class) ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)), quando várias funções compartilham os mesmos argumentos

## Dados Globais (Global Data, p. 74)
**Sintomas:** dados que qualquer código pode alterar e que ninguém consegue rastrear (variáveis globais, estáticos no nível da classe, singletons).
**Tente:**
- Encapsular Variável (Encapsulate Variable) ([encapsulate-variable.md](first-set/encapsulate-variable.md)), primeiro, para que o acesso passe por uma função; depois reduza o escopo para uma classe ou módulo

## Dados Mutáveis (Mutable Data, p. 75)
**Sintomas:** valores que mudam de formas surpreendentes, longe de onde são lidos; variáveis que guardam coisas diferentes em momentos diferentes; dados que poderiam ser calculados, mas são armazenados e atualizados.
O escopo determina a gravidade: uma variável alterada dentro de duas linhas é inofensiva; quanto maior o alcance, mais urgente a correção.
**Tente:**
- Encapsular Variável ([encapsulate-variable.md](first-set/encapsulate-variable.md)), para que as atualizações passem por funções estreitas
- Dividir Variável (Split Variable) ([split-variable.md](organizing-data/split-variable.md)), quando uma variável armazena coisas diferentes
- Deslocar Instruções ([slide-statements.md](moving-features/slide-statements.md)) e Extrair Função ([extract-function.md](first-set/extract-function.md)), para separar o código sem efeitos colaterais do código que atualiza
- Separar Consulta de Modificador (Separate Query from Modifier) ([separate-query-from-modifier.md](refactoring-apis/separate-query-from-modifier.md)), para que os chamadores não disparem efeitos colaterais ao ler
- Remover Método de Escrita (Remove Setting Method) ([remove-setting-method.md](refactoring-apis/remove-setting-method.md)), quando nenhum chamador precisar atribuir o campo
- Substituir Variável Derivada por Consulta (Replace Derived Variable with Query) ([replace-derived-variable-with-query.md](organizing-data/replace-derived-variable-with-query.md)), para dados armazenados que podem ser calculados
- Combinar Funções em Classe ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)) ou Combinar Funções em Transformação (Combine Functions into Transform) ([combine-functions-into-transform.md](first-set/combine-functions-into-transform.md)), para limitar quanto código pode atualizar os dados
- Mudar Referência para Valor (Change Reference to Value) ([change-reference-to-value.md](organizing-data/change-reference-to-value.md)), para substituir uma estrutura em vez de editá-la no lugar

## Alteração Divergente (Divergent Change, p. 76)
**Sintomas:** um módulo muda o tempo todo por motivos não relacionados (um conjunto de edições para um novo banco de dados, outro para um novo formato de relatório).
**Tente:**
- Dividir em Fases (Split Phase) ([split-phase.md](first-set/split-phase.md)), se as duas preocupações formarem uma sequência
- Mover Função (Move Function) ([move-function.md](moving-features/move-function.md)), para módulos separados quando as chamadas vão e voltam
- Extrair Função ([extract-function.md](first-set/extract-function.md)), para dividir funções que misturam as duas preocupações antes de movê-las
- Extrair Classe (Extract Class) ([extract-class.md](encapsulation/extract-class.md)), quando os módulos são classes

## Cirurgia com Espingarda (Shotgun Surgery, p. 76)
**Sintomas:** uma única mudança força pequenas edições em muitas classes; é fácil esquecer uma. O oposto de Alteração Divergente.
**Tente:**
- Mover Função ([move-function.md](moving-features/move-function.md)) e Mover Campo (Move Field) ([move-field.md](moving-features/move-field.md)), para reunir as edições em um módulo
- Combinar Funções em Classe ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)), para funções que trabalham sobre os mesmos dados
- Combinar Funções em Transformação ([combine-functions-into-transform.md](first-set/combine-functions-into-transform.md)), para funções que enriquecem uma estrutura
- Dividir em Fases ([split-phase.md](first-set/split-phase.md)), quando as funções compartilhadas podem alimentar uma fase consumidora
- Internalizar Função (Inline Function) ([inline-function.md](first-set/inline-function.md)) e Internalizar Classe (Inline Class) ([inline-class.md](encapsulation/inline-class.md)), para reunir primeiro a lógica mal dividida e depois extrair de novo (uma função ou classe grande temporária é aceitável)

## Inveja de Recursos (Feature Envy, p. 77)
**Sintomas:** uma função conversa mais com os dados ou getters de outro módulo do que com os seus próprios.
**Tente:**
- Mover Função ([move-function.md](moving-features/move-function.md)), para colocá-la junto dos dados
- Extrair Função ([extract-function.md](first-set/extract-function.md)), quando só parte da função tem inveja, e então mover essa parte
- Quando a função toca vários módulos, coloque-a junto do que guarda mais dados. Alguns padrões mantêm de propósito o comportamento separado dos dados, para que cada um possa variar por conta própria (Strategy, Visitor e Self Delegation, de Kent Beck); trate-os como exceções legítimas, e como remédios para Alteração Divergente.

## Agrupamentos de Dados (Data Clumps, p. 78)
**Sintomas:** os mesmos poucos valores aparecem juntos como campos em várias classes e como parâmetros em muitas assinaturas. Verificação rápida: se um valor perde o significado quando tomado sozinho, o grupo é um conceito esperando para virar objeto.
**Tente:**
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)), primeiro nos campos
- Introduzir Objeto de Parâmetros ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), depois nas assinaturas
- Preservar Objeto Inteiro ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), depois nas assinaturas
- Prefira uma classe (ou record) que possa ganhar comportamento depois, não um simples recipiente de dados ou tupla
- Ainda vale extrair quando um chamador precisa de apenas parte do novo objeto, desde que o objeto absorva dois ou mais dos campos ou argumentos desse chamador

## Obsessão por Primitivos (Primitive Obsession, p. 78)
**Sintomas:** conceitos do domínio guardados como números ou strings simples (quantidades sem unidades, intervalos como comparações em pares, códigos "stringly typed").
**Tente:**
- Substituir Primitivo por Objeto (Replace Primitive with Object) ([replace-primitive-with-object.md](encapsulation/replace-primitive-with-object.md))
- Substituir Código de Tipo por Subclasses (Replace Type Code with Subclasses) ([replace-type-code-with-subclasses.md](inheritance/replace-type-code-with-subclasses.md)), depois Substituir Condicional por Polimorfismo ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md)), quando o primitivo é um código de tipo que dirige condicionais
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)) e Introduzir Objeto de Parâmetros ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), para primitivos que viajam em grupos

**Kerievsky (2004), p. 41, acrescenta:**
- Substituir Código de Tipo por Classe (Replace Type Code with Class) ([replace-type-code-with-class.md](protection/replace-type-code-with-class.md)), quando um código de tipo primitivo comanda a lógica e aceita valores inválidos
- Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State) ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), quando campos primitivos e condicionais controlam as transições de estado
- Substituir Lógica Condicional por Strategy (Replace Conditional Logic with Strategy) ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), quando primitivos escolhem qual algoritmo executar
- Substituir Árvore Implícita por Composite (Replace Implicit Tree with Composite) ([replace-implicit-tree-with-composite.md](simplification/replace-implicit-tree-with-composite.md)), quando uma árvore é montada implicitamente em strings ou outros primitivos
- Substituir Linguagem Implícita por Interpreter (Replace Implicit Language with Interpreter) ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), quando existem muitos métodos para combinações de valores primitivos
- Mover Embelezamento para Decorator (Move Embellishment to Decorator) ([move-embellishment-to-decorator.md](simplification/move-embellishment-to-decorator.md)), quando primitivos existem só para ligar e desligar embelezamentos
- Encapsular Composite com Builder (Encapsulate Composite with Builder) ([encapsulate-composite-with-builder.md](creation/encapsulate-composite-with-builder.md)), quando montar um Composite é complicado demais para os clientes

## Switches Repetidos (Repeated Switches, p. 79)
**Sintomas:** o mesmo switch ou cascata de if/else sobre a mesma condição aparece em vários lugares, então cada novo caso exige uma caçada.
**Tente:**
- Substituir Condicional por Polimorfismo ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md))

**Kerievsky (2004), p. 44, como Comandos Switch (Switch Statements), acrescenta:**
- Substituir Despachante Condicional por Command (Replace Conditional Dispatcher with Command) ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), para quebrar um switch grande em objetos Command buscados por chave
- Mover Acumulação para Visitor (Move Accumulation to Visitor) ([move-accumulation-to-visitor.md](accumulation/move-accumulation-to-visitor.md)), quando um switch existe só para ler dados de classes com interfaces diferentes

## Laços (Loops, p. 79)
**Sintomas:** laços em que um pipeline de filtro/mapeamento mostraria o que é selecionado e o que é feito com isso.
**Tente:**
- Substituir Laço por Pipeline (Replace Loop with Pipeline) ([replace-loop-with-pipeline.md](moving-features/replace-loop-with-pipeline.md))

## Elemento Ocioso (Lazy Element, p. 80)
**Sintomas:** uma função, classe ou nível de hierarquia que já não justifica a sua estrutura (um nome que repete o corpo, uma classe que é uma única função trivial).
**Tente:**
- Internalizar Função ([inline-function.md](first-set/inline-function.md))
- Internalizar Classe ([inline-class.md](encapsulation/inline-class.md))
- Colapsar Hierarquia (Collapse Hierarchy) ([collapse-hierarchy.md](inheritance/collapse-hierarchy.md))

**Kerievsky (2004), p. 43, como Classe Preguiçosa (Lazy Class), acrescenta:**
- Internalizar Singleton (Inline Singleton) ([inline-singleton.md](creation/inline-singleton.md)), para um Singleton que não compensa o acesso global que acrescenta

## Generalidade Especulativa (Speculative Generality, p. 80)
**Sintomas:** ganchos, abstrações e parâmetros adicionados para necessidades que nunca vieram; às vezes só os testes os usam.
**Tente:**
- Colapsar Hierarquia ([collapse-hierarchy.md](inheritance/collapse-hierarchy.md)), para classes abstratas que fazem pouco
- Internalizar Função ([inline-function.md](first-set/inline-function.md)) e Internalizar Classe ([inline-class.md](encapsulation/inline-class.md)), para delegação desnecessária
- Mudar Declaração de Função ([change-function-declaration.md](first-set/change-function-declaration.md)), para eliminar parâmetros não usados
- Remover Código Morto (Remove Dead Code) ([remove-dead-code.md](moving-features/remove-dead-code.md)), inclusive código que só os testes chamam (apague esses testes também)

## Campo Temporário (Temporary Field, p. 80)
**Sintomas:** um campo definido só em algumas circunstâncias, então os leitores se perguntam por que ele existe quando está vazio.
**Tente:**
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)), para dar um lar a esses campos
- Mover Função ([move-function.md](moving-features/move-function.md)), para mover o código que os usa para essa classe
- Introduzir Caso Especial (Introduce Special Case) ([introduce-special-case.md](conditional-logic/introduce-special-case.md)), para substituir as verificações de "campos não válidos" por uma classe alternativa

## Cadeias de Mensagens (Message Chains, p. 81)
**Sintomas:** um cliente navega objeto após objeto (`a.b().c().d()`), ficando acoplado à estrutura do caminho.
**Tente:**
- Ocultar Delegação (Hide Delegate) ([hide-delegate.md](encapsulation/hide-delegate.md)), em um ou mais pontos da cadeia
- Extrair Função ([extract-function.md](first-set/extract-function.md)) no código que usa o fim da cadeia, depois Mover Função ([move-function.md](moving-features/move-function.md)) pela cadeia abaixo; muitas vezes melhor que ocultar cada elo, o que cria intermediários
- Adicione um método no objeto intermediário que faça toda a navegação, quando vários clientes quiserem percorrer o resto da cadeia

## Intermediário (Middle Man, p. 81)
**Sintomas:** cerca de metade dos métodos de uma classe apenas repassa para outra classe.
**Tente:**
- Remover Intermediário (Remove Middle Man) ([remove-middle-man.md](encapsulation/remove-middle-man.md))
- Internalizar Função ([inline-function.md](first-set/inline-function.md)), se apenas alguns métodos só delegam
- Substituir Superclasse por Delegação (Replace Superclass with Delegate) ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)) ou Substituir Subclasse por Delegação (Replace Subclass with Delegate) ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)), quando o intermediário também tem comportamento próprio, para transformá-lo no colaborador de verdade

## Troca de Informações Privilegiadas (Insider Trading, p. 82)
**Sintomas:** módulos que trocam dados livremente demais; subclasses que sabem demais sobre os pais.
**Tente:**
- Mover Função ([move-function.md](moving-features/move-function.md)) e Mover Campo ([move-field.md](moving-features/move-field.md)), para reduzir a conversa
- Ocultar Delegação ([hide-delegate.md](encapsulation/hide-delegate.md)), para usar um intermediário
- Crie um terceiro módulo para os interesses compartilhados
- Substituir Subclasse por Delegação ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)) ou Substituir Superclasse por Delegação ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)), para conluio por herança

## Classe Grande (Large Class, p. 82)
**Sintomas:** campos demais (muitas vezes com prefixos ou sufixos comuns) ou código demais; a duplicação cresce lá dentro. Clientes que usam só um subconjunto dos recursos sugerem a divisão.
**Tente:**
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)), para agrupar campos relacionados ou um subconjunto usado por clientes; uma classe que não usa todos os seus campos o tempo todo pode ser dividida mais de uma vez
- Extrair Superclasse (Extract Superclass) ([extract-superclass.md](inheritance/extract-superclass.md)), quando o componente faz sentido como herança
- Substituir Código de Tipo por Subclasses ([replace-type-code-with-subclasses.md](inheritance/replace-type-code-with-subclasses.md)), que na prática é extrair uma subclasse

**Kerievsky (2004), p. 44, acrescenta:**
- Substituir Despachante Condicional por Command (Replace Conditional Dispatcher with Command) ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), quando boa parte da classe é lógica de despacho
- Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State) ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), quando boa parte da classe é lógica de transição de estado
- Substituir Linguagem Implícita por Interpreter (Replace Implicit Language with Interpreter) ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), quando a classe tem um método para cada combinação de uma linguagem implícita

## Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces, p. 83)
**Sintomas:** duas classes fazem o mesmo trabalho, mas não podem ser trocadas porque os nomes e assinaturas dos métodos diferem.
**Tente:**
- Mudar Declaração de Função ([change-function-declaration.md](first-set/change-function-declaration.md)), para fazer as assinaturas coincidirem
- Mover Função ([move-function.md](moving-features/move-function.md)), até que os protocolos coincidam
- Extrair Superclasse ([extract-superclass.md](inheritance/extract-superclass.md)), se o alinhamento deixar duplicação

**Kerievsky (2004), p. 43, acrescenta:**
- Unificar Interfaces com Adapter (Unify Interfaces with Adapter) ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), quando não dá para alterar uma das classes (código de terceiros)

## Classe de Dados (Data Class, p. 83)
**Sintomas:** uma classe com campos e acessores e nada mais, manipulada em detalhe por outras (muitas vezes com campos públicos). Exceção: um record de resultado imutável, como o que fica entre duas fases após um Dividir em Fases.
**Tente:**
- Encapsular Registro (Encapsulate Record) ([encapsulate-record.md](encapsulation/encapsulate-record.md)), de imediato, para campos públicos
- Remover Método de Escrita ([remove-setting-method.md](refactoring-apis/remove-setting-method.md)), para campos que não devem mudar
- Mover Função ([move-function.md](moving-features/move-function.md)), para trazer o comportamento dos clientes para dentro da classe
- Extrair Função ([extract-function.md](first-set/extract-function.md)), para isolar primeiro um trecho movível

## Herança Recusada (Refused Bequest, p. 83)
**Sintomas:** uma subclasse usa pouco do que herda. Costuma ser um smell fraco; forte quando a subclasse recusa a interface do pai e não só a implementação.
**Tente:**
- Descer Método (Push Down Method) ([push-down-method.md](inheritance/push-down-method.md)) e Descer Campo (Push Down Field) ([push-down-field.md](inheritance/push-down-field.md)), movendo os membros não usados para uma nova irmã (o conselho tradicional; só vale a pena quando causa confusão real)
- Substituir Subclasse por Delegação ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)) ou Substituir Superclasse por Delegação ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)), quando a interface é recusada

## Comentários (Comments, p. 84)
**Sintomas:** comentários que existem porque o código não é claro. Comentários que explicam o porquê, ou admitem dúvida, são bons.
**Tente:**
- Extrair Função ([extract-function.md](first-set/extract-function.md)), quando um comentário explica um bloco
- Mudar Declaração de Função ([change-function-declaration.md](first-set/change-function-declaration.md)), para renomear uma função que ainda precisa de um comentário
- Introduzir Asserção (Introduce Assertion) ([introduce-assertion.md](conditional-logic/introduce-assertion.md)), para declarar uma regra sobre o estado necessário

---

# Smells de Kerievsky (2004)

Cap. 4. Cada um aponta principalmente para uma refatoração para padrão.

## Complexidade Condicional (Conditional Complexity, p. 41)
**Sintomas:** lógica condicional que começou pequena e cresceu a cada funcionalidade até ficar difícil de acompanhar.
**Tente:**
- Substituir Lógica Condicional por Strategy (Replace Conditional Logic with Strategy) ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), quando as condicionais escolhem uma de várias variantes de um cálculo
- Mover Embelezamento para Decorator (Move Embellishment to Decorator) ([move-embellishment-to-decorator.md](simplification/move-embellishment-to-decorator.md)), quando ligam comportamento opcional por cima do trabalho principal da classe
- Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State) ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), quando decidem como o objeto passa de um estado para outro
- Introduzir Null Object (Introduce Null Object) ([introduce-null-object.md](protection/introduce-null-object.md)), quando a mesma verificação de nulo, com a mesma alternativa, se repete pelo código

## Exposição Indecente (Indecent Exposure, p. 42)
**Sintomas:** classes ou métodos de que os clientes não precisam são públicos, então os clientes dependem de detalhes (falta de ocultação de informação).
**Tente:**
- Encapsular Classes com Factory (Encapsulate Classes with Factory) ([encapsulate-classes-with-factory.md](creation/encapsulate-classes-with-factory.md)), quando os clientes deveriam chegar a um conjunto de classes só pela interface comum delas

## Solução Espalhada (Solution Sprawl, p. 43)
**Sintomas:** o código e os dados de uma responsabilidade estão espalhados por muitas classes, em geral depois de uma funcionalidade acrescentada às pressas. É o mesmo problema da Cirurgia com Espingarda (Shotgun Surgery), percebido ao ler o código em vez de ao alterá-lo.
**Tente:**
- Mover Conhecimento de Criação para Factory (Move Creation Knowledge to Factory) ([move-creation-knowledge-to-factory.md](creation/move-creation-knowledge-to-factory.md)), quando a responsabilidade espalhada é a criação de objetos
- As refatorações de Cirurgia com Espingarda acima, para outras responsabilidades

## Explosão Combinatória (Combinatorial Explosion, p. 45)
**Sintomas:** muitos trechos fazem a mesma coisa com tipos ou quantidades diferentes de dados, como um método de consulta para cada combinação de critérios.
**Tente:**
- Substituir Linguagem Implícita por Interpreter (Replace Implicit Language with Interpreter) ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), para trocar os métodos por uma pequena linguagem que combina os critérios

## Solução Destoante (Oddball Solution, p. 45)
**Sintomas:** o mesmo problema é resolvido de um jeito na maior parte do sistema e de outro em algum lugar; em geral, duplicação escondida.
**Tente:**
- Substituir Algoritmo ([substitute-algorithm.md](encapsulation/substitute-algorithm.md)), para que todos os lugares usem a solução preferida e, depois, movê-la para um só lugar
- Unificar Interfaces com Adapter (Unify Interfaces with Adapter) ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), quando as classes envolvidas têm interfaces diferentes e por isso não podem ser usadas do mesmo jeito
