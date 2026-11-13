# Change Reference to Value

Fowler (2018), ch. 9, p. 252. Formerly / aka: —. Inverse: Change Value to Reference
([change-value-to-reference.md](change-value-to-reference.md)).

## When to use
Smell: Mutable Data. An object nested inside another is changed by assigning to its
properties, so the same instance is updated in place. If the inner object has no identity of
its own (two with the same contents are interchangeable), treat it as a value instead:
immutable, replaced as a whole when something changes, and equal when its fields are equal.
Immutable values are safe to share and to read from several threads, since nobody can mutate
them.

Do not apply it when several owners must share one object and see each other's changes. That
object is a real reference, and the right move may be the inverse refactoring.

## Mechanics
1. Check that the class is immutable or can become so: no outside code needs to mutate the
   same instance and observe the change elsewhere.
2. Remove the mutability one setter at a time, using
   [remove-setting-method.md](../refactoring-apis/remove-setting-method.md). First move the fields into the
   constructor, then rewrite each caller of a setter so it builds a new instance and assigns
   it to the owner's field. Test after each setter.
3. Add value-based equality over all the fields, and the matching hash code. Write tests that
   compare two independently built instances with the same contents, instances that differ in
   each field, `null`, and an object of another type.
4. Check the callers that compared the old instances by identity, or used them as keys, and
   update them to the new equality.

## Example
Before: a device owns a mutable calibration, and its properties update that calibration in place.

```csharp
public class Calibration
{
    public double Offset { get; set; }
    public double Scale { get; set; } = 1;
}

public class Device
{
    private Calibration _calibration = new Calibration();

    public double CalibrationOffset
    {
        get => _calibration.Offset;
        set => _calibration.Offset = value;
    }

    public double CalibrationScale
    {
        get => _calibration.Scale;
        set => _calibration.Scale = value;
    }
}
```

Step 1, remove the setters one at a time. The constructor takes the fields, and each setter
on `Device` replaces the whole calibration:

```csharp
public class Calibration
{
    public Calibration(double offset, double scale)
    {
        Offset = offset;
        Scale = scale;
    }

    public double Offset { get; }
    public double Scale { get; }
}

public class Device
{
    private Calibration _calibration = new Calibration(0, 1);

    public double CalibrationOffset
    {
        get => _calibration.Offset;
        set => _calibration = new Calibration(value, _calibration.Scale);
    }

    public double CalibrationScale
    {
        get => _calibration.Scale;
        set => _calibration = new Calibration(_calibration.Offset, value);
    }
}
```

Step 2, give it value equality (here by hand; see the C# notes for the shorter form):

```csharp
// fragment
using System;

public sealed class Calibration : IEquatable<Calibration>
{
    public Calibration(double offset, double scale)
    {
        Offset = offset;
        Scale = scale;
    }

    public double Offset { get; }
    public double Scale { get; }

    public bool Equals(Calibration other) =>
        other is not null && Offset == other.Offset && Scale == other.Scale;

    public override bool Equals(object obj) => Equals(obj as Calibration);

    public override int GetHashCode() => HashCode.Combine(Offset, Scale);
}
```

Behavior seen from outside `Device` is the same; `new Calibration(0.5, 1)` now equals
another instance built from the same arguments.

## C# notes
- A `record` (C# 9+; on Unity it needs an `IsExternalInit` shim), `readonly record struct` or an immutable class with value equality
  (`Equals`/`GetHashCode`) all fit. With a `record Calibration(double Offset, double Scale)`,
  equality and hash code are generated, and the owner's setter can be
  `_calibration = _calibration with { Scale = value };`.
- Whenever `Equals` is overridden, override `GetHashCode` with the same fields, or hash-based
  collections misbehave. Consider `==`/`!=` operators too if callers use them.
- Keep the value's fields themselves immutable (or compared by value), otherwise the value can
  still be changed from inside.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The equality tests from step 3 pass, including `null` and other types.
