# The 29 smells

Fowler (2018), ch. 3, pp. 71-84, gives 24 smells (each smell's page is in its heading). Kerievsky (2004), ch. 4, pp. 39-45, gives 12: seven match a Fowler smell and are listed under it, with the refactorings to patterns they add; the other five are at the end of this file. Symptoms are paraphrased; the refactoring lists follow the chapter's text. Each refactoring links to its file in this folder (`<slug>.md`).

A smell is a hint, not a verdict. Decide by reading the code; no metric replaces judgment.

---

## Mysterious Name (p. 72)
**Symptoms:** you must read the body to learn what a function, variable, field or class is for; no good name comes to mind (often a sign the design is muddled).
**Try:**
- Change Function Declaration ([change-function-declaration.md](first-set/change-function-declaration.md)), to rename a function
- Rename Variable ([rename-variable.md](first-set/rename-variable.md))
- Rename Field ([rename-field.md](organizing-data/rename-field.md))

## Duplicated Code (p. 72)
**Symptoms:** the same structure in more than one place, so each reader must compare the copies and each change must hit them all.
**Try:**
- Extract Function ([extract-function.md](first-set/extract-function.md)), for identical code in the same class
- Slide Statements ([slide-statements.md](moving-features/slide-statements.md)), to group similar-but-not-identical fragments before extracting
- Pull Up Method ([pull-up-method.md](inheritance/pull-up-method.md)), for copies in sibling subclasses

**Kerievsky (2004), p. 39, adds:**
- Form Template Method ([form-template-method.md](generalization/form-template-method.md)), for similar methods in sibling subclasses
- Introduce Polymorphic Creation with Factory Method ([introduce-polymorphic-creation-with-factory-method.md](creation/introduce-polymorphic-creation-with-factory-method.md)), when such methods differ only in the object they create
- Chain Constructors ([chain-constructors.md](utilities/chain-constructors.md)), for duplicated code across a class's constructors
- Replace One/Many Distinctions with Composite ([replace-one-many-distinctions-with-composite.md](generalization/replace-one-many-distinctions-with-composite.md)), for separate code that handles one object and a collection of them
- Extract Composite ([extract-composite.md](generalization/extract-composite.md)), for the same Composite logic in several classes of a hierarchy
- Unify Interfaces with Adapter ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), when objects are handled differently only because their interfaces differ
- Introduce Null Object ([introduce-null-object.md](protection/introduce-null-object.md)), for the same null check and fallback repeated across the code

## Long Function (p. 73)
**Symptoms:** a function you need to scroll through; blocks that need a comment to say what they do; many temps and parameters; loops or conditionals doing several jobs.
**Try:**
- Extract Function ([extract-function.md](first-set/extract-function.md)), the usual answer, driven by the intent behind a comment
- Extract Function on each branch of a large `switch`, so every branch becomes a single call
- Extract a loop together with its body, as one function, before considering whether to split it
- Replace Temp with Query ([replace-temp-with-query.md](encapsulation/replace-temp-with-query.md)), when temps block extraction
- Introduce Parameter Object ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)) and Preserve Whole Object ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), when parameters block extraction
- Replace Function with Command ([replace-function-with-command.md](refactoring-apis/replace-function-with-command.md)), when temps and parameters still get in the way
- Decompose Conditional ([decompose-conditional.md](conditional-logic/decompose-conditional.md)), for big conditionals
- Replace Conditional with Polymorphism ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md)), for the same switch repeated
- Split Loop ([split-loop.md](moving-features/split-loop.md)), when a loop does two things and the extracted piece has no good name

**Kerievsky (2004), p. 40, as Long Method, adds:**
- Compose Method ([compose-method.md](simplification/compose-method.md)), to turn the method into a few calls at one level of detail
- Move Accumulation to Collecting Parameter ([move-accumulation-to-collecting-parameter.md](accumulation/move-accumulation-to-collecting-parameter.md)), when the method builds up one result piece by piece
- Replace Conditional Dispatcher with Command ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), when the method is a large dispatcher on a request name
- Move Accumulation to Visitor ([move-accumulation-to-visitor.md](accumulation/move-accumulation-to-visitor.md)), when a switch gathers data from classes with different interfaces
- Replace Conditional Logic with Strategy ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), when the method holds several variants of an algorithm and picks one at runtime

