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
   [remove-setting-method.md](remove-setting-method.md). First move the fields into the
   constructor, then rewrite each caller of a setter so it builds a new instance and assigns
   it to the owner's field. Test after each setter.
3. Add value-based equality over all the fields, and the matching hash code. Write tests that
   compare two independently built instances with the same contents, instances that differ in
   each field, `null`, and an object of another type.
4. Check the callers that compared the old instances by identity, or used them as keys, and
   update them to the new equality.

## Example
Before: an order owns a mutable address, and its properties update that address in place.

```csharp
public class PostalAddress
{
    public string Street { get; set; }
    public string City { get; set; }
}

public class Order
{
    private PostalAddress _shippingAddress = new PostalAddress();

    public string ShippingStreet
    {
        get => _shippingAddress.Street;
        set => _shippingAddress.Street = value;
    }

    public string ShippingCity
    {
        get => _shippingAddress.City;
        set => _shippingAddress.City = value;
    }
}
```

Step 1, remove the setters one at a time. The constructor takes the fields, and each setter
on `Order` replaces the whole address:

```csharp
public class PostalAddress
{
    public PostalAddress(string street, string city)
    {
        Street = street;
        City = city;
    }

    public string Street { get; }
    public string City { get; }
}

public class Order
{
    private PostalAddress _shippingAddress = new PostalAddress(null, null);

    public string ShippingStreet
    {
        get => _shippingAddress.Street;
        set => _shippingAddress = new PostalAddress(value, _shippingAddress.City);
    }

    public string ShippingCity
    {
        get => _shippingAddress.City;
        set => _shippingAddress = new PostalAddress(_shippingAddress.Street, value);
    }
}
```

Step 2, give it value equality (here by hand; see the C# notes for the shorter form):

```csharp
using System;

public sealed class PostalAddress : IEquatable<PostalAddress>
{
    public PostalAddress(string street, string city)
    {
        Street = street;
        City = city;
    }

    public string Street { get; }
    public string City { get; }

    public bool Equals(PostalAddress other) =>
        other is not null && Street == other.Street && City == other.City;

    public override bool Equals(object obj) => Equals(obj as PostalAddress);

    public override int GetHashCode() => HashCode.Combine(Street, City);
}
```

Behavior seen from outside `Order` is the same; `new PostalAddress("A", "B")` now equals
another instance built from the same arguments.

## C# notes
- A `record`, `readonly record struct` or an immutable class with value equality
  (`Equals`/`GetHashCode`) all fit. With a `record PostalAddress(string Street, string City)`,
  equality and hash code are generated, and the owner's setter can be
  `_shippingAddress = _shippingAddress with { City = value };`.
- Whenever `Equals` is overridden, override `GetHashCode` with the same fields, or hash-based
  collections misbehave. Consider `==`/`!=` operators too if callers use them.
- Keep the value's fields themselves immutable (or compared by value), otherwise the value can
  still be changed from inside.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The equality tests from step 3 pass, including `null` and other types.
