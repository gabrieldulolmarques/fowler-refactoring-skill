---
name: fowler-refactoring
description: Martin Fowler's refactoring catalog (Refactoring, 2nd ed.): the 24 code smells and the 66 refactorings that fix them, each with step-by-step mechanics, a C# example and verification. Use when code is hard to read or change (long functions, large classes, duplicated code, long parameter lists, repeated switches, feature envy, message chains, mutable or global data, unclear names), when asked to refactor or clean up code without changing behavior, or when asked for a named refactoring such as Extract Function, Inline Variable, Move Function, Extract Class, Replace Conditional with Polymorphism, Introduce Parameter Object or Replace Temp with Query.
---

# Fowler's refactoring catalog

Fowler (2018), ch. 2-4 (smells and discipline) and ch. 6-12 (the catalog), plus five
refactorings that exist only in the book's web edition.

Flow: **smell -> refactoring -> its file in `references/`.**

1. Name the smell. Use the quick index below, or the symptoms in
   [references/smells.md](references/smells.md) for the full list of 24.
2. Pick one refactoring for that smell and open its file from the table further down.
3. Before changing anything, check the safety net in
   [references/discipline.md](references/discipline.md): passing tests, small steps, a commit
   after each green refactoring. If the code has no tests, write them first.
4. Follow the mechanics one step at a time. Compile and run the tests after each step; if
   anything fails, undo the step.

If the request names a refactoring, skip to step 3 and open its file directly.

## Smell quick index

| Smell | First thing to try |
|---|---|
| Mysterious Name | [change-function-declaration](references/first-set/change-function-declaration.md), [rename-variable](references/first-set/rename-variable.md), [rename-field](references/organizing-data/rename-field.md) |
| Duplicated Code | [extract-function](references/first-set/extract-function.md), [pull-up-method](references/inheritance/pull-up-method.md) (same code in sibling subclasses) |
| Long Function | [extract-function](references/first-set/extract-function.md) |
| Long Parameter List | [introduce-parameter-object](references/first-set/introduce-parameter-object.md), [preserve-whole-object](references/refactoring-apis/preserve-whole-object.md) |
| Global Data | [encapsulate-variable](references/first-set/encapsulate-variable.md) |
| Mutable Data | [encapsulate-variable](references/first-set/encapsulate-variable.md), [split-variable](references/organizing-data/split-variable.md) |
| Divergent Change | [split-phase](references/first-set/split-phase.md), [extract-class](references/encapsulation/extract-class.md) |
| Shotgun Surgery | [move-function](references/moving-features/move-function.md), [move-field](references/moving-features/move-field.md) |
| Feature Envy | [move-function](references/moving-features/move-function.md) |
| Data Clumps | [extract-class](references/encapsulation/extract-class.md) |
| Primitive Obsession | [replace-primitive-with-object](references/encapsulation/replace-primitive-with-object.md) |
| Repeated Switches | [replace-conditional-with-polymorphism](references/conditional-logic/replace-conditional-with-polymorphism.md) |
| Loops | [replace-loop-with-pipeline](references/moving-features/replace-loop-with-pipeline.md) |
| Lazy Element | [inline-function](references/first-set/inline-function.md), [inline-class](references/encapsulation/inline-class.md) |
| Speculative Generality | [collapse-hierarchy](references/inheritance/collapse-hierarchy.md), [remove-dead-code](references/moving-features/remove-dead-code.md) |
| Temporary Field | [extract-class](references/encapsulation/extract-class.md) |
| Message Chains | [hide-delegate](references/encapsulation/hide-delegate.md) |
| Middle Man | [remove-middle-man](references/encapsulation/remove-middle-man.md) |
| Insider Trading | [move-function](references/moving-features/move-function.md), [move-field](references/moving-features/move-field.md) |
| Large Class | [extract-class](references/encapsulation/extract-class.md) |
| Alternative Classes with Different Interfaces | [change-function-declaration](references/first-set/change-function-declaration.md) |
| Data Class | [encapsulate-record](references/encapsulation/encapsulate-record.md), [move-function](references/moving-features/move-function.md) |
| Refused Bequest | [push-down-method](references/inheritance/push-down-method.md), [push-down-field](references/inheritance/push-down-field.md), [replace-subclass-with-delegate](references/inheritance/replace-subclass-with-delegate.md), [replace-superclass-with-delegate](references/inheritance/replace-superclass-with-delegate.md) |
| Comments | [extract-function](references/first-set/extract-function.md) |

## The refactorings

