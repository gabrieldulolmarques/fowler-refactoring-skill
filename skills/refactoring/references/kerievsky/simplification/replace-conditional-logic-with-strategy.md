# Replace Conditional Logic with Strategy

Kerievsky (2004), ch. 7, p. 129. Pattern: Strategy. Direction: to, towards.

## When to use
Smells: Conditional Complexity, Long Method, Primitive Obsession.

- A calculation method holds a lot of conditional logic that picks one of several variants of an algorithm, and small helper methods that serve only one variant are crowding the class.
- Prefer a Strategy (composition) over [replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md) (inheritance) when the host class has no subclasses yet, when subclassing would multiply classes (variants of one algorithm times other axes), or when callers must swap the algorithm at runtime without changing the object's class.
- If the host already has subclasses that map cleanly to the variants, or one type code drives the conditionals, polymorphism is simpler.
- Liabilities: it complicates the design if a simpler conditional refactoring was enough, and the strategies now need a way to read the context's data (see step 2).

## Mechanics
Identify the context: the class with the calculation method full of conditionals.

1. Create a concrete class, the strategy, named after what the calculation does (a `Strategy` suffix is fine). It becomes a real concrete strategy by the end.
2. Apply Move Function ([move-function.md](../../fowler/moving-features/move-function.md)) to move the calculation method to the strategy. Keep a method on the context that delegates to it through a new field. Decide how the strategy gets its data:
   - Pass the context (to the constructor or the method). Fewer parameters, and new context members are available at once, but the context must expose more of itself.
   - Pass only the data, as parameters. Least coupling, but every strategy receives data it may not need. If the list grows long, apply Introduce Parameter Object ([introduce-parameter-object.md](../../fowler/first-set/introduce-parameter-object.md)) or pass the context instead. Data needed by one variant only can go to that variant's constructor later.

   Move helper methods used only by the calculation into the strategy. Compile and test.
3. Let clients choose the strategy: apply Extract Parameter ([extract-parameter.md](../utilities/extract-parameter.md)) on the context code that creates the strategy and assigns the field. Compile and test.
4. Apply Replace Conditional with Polymorphism ([replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md)) to the strategy's calculation method. Use Replace Type Code with Subclasses ([replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md)) as its first step, even if the variants are only implied by conditions and there is no explicit code. Build one subclass at a time, and make the strategy abstract (or an interface) if you can. Compile and test with every combination of context and concrete strategy.
5. If the context is built in many places, hide strategy construction behind a creation method ([encapsulate-classes-with-factory.md](../creation/encapsulate-classes-with-factory.md)).

## Example
Before: the variant is guessed from which nullable fields are set, and one combination falls through to zero.

```csharp
using System;

public class Order
{
    public decimal Weight { get; init; }
    public decimal DistanceKm { get; init; }
    public bool Fragile { get; init; }
    public DateTime? ExpressDeadline { get; init; }
    public string? PickupPoint { get; init; }

    public decimal ShippingCost()
    {
        if (PickupPoint != null && ExpressDeadline == null)
            return 2m;
        if (ExpressDeadline != null && PickupPoint == null)
        {
            decimal cost = Weight * 3m + DistanceKm * 0.5m;
            return Fragile ? cost + 10m : cost;
        }
        if (PickupPoint == null && ExpressDeadline == null)
            return Weight * 1.2m + DistanceKm * 0.1m;
        return 0m;
    }
}
```

After: each variant is a strategy and the order is handed one. The order passes itself because the strategies read several of its properties. The impossible "both set" case is gone, because the caller now chooses the variant explicitly. Swapping is a property assignment.

```csharp
public interface IShippingStrategy
{
    decimal Cost(Order order);
}

public class PickupShipping : IShippingStrategy
{
    public decimal Cost(Order order) => 2m;
}

public class ExpressShipping : IShippingStrategy
{
    public decimal Cost(Order order)
    {
        decimal cost = order.Weight * 3m + order.DistanceKm * 0.5m;
        return order.Fragile ? cost + 10m : cost;
    }
}

public class StandardShipping : IShippingStrategy
{
    public decimal Cost(Order order) => order.Weight * 1.2m + order.DistanceKm * 0.1m;
}

public class Order
{
    public decimal Weight { get; init; }
    public decimal DistanceKm { get; init; }
    public bool Fragile { get; init; }
    public IShippingStrategy Shipping { get; set; } = new StandardShipping();

    public decimal ShippingCost() => Shipping.Cost(this);
}
```

## C# notes
- An interface is enough when the strategies share no code. Use an abstract class if they share helpers.
- Stateless strategies can be shared as `static readonly` instances. Do it when a profiler asks for it, not before.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- A test per concrete strategy, plus one that swaps the strategy on an existing context and checks the new result.
- Check that no input the old conditional accepted is now unreachable or priced differently (here, the old zero fall-through).
