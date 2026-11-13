# State

Gamma et al. (1995), ch. 5, p. 305. Also known as: Objects for States. Category: object behavioral.

## Intent
Let an object change its behavior when its internal state changes, by delegating to a separate object per state. To callers, the object seems to change its class.

## When it pays off
- Behavior depends on the current state and must change at run time.
- Several operations repeat the same large `if` or `switch` on a status field. Each branch becomes a class and the switches disappear.
- Benefits: the behavior of each state sits in one place; transitions are explicit; a transition is one reference assignment, so the context is never half-changed; stateless state objects can be shared.
- Liabilities: more classes than one big class. This is worth it with many states or many state-dependent operations, and not worth it with two states and one operation.
- Skip it when the states and transitions are plain data with no behavior; an enum and a transition table (see Variations) are enough.

## Participants in C#
- **Context** (`Ride`): the type clients use. Holds the current state object and forwards state-dependent calls to it.
- **State** (`RideState`): abstract class that declares one method per state-dependent operation. Its default implementation rejects the operation, so each concrete state overrides only what it allows. An interface also works when there are no defaults.
- **ConcreteState** (`RequestedState`, `AcceptedState`, `InProgressState`, `CompletedState`): behavior and outgoing transitions for one state.

## Example (C#)
A ride-sharing trip moves through four states: Requested, then Accepted (a driver took it), then InProgress (the passenger is on board), then Completed (a fare is charged). Each state allows only its own next step; anything else throws. The states hold no data, so each has one shared instance, and each decides its successor.

```csharp
using System;

public class Ride
{
    public RideState State { get; private set; } = RequestedState.Instance;
    public string? DriverId { get; private set; }
    public decimal Fare { get; private set; }

    // Operations forwarded to the current state.
    public void Accept(string driverId) => State.Accept(this, driverId);
    public void Start() => State.Start(this);
    public void Complete(decimal fare) => State.Complete(this, fare);

    // Used by the states, to change state and to record data.
    public void TransitionTo(RideState next) => State = next;
    public void AssignDriver(string driverId) => DriverId = driverId;
    public void Charge(decimal fare) => Fare = fare;
}

public abstract class RideState
{
    public string Name => GetType().Name.Replace("State", "");

    public virtual void Accept(Ride ride, string driverId) => throw Reject("accept");
    public virtual void Start(Ride ride) => throw Reject("start");
    public virtual void Complete(Ride ride, decimal fare) => throw Reject("complete");

    private InvalidOperationException Reject(string action) =>
        new($"Cannot {action} a ride that is {Name}.");
}

public sealed class RequestedState : RideState
{
    public static readonly RequestedState Instance = new();
    private RequestedState() { }

    public override void Accept(Ride ride, string driverId)
    {
        ride.AssignDriver(driverId);
        ride.TransitionTo(AcceptedState.Instance);
    }
}

public sealed class AcceptedState : RideState
{
    public static readonly AcceptedState Instance = new();
    private AcceptedState() { }

    public override void Start(Ride ride) => ride.TransitionTo(InProgressState.Instance);
}

public sealed class InProgressState : RideState
{
    public static readonly InProgressState Instance = new();
    private InProgressState() { }

    public override void Complete(Ride ride, decimal fare)
    {
        ride.Charge(fare);
        ride.TransitionTo(CompletedState.Instance);
    }
}

public sealed class CompletedState : RideState
{
    public static readonly CompletedState Instance = new();
    private CompletedState() { }
    // Terminal: every operation is rejected by the base class.
}

public static class Program
{
    public static void Main()
    {
        var ride = new Ride();
        ride.Accept("driver-7");
        ride.Start();
        ride.Complete(18.50m);
        Console.WriteLine($"{ride.State.Name} {ride.DriverId} {ride.Fare}");   // Completed driver-7 18.50

        try { ride.Start(); }
        catch (InvalidOperationException e) { Console.WriteLine(e.Message); }  // Cannot start a ride that is Completed.
    }
}
```

The shared instances are static fields only because the states carry no data. If a state needs per-ride data, create a new object per transition and keep that data in it.

A table-driven version of the same machine, for when the transitions are all that varies and there is no per-state behavior:

```csharp
using System.Collections.Generic;

public enum RideStatus { Requested, Accepted, InProgress, Completed }
public enum RideEvent { Accept, Start, Complete }

public class RideMachine
{
    private static readonly Dictionary<(RideStatus, RideEvent), RideStatus> Transitions = new()
    {
        [(RideStatus.Requested, RideEvent.Accept)] = RideStatus.Accepted,
        [(RideStatus.Accepted, RideEvent.Start)] = RideStatus.InProgress,
        [(RideStatus.InProgress, RideEvent.Complete)] = RideStatus.Completed,
    };

    public RideStatus Status { get; private set; } = RideStatus.Requested;

    public bool TryFire(RideEvent e)
    {
        if (!Transitions.TryGetValue((Status, e), out var next)) return false;
        Status = next;
        return true;
    }
}
```

## Variations
- **Who decides the next state.** If the rules are fixed, the context can hold them. It is usually more flexible to let each state pick its successor, as above. The cost is that states know about each other.
- **Table-driven machine.** A table maps (state, event) to the next state. Rules become data and are easy to read as a whole, but a lookup is slower than a virtual call, the logic is less explicit, and attaching actions to transitions takes extra work. State models behavior per state; a table models only the transitions.
- **Create or reuse state objects.** Creating on demand suits states that carry much data and change rarely. Creating once and reusing suits frequent transitions, but the context must be able to reach every state.
- **Sharing.** A state with no instance fields, whose meaning is carried entirely by its type, can be shared across all contexts, passing the context as an argument so it can act on it.
- **Changing class at run time.** Few languages let an object swap its class. Delegating to a replaceable state object gets the same effect in C#.

## Risks and C# alternatives
- For a few states and one or two operations, a `switch` expression over an enum is shorter and easier to follow. Move to State when the same `switch` appears in several methods or each branch grows.
- A static `Instance` on each state is a singleton. That is acceptable for stateless objects, but it hides the dependency. Passing the instances from the context, or from a small registry, is easier to test.
- State objects that mutate the context through public methods (`TransitionTo`, `AssignDriver`) weaken the context's invariants. Keep those methods `internal` when the types share an assembly, or expose only what the states need.
- Transitions that need I/O or must be thread-safe need locking or serialization around the state change. A reference assignment is atomic, but the read-then-act sequence is not.
- Base-class defaults that throw turn a forbidden operation into a run-time error. If callers should be able to ask first, add a `CanStart`-style method or return a result type instead of throwing.

## Related patterns
- [Flyweight](../structural/flyweight.md): covers the conditions and the technique for sharing state objects.
- [Singleton](../creational/singleton.md): shared stateless state objects are often singletons.

**Beyond the book:** [Strategy](strategy.md) has the same shape (a context delegating to a replaceable object) but a different intent. A strategy is chosen from outside and rarely changes itself; a state replaces itself as the object moves through its life.

## Verification
- No method of the context contains a `switch` or `if` on a status value; each state-dependent call is one forward to the state.
- Adding a state means adding a class and changing only the states that lead into it.
- Every illegal transition is covered by a test that expects the rejection, and every legal one by a test that checks the next state.
- The context never ends up with a half-applied transition: the state changes by one assignment, after the state's work is done.
