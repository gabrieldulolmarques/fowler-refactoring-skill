# Os 23 padrões

Gamma et al. (1995), cap. 1, pp. 8-28, e as comparações que fecham os cap. 3-5 (pp. 135, 219, 345).
Paráfrase. Comece aqui para encontrar um padrão para um problema de design; cada padrão aponta para o seu arquivo.
Como escolher e aplicar um deles está em [principles.md](principles.md).

---

## Por propósito e escopo (p. 10)

*Propósito* diz o que um padrão faz: padrões criacionais tratam da criação de objetos, padrões estruturais da composição de classes ou objetos, padrões comportamentais de como objetos interagem e dividem responsabilidades. *Escopo* diz se o padrão funciona principalmente por herança (de classe, fixada em tempo de compilação) ou por composição de objetos (de objeto, alterável em tempo de execução).

| Escopo | Criacionais | Estruturais | Comportamentais |
|---|---|---|---|
| Classe | Factory Method | Adapter (de classe) | Interpreter, Template Method |
| Objeto | Abstract Factory, Builder, Prototype, Singleton | Adapter (de objeto), Bridge, Composite, Decorator, Facade, Flyweight, Proxy | Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Visitor |

## Intenção de cada padrão (pp. 8-9)

### Criacionais
- [Abstract Factory](creational/abstract-factory.md) (p. 87): criar famílias de objetos relacionados por meio de uma interface, sem nomear suas classes concretas.
- [Builder](creational/builder.md) (p. 97): executar uma mesma sequência de passos de construção que não depende da forma final, para que ela possa gerar várias formas de um objeto complexo.
- [Factory Method](creational/factory-method.md) (p. 107): declarar uma operação que cria um objeto e deixar as subclasses decidirem qual classe criar.
- [Prototype](creational/prototype.md) (p. 117): obter novos objetos clonando uma instância já configurada, o que também define os tipos disponíveis.
- [Singleton](creational/singleton.md) (p. 127): garantir que uma classe tenha uma única instância e oferecer um ponto de acesso global a ela.

### Estruturais
- [Adapter](structural/adapter.md) (p. 139): tornar uma classe utilizável por meio de uma interface que ela não implementa.
- [Bridge](structural/bridge.md) (p. 151): separar uma abstração da sua implementação, para que cada uma possa variar de forma independente.
- [Composite](structural/composite.md) (p. 163): organizar objetos em árvores que modelam hierarquias parte-todo e permitir que o cliente trate um objeto isolado e um grupo de objetos da mesma forma.
- [Decorator](structural/decorator.md) (p. 175): acrescentar responsabilidades a um objeto em tempo de execução, envolvendo-o, em vez de criar subclasses.
- [Facade](structural/facade.md) (p. 185): oferecer a um subsistema uma única interface mais simples.
- [Flyweight](structural/flyweight.md) (p. 195): compartilhar objetos de granularidade fina para que grandes quantidades deles continuem baratas.
- [Proxy](structural/proxy.md) (p. 207): colocar um substituto na frente de um objeto, para que o substituto decida como e quando o objeto real é acessado.

### Comportamentais
- [Chain of Responsibility](behavioral/chain-of-responsibility.md) (p. 223): passar uma requisição ao longo de uma cadeia de handlers até que um deles a trate, para que o remetente não conheça o destinatário.
- [Command](behavioral/command.md) (p. 233): transformar uma requisição em um objeto, para que ela possa ser enfileirada, registrada, parametrizada ou desfeita.
- [Interpreter](behavioral/interpreter.md) (p. 243): representar a gramática de uma linguagem pequena como classes e avaliar sentenças com elas.
- [Iterator](behavioral/iterator.md) (p. 257): percorrer os elementos de uma coleção um após o outro sem expor como ela é armazenada.
- [Mediator](behavioral/mediator.md) (p. 273): concentrar a interação entre um conjunto de objetos em um único objeto, para que eles não se referenciem mutuamente.
- [Memento](behavioral/memento.md) (p. 283): capturar o estado interno de um objeto fora dele, sem quebrar o encapsulamento, para que possa ser restaurado depois.
- [Observer](behavioral/observer.md) (p. 293): quando um objeto muda, notificar todos os objetos que dependem dele.
- [State](behavioral/state.md) (p. 305): entregar o comportamento de um objeto a um objeto separado por estado, de modo que o comportamento acompanhe o estado e o objeto pareça pertencer a outra classe.
- [Strategy](behavioral/strategy.md) (p. 315): colocar cada algoritmo de uma família atrás de uma mesma interface, para que sejam intercambiáveis.
- [Template Method](behavioral/template-method.md) (p. 325): definir o esqueleto de um algoritmo e deixar as subclasses preencherem alguns passos, sem alterar a estrutura do algoritmo.
- [Visitor](behavioral/visitor.md) (p. 331): adicionar operações sobre os elementos de uma estrutura sem alterar as classes deles.

## Da causa de reprojeto aos padrões que a evitam (p. 24)

