# Compose Method

Kerievsky (2004), ch. 7, p. 123. Pattern: Composed Method. Direction: to.

## When to use
Smells: Long Method.

- You cannot grasp what a method does without reading every line, because high-level calls sit next to loops, conditionals and index arithmetic.
- The goal is a method of about five lines (rarely over ten) made of calls to well-named methods, all at the same level of detail. The name says what, the body says how.
- This is the same work as [extract-function.md](../../fowler/first-set/extract-function.md) and [slide-statements.md](../../fowler/moving-features/slide-statements.md), aimed at one result. The book gives no fixed recipe, only guidelines.
- Liabilities: it can leave many tiny private methods (a hint to apply [extract-class.md](../../fowler/encapsulation/extract-class.md)), and the real work becomes harder to find in a debugger. Performance is not a reason to stop unless a profiler says so.

## Mechanics
Follow [extract-function.md](../../fowler/first-set/extract-function.md); there is no separate procedure. What Kerievsky adds is how to steer it:

1. Remove duplication and dead code first ([remove-dead-code.md](../../fowler/moving-features/remove-dead-code.md)), so there is less to read.
2. Flatten nesting where it hides the main path: [replace-nested-conditional-with-guard-clauses.md](../../fowler/conditional-logic/replace-nested-conditional-with-guard-clauses.md) and [consolidate-conditional-expression.md](../../fowler/conditional-logic/consolidate-conditional-expression.md).
3. Find the lines that are at a different level of detail from their neighbors (a raw condition, a loop, an array write among calls). Push each one down with [extract-function.md](../../fowler/first-set/extract-function.md), named for its intention.
4. If you cannot find a good name for what you extracted, you took too much or too little. Undo it with [inline-function.md](../../fowler/first-set/inline-function.md) and cut along a different line.
5. Replace magic literals with named constants ([replace-magic-literal.md](../../fowler/organizing-data/replace-magic-literal.md)).
6. Stop when every statement in the method says what, and the details live one call down. Compile and test after each step.

## Example
Before: the settling method nests two checks around mixed-level code.

```csharp
using System;
using System.Collections.Generic;

public class Payment
{
    public int Id { get; }
    public decimal Amount { get; }
    public DateTime AuthorizationExpires { get; }

    public Payment(int id, decimal amount, DateTime authorizationExpires)
    {
        Id = id;
        Amount = amount;
        AuthorizationExpires = authorizationExpires;
    }
}

public class SettlementDesk
{
    private readonly List<Payment> _settled = new();
    private readonly List<string> _log = new();

    public bool Closed { get; set; }

    public void Settle(Payment payment)
    {
        if (!Closed)
        {
            if (payment.Amount > 0)
            {
                _settled.Add(payment);
                if (payment.AuthorizationExpires < DateTime.UtcNow.Date)
                    _log.Add($"payment {payment.Id} settled after authorization expired");
                else
                    _log.Add($"payment {payment.Id} settled");
            }
        }
    }
}
```

After: a guard clause first, then two steps at the same level. The expiry rule has a name.

```csharp
using System;
using System.Collections.Generic;

public class SettlementDesk
{
    private readonly List<Payment> _settled = new();
    private readonly List<string> _log = new();

    public bool Closed { get; set; }

    public void Settle(Payment payment)
    {
        if (Closed || payment.Amount <= 0)
            return;
        Add(payment);
        LogSettlement(payment);
    }

    private void Add(Payment payment) => _settled.Add(payment);

    private void LogSettlement(Payment payment) =>
        _log.Add(IsExpired(payment)
            ? $"payment {payment.Id} settled after authorization expired"
            : $"payment {payment.Id} settled");

    private static bool IsExpired(Payment payment) =>
        payment.AuthorizationExpires < DateTime.UtcNow.Date;
}
```

## C# notes
- Expression-bodied members keep the extracted pieces short. Use a local function when a piece serves one method only.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Read the top method aloud: each line should be a step you would name in a sentence, with no operators or indexing left in it.
