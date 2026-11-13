---
name: refactoring
description: Refactoring catalogs of Martin Fowler (Refactoring, 2nd ed.) and Joshua Kerievsky (Refactoring to Patterns): 29 code smells, 66 refactorings and 27 refactorings to patterns (Strategy, State, Command, Observer, Composite, Factory, Template Method...), each with mechanics, a C# example and verification. Use to refactor or clean up code without changing behavior, when code is hard to read or change, when conditionals or switches keep growing, or when a refactoring, code smell or design pattern is named.
---

# Refactoring catalogs: Fowler and Kerievsky

Fowler (2018), ch. 2-4 (smells and discipline) and ch. 6-12 (the catalog), plus five
refactorings that exist only in the book's web edition. Kerievsky (2004), ch. 4 (smells) and
ch. 6-11 (refactorings to patterns), which build on Fowler's refactorings.

Flow: **smell -> refactoring -> its file in `references/`.**

1. Name the smell. Use the quick index below, or the symptoms in
   [references/fowler/smells.md](references/fowler/smells.md) (Fowler, 24) and
   [references/kerievsky/smells.md](references/kerievsky/smells.md) (Kerievsky, 12).
2. Pick one refactoring for that smell and open its file from the tables further down. Start
   with the simplest one. Reach for a refactoring to a pattern only when the smell calls for
   it, and stop as soon as the smell is gone: going *towards* a pattern is often enough.
3. Before changing anything, check the safety net in
   [references/fowler/discipline.md](references/fowler/discipline.md): passing tests, small steps, a commit
   after each green refactoring. If the code has no tests, write them first. For a refactoring
   to a pattern, also read [references/kerievsky/discipline.md](references/kerievsky/discipline.md):
   when a pattern pays off, and when to stop.
4. Follow the mechanics one step at a time. Compile and run the tests after each step; if
   anything fails, undo the step.

If the request names a refactoring, skip to step 3 and open its file directly.

## Smell quick index