Each file has: When to use, Mechanics, Example (C#), C# notes where the catalog has one, and
Verification. "(web)" marks a refactoring that exists only in the book's web edition, with no print
page.

### A first set (ch. 6)

| Refactoring | When | File |
|---|---|---|
| Extract Function | a fragment needs a comment to say what it does, or a function is too long | [extract-function.md](references/first-set/extract-function.md) |
| Inline Function | a function's body says as much as its name, or it only delegates | [inline-function.md](references/first-set/inline-function.md) |
| Extract Variable | an expression is long or hard to read | [extract-variable.md](references/first-set/extract-variable.md) |
| Inline Variable | a variable's name says no more than its expression | [inline-variable.md](references/first-set/inline-variable.md) |
| Change Function Declaration | rename a function, or add, remove or change a parameter | [change-function-declaration.md](references/first-set/change-function-declaration.md) |
| Encapsulate Variable | a field or global is read and written from many places | [encapsulate-variable.md](references/first-set/encapsulate-variable.md) |
| Rename Variable | a variable's name is cryptic, misleading or out of date | [rename-variable.md](references/first-set/rename-variable.md) |
| Introduce Parameter Object | the same group of values travels together through several signatures | [introduce-parameter-object.md](references/first-set/introduce-parameter-object.md) |
| Combine Functions into Class | several functions work on the same data | [combine-functions-into-class.md](references/first-set/combine-functions-into-class.md) |
| Combine Functions into Transform | the same derived values are computed in several places from read-only data | [combine-functions-into-transform.md](references/first-set/combine-functions-into-transform.md) |
| Split Phase | one piece of code does two things in sequence (parse then calculate, calculate then format) | [split-phase.md](references/first-set/split-phase.md) |

### Encapsulation (ch. 7)

| Refactoring | When | File |
|---|---|---|
| Encapsulate Record | loose data (dictionary, tuple) is read and written all over the program | [encapsulate-record.md](references/encapsulation/encapsulate-record.md) |
| Encapsulate Collection | callers can change a collection the owner should control | [encapsulate-collection.md](references/encapsulation/encapsulate-collection.md) |
| Replace Primitive with Object | a string or number carries meaning and rules of its own | [replace-primitive-with-object.md](references/encapsulation/replace-primitive-with-object.md) |
| Replace Temp with Query | a temp holds a calculation that blocks extraction or repeats elsewhere | [replace-temp-with-query.md](references/encapsulation/replace-temp-with-query.md) |
| Extract Class | a class does too much or changes for unrelated reasons | [extract-class.md](references/encapsulation/extract-class.md) |
| Inline Class | a class no longer does enough to justify itself | [inline-class.md](references/encapsulation/inline-class.md) |
| Hide Delegate | clients reach through one object to call another (`a.B.C()`) | [hide-delegate.md](references/encapsulation/hide-delegate.md) |
| Remove Middle Man | a class is mostly one-line methods that forward to another | [remove-middle-man.md](references/encapsulation/remove-middle-man.md) |
| Substitute Algorithm | a simpler way, or a library call, does the same job | [substitute-algorithm.md](references/encapsulation/substitute-algorithm.md) |

### Moving features (ch. 8)

| Refactoring | When | File |
|---|---|---|
| Move Function | a function uses another class's data more than its own | [move-function.md](references/moving-features/move-function.md) |
| Move Field | a field is always used or changed together with another object | [move-field.md](references/moving-features/move-field.md) |
| Move Statements into Function | the same lines run before or after every call to a function | [move-statements-into-function.md](references/moving-features/move-statements-into-function.md) |
| Move Statements to Callers | part of a function must start to vary between callers | [move-statements-to-callers.md](references/moving-features/move-statements-to-callers.md) |
| Replace Inline Code with Function Call | inline code repeats what an existing function already does | [replace-inline-code-with-function-call.md](references/moving-features/replace-inline-code-with-function-call.md) |
| Slide Statements | related statements are apart, or a declaration is far from its use | [slide-statements.md](references/moving-features/slide-statements.md) |
| Split Loop | one loop computes two or more unrelated things | [split-loop.md](references/moving-features/split-loop.md) |
| Replace Loop with Pipeline | a loop filters, maps or accumulates in a way a pipeline (LINQ) says more clearly | [replace-loop-with-pipeline.md](references/moving-features/replace-loop-with-pipeline.md) |
| Remove Dead Code | code is never called or a condition is always false | [remove-dead-code.md](references/moving-features/remove-dead-code.md) |

### Organizing data (ch. 9)

| Refactoring | When | File |
|---|---|---|
| Split Variable | a variable is assigned more than once for different purposes | [split-variable.md](references/organizing-data/split-variable.md) |
| Rename Field | a field's name is misleading or out of date | [rename-field.md](references/organizing-data/rename-field.md) |
| Replace Derived Variable with Query | a stored value can be computed from other data and may drift from it | [replace-derived-variable-with-query.md](references/organizing-data/replace-derived-variable-with-query.md) |
| Change Reference to Value | a small object is mutated in place but should be copied and compared by value | [change-reference-to-value.md](references/organizing-data/change-reference-to-value.md) |
| Change Value to Reference | copies of the same entity must all see one update | [change-value-to-reference.md](references/organizing-data/change-value-to-reference.md) |
| Replace Magic Literal (web) | a number or string appears inline and the reader must guess its meaning | [replace-magic-literal.md](references/organizing-data/replace-magic-literal.md) |

### Simplifying conditional logic (ch. 10)

| Refactoring | When | File |
|---|---|---|
| Decompose Conditional | a condition or its branches are long and need a comment | [decompose-conditional.md](references/conditional-logic/decompose-conditional.md) |
| Consolidate Conditional Expression | several checks lead to the same result | [consolidate-conditional-expression.md](references/conditional-logic/consolidate-conditional-expression.md) |
| Replace Nested Conditional with Guard Clauses | nested ifs hide the normal path among special cases | [replace-nested-conditional-with-guard-clauses.md](references/conditional-logic/replace-nested-conditional-with-guard-clauses.md) |
| Replace Conditional with Polymorphism | the same switch on a type appears in several places | [replace-conditional-with-polymorphism.md](references/conditional-logic/replace-conditional-with-polymorphism.md) |
| Introduce Special Case | many callers check for the same special value (often null) and react the same way | [introduce-special-case.md](references/conditional-logic/introduce-special-case.md) |
| Introduce Assertion | code only works if a condition holds, and nothing says so | [introduce-assertion.md](references/conditional-logic/introduce-assertion.md) |
| Replace Control Flag with Break (web) | a flag variable controls when a loop stops | [replace-control-flag-with-break.md](references/conditional-logic/replace-control-flag-with-break.md) |

### Refactoring APIs (ch. 11)

| Refactoring | When | File |
|---|---|---|
| Separate Query from Modifier | a function returns a value and also has side effects | [separate-query-from-modifier.md](references/refactoring-apis/separate-query-from-modifier.md) |
| Parameterize Function | several functions differ only in a literal value | [parameterize-function.md](references/refactoring-apis/parameterize-function.md) |
| Remove Flag Argument | a boolean or enum argument selects what the function does | [remove-flag-argument.md](references/refactoring-apis/remove-flag-argument.md) |
| Preserve Whole Object | callers unpack an object just to pass its fields | [preserve-whole-object.md](references/refactoring-apis/preserve-whole-object.md) |
| Replace Parameter with Query | the function can work out a parameter's value itself | [replace-parameter-with-query.md](references/refactoring-apis/replace-parameter-with-query.md) |
| Replace Query with Parameter | a function depends on global or changing state that callers should supply | [replace-query-with-parameter.md](references/refactoring-apis/replace-query-with-parameter.md) |
| Remove Setting Method | a field should not change after construction | [remove-setting-method.md](references/refactoring-apis/remove-setting-method.md) |
| Replace Constructor with Factory Function | a constructor's name or fixed return type gets in the way | [replace-constructor-with-factory-function.md](references/refactoring-apis/replace-constructor-with-factory-function.md) |
| Replace Function with Command | a function needs undo, staged setup, or is too tangled to split | [replace-function-with-command.md](references/refactoring-apis/replace-function-with-command.md) |
| Replace Command with Function | a command object does nothing a plain function could not | [replace-command-with-function.md](references/refactoring-apis/replace-command-with-function.md) |
| Return Modified Value (web) | a function changes outside data and returns nothing | [return-modified-value.md](references/refactoring-apis/return-modified-value.md) |
| Replace Error Code with Exception (web) | callers ignore or tangle with returned error codes | [replace-error-code-with-exception.md](references/refactoring-apis/replace-error-code-with-exception.md) |
| Replace Exception with Precheck (web) | an exception is used for a condition the caller could test first | [replace-exception-with-precheck.md](references/refactoring-apis/replace-exception-with-precheck.md) |

### Dealing with inheritance (ch. 12)

| Refactoring | When | File |
|---|---|---|
| Pull Up Method | sibling subclasses have the same method | [pull-up-method.md](references/inheritance/pull-up-method.md) |
| Pull Up Field | sibling subclasses hold the same field | [pull-up-field.md](references/inheritance/pull-up-field.md) |
| Pull Up Constructor Body | subclass constructors repeat the same setup | [pull-up-constructor-body.md](references/inheritance/pull-up-constructor-body.md) |
| Push Down Method | a superclass method matters to only some subclasses | [push-down-method.md](references/inheritance/push-down-method.md) |
| Push Down Field | a superclass field is used by only some subclasses | [push-down-field.md](references/inheritance/push-down-field.md) |
| Replace Type Code with Subclasses | behavior or data varies by a type code | [replace-type-code-with-subclasses.md](references/inheritance/replace-type-code-with-subclasses.md) |
| Remove Subclass | subclasses do too little to justify themselves | [remove-subclass.md](references/inheritance/remove-subclass.md) |
| Extract Superclass | two classes share data or behavior | [extract-superclass.md](references/inheritance/extract-superclass.md) |
| Collapse Hierarchy | a subclass is no longer different enough from its parent | [collapse-hierarchy.md](references/inheritance/collapse-hierarchy.md) |
| Replace Subclass with Delegate | inheritance is already used for another variation, or the variant must change at runtime | [replace-subclass-with-delegate.md](references/inheritance/replace-subclass-with-delegate.md) |
| Replace Superclass with Delegate | the subclass is not really a kind of its parent | [replace-superclass-with-delegate.md](references/inheritance/replace-superclass-with-delegate.md) |

Source: Martin Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed.,
Addison-Wesley (Pearson Education), 2018, and the online catalog at
https://refactoring.com/catalog/. Paraphrased; see the package NOTICE.
