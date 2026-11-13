# The 23 patterns

Gamma et al. (1995), ch. 1, pp. 8-28, and the comparisons that close ch. 3-5 (pp. 135, 219, 345).
Paraphrased. Start here to find a pattern for a design problem; each pattern links to its file.
How to choose and apply one is in [principles.md](principles.md).

---

## By purpose and scope (p. 10)

*Purpose* says what a pattern does: creational patterns deal with creating objects, structural
patterns with composing classes or objects, behavioral patterns with how objects interact and share
responsibilities. *Scope* says whether the pattern works mainly through inheritance (class, fixed at
compile time) or through object composition (object, changeable at run time).

| Scope | Creational | Structural | Behavioral |
|---|---|---|---|
| Class | Factory Method | Adapter (class) | Interpreter, Template Method |
| Object | Abstract Factory, Builder, Prototype, Singleton | Adapter (object), Bridge, Composite, Decorator, Facade, Flyweight, Proxy | Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Visitor |

## Intent of each pattern (pp. 8-9)

### Creational
- [Abstract Factory](creational/abstract-factory.md) (p. 87): create families of related objects through one interface, without naming their concrete classes.
- [Builder](creational/builder.md) (p. 97): run one sequence of construction steps that does not depend on the final form, so the same sequence can yield several forms of a complex object.
- [Factory Method](creational/factory-method.md) (p. 107): declare an operation that creates an object and let subclasses decide which class to create.
- [Prototype](creational/prototype.md) (p. 117): obtain new objects by cloning an instance that is already configured, which also defines the available kinds.
- [Singleton](creational/singleton.md) (p. 127): guarantee a class has one instance and give a global access point to it.

### Structural
- [Adapter](structural/adapter.md) (p. 139): make a class usable through an interface it does not implement.
- [Bridge](structural/bridge.md) (p. 151): split an abstraction from its implementation so each can vary on its own.
- [Composite](structural/composite.md) (p. 163): arrange objects in trees that model part-whole hierarchies, and let clients treat a single object and a group of objects the same way.
- [Decorator](structural/decorator.md) (p. 175): add responsibilities to an object at run time by wrapping it, instead of subclassing.
- [Facade](structural/facade.md) (p. 185): give a subsystem one simpler interface.
- [Flyweight](structural/flyweight.md) (p. 195): share fine-grained objects so that large numbers of them stay cheap.
- [Proxy](structural/proxy.md) (p. 207): put a substitute in front of an object, so the substitute decides how and when the real one is reached.

### Behavioral
- [Chain of Responsibility](behavioral/chain-of-responsibility.md) (p. 223): pass a request along a chain of handlers until one handles it, so the sender does not know the receiver.
- [Command](behavioral/command.md) (p. 233): turn a request into an object, so it can be queued, logged, parameterized or undone.
- [Interpreter](behavioral/interpreter.md) (p. 243): represent the grammar of a small language as classes and evaluate sentences with them.
- [Iterator](behavioral/iterator.md) (p. 257): walk the elements of a collection one after another without exposing how it is stored.
- [Mediator](behavioral/mediator.md) (p. 273): put the interaction between a set of objects in one object, so they do not refer to each other.
- [Memento](behavioral/memento.md) (p. 283): capture an object's internal state outside it, without breaking encapsulation, so it can be restored later.
- [Observer](behavioral/observer.md) (p. 293): when one object changes, notify all the objects that depend on it.
- [State](behavioral/state.md) (p. 305): hand an object's behavior to a separate object per state, so that behavior follows the state and the object seems to belong to another class.
- [Strategy](behavioral/strategy.md) (p. 315): put each algorithm of a family behind one interface so they are interchangeable.
- [Template Method](behavioral/template-method.md) (p. 325): define the skeleton of an algorithm and let subclasses fill in some steps, without changing the algorithm's structure.
- [Visitor](behavioral/visitor.md) (p. 331): add operations over the elements of a structure without changing their classes.

## From a cause of redesign to the patterns that prevent it (p. 24)