| Smell | Fowler | Kerievsky |
|---|---|---|
| Mysterious Name | [change-function-declaration](references/fowler/first-set/change-function-declaration.md), [rename-variable](references/fowler/first-set/rename-variable.md), [rename-field](references/fowler/organizing-data/rename-field.md) | — |
| Duplicated Code | [extract-function](references/fowler/first-set/extract-function.md), [pull-up-method](references/fowler/inheritance/pull-up-method.md) (same code in sibling subclasses) | [form-template-method](references/kerievsky/generalization/form-template-method.md), [chain-constructors](references/kerievsky/utilities/chain-constructors.md) |
| Long Function (Kerievsky: Long Method) | [extract-function](references/fowler/first-set/extract-function.md) | [compose-method](references/kerievsky/simplification/compose-method.md), [move-accumulation-to-collecting-parameter](references/kerievsky/accumulation/move-accumulation-to-collecting-parameter.md) |
| Long Parameter List | [introduce-parameter-object](references/fowler/first-set/introduce-parameter-object.md), [preserve-whole-object](references/fowler/refactoring-apis/preserve-whole-object.md) | — |
| Global Data | [encapsulate-variable](references/fowler/first-set/encapsulate-variable.md) | — |
| Mutable Data | [encapsulate-variable](references/fowler/first-set/encapsulate-variable.md), [split-variable](references/fowler/organizing-data/split-variable.md) | — |
| Divergent Change | [split-phase](references/fowler/first-set/split-phase.md), [extract-class](references/fowler/encapsulation/extract-class.md) | — |
| Shotgun Surgery | [move-function](references/fowler/moving-features/move-function.md), [move-field](references/fowler/moving-features/move-field.md) | — |
| Feature Envy | [move-function](references/fowler/moving-features/move-function.md) | — |
| Data Clumps | [extract-class](references/fowler/encapsulation/extract-class.md) | — |
| Primitive Obsession | [replace-primitive-with-object](references/fowler/encapsulation/replace-primitive-with-object.md) | [replace-type-code-with-class](references/kerievsky/protection/replace-type-code-with-class.md), [replace-state-altering-conditionals-with-state](references/kerievsky/simplification/replace-state-altering-conditionals-with-state.md) |
| Repeated Switches (Kerievsky: Switch Statements) | [replace-conditional-with-polymorphism](references/fowler/conditional-logic/replace-conditional-with-polymorphism.md) | [replace-conditional-dispatcher-with-command](references/kerievsky/simplification/replace-conditional-dispatcher-with-command.md), [move-accumulation-to-visitor](references/kerievsky/accumulation/move-accumulation-to-visitor.md) |
| Loops | [replace-loop-with-pipeline](references/fowler/moving-features/replace-loop-with-pipeline.md) | — |
| Lazy Element (Kerievsky: Lazy Class) | [inline-function](references/fowler/first-set/inline-function.md), [inline-class](references/fowler/encapsulation/inline-class.md) | [inline-singleton](references/kerievsky/creation/inline-singleton.md) |
| Speculative Generality | [collapse-hierarchy](references/fowler/inheritance/collapse-hierarchy.md), [remove-dead-code](references/fowler/moving-features/remove-dead-code.md) | — |
| Temporary Field | [extract-class](references/fowler/encapsulation/extract-class.md) | — |
| Message Chains | [hide-delegate](references/fowler/encapsulation/hide-delegate.md) | — |
| Middle Man | [remove-middle-man](references/fowler/encapsulation/remove-middle-man.md) | — |
| Insider Trading | [move-function](references/fowler/moving-features/move-function.md), [move-field](references/fowler/moving-features/move-field.md) | — |
| Large Class | [extract-class](references/fowler/encapsulation/extract-class.md) | [replace-conditional-dispatcher-with-command](references/kerievsky/simplification/replace-conditional-dispatcher-with-command.md), [replace-state-altering-conditionals-with-state](references/kerievsky/simplification/replace-state-altering-conditionals-with-state.md) |
| Alternative Classes with Different Interfaces | [change-function-declaration](references/fowler/first-set/change-function-declaration.md) | [unify-interfaces-with-adapter](references/kerievsky/generalization/unify-interfaces-with-adapter.md) |
| Data Class | [encapsulate-record](references/fowler/encapsulation/encapsulate-record.md), [move-function](references/fowler/moving-features/move-function.md) | — |
| Refused Bequest | [push-down-method](references/fowler/inheritance/push-down-method.md), [push-down-field](references/fowler/inheritance/push-down-field.md), [replace-subclass-with-delegate](references/fowler/inheritance/replace-subclass-with-delegate.md), [replace-superclass-with-delegate](references/fowler/inheritance/replace-superclass-with-delegate.md) | — |
| Comments | [extract-function](references/fowler/first-set/extract-function.md) | — |
| Conditional Complexity | — | [replace-conditional-logic-with-strategy](references/kerievsky/simplification/replace-conditional-logic-with-strategy.md), [replace-state-altering-conditionals-with-state](references/kerievsky/simplification/replace-state-altering-conditionals-with-state.md), [move-embellishment-to-decorator](references/kerievsky/simplification/move-embellishment-to-decorator.md), [introduce-null-object](references/kerievsky/protection/introduce-null-object.md) |
| Indecent Exposure | — | [encapsulate-classes-with-factory](references/kerievsky/creation/encapsulate-classes-with-factory.md) |
| Solution Sprawl | — | [move-creation-knowledge-to-factory](references/kerievsky/creation/move-creation-knowledge-to-factory.md) |
| Combinatorial Explosion | — | [replace-implicit-language-with-interpreter](references/kerievsky/generalization/replace-implicit-language-with-interpreter.md) |
| Oddball Solution | [substitute-algorithm](references/fowler/encapsulation/substitute-algorithm.md) | [unify-interfaces-with-adapter](references/kerievsky/generalization/unify-interfaces-with-adapter.md) |

The first 24 smells are Fowler's and the last five are Kerievsky's. Seven of Kerievsky's twelve
match a Fowler smell; where his name differs, it is in parentheses. Each book's `smells.md`
lists every option.

## Fowler: the refactorings

