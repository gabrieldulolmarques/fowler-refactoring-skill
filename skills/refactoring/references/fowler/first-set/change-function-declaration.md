# Change Function Declaration

Fowler (2018), ch. 6, p. 124. Formerly / aka: Rename Function, Change Signature; formerly Rename Method, Add Parameter, Remove Parameter. Inverse: —.

## When to use
Smells: Mysterious Name, Alternative Classes with Different Interfaces, Speculative Generality (unused parameters), Comments (a comment explaining the function is often a better name).

- The name does not tell a reader what the function does. Rename as soon as you know a better name; a good trick is to write a comment describing the purpose and turn it into the name.
- A parameter ties the function to a type it does not really need (pass the value, not the whole object) so it can be reused elsewhere and the coupling drops.
- The opposite case: a function needs more of an object than one value, and passing the object keeps callers stable when the logic grows.
- A parameter is unused, or a new one is needed.

There is no permanently right choice of parameters; the declaration should follow your current understanding, so expect to change it again.

## Mechanics
Pick one of two routes. Use the simple one when you can change the declaration and every caller at once. Use the migration one when there are many callers, some are hard to reach, the function is polymorphic, the change is complex, or it is a published API.

Change one thing at a time: if you need to rename and add a parameter, do the rename, test, then the parameter, test.

**Simple route**
1. If removing a parameter, confirm the body no longer uses it.
2. Change the declaration to the new name or parameter list.
3. Find every reference to the old declaration and update it.
4. Compile and test. If it goes wrong, revert and use the migration route.

**Migration route**
1. If needed, reshape the body so the next step is easy (for example, Extract Variable on the value that will become the new parameter, [extract-variable.md](extract-variable.md)).
2. Apply Extract Function ([extract-function.md](extract-function.md)) to the whole body to create the new function. While both functions exist, the new one needs a unique, easy-to-search placeholder name; you will swap it for the final name (possibly the old one) at the end.
3. If the new function needs extra parameters, add them with the simple route.
4. Test.
5. Apply Inline Function ([inline-function.md](inline-function.md)) to the old function, which moves callers to the new one, one at a time if you like, testing as you go.
6. If you used a temporary name, rename it to the final name with the simple route.
7. Test.

Polymorphism: each binding that callers can reach needs the forwarding function. Within one hierarchy, a forwarder on the base type is enough; for unrelated implementations, add one on each.

Published API: stop after creating the new function, mark the old one deprecated and keep it forwarding to the new one until clients have moved; delete it only when you are confident (or never, if you cannot reach them).

## Example
Goal: `QualifiesForFreeShipping(Cart)` should take only the subtotal, so it also works for anything that has a subtotal (a quote, a saved basket). Migration route, with a temporary name.

Before:

```csharp
public class Cart
{
    public decimal Subtotal { get; }

    public Cart(decimal subtotal) => Subtotal = subtotal;
}

public static class Shipping
{
    public static bool QualifiesForFreeShipping(Cart cart) =>
        cart.Subtotal >= 50m;
}

// caller
// var eligible = carts.Where(c => Shipping.QualifiesForFreeShipping(c));
```

Step 1, extract the body into a new function with a temporary name and the wanted parameter:

```csharp
// fragment
public static bool QualifiesForFreeShipping(Cart cart) =>
    QualifiesForFreeShipping_new(cart.Subtotal);

public static bool QualifiesForFreeShipping_new(decimal subtotal) =>
    subtotal >= 50m;
```

Step 2, inline `QualifiesForFreeShipping` into each caller (test after each one), then delete it:

```csharp
// fragment
// var eligible = carts.Where(c => Shipping.QualifiesForFreeShipping_new(c.Subtotal));
```

Step 3, rename `QualifiesForFreeShipping_new` back to `QualifiesForFreeShipping`:

```csharp
// fragment
public static bool QualifiesForFreeShipping(decimal subtotal) =>
    subtotal >= 50m;

// var eligible = carts.Where(c => Shipping.QualifiesForFreeShipping(c.Subtotal));
```

Same behavior throughout; the build stays green after every step.

## C# notes
- The compiler finds direct callers, but not reflection, string-based lookups (`nameof` aside), or serialized names; search for those separately.
- On a public API, keep the old signature as an `[Obsolete]` forwarder to the new one during the migration.
- Changing an `override`, a `virtual` member or an interface member affects every implementation; update them together or forward from each.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