| Cause of redesign | Patterns |
|---|---|
| Creating an object by naming its concrete class | Abstract Factory, Factory Method, Prototype |
| Depending on one specific operation to serve a request | Chain of Responsibility, Command |
| Depending on a platform or an external API | Abstract Factory, Bridge |
| Clients knowing how an object is represented, stored or implemented | Abstract Factory, Bridge, Memento, Proxy |
| Depending on an algorithm that is likely to change | Builder, Iterator, Strategy, Template Method, Visitor |
| Tight coupling between classes | Abstract Factory, Bridge, Chain of Responsibility, Command, Facade, Mediator, Observer |
| Extending behavior only by subclassing | Bridge, Chain of Responsibility, Composite, Decorator, Observer, Strategy |
| A class you cannot change conveniently (no source, many subclasses) | Adapter, Decorator, Visitor |

## What each pattern lets you vary (§1.7, Table 1.2)

| Pattern | What can vary without redesign |
|---|---|
| Abstract Factory | the family of product objects |
| Builder | how a composite object is created |
| Factory Method | which subclass of the product is instantiated |
| Prototype | which class of object is instantiated |
| Singleton | the single instance of a class |
| Adapter | the interface to an object |
| Bridge | the implementation of an object |
| Composite | the structure and composition of an object |
| Decorator | an object's responsibilities, without subclassing |
| Facade | the interface to a subsystem |
| Flyweight | the storage cost of objects |
| Proxy | how an object is reached, and where it lives |
| Chain of Responsibility | the object that serves a request |
| Command | when and how a request is carried out |
| Interpreter | the grammar and interpretation of a language |
| Iterator | how the elements of a collection are accessed and traversed |
| Mediator | how, and which, objects interact |
| Memento | what private state is stored outside an object, and when |
| Observer | how many objects depend on another, and how they stay up to date |
| State | the states of an object |
| Strategy | an algorithm |
| Template Method | some steps of an algorithm |
| Visitor | the operations applied to objects, without changing their classes |

---

## Choosing between similar patterns

### Creational (p. 135)
- There are two ways to make a system independent of the classes it creates: **subclass** the
  creator (Factory Method), or **pass in an object** that knows the classes (Abstract Factory,
  Builder, Prototype).
- Factory Method adds only an operation, so it is the cheapest start; but each new product may
  need a new creator subclass.
- Abstract Factory, Builder and Prototype are more flexible and more complex. Designs often start
  with Factory Method and move to one of them when more flexibility is really needed.
- Prototype can replace a parallel hierarchy of factories when each product can copy itself.

### Structural (p. 219)
- **Adapter vs Bridge:** both add indirection to another object. Adapter reconciles two interfaces
  that already exist, usually after the fact; Bridge separates an abstraction from its
  implementations up front, so both can evolve.
- **Facade vs Adapter:** a facade defines a new, simpler interface to many objects; an adapter makes
  one existing object fit an existing interface.
- **Composite vs Decorator vs Proxy:** all three keep a reference to other objects of a common
  type. Composite builds trees and treats parts and wholes alike; Decorator adds responsibilities to
  one object without subclassing; Proxy controls access to an object that holds the real behavior.
  Composite and Decorator are often used together.

### Behavioral (p. 345)
- **Encapsulating what varies:** Strategy (an algorithm), State (state-dependent behavior), Mediator
  (the protocol between objects) and Iterator (traversal) each put a changing aspect in its own
  object.
- **Objects passed as arguments:** a Visitor is passed to the objects it visits; Command and Memento
  are tokens kept and used later (a request; a saved state).
- **Mediator vs Observer:** Mediator puts the communication in one place, which is easier to follow;
  Observer spreads it over subjects and observers, which is easier to reuse.
- **Decoupling senders and receivers:** Command binds one sender to one receiver through an object;
  Observer lets any number of receivers subscribe; Mediator routes everything through one object;
  Chain of Responsibility passes the request until someone handles it.
- Behavioral patterns combine well: a handler in a chain often uses Template Method; a Composite is
  often traversed with Iterator or extended with Visitor.

## Patterns often used together (§1.5)

- Composite with Iterator or Visitor.
- Prototype as an alternative to Abstract Factory.
- Composite and Decorator have similar structures with different intents.
- Each pattern file lists its related patterns.
