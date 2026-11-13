# Replace State-Altering Conditionals with State

Kerievsky (2004), ch. 7, p. 166. Direction: to, towards. Pattern: State (GoF, p. 305).

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
The domain is a support ticket with four states and these transitions. Anything not in the table is rejected with an `InvalidOperationException`.

| From | Call | To |
|---|---|---|
| Open | Assign | Assigned |
| Open | Close | Closed |
| Assigned | Unassign | Open |
| Assigned | Resolve | Resolved |
| Resolved | Reopen (at most twice) | Assigned |
| Resolved | Close | Closed |
| Closed | (none) | |

Comments are accepted in every state except Closed.

Before: every method repeats a status check and sets the next status.

```csharp
using System;

public enum TicketStatus { Open, Assigned, Resolved, Closed }

public class Ticket
{
    private TicketStatus _status = TicketStatus.Open;

    public string? Assignee { get; private set; }
    public int ReopenCount { get; private set; }
    public string StatusName => _status.ToString();
    public bool AcceptsComments => _status != TicketStatus.Closed;

    public void Assign(string agent)
    {
        if (_status != TicketStatus.Open)
            throw new InvalidOperationException($"cannot assign a ticket that is {_status}");
        Assignee = agent;
        _status = TicketStatus.Assigned;
    }

    public void Unassign()
    {
        if (_status != TicketStatus.Assigned)
            throw new InvalidOperationException($"cannot unassign a ticket that is {_status}");
        Assignee = null;
        _status = TicketStatus.Open;
    }

    public void Resolve()
    {
        if (_status != TicketStatus.Assigned)
            throw new InvalidOperationException($"cannot resolve a ticket that is {_status}");
        _status = TicketStatus.Resolved;
    }

    public void Reopen()
    {
        if (_status != TicketStatus.Resolved)
            throw new InvalidOperationException($"cannot reopen a ticket that is {_status}");
        if (ReopenCount >= 2)
            throw new InvalidOperationException("reopen limit reached");
        ReopenCount++;
        _status = TicketStatus.Assigned;
    }

    public void Close()
    {
        if (_status != TicketStatus.Open && _status != TicketStatus.Resolved)
            throw new InvalidOperationException($"cannot close a ticket that is {_status}");
        _status = TicketStatus.Closed;
    }
}
```

After steps 1 and 2, the enum is a class with four constants, each an instance of a private nested subclass of an abstract `TicketState`. The context keeps a `State` property (now with an internal setter) instead of `_status`. Nothing else has changed yet.

During step 3, `Assign` is copied to the state superclass with the context as a parameter, and the context method only delegates:

```csharp
// in TicketState
internal virtual void Assign(Ticket ticket, string agent)
{
    if (ticket.State != Open)
        throw new InvalidOperationException($"cannot assign a ticket that is {Name}");
    ticket.Assignee = agent;
    ticket.State = Assigned;
}

// in Ticket
public void Assign(string agent) => State.Assign(this, agent);
```

In step 4, `OpenState` gets the only branch that applies to it. The check and the other states' branches are gone from the override:

```csharp
// in OpenState
internal override void Assign(Ticket ticket, string agent)
{
    ticket.Assignee = agent;
    ticket.State = Assigned;
}
```

In step 5, the base `Assign` shrinks to the default, `throw NotAllowed("assign")`. Doing this for every method gives the final code. Each state lists exactly the transitions it allows, and a state that does not override a method rejects it.

```csharp
using System;

public class Ticket
{
    public TicketState State { get; internal set; } = TicketState.Open;
    public string? Assignee { get; internal set; }
    public int ReopenCount { get; internal set; }
    public string StatusName => State.Name;
    public bool AcceptsComments => State.AcceptsComments;

    public void Assign(string agent) => State.Assign(this, agent);
    public void Unassign() => State.Unassign(this);
    public void Resolve() => State.Resolve(this);
    public void Reopen() => State.Reopen(this);
    public void Close() => State.Close(this);
}

public abstract class TicketState
{
    public static readonly TicketState Open = new OpenState();
    public static readonly TicketState Assigned = new AssignedState();
    public static readonly TicketState Resolved = new ResolvedState();
    public static readonly TicketState Closed = new ClosedState();

    public abstract string Name { get; }
    public virtual bool AcceptsComments => true;

    internal virtual void Assign(Ticket ticket, string agent) => throw NotAllowed("assign");
    internal virtual void Unassign(Ticket ticket) => throw NotAllowed("unassign");
    internal virtual void Resolve(Ticket ticket) => throw NotAllowed("resolve");
    internal virtual void Reopen(Ticket ticket) => throw NotAllowed("reopen");
    internal virtual void Close(Ticket ticket) => throw NotAllowed("close");

    private InvalidOperationException NotAllowed(string action) =>
        new($"cannot {action} a ticket that is {Name}");

    private sealed class OpenState : TicketState
    {
        public override string Name => "Open";

        internal override void Assign(Ticket ticket, string agent)
        {
            ticket.Assignee = agent;
            ticket.State = Assigned;
        }

        internal override void Close(Ticket ticket) => ticket.State = Closed;
    }

    private sealed class AssignedState : TicketState
    {
        public override string Name => "Assigned";

        internal override void Unassign(Ticket ticket)
        {
            ticket.Assignee = null;
            ticket.State = Open;
        }

        internal override void Resolve(Ticket ticket) => ticket.State = Resolved;
    }

    private sealed class ResolvedState : TicketState
    {
        public override string Name => "Resolved";

        internal override void Reopen(Ticket ticket)
        {
            if (ticket.ReopenCount >= 2)
                throw new InvalidOperationException("reopen limit reached");
            ticket.ReopenCount++;
            ticket.State = Assigned;
        }

        internal override void Close(Ticket ticket) => ticket.State = Closed;
    }

    private sealed class ClosedState : TicketState
    {
        public override string Name => "Closed";
        public override bool AcceptsComments => false;
    }
}
```

Adding a state (say, `Escalated`) now means one new nested class and the transitions that lead to it. The existing methods on `Ticket` do not change.

## C# notes
- The state objects hold no per-ticket data, so the four `static readonly` instances are shared by all tickets. Keep it that way: if a state needs its own data, create an instance per context instead of a shared constant.
- Nested `private sealed` subclasses keep the constants as the only way to obtain a state. `internal` members let the states change the context without exposing setters publicly. If the states live in another assembly, use a small public interface on the context instead.
- A `switch` expression on the old enum, if one survives elsewhere (for example in a mapper or a UI label), must be replaced by a state member or compare `State` to the constants.
- If the status is persisted, keep a stable code (the `Name`, or the old enum value) and map it back to the constant when the object is loaded.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Write the transition table as a test before step 1, covering every allowed move and at least one rejected call per state (including the reopen limit), and keep it passing through all five steps.
- After step 4, temporarily make the base methods throw (step 5 early) on a branch: any test that fails shows a state you forgot to give an override.
- Check that no code outside the context and the states reads `State` to branch on it. That would recreate the conditional somewhere else.