## Long Parameter List (p. 74)
**Symptoms:** a signature that is hard to read or call correctly.
**Try:**
- Replace Parameter with Query ([replace-parameter-with-query.md](refactoring-apis/replace-parameter-with-query.md)), if one argument can be derived from another
- Preserve Whole Object ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), instead of unpacking a structure into many arguments
- Introduce Parameter Object ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), for arguments that always travel together
- Remove Flag Argument ([remove-flag-argument.md](refactoring-apis/remove-flag-argument.md)), when a parameter selects the behavior
- Combine Functions into Class ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)), when several functions share the same arguments

## Global Data (p. 74)
**Symptoms:** data that any code can change and nobody can trace (global variables, class-level statics, singletons).
**Try:**
- Encapsulate Variable ([encapsulate-variable.md](first-set/encapsulate-variable.md)), first, so access goes through a function; then shrink the scope into a class or module

## Mutable Data (p. 75)
**Symptoms:** values that change in surprising ways far from where they are read; variables that hold different things at different times; data that could be computed but is stored and updated.
Scope drives severity: a variable mutated within a couple of lines is harmless; the wider its reach, the more urgent the fix.
**Try:**
- Encapsulate Variable ([encapsulate-variable.md](first-set/encapsulate-variable.md)), so updates pass through narrow functions
- Split Variable ([split-variable.md](organizing-data/split-variable.md)), when one variable stores different things
- Slide Statements ([slide-statements.md](moving-features/slide-statements.md)) and Extract Function ([extract-function.md](first-set/extract-function.md)), to separate side-effect-free code from the code that updates
- Separate Query from Modifier ([separate-query-from-modifier.md](refactoring-apis/separate-query-from-modifier.md)), so callers do not trigger side effects by reading
- Remove Setting Method ([remove-setting-method.md](refactoring-apis/remove-setting-method.md)), once no caller needs to assign the field
- Replace Derived Variable with Query ([replace-derived-variable-with-query.md](organizing-data/replace-derived-variable-with-query.md)), for stored data that can be computed
- Combine Functions into Class ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)) or Combine Functions into Transform ([combine-functions-into-transform.md](first-set/combine-functions-into-transform.md)), to limit how much code can update the data
- Change Reference to Value ([change-reference-to-value.md](organizing-data/change-reference-to-value.md)), to replace a structure instead of editing it in place

## Divergent Change (p. 76)
**Symptoms:** one module keeps changing for unrelated reasons (one set of edits for a new database, another for a new report format).
**Try:**
- Split Phase ([split-phase.md](first-set/split-phase.md)), if the two concerns form a sequence
- Move Function ([move-function.md](moving-features/move-function.md)), to separate modules when calls go back and forth
- Extract Function ([extract-function.md](first-set/extract-function.md)), to split functions that mix both concerns before moving them
- Extract Class ([extract-class.md](encapsulation/extract-class.md)), when the modules are classes

## Shotgun Surgery (p. 76)
**Symptoms:** a single change forces small edits in many classes; easy to miss one. The opposite of Divergent Change.
**Try:**
- Move Function ([move-function.md](moving-features/move-function.md)) and Move Field ([move-field.md](moving-features/move-field.md)), to gather the edits in one module
- Combine Functions into Class ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)), for functions working on the same data
- Combine Functions into Transform ([combine-functions-into-transform.md](first-set/combine-functions-into-transform.md)), for functions enriching a structure
- Split Phase ([split-phase.md](first-set/split-phase.md)), when the shared functions can feed a consuming phase
- Inline Function ([inline-function.md](first-set/inline-function.md)) and Inline Class ([inline-class.md](encapsulation/inline-class.md)), to pull badly split logic together first, then re-extract (a temporary big function or class is acceptable)

## Feature Envy (p. 77)
**Symptoms:** a function talks to another module's data or getters more than to its own.
**Try:**
- Move Function ([move-function.md](moving-features/move-function.md)), to put it with the data
- Extract Function ([extract-function.md](first-set/extract-function.md)), when only part of the function is envious, then move that part
- When the function touches several modules, put it with the one holding most of the data. Some patterns deliberately keep behavior apart from data so each can vary on its own (Strategy, Visitor, and Self Delegation from Kent Beck); treat them as legitimate exceptions, and as remedies for Divergent Change.

