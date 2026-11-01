# Push Down Field

Fowler (2018), ch. 12, p. 361. Formerly / aka: —. Inverse: Pull Up Field ([pull-up-field.md](pull-up-field.md)).

## When to use
Smell: Refused Bequest. A field sits in a superclass but only one subclass, or a small share of them, uses it. The other subclasses carry state they never touch, and a reader of the base class is misled about what every instance has.

Not worth it when most subclasses use the field, or when code that works through the base type reads it. In that case the field belongs in the base class (see [pull-up-field.md](pull-up-field.md)).

## Mechanics
1. Confirm which subclasses use the field.
2. Search every usage of the field, and check that no code reaches it through the superclass type. Include reflection and serialization that may name it: a field persisted or serialized under its name must keep that name in the subclass, or the mapping must be updated.
3. Declare the field in every subclass that needs it.
4. Remove the field from the superclass.
5. Compile and run the tests. Any error shows code that still reads the field through the base type: deal with it before going on.
6. Remove the field from any subclass that declared it but does not use it.
7. Compile and run the tests.

## Example
Before: `Radius` is declared in the base class, but only `Circle` uses it.

```csharp
public abstract class Shape
{
    public string Label { get; init; } = "";
    protected double Radius;
}

public class Square : Shape { }

public class Circle : Shape
{
    public double Area() => Math.PI * Radius * Radius;
    public void SetRadius(double value) => Radius = value;
}
```

After: the field lives only where it is used.

```csharp
public abstract class Shape
{
    public string Label { get; init; } = "";
}

public class Square : Shape { }

public class Circle : Shape
{
    private double _radius;
    public double Area() => Math.PI * _radius * _radius;
    public void SetRadius(double value) => _radius = value;
}
```

Behavior is the same.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
