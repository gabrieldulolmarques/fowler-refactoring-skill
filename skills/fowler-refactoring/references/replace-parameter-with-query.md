# Replace Parameter with Query

Fowler (2018), ch. 11, p. 324. Formerly / aka: formerly Replace Parameter with Method. Inverse: Replace Query with Parameter ([replace-query-with-parameter.md](replace-query-with-parameter.md)).

## When to use
Smell: Long Parameter List. A caller passes a value that the function could obtain just as easily itself, usually from the receiver or from another parameter. The caller does extra work and the parameter list repeats information it already holds. The safest case is a parameter that is computed purely from another parameter in the same list: passing both adds nothing.

Do not use it when the removal gives the function an unwanted dependency: a call to something it should not know about, or access to something you plan to move out later. Also avoid it when the function is deterministic (same inputs, same result) and the query would read mutable global state, because that loses the property and makes the function harder to test.

## Mechanics
1. If the value is computed by an expression or several statements in the caller, extract that calculation into its own function or property ([extract-function.md](extract-function.md)), so there is a single query to call.
2. Inside the function body, replace each use of the parameter with a call to that query. Compile and test after each replacement.
3. Remove the now unused parameter from the declaration and from every caller ([change-function-declaration.md](change-function-declaration.md)). Compile and test.

## Example
Before:

```csharp
public class Customer
{
    public string Country { get; }

    public Customer(string country) => Country = country;
}

public class Account
{
    private readonly decimal _balance;
    private readonly Customer _customer;

    public Account(decimal balance, Customer customer)
    {
        _balance = balance;
        _customer = customer;
    }

    public decimal MonthlyFee()
    {
        decimal baseFee = _balance < 1000m ? 12m : 0m;
        bool abroad = _customer.Country != "BR";
        return AddSurcharge(baseFee, abroad);
    }

    private decimal AddSurcharge(decimal baseFee, bool abroad)
    {
        return abroad ? baseFee + 25m : baseFee;
    }
}
```

Step 1: turn the local `abroad` into a query ([replace-temp-with-query.md](replace-temp-with-query.md)), which gives the parameter a single source:

```csharp
    public decimal MonthlyFee()
    {
        decimal baseFee = _balance < 1000m ? 12m : 0m;
        return AddSurcharge(baseFee, IsAbroad);
    }

    private bool IsAbroad => _customer.Country != "BR";
```

Step 2: inside `AddSurcharge`, use `IsAbroad` instead of the parameter. Step 3: drop the parameter.

After:

```csharp
    public decimal MonthlyFee()
    {
        decimal baseFee = _balance < 1000m ? 12m : 0m;
        return AddSurcharge(baseFee);
    }

    private bool IsAbroad => _customer.Country != "BR";

    private decimal AddSurcharge(decimal baseFee)
    {
        return IsAbroad ? baseFee + 25m : baseFee;
    }
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