## Data Clumps (p. 78)
**Symptoms:** the same few values appear together as fields in several classes and as parameters in many signatures. Quick check: if a value loses its meaning when taken alone, the group is one concept waiting to become an object.
**Try:**
- Extract Class ([extract-class.md](encapsulation/extract-class.md)), on the fields first
- Introduce Parameter Object ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), then on signatures
- Preserve Whole Object ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), then on signatures
- Prefer a class (or record) that can later gain behavior, not a bare data holder or tuple
- Still worth extracting when a caller needs only part of the new object, provided the object absorbs two or more of that caller's fields or arguments

## Primitive Obsession (p. 78)
**Symptoms:** domain concepts held as plain numbers or strings (quantities without units, ranges as paired comparisons, "stringly typed" codes).
**Try:**
- Replace Primitive with Object ([replace-primitive-with-object.md](encapsulation/replace-primitive-with-object.md))
- Replace Type Code with Subclasses ([replace-type-code-with-subclasses.md](inheritance/replace-type-code-with-subclasses.md)), then Replace Conditional with Polymorphism ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md)), when the primitive is a type code driving conditionals
- Extract Class ([extract-class.md](encapsulation/extract-class.md)) and Introduce Parameter Object ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), for primitives that travel in groups

**Kerievsky (2004), p. 41, adds:**
- Replace Type Code with Class ([replace-type-code-with-class.md](protection/replace-type-code-with-class.md)), when a primitive type code drives logic and can take invalid values
- Replace State-Altering Conditionals with State ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), when primitive fields and conditionals control state transitions
- Replace Conditional Logic with Strategy ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), when primitives choose which algorithm runs
- Replace Implicit Tree with Composite ([replace-implicit-tree-with-composite.md](simplification/replace-implicit-tree-with-composite.md)), when a tree is built implicitly in strings or other primitives
- Replace Implicit Language with Interpreter ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), when many methods exist for combinations of primitive values
- Move Embellishment to Decorator ([move-embellishment-to-decorator.md](simplification/move-embellishment-to-decorator.md)), when primitives exist only to switch embellishments on and off
- Encapsulate Composite with Builder ([encapsulate-composite-with-builder.md](creation/encapsulate-composite-with-builder.md)), when a Composite is too tricky for clients to build

## Repeated Switches (p. 79)
**Symptoms:** the same switch or if/else cascade on the same condition appears in several places, so each new case means a hunt.
**Try:**
- Replace Conditional with Polymorphism ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md))

**Kerievsky (2004), p. 44, as Switch Statements, adds:**
- Replace Conditional Dispatcher with Command ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), to break a large switch into Command objects looked up by key
- Move Accumulation to Visitor ([move-accumulation-to-visitor.md](accumulation/move-accumulation-to-visitor.md)), when a switch exists only to read data from classes with different interfaces

## Loops (p. 79)
**Symptoms:** loops where a filter/map pipeline would show what is selected and what is done to it.
**Try:**
- Replace Loop with Pipeline ([replace-loop-with-pipeline.md](moving-features/replace-loop-with-pipeline.md))

## Lazy Element (p. 80)
**Symptoms:** a function, class or hierarchy level that no longer earns its structure (a name that restates its body, a class that is one trivial function).
**Try:**
- Inline Function ([inline-function.md](first-set/inline-function.md))
- Inline Class ([inline-class.md](encapsulation/inline-class.md))
- Collapse Hierarchy ([collapse-hierarchy.md](inheritance/collapse-hierarchy.md))

**Kerievsky (2004), p. 43, as Lazy Class, adds:**
- Inline Singleton ([inline-singleton.md](creation/inline-singleton.md)), for a Singleton that does not pay for the global access it adds

