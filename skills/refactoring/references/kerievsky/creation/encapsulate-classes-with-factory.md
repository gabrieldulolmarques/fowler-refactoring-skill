# Encapsulate Classes with Factory

Kerievsky (2004), ch. 6, p. 80. Direction: to. Pattern: Factory (not in GoF).

## When to use
Smells: Indecent Exposure.

- Several classes live in one package or assembly, share one interface or base class, and clients do not need to know the concrete classes exist. Today clients call their constructors directly.
- Hiding them lets you apply "program to an interface" strictly: clients can only see the shared type. It also cuts the number of public classes a newcomer has to learn, and it gathers the available kinds of instance in one set of well-named Creation Methods.
- It reduces mistakes. In the book's case, programmers sometimes chose the wrong subclass, or the right one with the wrong argument types. One place with named methods removed that.
- Cost: every new subclass, and every change to a subclass constructor, needs a new or changed Creation Method on the factory. If subclasses are added often, skip it or encapsulate only the common ones and leave the rest public.
- If you ship compiled code that clients cannot modify, they also cannot add their own kinds of instance. Weigh that.
- The factory may end up being both a factory and a base class with behavior. If that blurs the class's purpose, split the factory out (Extract Factory in [replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md)).
- Related: [replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md) starts with one class and its own constructors. This one makes a whole family of subclasses private behind their base type.

## Mechanics
Use it when the classes share a public interface or superclass and live in the same package or assembly.
1. Find a client that calls a subclass constructor to get one kind of instance. Apply Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) on the call to get a public static method, then Move Function ([move-function.md](../../fowler/moving-features/move-function.md)) to the superclass (or the interface's companion class). Compile and test.
2. Change all other callers of that constructor that want the same kind of instance to use the Creation Method. Compile and test.
3. Repeat steps 1 and 2 for the other kinds of instance the constructor can produce.
4. Make the subclass constructor non-public (`internal` or `private`). Compile.
5. Repeat for each subclass you want to hide.

## Example
Before: the three shipping classes are public, and callers pick one with `new`.

```csharp
public abstract class Shipping { public abstract decimal Cost(decimal kg); }
public class GroundShipping : Shipping { public override decimal Cost(decimal kg) => 2m * kg; }
public class AirShipping : Shipping { public override decimal Cost(decimal kg) => 9m * kg; }
public class PickupShipping : Shipping { public override decimal Cost(decimal kg) => 0m; }

Shipping s = new AirShipping();
```

After: the subclasses are private nested classes of `Shipping`, which now serves as the factory. Callers see only the base type.

```csharp
public abstract class Shipping
{
    public static Shipping Ground() => new GroundShipping();
    public static Shipping Air() => new AirShipping();
    public static Shipping Pickup() => new PickupShipping();

    public abstract decimal Cost(decimal kg);

    private sealed class GroundShipping : Shipping { public override decimal Cost(decimal kg) => 2m * kg; }
    private sealed class AirShipping : Shipping { public override decimal Cost(decimal kg) => 9m * kg; }
    private sealed class PickupShipping : Shipping { public override decimal Cost(decimal kg) => 0m; }
}

Shipping s = Shipping.Air();
```

The same shape appears in the standard library's wrappers that make a collection read-only: the proxy classes are hidden, and static methods return them as the common interface type. The book calls this the inner-class variation.

## C# notes
- Nested `private` classes are the strictest form. When the subclasses are in separate files, make them `internal` with `internal` constructors, and put the Creation Methods on a public class in the same assembly.
- Mark hidden classes `sealed` if they are not meant to be extended.
- Tests that need a concrete type can use `InternalsVisibleTo`, or test through the factory.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No code outside the assembly (or outside the base class, for nested types) refers to the concrete classes.
- Each Creation Method returns the shared type, not the concrete one.
