# Replace Command with Function

Fowler (2018), ch. 11, p. 344. Formerly / aka: —. Inverse: Replace Function with Command
([replace-function-with-command.md](replace-function-with-command.md)).

## When to use
Convert when the class only takes its inputs, runs one computation and returns the result,
and the logic is simple enough to read as one function (or a few small ones). Do not convert
when callers rely on undo, queuing, several entry points or incremental setup.

## Mechanics
1. Extract a function that wraps creating the command and calling its execute method ([extract-function.md](extract-function.md)). This will be the replacement function, and callers now go through it.
2. For each helper the execute method calls, inline it into the execute method ([inline-function.md](inline-function.md)). If the helper returns a value, first extract that call into a variable ([extract-variable.md](extract-variable.md)), then inline.
3. Change the execute method's signature so it takes every constructor parameter ([change-function-declaration.md](change-function-declaration.md)). Update the wrapper function to pass them.
4. In the execute method, replace each use of a field with the matching parameter, one field at a time, testing after each. Also remove the field's assignment in the constructor, so a missed use fails loudly. The constructor and its fields are now dead, but they stay until step 7 deletes the class.
5. Inline the constructor call and the execute call into the wrapper function, so it holds the logic directly.
6. Test.
7. Delete the now unused command class ([remove-dead-code.md](remove-dead-code.md)).

## Example
Before:

```csharp
public class InvoiceTotalCalculator
{
    private readonly Customer _customer;
    private readonly int _units;
    private readonly ShippingPolicy _shipping;

    public InvoiceTotalCalculator(Customer customer, int units, ShippingPolicy shipping)
    {
        _customer = customer;
        _units = units;
        _shipping = shipping;
    }

    private decimal Subtotal() => _customer.UnitPrice * _units;

    public decimal Execute()
    {
        return Subtotal() + _shipping.Fee;
    }
}

// caller
decimal total = new InvoiceTotalCalculator(customer, units, shipping).Execute();
```

Step 1, wrap the call:

```csharp
public static decimal InvoiceTotal(Customer customer, int units, ShippingPolicy shipping)
    => new InvoiceTotalCalculator(customer, units, shipping).Execute();
```

Steps 2 to 4, `Subtotal` inlined, parameters moved to `Execute`, fields no longer used. The
static wrapper from step 1 lives in the same class or a static helper class, and now calls
`new InvoiceTotalCalculator(customer, units, shipping).Execute(customer, units, shipping)`.
The constructor still takes its three arguments, but it no longer stores them; it goes away
with the class in step 7:

```csharp
public decimal Execute(Customer customer, int units, ShippingPolicy shipping)
{
    var subtotal = customer.UnitPrice * units;
    return subtotal + shipping.Fee;
}
```

Steps 5 to 7, logic inlined into the wrapper, class deleted:

```csharp
public static decimal InvoiceTotal(Customer customer, int units, ShippingPolicy shipping)
{
    var subtotal = customer.UnitPrice * units;
    return subtotal + shipping.Fee;
}

// caller
decimal total = InvoiceTotal(customer, units, shipping);
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
