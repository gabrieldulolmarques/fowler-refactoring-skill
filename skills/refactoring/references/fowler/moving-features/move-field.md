# Move Field

Fowler (2018), ch. 8, p. 207. Formerly / aka: —. Inverse: —.

## When to use
Smells: Shotgun Surgery, Insider Trading.

- Signs the field is in the wrong place: it travels with another object in every call, editing
  one object forces an edit to a field of another, or one value is kept in several structures
  and must be updated in each.
- Do it as soon as the mismatch is clear; a misplaced field gets more expensive as code grows
  around it.
- Preconditions: reads and writes go through accessors (otherwise encapsulate first), and the
  source can reach the target. With a bare record, consider
  [encapsulate-record.md](../encapsulation/encapsulate-record.md) first.
- Usually part of a bigger change. Callers can move to the new owner afterwards, or the move
  may need to wait until usage is reshaped.

## Mechanics
1. Make sure the source field is encapsulated: all reads and writes go through accessors
   ([encapsulate-variable.md](../first-set/encapsulate-variable.md)). Test.
2. Add the field, with accessors, to the target class. Build and run static checks.
3. Make sure the source can get hold of the target: through something it already has, through a
   new lookup method, or, as a last resort, through a new field (perhaps temporary).
4. Point the source accessors at the target's field. Test.
   - If several source objects share one target, first make the setter write both the old and
     the new field and add an assertion ([introduce-assertion.md](../conditional-logic/introduce-assertion.md))
     that they agree. When it holds in practice, switch the accessors fully.
5. Remove the source field. Test.

### Watch out
- Construction order: a constructor that sets the field before the target object exists will
  break once the setter points at the target. Undo the redirect, reorder with
  [slide-statements.md](slide-statements.md), test, and redirect again.
- When several source objects point at one target, they may currently hold different values for
  the field. Check that they all agree with the target's value first; if they do not, moving
  the field changes behavior and is not a refactoring.
- Plain data records have no accessors to redirect. Introduce accessor functions, route every
  use through them, and for an immutable field write to both copies on set while reads migrate
  one by one.

## Example
Before: the retry limit lives on the shipment, though it is really a term of its delivery plan.

```csharp
using System;

public class Shipment
{
    private readonly DeliveryPlan _plan;
    private int _maxAttempts;

    public Shipment(string trackingCode, int maxAttempts)
    {
        TrackingCode = trackingCode;
        _maxAttempts = maxAttempts;
        _plan = new DeliveryPlan(DateTime.UtcNow.Date);
    }

    public string TrackingCode { get; }
    public int MaxAttempts => _maxAttempts;

    public void Escalate() => _maxAttempts += 1;

    public bool CanRetry(int attemptsMade) => attemptsMade < _maxAttempts;
}

public class DeliveryPlan
{
    public DeliveryPlan(DateTime plannedFor) => PlannedFor = plannedFor;
    public DateTime PlannedFor { get; }
}
```

Step 1, encapsulate the field. The constructor now goes through the setter:

```csharp
// fragment
public Shipment(string trackingCode, int maxAttempts)
{
    TrackingCode = trackingCode;
    SetMaxAttempts(maxAttempts);
    _plan = new DeliveryPlan(DateTime.UtcNow.Date);
}

public int MaxAttempts => _maxAttempts;
private void SetMaxAttempts(int value) => _maxAttempts = value;

public void Escalate() => SetMaxAttempts(MaxAttempts + 1);
public bool CanRetry(int attemptsMade) => attemptsMade < MaxAttempts;
```

Step 2, add the field and accessors to `DeliveryPlan`. The new parameter is optional for now, so
`Shipment` still compiles unchanged:

```csharp
using System;

public class DeliveryPlan
{
    public DeliveryPlan(DateTime plannedFor, int maxAttempts = 0)
    {
        PlannedFor = plannedFor;
        MaxAttempts = maxAttempts;
    }

    public DateTime PlannedFor { get; }
    public int MaxAttempts { get; set; }
}
```

Step 4, first attempt: redirect the accessors while the constructor is still in its old order.

```csharp
// fragment
public int MaxAttempts => _plan.MaxAttempts;
private void SetMaxAttempts(int value) => _plan.MaxAttempts = value;
// the constructor calls SetMaxAttempts before _plan is assigned:
// NullReferenceException on construction
```

Revert the accessors and reorder the constructor so `_plan` exists before the setter
runs. Test:

```csharp
// fragment
public Shipment(string trackingCode, int maxAttempts)
{
    TrackingCode = trackingCode;
    _plan = new DeliveryPlan(DateTime.UtcNow.Date);
    SetMaxAttempts(maxAttempts);
}
```

Redirect the accessors again. Test:

```csharp
// fragment
public int MaxAttempts => _plan.MaxAttempts;
private void SetMaxAttempts(int value) => _plan.MaxAttempts = value;
```

Step 5: delete `_maxAttempts`. Test.

Optional cleanup, as a separate step: the constructor can hand the initial limit straight to
`DeliveryPlan`, and the temporary default on the new parameter goes away. `SetMaxAttempts` stays
for `Escalate`:

```csharp
// fragment
public Shipment(string trackingCode, int maxAttempts)
{
    TrackingCode = trackingCode;
    _plan = new DeliveryPlan(DateTime.UtcNow.Date, maxAttempts);
}
```

Moving to a shared object: a parcel's insurance percentage becomes its service level's percentage.
During the transition the parcel still stores the value but asserts it matches:

```csharp
using System.Diagnostics;

public class ServiceLevel
{
    public ServiceLevel(string name, decimal insurancePercent)
    {
        Name = name;
        InsurancePercent = insurancePercent;
    }

    public string Name { get; }
    public decimal InsurancePercent { get; }
}

public class Parcel
{
    private readonly ServiceLevel _level;
    private readonly decimal _insurancePercent;

    public Parcel(string trackingCode, ServiceLevel level, decimal insurancePercent)
    {
        Debug.Assert(insurancePercent == level.InsurancePercent);
        TrackingCode = trackingCode;
        _level = level;
        _insurancePercent = insurancePercent;
    }

    public string TrackingCode { get; }
    public decimal InsurancePercent => _insurancePercent;
}
```

Once the assertion has held, drop the constructor parameter and the field and return
`_level.InsurancePercent`.

## C# notes
- A field that is persisted or serialized keeps its stored name only if the mapping is updated
  too (column, JSON property name, serializer attributes). Moving it to another class changes
  the stored shape, so migrate or map the data.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- For the shared-object case, query the stored data for rows whose value differs from the
  target's, or run with the assertion enabled (or a log line in its place) and confirm that
  nothing fires before removing the old field.
