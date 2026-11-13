# Rename Variable

Fowler (2018), ch. 6, p. 137. Formerly / aka: —. Inverse: —.

## When to use
Smell: Mysterious Name. The wider a name reaches, the more it matters:

- A local in a one-line lambda or a short function can stay terse; context explains it.
- A long-lived field, or anything used across many functions or files, deserves the most
  careful name.

Names go wrong for a few reasons: they were picked in a hurry, the understanding of the
problem changed, or the code now does something else.

Do not do this by hand for a variable that belongs to a published API, where callers you
cannot edit still use the old name.

## Mechanics
1. If the variable is used widely, apply Encapsulate Variable first ([encapsulate-variable.md](encapsulate-variable.md)), so the rename touches one place.
2. Find every reference and change each one. Use the IDE or compiler rename, not text search alone, and also search for the old name where the compiler cannot see it: reflection, serialized names, configuration keys, string templates.
3. If the variable is never reassigned, you can do it gradually: declare the new name, make the old name copy the new one (so the old name is easy to restore if a test fails), move references over in small batches testing between batches, then delete the old name.
4. Build and test.

If the variable is visible to code outside your code base, it is published and this
refactoring does not apply as is.

## Example
A widely used mutable value. Before:

```csharp
public static class ShippingSettings
{
    public static string dflMethod = "standard";

    public static string Describe(decimal fee) => $"{fee:0.00} via {dflMethod}";
}

// elsewhere
// ShippingSettings.dflMethod = cart.PreferredMethod;
```

Step 1, encapsulate so there is one place to rename:

```csharp
public static class ShippingSettings
{
    private static string dflMethod = "standard";

    public static string DefaultMethod
    {
        get => dflMethod;
        set => dflMethod = value;
    }

    public static string Describe(decimal fee) => $"{fee:0.00} via {DefaultMethod}";
}

// elsewhere
// ShippingSettings.DefaultMethod = cart.PreferredMethod;
```

Step 2, rename the now-private field. Keep the property rather than inlining it: the value
is widely used, so the encapsulation is worth keeping.

```csharp
public static class ShippingSettings
{
    private static string defaultMethod = "standard";

    public static string DefaultMethod
    {
        get => defaultMethod;
        set => defaultMethod = value;
    }

    public static string Describe(decimal fee) => $"{fee:0.00} via {DefaultMethod}";
}
```

Renaming a constant gradually, by copy:

```csharp
// fragment
// before
public const decimal fst = 50m;

// during: both exist, callers move over a few at a time
public const decimal FreeShippingThreshold = 50m;
public const decimal fst = FreeShippingThreshold;

// after: the old name is deleted once nothing uses it
public const decimal FreeShippingThreshold = 50m;
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