Each file has: When to use, Mechanics, Example (C#), C# notes where the catalog has one, and
Verification. A Kerievsky file also gives the target pattern and the
direction: *to* the pattern, *towards* it, or *away* from it. "(web)" marks a refactoring that exists only in the book's web edition, with no print
page.

### A first set (ch. 6)

| Refactoring | When | File |
|---|---|---|
| Extract Function | a fragment needs a comment to say what it does, or a function is too long | [extract-function.md](references/fowler/first-set/extract-function.md) |
| Inline Function | a function's body says as much as its name, or it only delegates | [inline-function.md](references/fowler/first-set/inline-function.md) |
| Extract Variable | an expression is long or hard to read | [extract-variable.md](references/fowler/first-set/extract-variable.md) |
| Inline Variable | a variable's name says no more than its expression | [inline-variable.md](references/fowler/first-set/inline-variable.md) |
| Change Function Declaration | rename a function, or add, remove or change a parameter | [change-function-declaration.md](references/fowler/first-set/change-function-declaration.md) |
| Encapsulate Variable | a field or global is read and written from many places | [encapsulate-variable.md](references/fowler/first-set/encapsulate-variable.md) |
| Rename Variable | a variable's name is cryptic, misleading or out of date | [rename-variable.md](references/fowler/first-set/rename-variable.md) |
| Introduce Parameter Object | the same group of values travels together through several signatures | [introduce-parameter-object.md](references/fowler/first-set/introduce-parameter-object.md) |
| Combine Functions into Class | several functions work on the same data | [combine-functions-into-class.md](references/fowler/first-set/combine-functions-into-class.md) |
| Combine Functions into Transform | the same derived values are computed in several places from read-only data | [combine-functions-into-transform.md](references/fowler/first-set/combine-functions-into-transform.md) |
| Split Phase | one piece of code does two things in sequence (parse then calculate, calculate then format) | [split-phase.md](references/fowler/first-set/split-phase.md) |

### Encapsulation (ch. 7)

| Refactoring | When | File |
|---|---|---|
| Encapsulate Record | loose data (dictionary, tuple) is read and written all over the program | [encapsulate-record.md](references/fowler/encapsulation/encapsulate-record.md) |
| Encapsulate Collection | callers can change a collection the owner should control | [encapsulate-collection.md](references/fowler/encapsulation/encapsulate-collection.md) |
| Replace Primitive with Object | a string or number carries meaning and rules of its own | [replace-primitive-with-object.md](references/fowler/encapsulation/replace-primitive-with-object.md) |
| Replace Temp with Query | a temp holds a calculation that blocks extraction or repeats elsewhere | [replace-temp-with-query.md](references/fowler/encapsulation/replace-temp-with-query.md) |
| Extract Class | a class does too much or changes for unrelated reasons | [extract-class.md](references/fowler/encapsulation/extract-class.md) |
| Inline Class | a class no longer does enough to justify itself | [inline-class.md](references/fowler/encapsulation/inline-class.md) |
| Hide Delegate | clients reach through one object to call another (`a.B.C()`) | [hide-delegate.md](references/fowler/encapsulation/hide-delegate.md) |
| Remove Middle Man | a class is mostly one-line methods that forward to another | [remove-middle-man.md](references/fowler/encapsulation/remove-middle-man.md) |
| Substitute Algorithm | a simpler way, or a library call, does the same job | [substitute-algorithm.md](references/fowler/encapsulation/substitute-algorithm.md) |

### Moving features (ch. 8)

| Refactoring | When | File |
|---|---|---|
| Move Function | a function uses another class's data more than its own | [move-function.md](references/fowler/moving-features/move-function.md) |
| Move Field | a field is always used or changed together with another object | [move-field.md](references/fowler/moving-features/move-field.md) |
| Move Statements into Function | the same lines run before or after every call to a function | [move-statements-into-function.md](references/fowler/moving-features/move-statements-into-function.md) |
| Move Statements to Callers | part of a function must start to vary between callers | [move-statements-to-callers.md](references/fowler/moving-features/move-statements-to-callers.md) |
| Replace Inline Code with Function Call | inline code repeats what an existing function already does | [replace-inline-code-with-function-call.md](references/fowler/moving-features/replace-inline-code-with-function-call.md) |
| Slide Statements | related statements are apart, or a declaration is far from its use | [slide-statements.md](references/fowler/moving-features/slide-statements.md) |
| Split Loop | one loop computes two or more unrelated things | [split-loop.md](references/fowler/moving-features/split-loop.md) |
| Replace Loop with Pipeline | a loop filters, maps or accumulates in a way a pipeline (LINQ) says more clearly | [replace-loop-with-pipeline.md](references/fowler/moving-features/replace-loop-with-pipeline.md) |
| Remove Dead Code | code is never called or a condition is always false | [remove-dead-code.md](references/fowler/moving-features/remove-dead-code.md) |

### Organizing data (ch. 9)

| Refactoring | When | File |
|---|---|---|
| Split Variable | a variable is assigned more than once for different purposes | [split-variable.md](references/fowler/organizing-data/split-variable.md) |
| Rename Field | a field's name is misleading or out of date | [rename-field.md](references/fowler/organizing-data/rename-field.md) |
| Replace Derived Variable with Query | a stored value can be computed from other data and may drift from it | [replace-derived-variable-with-query.md](references/fowler/organizing-data/replace-derived-variable-with-query.md) |
| Change Reference to Value | a small object is mutated in place but should be copied and compared by value | [change-reference-to-value.md](references/fowler/organizing-data/change-reference-to-value.md) |
| Change Value to Reference | copies of the same entity must all see one update | [change-value-to-reference.md](references/fowler/organizing-data/change-value-to-reference.md) |
| Replace Magic Literal (web) | a number or string appears inline and the reader must guess its meaning | [replace-magic-literal.md](references/fowler/organizing-data/replace-magic-literal.md) |

### Simplifying conditional logic (ch. 10)

| Refactoring | When | File |
|---|---|---|
| Decompose Conditional | a condition or its branches are long and need a comment | [decompose-conditional.md](references/fowler/conditional-logic/decompose-conditional.md) |
| Consolidate Conditional Expression | several checks lead to the same result | [consolidate-conditional-expression.md](references/fowler/conditional-logic/consolidate-conditional-expression.md) |
| Replace Nested Conditional with Guard Clauses | nested ifs hide the normal path among special cases | [replace-nested-conditional-with-guard-clauses.md](references/fowler/conditional-logic/replace-nested-conditional-with-guard-clauses.md) |
| Replace Conditional with Polymorphism | the same switch on a type appears in several places | [replace-conditional-with-polymorphism.md](references/fowler/conditional-logic/replace-conditional-with-polymorphism.md) |
| Introduce Special Case | many callers check for the same special value (often null) and react the same way | [introduce-special-case.md](references/fowler/conditional-logic/introduce-special-case.md) |
| Introduce Assertion | code only works if a condition holds, and nothing says so | [introduce-assertion.md](references/fowler/conditional-logic/introduce-assertion.md) |
| Replace Control Flag with Break (web) | a flag variable controls when a loop stops | [replace-control-flag-with-break.md](references/fowler/conditional-logic/replace-control-flag-with-break.md) |

### Refactoring APIs (ch. 11)

| Refactoring | When | File |
|---|---|---|
| Separate Query from Modifier | a function returns a value and also has side effects | [separate-query-from-modifier.md](references/fowler/refactoring-apis/separate-query-from-modifier.md) |
| Parameterize Function | several functions differ only in a literal value | [parameterize-function.md](references/fowler/refactoring-apis/parameterize-function.md) |
| Remove Flag Argument | a boolean or enum argument selects what the function does | [remove-flag-argument.md](references/fowler/refactoring-apis/remove-flag-argument.md) |
| Preserve Whole Object | callers unpack an object just to pass its fields | [preserve-whole-object.md](references/fowler/refactoring-apis/preserve-whole-object.md) |
| Replace Parameter with Query | the function can work out a parameter's value itself | [replace-parameter-with-query.md](references/fowler/refactoring-apis/replace-parameter-with-query.md) |
| Replace Query with Parameter | a function depends on global or changing state that callers should supply | [replace-query-with-parameter.md](references/fowler/refactoring-apis/replace-query-with-parameter.md) |
| Remove Setting Method | a field should not change after construction | [remove-setting-method.md](references/fowler/refactoring-apis/remove-setting-method.md) |
| Replace Constructor with Factory Function | a constructor's name or fixed return type gets in the way | [replace-constructor-with-factory-function.md](references/fowler/refactoring-apis/replace-constructor-with-factory-function.md) |
| Replace Function with Command | a function needs undo, staged setup, or is too tangled to split | [replace-function-with-command.md](references/fowler/refactoring-apis/replace-function-with-command.md) |
| Replace Command with Function | a command object does nothing a plain function could not | [replace-command-with-function.md](references/fowler/refactoring-apis/replace-command-with-function.md) |
| Return Modified Value (web) | a function changes outside data and returns nothing | [return-modified-value.md](references/fowler/refactoring-apis/return-modified-value.md) |
| Replace Error Code with Exception (web) | callers ignore or tangle with returned error codes | [replace-error-code-with-exception.md](references/fowler/refactoring-apis/replace-error-code-with-exception.md) |
| Replace Exception with Precheck (web) | an exception is used for a condition the caller could test first | [replace-exception-with-precheck.md](references/fowler/refactoring-apis/replace-exception-with-precheck.md) |

### Dealing with inheritance (ch. 12)

| Refactoring | When | File |
|---|---|---|
| Pull Up Method | sibling subclasses have the same method | [pull-up-method.md](references/fowler/inheritance/pull-up-method.md) |
| Pull Up Field | sibling subclasses hold the same field | [pull-up-field.md](references/fowler/inheritance/pull-up-field.md) |
| Pull Up Constructor Body | subclass constructors repeat the same setup | [pull-up-constructor-body.md](references/fowler/inheritance/pull-up-constructor-body.md) |
| Push Down Method | a superclass method matters to only some subclasses | [push-down-method.md](references/fowler/inheritance/push-down-method.md) |
| Push Down Field | a superclass field is used by only some subclasses | [push-down-field.md](references/fowler/inheritance/push-down-field.md) |
| Replace Type Code with Subclasses | behavior or data varies by a type code | [replace-type-code-with-subclasses.md](references/fowler/inheritance/replace-type-code-with-subclasses.md) |
| Remove Subclass | subclasses do too little to justify themselves | [remove-subclass.md](references/fowler/inheritance/remove-subclass.md) |
| Extract Superclass | two classes share data or behavior | [extract-superclass.md](references/fowler/inheritance/extract-superclass.md) |
| Collapse Hierarchy | a subclass is no longer different enough from its parent | [collapse-hierarchy.md](references/fowler/inheritance/collapse-hierarchy.md) |
| Replace Subclass with Delegate | inheritance is already used for another variation, or the variant must change at runtime | [replace-subclass-with-delegate.md](references/fowler/inheritance/replace-subclass-with-delegate.md) |
| Replace Superclass with Delegate | the subclass is not really a kind of its parent | [replace-superclass-with-delegate.md](references/fowler/inheritance/replace-superclass-with-delegate.md) |


## Kerievsky: the refactorings to patterns

Each one is a sequence of smaller refactorings, many of them Fowler's, that ends at a pattern,
moves towards it, or removes one. The Pattern column gives the direction.

### Creation (Kerievsky, ch. 6)

| Refactoring | Pattern | When | File |
|---|---|---|---|
| Replace Constructors with Creation Methods | Creation Method (to) | several constructors make it hard to know which one to call | [replace-constructors-with-creation-methods.md](references/kerievsky/creation/replace-constructors-with-creation-methods.md) |
| Move Creation Knowledge to Factory | Factory (to) | the data and code used to create an object are spread over many classes | [move-creation-knowledge-to-factory.md](references/kerievsky/creation/move-creation-knowledge-to-factory.md) |
| Encapsulate Classes with Factory | Factory (to) | clients instantiate classes of one package that share an interface and could be hidden | [encapsulate-classes-with-factory.md](references/kerievsky/creation/encapsulate-classes-with-factory.md) |
| Introduce Polymorphic Creation with Factory Method | Factory Method (to) | sibling classes repeat a method except for the object it creates | [introduce-polymorphic-creation-with-factory-method.md](references/kerievsky/creation/introduce-polymorphic-creation-with-factory-method.md) |
| Encapsulate Composite with Builder | Builder (to) | building a Composite is repetitive, complicated or error-prone | [encapsulate-composite-with-builder.md](references/kerievsky/creation/encapsulate-composite-with-builder.md) |
| Inline Singleton | Singleton (away) | code needs an object but not global access to it | [inline-singleton.md](references/kerievsky/creation/inline-singleton.md) |

### Simplification (Kerievsky, ch. 7)

| Refactoring | Pattern | When | File |
|---|---|---|---|
| Compose Method | Composed Method (to) | a method's logic is hard to follow at a glance | [compose-method.md](references/kerievsky/simplification/compose-method.md) |
| Replace Conditional Logic with Strategy | Strategy (to, towards) | conditionals choose which variant of a calculation runs | [replace-conditional-logic-with-strategy.md](references/kerievsky/simplification/replace-conditional-logic-with-strategy.md) |
| Move Embellishment to Decorator | Decorator (to, towards) | code adds optional behavior on top of a class's core job | [move-embellishment-to-decorator.md](references/kerievsky/simplification/move-embellishment-to-decorator.md) |
| Replace State-Altering Conditionals with State | State (to, towards) | conditionals that control an object's state transitions are complex | [replace-state-altering-conditionals-with-state.md](references/kerievsky/simplification/replace-state-altering-conditionals-with-state.md) |
| Replace Implicit Tree with Composite | Composite (to) | a tree is built implicitly with strings or other primitives | [replace-implicit-tree-with-composite.md](references/kerievsky/simplification/replace-implicit-tree-with-composite.md) |
| Replace Conditional Dispatcher with Command | Command (to, towards) | conditionals dispatch requests and run their actions | [replace-conditional-dispatcher-with-command.md](references/kerievsky/simplification/replace-conditional-dispatcher-with-command.md) |

### Generalization (Kerievsky, ch. 8)

| Refactoring | Pattern | When | File |
|---|---|---|---|
| Form Template Method | Template Method (to) | two subclasses do similar steps in the same order | [form-template-method.md](references/kerievsky/generalization/form-template-method.md) |
| Extract Composite | Composite (to) | subclasses of a hierarchy implement the same Composite | [extract-composite.md](references/kerievsky/generalization/extract-composite.md) |
| Replace One/Many Distinctions with Composite | Composite (to) | one piece of code handles a single object and another handles a collection | [replace-one-many-distinctions-with-composite.md](references/kerievsky/generalization/replace-one-many-distinctions-with-composite.md) |
| Replace Hard-Coded Notifications with Observer | Observer (to, towards) | classes notify specific receivers in hard-coded calls | [replace-hard-coded-notifications-with-observer.md](references/kerievsky/generalization/replace-hard-coded-notifications-with-observer.md) |
| Unify Interfaces with Adapter | Adapter (to, towards) | clients use two classes the same way but their interfaces differ | [unify-interfaces-with-adapter.md](references/kerievsky/generalization/unify-interfaces-with-adapter.md) |
| Extract Adapter | Adapter (to) | one class adapts several versions of a component, library or API | [extract-adapter.md](references/kerievsky/generalization/extract-adapter.md) |
| Replace Implicit Language with Interpreter | Interpreter (to) | many methods or combinations of them express the elements of an implicit language | [replace-implicit-language-with-interpreter.md](references/kerievsky/generalization/replace-implicit-language-with-interpreter.md) |

### Protection (Kerievsky, ch. 9)

| Refactoring | Pattern | When | File |
|---|---|---|---|
| Replace Type Code with Class | — | a field's type (a string or int) does not protect it from invalid values | [replace-type-code-with-class.md](references/kerievsky/protection/replace-type-code-with-class.md) |
| Limit Instantiation with Singleton | Singleton (to) | code creates many instances of an object when one is enough and that costs memory or time | [limit-instantiation-with-singleton.md](references/kerievsky/protection/limit-instantiation-with-singleton.md) |
| Introduce Null Object | Null Object (to) | the same check for a null field or variable is repeated across the code | [introduce-null-object.md](references/kerievsky/protection/introduce-null-object.md) |

### Accumulation (Kerievsky, ch. 10)

| Refactoring | Pattern | When | File |
|---|---|---|---|
| Move Accumulation to Collecting Parameter | Collecting Parameter (to) | one large method gathers information into a local variable | [move-accumulation-to-collecting-parameter.md](references/kerievsky/accumulation/move-accumulation-to-collecting-parameter.md) |
| Move Accumulation to Visitor | Visitor (to, towards) | one method gathers information from classes with different interfaces | [move-accumulation-to-visitor.md](references/kerievsky/accumulation/move-accumulation-to-visitor.md) |

### Utilities (Kerievsky, ch. 11)

| Refactoring | Pattern | When | File |
|---|---|---|---|
| Chain Constructors | — | several constructors repeat the same code | [chain-constructors.md](references/kerievsky/utilities/chain-constructors.md) |
| Unify Interfaces | — | a superclass or interface needs the same interface as a subclass | [unify-interfaces.md](references/kerievsky/utilities/unify-interfaces.md) |
| Extract Parameter | — | a method or constructor assigns a field to a locally created value | [extract-parameter.md](references/kerievsky/utilities/extract-parameter.md) |

Sources: Martin Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed.,
Addison-Wesley (Pearson Education), 2018, and the online catalog at
https://refactoring.com/catalog/; Joshua Kerievsky, *Refactoring to Patterns*, Addison-Wesley
(Pearson Education), 2004, and the online catalog at
https://www.industriallogic.com/refactoring-to-patterns/catalog/. Paraphrased; see the package NOTICE.
