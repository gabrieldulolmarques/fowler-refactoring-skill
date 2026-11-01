# Remove Setting Method

Fowler (2018), ch. 11, p. 331. Formerly / aka: —. Inverse: —.

## When to use
Smells: Mutable Data, Data Class.

- A setter says "this value may change". If a value must stay fixed for the lifetime of the object (an id, a creation date, an account number), the setter tells callers something false and lets them break the rule.
- Typical case 1: the constructor is the only code that still calls the setter, because the class routes even its own initialization through the member.
- Typical case 2: objects are assembled right after construction by a run of assignments, and nothing changes those values afterwards.
- Do not use it when callers really update a shared, long-lived object through the setter and cannot be rewritten to create a new object instead. In that case the value is genuinely mutable: keep the setter.

## Mechanics
1. If the constructor does not receive the value yet, add it as a parameter (see [change-function-declaration.md](change-function-declaration.md)) and call the setter with it from inside the constructor (`Id = id;`). When removing several setters, add all their values at once.
2. Find every call to the setter outside the constructor. Replace each with the value passed to the constructor at the creation site. Compile and test after each one.
3. If a call cannot be replaced by creating a new object (it updates an object that other code shares), stop and undo: the value is not really fixed.
4. Apply Inline Function to the setter (see [inline-function.md](inline-function.md)), then delete it and make the member read-only if the language allows.
5. Compile and run the tests.

## Example
Before: `Id` is assigned once at creation, but anyone can reassign it later.

```csharp
public class Customer
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
}

public static class Program
{
    public static void Main()
    {
        var customer = new Customer();
        customer.Name = "Ada";
        customer.Id = "C-1001";
        System.Console.WriteLine($"{customer.Id} {customer.Name}");
    }
}
```

After: the id arrives through the constructor and has no setter. `Name` may still change, so it keeps its setter.

```csharp
public class Customer
{
    public Customer(string id)
    {
        Id = id;
    }

    public string Id { get; }
    public string Name { get; set; } = "";
}

public static class Program
{
    public static void Main()
    {
        var customer = new Customer("C-1001");
        customer.Name = "Ada";
        System.Console.WriteLine($"{customer.Id} {customer.Name}");
    }
}
```

## C# notes
- Use `{ get; }` for a value set only in the constructor, or `{ get; init; }` when callers may still set it in an object initializer (`new Customer { Id = "C-1001" }`) but not afterwards.
- `init` is a lighter first step when many creation sites use initializers: it blocks later assignment without forcing a constructor change at once. Prefer `{ get; }` plus a constructor when the value is mandatory, so the compiler rejects objects built without it.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
