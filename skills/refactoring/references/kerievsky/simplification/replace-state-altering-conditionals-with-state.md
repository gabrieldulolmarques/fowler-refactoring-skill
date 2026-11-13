# Replace State-Altering Conditionals with State

Kerievsky (2004), ch. 7, p. 166. Pattern: State. Direction: to, towards.

## When to use
Smells: Conditional Complexity, Large Class, Primitive Obsession.

- An object has a status field (an enum, constants, strings) and its methods check that field to decide what is allowed and what the next status is. The same checks are repeated in every method that moves the object between states, and the transitions are scattered through the class.
- Each state becomes a class that knows which transitions it allows and where they lead. The object (the context) forwards state-dependent calls to its current state object and switches states by pointing at a different one. The state classes together give a readable map of the whole machine.
- This is not Replace Type Code with Subclasses. There the type is fixed for the object's life, so subclasses of the object itself are enough. Here the object changes state while it lives, so the variation must sit in a separate object it can swap. It is also not [replace-conditional-logic-with-strategy.md](replace-conditional-logic-with-strategy.md): a Strategy is chosen from outside to run an algorithm, while states choose their own successor.
- If the transition logic is still easy to follow, do not do it. Try [extract-function.md](../../fowler/first-set/extract-function.md) first. Two or three states with a couple of transitions are usually better left as a field and a few `if`s. Do it when the logic is hard to follow, or when many more transitions are coming.
- Liability: more classes, and the rules for one transition now live in the state class that starts it, not in the context.

## Mechanics
The context is the class that owns the status field (the original state field). It is assigned or compared against a set of constants as transitions happen.

1. Apply Replace Type Code with Class ([replace-type-code-with-class.md](../protection/replace-type-code-with-class.md)) to the status field, so its type is a new class: the state superclass. Callers and every `switch` on the old type must now compare against the class's constants. Compile.
2. Each constant is now an instance of the state superclass. Create one subclass per constant (Replace Type Code with Subclasses, [replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md), whose second step is what the book calls Extract Subclass), and make each constant refer to its subclass instance. Declare the state superclass `abstract`. Compile.
3. Take one context method that changes the status according to the transition rules. Copy it to the state superclass with the fewest changes that make it work (usually add the context as a parameter and call its members through it). Replace the context method's body with a call to the copy. Compile and test. Repeat for every method that changes the status.
4. Take one state. Find which of the copied superclass methods make a transition out of that state. Copy each into that state's subclass (as an override) and delete everything unrelated from the copy: the check of the current state and the branches that belong to other states. Compile and test. Repeat for every state.
5. Replace the body of each method copied in step 3 with the default behavior: usually reject the call or do nothing. Compile and test.
6. If other methods branch on the status (not only the ones that change it), move them too, with [replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md): a virtual member on the state with the common answer, overridden by the states that differ.

Data that belongs to the object (who is assigned, how many times it was reopened) stays in the context. States read and write it through the context they receive.

## Example
The domain is an instant payment with four states and these transitions. Anything not in the table is rejected with an `InvalidOperationException`.

| From | Call | To |
|---|---|---|
| Created | Authorize (at most 3 attempts) | Authorized |
| Authorized | Release | Created |
| Authorized | Settle | Settled |
| Settled | Refund | Refunded |
| Refunded | (none) | |

Reconciliation is allowed only in Settled and Refunded.

Before: every method repeats a status check and sets the next status.

```csharp
using System;

public enum PaymentStatus { Created, Authorized, Settled, Refunded }

public class Payment
{
    private PaymentStatus _status = PaymentStatus.Created;

    public string? AuthCode { get; private set; }
    public int AuthAttempts { get; private set; }
    public string StatusName => _status.ToString();
    public bool AllowsReconciliation => _status == PaymentStatus.Settled || _status == PaymentStatus.Refunded;

    public void Authorize(string code)
    {
        if (_status != PaymentStatus.Created)
            throw new InvalidOperationException($"cannot authorize a payment that is {_status}");
        if (AuthAttempts >= 3)
            throw new InvalidOperationException("authorization attempt limit reached");
        AuthAttempts++;
        AuthCode = code;
        _status = PaymentStatus.Authorized;
    }

    public void Release()
    {
        if (_status != PaymentStatus.Authorized)
            throw new InvalidOperationException($"cannot release a payment that is {_status}");
        AuthCode = null;
        _status = PaymentStatus.Created;
    }

    public void Settle()
    {
        if (_status != PaymentStatus.Authorized)
            throw new InvalidOperationException($"cannot settle a payment that is {_status}");
        _status = PaymentStatus.Settled;
    }

    public void Refund()
    {
        if (_status != PaymentStatus.Settled)
            throw new InvalidOperationException($"cannot refund a payment that is {_status}");
        _status = PaymentStatus.Refunded;
    }
}
```

