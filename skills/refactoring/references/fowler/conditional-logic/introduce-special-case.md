# Introduce Special Case

Fowler (2018), ch. 10, p. 289. Formerly / aka: Introduce Null Object. Inverse: —.

## When to use
Smells: Temporary Field.
- Many callers of a data structure check for the same special value (null, a sentinel string, a magic id) and most of them respond the same way.
- You want that shared response in one place, so callers just ask the object for what they need.
- Null is the commonest special value, hence the name Null Object, but the technique works for any special case ("unknown", "guest", "no plan").
- Keep a real check where a caller genuinely needs different behavior; a few exceptions are normal.

## Mechanics
Start from a container (class or record) whose property, the subject, can hold the special value, and clients that compare it to that value.

1. Add an `IsSpecialCase`-style property to the subject class, returning `false`.
2. Create the special-case type with only that property, returning `true`.
3. Extract Function ([extract-function.md](../first-set/extract-function.md)) on the special-value comparison, and make every client call the new function instead of comparing directly. Optionally make it throw on unexpected values while you migrate.
4. Make the container return the special-case object instead of the raw special value (or add it through a transform step for plain records).
5. Change the body of the extracted check to use the new property. Compile and test.
6. For each client, find the shared reaction and move it into the special-case type (Combine Functions into Class, [combine-functions-into-class.md](../first-set/combine-functions-into-class.md), or into Transform, [combine-functions-into-transform.md](../first-set/combine-functions-into-transform.md)). Replace the client's conditional with a plain call. Test after each client.
7. Related objects the special case must return are themselves special cases (for example a null history object). Writes that clients used to skip become no-ops on the special case.
8. For clients that still need different behavior, Inline Function ([inline-function.md](../first-set/inline-function.md)) the extracted check into a direct property test.
9. Remove Dead Code ([remove-dead-code.md](../moving-features/remove-dead-code.md)) on the extracted check once nobody calls it.

Treat the special case as a value: it should not change after creation, whatever the real objects it replaces allow. If clients only read, a constant or literal instance can be enough.

## Example
Before: four clients handle a cart with no promotion. The example skips the extracted-check stage (step 3) and goes straight to the final shape.

```csharp
public class Promotion
{
    public string Name { get; }
    public decimal DiscountRate { get; }
    public int DaysLeft { get; }
    public virtual int Redemptions { get; set; }

    public Promotion(string name, decimal discountRate, int daysLeft)
    {
        Name = name;
        DiscountRate = discountRate;
        DaysLeft = daysLeft;
    }
}

public class Cart
{
    private readonly Promotion? _promotion;
    public Cart(Promotion? promotion) => _promotion = promotion;
    public Promotion? Promotion => _promotion;
}

public class PromotionClients
{
    public string Label(Cart cart) => cart.Promotion == null ? "no promotion" : cart.Promotion.Name;
    public decimal Rate(Cart cart) => cart.Promotion == null ? 0m : cart.Promotion.DiscountRate;
    public int DaysLeft(Cart cart) => cart.Promotion == null ? 0 : cart.Promotion.DaysLeft;

    public void Redeem(Cart cart)
    {
        if (cart.Promotion != null) cart.Promotion.Redemptions++;
    }
}
```

After: the missing promotion is a special-case object.

```csharp
public class Promotion
{
    public virtual bool IsMissing => false;
    public string Name { get; }
    public decimal DiscountRate { get; }
    public int DaysLeft { get; }
    public virtual int Redemptions { get; set; }

    public Promotion(string name, decimal discountRate, int daysLeft)
    {
        Name = name;
        DiscountRate = discountRate;
        DaysLeft = daysLeft;
    }
}

public sealed class MissingPromotion : Promotion
{
    public MissingPromotion() : base("no promotion", 0m, 0) { }
    public override bool IsMissing => true;
    public override int Redemptions { get => 0; set { /* ignored */ } }
}

public class Cart
{
    private readonly Promotion? _promotion;
    public Cart(Promotion? promotion) => _promotion = promotion;
    public Promotion Promotion => _promotion ?? new MissingPromotion();
}

public class PromotionClients
{
    public string Label(Cart cart) => cart.Promotion.Name;
    public decimal Rate(Cart cart) => cart.Promotion.DiscountRate;
    public int DaysLeft(Cart cart) => cart.Promotion.DaysLeft;
    public void Redeem(Cart cart) => cart.Promotion.Redemptions++;

    // the one client that must behave differently keeps an explicit test
    public string Banner(Cart cart) =>
        cart.Promotion.IsMissing ? "Join the newsletter for coupons" : $"{cart.Promotion.Name} ends soon";
}
```

`Banner` is a fifth client that is not in the Before; it is added only to show a client that keeps its own explicit test. Apart from it, the behavior is the same: callers get the same values as before, and the write to a missing promotion is still a no-op.

## C# notes
- With nullable reference types enabled, the special case removes `?` and null checks at the call sites: the property becomes non-nullable and never returns null.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
