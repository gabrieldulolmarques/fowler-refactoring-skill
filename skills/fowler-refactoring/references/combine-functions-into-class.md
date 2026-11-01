# Combine Functions into Class

Fowler (2018), ch. 6, p. 144. Formerly / aka: —. Inverse: —. Alternative:
Combine Functions into Transform ([combine-functions-into-transform.md](combine-functions-into-transform.md)).

## When to use
Smells: Long Parameter List, Mutable Data, Shotgun Surgery.

- Several functions receive the same record (or the same few values) and compute things
  from it. A class makes that shared environment explicit and lets the calls drop the
  repeated arguments.
- The same derived value is calculated inline in several clients, or a helper exists but
  nobody finds it because it is a free function far from the data.
- The source data can change after it is read. Methods compute derived values on demand,
  so they stay consistent with the data. A transform that copies derived values into a new
  record goes stale when the source changes; prefer the class in that case.
- Prefer a class over a function nested in another function: it is easier to test, and it
  is needed when more than one of the functions must be visible to other code.

Do not use it for a single function (just move it) or when the functions share no data.

## Mechanics
1. Make sure the shared data is one structure. If it is a loose record, dictionary or tuple,
   wrap it in a class ([encapsulate-record.md](encapsulate-record.md)). If it is only a group of separate
   arguments, first bundle them ([introduce-parameter-object.md](introduce-parameter-object.md)).
2. Build the new instance where the data is first obtained, so clients hold the object
   instead of the raw data.
3. Move one function at a time into the class ([move-function.md](move-function.md)). Parameters that are
   now members of the class disappear from the signature. Update the callers and test.
4. Rename each moved function if its name repeated the data type or reads badly as a
   method or property.
5. Replace each duplicated inline calculation in the clients with a call to the new method.
6. Look for logic in the clients that works on the data. Extract it
   ([extract-function.md](extract-function.md)), then move it into the class too. Test after each one.

## Example
Before: free functions that all take the same mutable record.

```csharp
public class OrderData
{
    public string Customer { get; set; } = "";
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public int Year { get; set; }
}

public static class OrderPricing
{
    public static decimal Subtotal(OrderData order) =>
        order.Quantity * order.UnitPrice;

    public static decimal FreeAllowance(int year) => year >= 2020 ? 100m : 50m;

    public static decimal Billable(OrderData order) =>
        Math.Max(0, Subtotal(order) - FreeAllowance(order.Year));
}

// clients
var data = LoadOrder();
decimal subtotal = data.Quantity * data.UnitPrice;         // duplicated formula
decimal billable = OrderPricing.Billable(data);
```

After: the record becomes the state of a class and the functions become members.

```csharp
public class Order
{
    private readonly OrderData _data;

    public Order(OrderData data) => _data = data;

    public string Customer => _data.Customer;
    public int Quantity => _data.Quantity;
    public decimal UnitPrice => _data.UnitPrice;
    public int Year => _data.Year;

    public decimal Subtotal => Quantity * UnitPrice;

    public decimal FreeAllowance => Year >= 2020 ? 100m : 50m;

    public decimal Billable => Math.Max(0, Subtotal - FreeAllowance);
}

// clients
var order = new Order(LoadOrder());
decimal subtotal = order.Subtotal;
decimal billable = order.Billable;
```

Every derived value is computed on demand, so if `Quantity` changes later, `Subtotal` and
`Billable` still agree with it. Callers cannot tell a stored value from a derived one.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