After steps 1 and 2, the enum is a class with four constants, each an instance of a private nested subclass of an abstract `PaymentState`. The context keeps a `State` property (now with an internal setter) instead of `_status`. Nothing else has changed yet.

During step 3, `Authorize` is copied to the state superclass with the context as a parameter, and the context method only delegates:

```csharp
// fragment
// in PaymentState
internal virtual void Authorize(Payment payment, string code)
{
    if (payment.State != Created)
        throw new InvalidOperationException($"cannot authorize a payment that is {Name}");
    if (payment.AuthAttempts >= 3)
        throw new InvalidOperationException("authorization attempt limit reached");
    payment.AuthAttempts++;
    payment.AuthCode = code;
    payment.State = Authorized;
}

// in Payment
public void Authorize(string code) => State.Authorize(this, code);
```

In step 4, `CreatedState` gets the only branch that applies to it. The check of the current state and the other states' branches are gone from the override:

```csharp
// fragment
// in CreatedState
internal override void Authorize(Payment payment, string code)
{
    if (payment.AuthAttempts >= 3)
        throw new InvalidOperationException("authorization attempt limit reached");
    payment.AuthAttempts++;
    payment.AuthCode = code;
    payment.State = Authorized;
}
```

In step 5, the base `Authorize` shrinks to the default, `throw NotAllowed("authorize")`. Doing this for every method gives the final code. Each state lists exactly the transitions it allows, and a state that does not override a method rejects it.

```csharp
using System;

public class Payment
{
    public PaymentState State { get; internal set; } = PaymentState.Created;
    public string? AuthCode { get; internal set; }
    public int AuthAttempts { get; internal set; }
    public string StatusName => State.Name;
    public bool AllowsReconciliation => State.AllowsReconciliation;

    public void Authorize(string code) => State.Authorize(this, code);
    public void Release() => State.Release(this);
    public void Settle() => State.Settle(this);
    public void Refund() => State.Refund(this);
}

public abstract class PaymentState
{
    public static readonly PaymentState Created = new CreatedState();
    public static readonly PaymentState Authorized = new AuthorizedState();
    public static readonly PaymentState Settled = new SettledState();
    public static readonly PaymentState Refunded = new RefundedState();

    public abstract string Name { get; }
    public virtual bool AllowsReconciliation => false;

    internal virtual void Authorize(Payment payment, string code) => throw NotAllowed("authorize");
    internal virtual void Release(Payment payment) => throw NotAllowed("release");
    internal virtual void Settle(Payment payment) => throw NotAllowed("settle");
    internal virtual void Refund(Payment payment) => throw NotAllowed("refund");

    private InvalidOperationException NotAllowed(string action) =>
        new($"cannot {action} a payment that is {Name}");

    private sealed class CreatedState : PaymentState
    {
        public override string Name => "Created";

        internal override void Authorize(Payment payment, string code)
        {
            if (payment.AuthAttempts >= 3)
                throw new InvalidOperationException("authorization attempt limit reached");
            payment.AuthAttempts++;
            payment.AuthCode = code;
            payment.State = Authorized;
        }
    }

    private sealed class AuthorizedState : PaymentState
    {
        public override string Name => "Authorized";

        internal override void Release(Payment payment)
        {
            payment.AuthCode = null;
            payment.State = Created;
        }

        internal override void Settle(Payment payment) => payment.State = Settled;
    }

    private sealed class SettledState : PaymentState
    {
        public override string Name => "Settled";
        public override bool AllowsReconciliation => true;

        internal override void Refund(Payment payment) => payment.State = Refunded;
    }

    private sealed class RefundedState : PaymentState
    {
        public override string Name => "Refunded";
        public override bool AllowsReconciliation => true;
    }
}
```

Adding a state (say, `Disputed`) now means one new nested class and the transitions that lead to it. The existing methods on `Payment` do not change.

## C# notes
- The state objects hold no per-payment data, so the four `static readonly` instances are shared by all payments. Keep it that way: if a state needs its own data, create an instance per context instead of a shared constant.
- Nested `private sealed` subclasses keep the constants as the only way to obtain a state. `internal` members let the states change the context without exposing setters publicly. If the states live in another assembly, use a small public interface on the context instead.
- If the status is persisted, keep a stable code (the `Name`, or the old enum value) and map it back to the constant when the object is loaded.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Write the transition table as a test before step 1, covering every allowed move and at least one rejected call per state (including the attempt limit), and keep it passing through all five steps.
- After step 4, temporarily make the base methods throw (step 5 early) on a branch: any test that fails shows a state you forgot to give an override.
- Check that no code outside the context and the states reads `State` to branch on it. That would recreate the conditional somewhere else.