| Causa de reprojeto | Padrões |
|---|---|
| Criar um objeto nomeando sua classe concreta | Abstract Factory, Factory Method, Prototype |
| Depender de uma operação específica para atender a uma requisição | Chain of Responsibility, Command |
| Depender de uma plataforma ou de uma API externa | Abstract Factory, Bridge |
| Clientes conhecerem como um objeto é representado, armazenado ou implementado | Abstract Factory, Bridge, Memento, Proxy |
| Depender de um algoritmo que provavelmente vai mudar | Builder, Iterator, Strategy, Template Method, Visitor |
| Acoplamento forte entre classes | Abstract Factory, Bridge, Chain of Responsibility, Command, Facade, Mediator, Observer |
| Estender o comportamento apenas por subclasses | Bridge, Chain of Responsibility, Composite, Decorator, Observer, Strategy |
| Uma classe que não se pode alterar com facilidade (sem código-fonte, com muitas subclasses) | Adapter, Decorator, Visitor |

## O que cada padrão permite variar (§1.7, Tabela 1.2)

| Padrão | O que pode variar sem reprojeto |
|---|---|
| Abstract Factory | a família de objetos produto |
| Builder | como um objeto composto é criado |
| Factory Method | qual subclasse do produto é instanciada |
| Prototype | qual classe de objeto é instanciada |
| Singleton | a única instância de uma classe |
| Adapter | a interface de um objeto |
| Bridge | a implementação de um objeto |
| Composite | a estrutura e a composição de um objeto |
| Decorator | as responsabilidades de um objeto, sem subclasses |
| Facade | a interface de um subsistema |
| Flyweight | o custo de armazenamento dos objetos |
| Proxy | como um objeto é acessado e onde ele vive |
| Chain of Responsibility | o objeto que atende a uma requisição |
| Command | quando e como uma requisição é executada |
| Interpreter | a gramática e a interpretação de uma linguagem |
| Iterator | como os elementos de uma coleção são acessados e percorridos |
| Mediator | como, e quais, objetos interagem |
| Memento | qual estado privado é armazenado fora de um objeto, e quando |
| Observer | quantos objetos dependem de outro, e como se mantêm atualizados |
| State | os estados de um objeto |
| Strategy | um algoritmo |
| Template Method | alguns passos de um algoritmo |
| Visitor | as operações aplicadas aos objetos, sem alterar as classes deles |

---

## Escolhendo entre padrões parecidos

### Criacionais (p. 135)
- Há duas formas de tornar um sistema independente das classes que ele cria: **criar subclasses** do criador (Factory Method), ou **passar um objeto** que conhece as classes (Abstract Factory, Builder, Prototype).
- Factory Method acrescenta apenas uma operação, por isso é o início mais barato; mas cada novo produto pode exigir uma nova subclasse de criador.
- Abstract Factory, Builder e Prototype são mais flexíveis e mais complexos. Os projetos costumam começar com Factory Method e migrar para um deles quando a flexibilidade realmente for necessária.
- Prototype pode substituir uma hierarquia paralela de fábricas quando cada produto consegue copiar a si mesmo.

### Estruturais (p. 219)
- **Adapter x Bridge:** ambos acrescentam indireção a outro objeto. Adapter concilia duas interfaces que já existem, normalmente depois do fato; Bridge separa uma abstração das suas implementações desde o início, para que ambas possam evoluir.
- **Facade x Adapter:** uma facade define uma interface nova e mais simples para muitos objetos; um adapter faz um objeto existente se encaixar em uma interface existente.
- **Composite x Decorator x Proxy:** os três mantêm uma referência a outros objetos de um tipo comum. Composite constrói árvores e trata partes e todo da mesma forma; Decorator acrescenta responsabilidades a um objeto sem criar subclasses; Proxy controla o acesso a um objeto que contém o comportamento real. Composite e Decorator são frequentemente usados juntos.

### Comportamentais (p. 345)
- **Encapsulando o que varia:** Strategy (um algoritmo), State (comportamento dependente do estado), Mediator (o protocolo entre objetos) e Iterator (percurso) colocam, cada um, um aspecto mutável em seu próprio objeto.
- **Objetos passados como argumentos:** um Visitor é passado aos objetos que ele visita; Command e Memento são tokens guardados e usados depois (uma requisição; um estado salvo).
- **Mediator x Observer:** Mediator concentra a comunicação em um único lugar, o que facilita o acompanhamento; Observer espalha a comunicação entre sujeitos e observadores, o que facilita o reúso.
- **Desacoplando remetentes e destinatários:** Command liga um remetente a um destinatário por meio de um objeto; Observer permite que qualquer número de destinatários se inscreva; Mediator faz tudo passar por um único objeto; Chain of Responsibility repassa a requisição até que alguém a trate.
- Padrões comportamentais combinam bem: um handler em uma cadeia costuma usar Template Method; um Composite costuma ser percorrido com Iterator ou estendido com Visitor.

## Padrões frequentemente usados juntos (§1.5)

- Composite com Iterator ou Visitor.
- Prototype como alternativa a Abstract Factory.
- Composite e Decorator têm estruturas parecidas com intenções diferentes.
- Cada arquivo de padrão lista seus padrões relacionados.
