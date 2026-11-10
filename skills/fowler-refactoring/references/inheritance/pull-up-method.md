# Pull Up Method

Fowler (2018), ch. 12, p. 350. Formerly / aka: —. Inverse: Push Down Method
([push-down-method.md](push-down-method.md)).

## When to use
Smell: Duplicated Code. Two or more subclasses hold methods that do the same thing. Each copy
is a place where a future change can be applied to one sibling and forgotten in another, and
the copies are hard to find later.

- The easy case is a byte-for-byte copy. When the bodies only look alike, compare them line by
  line before moving: the differences often reveal behavior no test covers.
- If the methods differ only by a value or a small detail, first apply Parameterize Function
  ([parameterize-function.md](../refactoring-apis/parameterize-function.md)) in each subclass so the bodies become identical, then pull up.
- If the body uses members that exist only in the subclasses, pull those members up first
  ([pull-up-field.md](pull-up-field.md), or this refactoring again for helper methods).
- If the methods share an overall flow but differ in some steps, the right tool is a template
  method in the superclass, with the varying steps left as overridable members.

Do not use it when the behavior is genuinely different per subclass, or when the superclass
should not know the concept (the method would then be a Refused Bequest for other siblings).

## Mechanics
1. Put the candidate methods side by side. If they achieve the same result but their bodies
   differ, edit them step by step until the bodies are identical.
2. Check that every member the body uses is visible from the superclass. If one is not, move
   it up first, or declare it on the superclass as abstract.
3. If names or signatures differ between the copies, apply Change Function Declaration
   ([change-function-declaration.md](../first-set/change-function-declaration.md)) until all copies match
   the signature wanted on the superclass. Compile and test.
4. Add the method to the superclass, with the body taken from one of the subclass copies.
5. Compile, to catch anything the superclass cannot resolve.
6. Remove one subclass copy and run the tests.
7. Remove the other copies the same way, one at a time, running the tests after each.

## Example
Two subclasses build the same heading text under different names.

Before:

```csharp
public abstract class Document
{
    public string Customer { get; init; } = "";
}

public class Invoice : Document
{
    public string Number { get; init; } = "";

    public string Heading() => $"{Number} for {Customer}";
}

public class CreditNote : Document
{
    public string Number { get; init; } = "";

    public string Caption() => $"{Number} for {Customer}";
}
```

Steps 2 and 3: both bodies are equal and use `Number`, which the superclass lacks. Declare it
there as abstract, keeping the `init` usage in the subclasses, and rename `Caption` to
`Heading`.

```csharp
public abstract class Document
{
    public string Customer { get; init; } = "";
    public abstract string Number { get; init; }
}

public class Invoice : Document
{
    public override string Number { get; init; } = "";

    public string Heading() => $"{Number} for {Customer}";
}

public class CreditNote : Document
{
    public override string Number { get; init; } = "";

    public string Heading() => $"{Number} for {Customer}";
}
```

Steps 4 to 7: add the method to the superclass, then delete the copies one by one, testing
each time.

After:

```csharp
public abstract class Document
{
    public string Customer { get; init; } = "";
    public abstract string Number { get; init; }

    public string Heading() => $"{Number} for {Customer}";
}

public class Invoice : Document
{
    public override string Number { get; init; } = "";
}

public class CreditNote : Document
{
    public override string Number { get; init; } = "";
}
```

Callers such as `new Invoice { Number = "A-1", Customer = "Acme" }` compile unchanged.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No subclass still defines a copy of the pulled-up method (unless it deliberately overrides it).
- Every subclass of the superclass, including ones outside the original pair, still behaves
  correctly with the inherited method.