## Speculative Generality (p. 80)
**Symptoms:** hooks, abstractions and parameters added for needs that never came; sometimes only tests use them.
**Try:**
- Collapse Hierarchy ([collapse-hierarchy.md](inheritance/collapse-hierarchy.md)), for abstract classes doing little
- Inline Function ([inline-function.md](first-set/inline-function.md)) and Inline Class ([inline-class.md](encapsulation/inline-class.md)), for needless delegation
- Change Function Declaration ([change-function-declaration.md](first-set/change-function-declaration.md)), to drop unused parameters
- Remove Dead Code ([remove-dead-code.md](moving-features/remove-dead-code.md)), including code only tests call (delete those tests too)

## Temporary Field (p. 80)
**Symptoms:** a field set only in some circumstances, so readers wonder why it exists when it is empty.
**Try:**
- Extract Class ([extract-class.md](encapsulation/extract-class.md)), to give those fields a home
- Move Function ([move-function.md](moving-features/move-function.md)), to move the code that uses them into that class
- Introduce Special Case ([introduce-special-case.md](conditional-logic/introduce-special-case.md)), to replace the checks for "fields not valid" with an alternative class

## Message Chains (p. 81)
**Symptoms:** a client navigates object after object (`a.b().c().d()`), so it is coupled to the structure of the path.
**Try:**
- Hide Delegate ([hide-delegate.md](encapsulation/hide-delegate.md)), at one or more points in the chain
- Extract Function ([extract-function.md](first-set/extract-function.md)) on the code using the end of the chain, then Move Function ([move-function.md](moving-features/move-function.md)) down the chain; often better than hiding every link, which creates middle men
- Add a method on the intermediate object that does the whole navigation, when several clients want to walk the rest of the chain

## Middle Man (p. 81)
**Symptoms:** about half of a class's methods just forward to another class.
**Try:**
- Remove Middle Man ([remove-middle-man.md](encapsulation/remove-middle-man.md))
- Inline Function ([inline-function.md](first-set/inline-function.md)), if only a few methods merely delegate
- Replace Superclass with Delegate ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)) or Replace Subclass with Delegate ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)), when the middle man also has behavior of its own, to turn it into the real collaborator

## Insider Trading (p. 82)
**Symptoms:** modules that swap data too freely; subclasses that know too much about their parents.
**Try:**
- Move Function ([move-function.md](moving-features/move-function.md)) and Move Field ([move-field.md](moving-features/move-field.md)), to cut the chatter
- Hide Delegate ([hide-delegate.md](encapsulation/hide-delegate.md)), to use an intermediary
- Create a third module for shared interests
- Replace Subclass with Delegate ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)) or Replace Superclass with Delegate ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)), for inheritance collusion

## Large Class (p. 82)
**Symptoms:** too many fields (often with common prefixes or suffixes) or too much code; duplication grows inside. Clients using only a subset of the features hint at the split.
**Try:**
- Extract Class ([extract-class.md](encapsulation/extract-class.md)), to bundle related fields or a client-used subset; a class that does not use all its fields all the time can be split more than once
- Extract Superclass ([extract-superclass.md](inheritance/extract-superclass.md)), when the component makes sense as inheritance
- Replace Type Code with Subclasses ([replace-type-code-with-subclasses.md](inheritance/replace-type-code-with-subclasses.md)), which is in effect extracting a subclass

**Kerievsky (2004), p. 44, adds:**
- Replace Conditional Dispatcher with Command ([replace-conditional-dispatcher-with-command.md](simplification/replace-conditional-dispatcher-with-command.md)), when much of the class is dispatch logic
- Replace State-Altering Conditionals with State ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), when much of the class is state-transition logic
- Replace Implicit Language with Interpreter ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), when the class has a method for each combination of an implicit language

## Alternative Classes with Different Interfaces (p. 83)
**Symptoms:** two classes do the same job but cannot be swapped because their method names and signatures differ.
**Try:**
- Change Function Declaration ([change-function-declaration.md](first-set/change-function-declaration.md)), to make signatures match
- Move Function ([move-function.md](moving-features/move-function.md)), until the protocols match
- Extract Superclass ([extract-superclass.md](inheritance/extract-superclass.md)), if the alignment leaves duplication

**Kerievsky (2004), p. 43, adds:**
- Unify Interfaces with Adapter ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), when you cannot change one of the classes (third-party code)

