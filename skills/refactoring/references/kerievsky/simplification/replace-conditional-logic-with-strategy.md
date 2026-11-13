# Replace Conditional Logic with Strategy

Kerievsky (2004), ch. 7, p. 129. Pattern: Strategy. Direction: to, towards.

## When to use
Smells: Conditional Complexity, Long Method, Primitive Obsession.

- A calculation method holds a lot of conditional logic that picks one of several variants of an algorithm, and small helper methods that serve only one variant are crowding the class.
- Prefer a Strategy (composition) over [replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md) (inheritance) when the host class has no subclasses yet, when subclassing would multiply classes (this reason is the skill's, not the book's), or when callers must swap the algorithm at runtime without changing the object's class.
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

**Beyond the book:** the book's mechanics stop at step 4. Optionally, if the context is built in many places, hide strategy construction behind a creation method ([encapsulate-classes-with-factory.md](../creation/encapsulate-classes-with-factory.md)); the book's Motivation points to Encapsulate Classes with Factory for this.

## Example
Before: the payment method is guessed from which nullable fields are set, and one combination falls through to zero.

```csharp
public class Payment
{
    public decimal Amount { get; }
    public bool CrossBorder { get; }
    public string? CardToken { get; }
    public string? TransferAlias { get; }

    public Payment(decimal amount, bool crossBorder, string? cardToken, string? transferAlias)
    {
        Amount = amount;
        CrossBorder = crossBorder;
        CardToken = cardToken;
        TransferAlias = transferAlias;
    }

    public decimal Fee()
    {
        if (TransferAlias != null && CardToken == null)
            return 0.5m;
        if (CardToken != null && TransferAlias == null)
        {
            decimal fee = Amount * 0.029m + 0.3m;
            return CrossBorder ? fee + Amount * 0.01m : fee;
        }
        if (CardToken == null && TransferAlias == null)
            return Amount * 0.008m;
        return 0m;
    }
}
```

After: each method is a strategy and the payment is handed one. The payment passes itself because the strategies read several of its properties. The impossible "both set" case is gone, because the caller now chooses the method explicitly. Swapping is a property assignment.

```csharp
public interface IFeeStrategy
{
    decimal Fee(Payment payment);
}

public class TransferFee : IFeeStrategy
{
    public decimal Fee(Payment payment) => 0.5m;
}

public class CardFee : IFeeStrategy
{
    public decimal Fee(Payment payment)
    {
        decimal fee = payment.Amount * 0.029m + 0.3m;
        return payment.CrossBorder ? fee + payment.Amount * 0.01m : fee;
    }
}

public class DebitFee : IFeeStrategy
{
    public decimal Fee(Payment payment) => payment.Amount * 0.008m;
}

public class Payment
{
    public decimal Amount { get; }
    public bool CrossBorder { get; }
    public IFeeStrategy FeeStrategy { get; set; } = new DebitFee();

    public Payment(decimal amount, bool crossBorder)
    {
        Amount = amount;
        CrossBorder = crossBorder;
    }

    public decimal Fee() => FeeStrategy.Fee(this);
}
```

## C# notes
- An interface is enough when the strategies share no code. Use an abstract class if they share helpers.
- Stateless strategies can be shared as `static readonly` instances. Do it when a profiler asks for it, not before.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- A test per concrete strategy, plus one that swaps the strategy on an existing context and checks the new result.
- Check that no input the old conditional accepted is now unreachable or priced differently (here, the old zero fall-through).
