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
  [encapsulate-record.md](encapsulate-record.md) first.
- Usually part of a bigger change. Callers can move to the new owner afterwards, or the move
  may need to wait until usage is reshaped.

## Mechanics
1. Make sure the source field is encapsulated: all reads and writes go through accessors
   ([encapsulate-variable.md](encapsulate-variable.md)). Test.
2. Add the field, with accessors, to the target class. Build and run static checks.
3. Make sure the source can get hold of the target: through something it already has, through a
   new lookup method, or, as a last resort, through a new field (perhaps temporary).
4. Point the source accessors at the target's field. Test.
   - If several source objects share one target, first make the setter write both the old and
     the new field and add an assertion ([introduce-assertion.md](introduce-assertion.md))
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
Before: the late fee lives on the member, though it is really a term of the membership.

```csharp
public class Member
{
    private readonly Membership _membership;
    private decimal _lateFeePerDay;

    public Member(string name, decimal lateFeePerDay)
    {
        Name = name;
        _lateFeePerDay = lateFeePerDay;
        _membership = new Membership(DateTime.UtcNow.Date);
    }

    public string Name { get; }
    public decimal LateFeePerDay => _lateFeePerDay;

    public void Upgrade() => _lateFeePerDay += 0.25m;

    public decimal FeeFor(int daysLate) => daysLate * _lateFeePerDay;
}

public class Membership
{
    public Membership(DateTime joinedOn) => JoinedOn = joinedOn;
    public DateTime JoinedOn { get; }
}
```

Step 1, encapsulate the field. The constructor now goes through the setter:

```csharp
public Member(string name, decimal lateFeePerDay)
{
    Name = name;
    SetLateFee(lateFeePerDay);
    _membership = new Membership(DateTime.UtcNow.Date);
}

public decimal LateFeePerDay => _lateFeePerDay;
private void SetLateFee(decimal value) => _lateFeePerDay = value;

public void Upgrade() => SetLateFee(LateFeePerDay + 0.25m);
public decimal FeeFor(int daysLate) => daysLate * LateFeePerDay;
```

Step 2, add the field and accessors to `Membership`. The new parameter is optional for now, so
`Member` still compiles unchanged:

```csharp
public class Membership
{
    public Membership(DateTime joinedOn, decimal lateFeePerDay = 0m)
    {
        JoinedOn = joinedOn;
        LateFeePerDay = lateFeePerDay;
    }

    public DateTime JoinedOn { get; }
    public decimal LateFeePerDay { get; set; }
}
```

Step 4, first attempt: redirect the accessors while the constructor is still in its old order.

```csharp
public decimal LateFeePerDay => _membership.LateFeePerDay;
private void SetLateFee(decimal value) => _membership.LateFeePerDay = value;
// the constructor calls SetLateFee before _membership is assigned:
// NullReferenceException on construction
```

Revert the accessors and reorder the constructor so `_membership` exists before the setter
runs. Test:

```csharp
public Member(string name, decimal lateFeePerDay)
{
    Name = name;
    _membership = new Membership(DateTime.UtcNow.Date);
    SetLateFee(lateFeePerDay);
}
```

Redirect the accessors again. Test:

```csharp
public decimal LateFeePerDay => _membership.LateFeePerDay;
private void SetLateFee(decimal value) => _membership.LateFeePerDay = value;
```

Step 5: delete `_lateFeePerDay`. Test.

Optional cleanup, as a separate step: the constructor can hand the initial fee straight to
`Membership`, and the temporary default on the new parameter goes away. `SetLateFee` stays for
`Upgrade`:

```csharp
public Member(string name, decimal lateFeePerDay)
{
    Name = name;
    _membership = new Membership(DateTime.UtcNow.Date, lateFeePerDay);
}
```

Moving to a shared object: a product's tax percentage becomes its category's percentage.
During the transition the product still stores the value but asserts it matches:

```csharp
using System.Diagnostics;

public class Product
{
    private readonly Category _category;
    private readonly decimal _vatPercent;

    public Product(string sku, Category category, decimal vatPercent)
    {
        Debug.Assert(vatPercent == category.VatPercent);
        Sku = sku;
        _category = category;
        _vatPercent = vatPercent;
    }

    public string Sku { get; }
    public decimal VatPercent => _vatPercent;
}
```

Once the assertion has held, drop the constructor parameter and the field and return
`_category.VatPercent`.

## C# notes
- A field that is persisted or serialized keeps its stored name only if the mapping is updated
  too (column, JSON property name, serializer attributes). Moving it to another class changes
  the stored shape, so migrate or map the data.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- For the shared-object case, query the stored data for rows whose value differs from the
  target's, or run with the assertion enabled (or a log line in its place) and confirm that
  nothing fires before removing the old field.