## Data Class (p. 83)
**Symptoms:** a class with fields and accessors and nothing else, manipulated in detail by others (often with public fields). Exception: an immutable result record, such as the one between two phases after a Split Phase.
**Try:**
- Encapsulate Record ([encapsulate-record.md](encapsulation/encapsulate-record.md)), at once, for public fields
- Remove Setting Method ([remove-setting-method.md](refactoring-apis/remove-setting-method.md)), for fields that must not change
- Move Function ([move-function.md](moving-features/move-function.md)), to bring client behavior into the class
- Extract Function ([extract-function.md](first-set/extract-function.md)), to isolate a movable piece first

## Refused Bequest (p. 83)
**Symptoms:** a subclass uses little of what it inherits. Usually a faint smell; strong when the subclass refuses the parent's interface and not just its implementation.
**Try:**
- Push Down Method ([push-down-method.md](inheritance/push-down-method.md)) and Push Down Field ([push-down-field.md](inheritance/push-down-field.md)), moving unused members to a new sibling (the traditional advice; worth doing only when it causes real confusion)
- Replace Subclass with Delegate ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)) or Replace Superclass with Delegate ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)), when the interface is refused

## Comments (p. 84)
**Symptoms:** comments that exist because the code is unclear. Comments that explain why, or admit doubt, are fine.
**Try:**
- Extract Function ([extract-function.md](first-set/extract-function.md)), when a comment explains a block
- Change Function Declaration ([change-function-declaration.md](first-set/change-function-declaration.md)), to rename a function that still needs a comment
- Introduce Assertion ([introduce-assertion.md](conditional-logic/introduce-assertion.md)), to state a rule about required state

---

# Smells from Kerievsky (2004)

Ch. 4. Each one points mainly to a refactoring to a pattern.

## Conditional Complexity (p. 41)
**Symptoms:** conditional logic that started small and grew with each feature until it is hard to follow.
**Try:**
- Replace Conditional Logic with Strategy ([replace-conditional-logic-with-strategy.md](simplification/replace-conditional-logic-with-strategy.md)), when the conditionals pick one of several variants of a calculation
- Move Embellishment to Decorator ([move-embellishment-to-decorator.md](simplification/move-embellishment-to-decorator.md)), when they switch optional behavior on top of the class's core job
- Replace State-Altering Conditionals with State ([replace-state-altering-conditionals-with-state.md](simplification/replace-state-altering-conditionals-with-state.md)), when they decide how the object moves between states
- Introduce Null Object ([introduce-null-object.md](protection/introduce-null-object.md)), when the same null check and fallback is repeated across the code

## Indecent Exposure (p. 42)
**Symptoms:** classes or methods that clients do not need are public, so clients depend on details (a lack of information hiding).
**Try:**
- Encapsulate Classes with Factory ([encapsulate-classes-with-factory.md](creation/encapsulate-classes-with-factory.md)), when clients should reach a set of classes only through their common interface

## Solution Sprawl (p. 43)
**Symptoms:** the code and data for one responsibility are spread over many classes, usually after a feature was added in a hurry. It is the same problem as Shotgun Surgery, seen by reading the code instead of by changing it.
**Try:**
- Move Creation Knowledge to Factory ([move-creation-knowledge-to-factory.md](creation/move-creation-knowledge-to-factory.md)), when the sprawling responsibility is object creation
- The Shotgun Surgery refactorings above, for other responsibilities

## Combinatorial Explosion (p. 45)
**Symptoms:** many pieces of code do the same thing with different kinds or amounts of data, such as one query method per combination of criteria.
**Try:**
- Replace Implicit Language with Interpreter ([replace-implicit-language-with-interpreter.md](generalization/replace-implicit-language-with-interpreter.md)), to replace the methods with a small language that combines the criteria

## Oddball Solution (p. 45)
**Symptoms:** the same problem is solved one way in most of the system and another way somewhere else; usually hidden duplication.
**Try:**
- Substitute Algorithm ([substitute-algorithm.md](encapsulation/substitute-algorithm.md)), to make every place use the preferred solution, then move it to one place
- Unify Interfaces with Adapter ([unify-interfaces-with-adapter.md](generalization/unify-interfaces-with-adapter.md)), when the classes involved have different interfaces and so cannot be used the same way
