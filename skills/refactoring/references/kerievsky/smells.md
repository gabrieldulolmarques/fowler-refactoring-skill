# The 12 smells

Kerievsky (2004), ch. 4, pp. 37-45 (each smell's page is in its heading), and the book's smell table
(inside back cover). Symptoms are paraphrased; each refactoring links to its file in this folder.

A smell is a hint, not a verdict. Most of these point to a refactoring to a pattern, and the pattern
is worth it only if it removes the smell more simply than the alternatives (see
[discipline.md](discipline.md)).

---

## Duplicated Code (p. 39)
**Symptoms:** the same or nearly the same code in several places, sometimes hidden: similar methods in sibling subclasses, constructors that repeat each other, separate code for one object and for many, the same null check everywhere.
**Try:**
- Form Template Method ([form-template-method.md](generalization/form-template-method.md)), for similar methods in sibling subclasses
- Introduce Polymorphic Creation with Factory Method ([introduce-polymorphic-creation-with-factory-method.md](creation/introduce-polymorphic-creation-with-factory-method.md)), when those methods differ only in the object they create
- Chain Constructors ([chain-constructors.md](utilities/chain-constructors.md)), for duplicated code across a class's constructors
- Replace One/Many Distinctions with Composite ([replace-one-many-distinctions-with-composite.md](generalization/replace-one-many-distinctions-with-composite.md)), for separate code that handles one object and a collection of them
- Extract Composite ([extract-composite.md](generalization/extract-composite.md)), for the same Composite logic in several classes of a hierarchy
- Unify Interfaces with Adapter ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), when objects are handled differently only because their interfaces differ
- Introduce Null Object ([introduce-null-object.md](protection/introduce-null-object.md)), for the same null check and fallback repeated across the code

## Long Method (p. 40)
**Symptoms:** a method too long to understand at a glance; it mixes levels of detail, builds up one result piece by piece, or holds several versions of an algorithm.
**Try:**
- Compose Method ([compose-method.md](simplification/compose-method.md)), to turn the method into a few calls at one level of detail
- Move Accumulation to Collecting Parameter ([move-accumulation-to-collecting-parameter.md](accumulation/move-accumulation-to-collecting-parameter.md)), when the method builds up one result piece by piece
- Replace Conditional Dispatcher with Command ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), when the method is a large dispatcher on a request name
- Move Accumulation to Visitor ([move-accumulation-to-visitor.md](accumulation/move-accumulation-to-visitor.md)), when a switch gathers data from classes with different interfaces
- Replace Conditional Logic with Strategy ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), when the method holds several variants of an algorithm and picks one at runtime

## Conditional Complexity (p. 41)
**Symptoms:** conditional logic that started small and grew with each feature until it is hard to follow.
**Try:**
- Replace Conditional Logic with Strategy ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), when the conditionals pick one of several variants of a calculation
- Move Embellishment to Decorator ([move-embellishment-to-decorator.md](simplification/move-embellishment-to-decorator.md)), when they switch optional behavior on top of the class's core job
- Replace State-Altering Conditionals with State ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), when they decide how the object moves between states
- Introduce Null Object ([introduce-null-object.md](protection/introduce-null-object.md)), when the same null check and fallback is repeated across the code

## Primitive Obsession (p. 41)
**Symptoms:** numbers, strings and other primitives where a class would model the idea more simply and attract the code that belongs to it.
**Try:**
- Replace Type Code with Class ([replace-type-code-with-class.md](protection/replace-type-code-with-class.md)), when a primitive type code drives logic and can take invalid values
- Replace State-Altering Conditionals with State ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), when primitive fields and conditionals control state transitions
- Replace Conditional Logic with Strategy ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), when primitives choose which algorithm runs
- Replace Implicit Tree with Composite ([replace-implicit-tree-with-composite.md](simplification/replace-implicit-tree-with-composite.md)), when a tree is built implicitly in strings or other primitives
- Replace Implicit Language with Interpreter ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), when many methods exist for combinations of primitive values
- Move Embellishment to Decorator ([move-embellishment-to-decorator.md](simplification/move-embellishment-to-decorator.md)), when primitives exist only to switch embellishments on and off
- Encapsulate Composite with Builder ([encapsulate-composite-with-builder.md](creation/encapsulate-composite-with-builder.md)), when a Composite is too tricky for clients to build

## Indecent Exposure (p. 42)
**Symptoms:** classes or methods that clients do not need are public, so clients depend on details (a lack of information hiding).
**Try:**
- Encapsulate Classes with Factory ([encapsulate-classes-with-factory.md](creation/encapsulate-classes-with-factory.md)), when clients should reach a set of classes only through their common interface

## Solution Sprawl (p. 43)
**Symptoms:** the code and data for one responsibility are spread over many classes, usually after a feature was added in a hurry. You notice it by reading the code, before a change forces edits in all those places.
**Try:**
- Move Creation Knowledge to Factory ([move-creation-knowledge-to-factory.md](creation/move-creation-knowledge-to-factory.md)), when the sprawling responsibility is object creation

## Alternative Classes with Different Interfaces (p. 43)
**Symptoms:** two classes do the same job through different interfaces, and one of them cannot be changed (third-party code).
**Try:**
- Unify Interfaces with Adapter ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md))

## Lazy Class (p. 43)
**Symptoms:** a class that does not do enough to pay for itself; often a Singleton that only adds global access.
**Try:**
- Inline Singleton ([inline-singleton.md](creation/inline-singleton.md))

## Large Class (p. 44)
**Symptoms:** a class with too many responsibilities, often because it holds a large dispatcher, a state machine or an implicit language.
**Try:**
- Replace Conditional Dispatcher with Command ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), when much of the class is dispatch logic
- Replace State-Altering Conditionals with State ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), when much of the class is state-transition logic
- Replace Implicit Language with Interpreter ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), when the class has a method for each combination of an implicit language

## Switch Statements (p. 44)
**Symptoms:** a switch (or `if`/`else if` chain) that makes the design more complicated or rigid than it needs to be. A switch is not bad in itself.
**Try:**
- Replace Conditional Dispatcher with Command ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), to break a large switch into Command objects looked up by key
- Move Accumulation to Visitor ([move-accumulation-to-visitor.md](accumulation/move-accumulation-to-visitor.md)), when a switch exists only to read data from classes with different interfaces

## Combinatorial Explosion (p. 45)
**Symptoms:** many pieces of code do the same thing with different kinds or amounts of data, such as one query method per combination of criteria.
**Try:**
- Replace Implicit Language with Interpreter ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), to replace the methods with a small language that combines the criteria

## Oddball Solution (p. 45)
**Symptoms:** the same problem is solved one way in most of the system and another way somewhere else; usually hidden duplication.
**Try:**
- Substitute Algorithm ([substitute-algorithm.md](../fowler/encapsulation/substitute-algorithm.md)), to make every place use the preferred solution, then move it to one place
- Unify Interfaces with Adapter ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), when the classes involved have different interfaces and so cannot be used the same way
