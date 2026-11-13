# Replace Type Code with Class

Kerievsky (2004), ch. 9, p. 286. Pattern: —. Direction: —.

## When to use
Smells: Primitive Obsession.

- A field holds a string or an int that is assigned from, and compared with, a fixed family of constants (order status, permission state). Nothing stops a misspelled string or a stray number from being assigned, and the object can end up in a state it can never leave.
- Giving the field a class as its type means every assignment and every comparison goes through a closed set of constants that cannot be impersonated by other values.
- A language enum does not make this obsolete. The class can later grow behavior, and that is what the next steps often need. The book's own example is the first step of [replace-state-altering-conditionals-with-state.md](../simplification/replace-state-altering-conditionals-with-state.md), which builds on this class and could not build on a plain enum.
- Cost: more code than a primitive.
- Relation to Fowler: this is [replace-primitive-with-object.md](../../fowler/encapsulation/replace-primitive-with-object.md) applied to a type code. Fowler's version wraps any primitive; Kerievsky's is specifically about a closed family of constants.

## Mechanics
Follow [replace-primitive-with-object.md](../../fowler/encapsulation/replace-primitive-with-object.md). What Kerievsky adds or orders differently:

1. Encapsulate the type-unsafe field first with Encapsulate Variable ([encapsulate-variable.md](../../fowler/first-set/encapsulate-variable.md)). Compile and test.
2. Create the new class, named after the kind of value it holds, with no public constructor yet.
3. For each constant the field is assigned or compared with, add a static instance of the new class. Compile. If the family must stay closed, make the constructor private and the class sealed.
4. Add a type-safe field of the new class next to the old field, and mirror every assignment to the old field with an assignment to the new one. Compile.
5. Make the new class able to produce the old value (a name or code), and make the old getter read from the new field. Compile and test.
6. Delete the old field, its setter and its assignments. Compile and test.
7. Replace every use of the old constants with the new ones, change the getter's return type to the new class, and fix the callers. Compare with `==` on the shared instances, or give the class equality if it can be created from outside. Compile and test.
8. Delete the old constants.

The example is in the Fowler file; the shape of the result is the sealed class with static instances shown there, for instance a sealed `FlagEnvironment` with `Development`, `Staging` and `Production`.

## C# notes
- A C# `enum` is only an integer underneath: `(FlagEnvironment)42` compiles and runs. If the set must be closed and the type must carry behavior, use a sealed class with a private constructor. If neither matters, an enum is fine and this refactoring is not needed.
- With a private constructor the instances are unique, so `==` on references is enough. Without it, override `Equals` and `GetHashCode` (or use a record, C# 9+; on Unity it needs an `IsExternalInit` shim).
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No `string` or `int` constant for the family remains, and no public way to create a value outside the family if the family is meant to be closed.
