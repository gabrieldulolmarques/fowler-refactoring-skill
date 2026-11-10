# Remove Subclass

Fowler (2018), ch. 12, p. 369. Formerly / aka: formerly Replace Subclass with Fields.
Inverse: Replace Type Code with Subclasses ([replace-type-code-with-subclasses.md](replace-type-code-with-subclasses.md)).

## When to use
Smell: none specific in the book (related: Lazy Element, Speculative Generality).

- A subclass was added for variation that never grew: it overrides a member or two to return a
  constant, and nothing else depends on its type. The class costs readers attention and
  gives nothing back.
- The behavior that justified the subclass moved elsewhere or was deleted, leaving a stump.
- Usually applied to a whole group of sibling subclasses. Prepare all of them first
  (factory, type tests), then fold them in one at a time.
- Before deleting, look at the clients for behavior that depends on the subclass. If it would
  belong inside the subclass, the subclass may still be worth keeping.
- Do not use it when the subclasses carry real polymorphic behavior or different data
  structure. That variation is what inheritance is for.

## Mechanics
1. Encapsulate construction: apply Replace Constructor with Factory Function
   ([replace-constructor-with-factory-function.md](replace-constructor-with-factory-function.md)) to each subclass constructor. If the
   callers pick the subclass from a data value (a code, a record field), move that selection
   logic into the factory. Compile and test.
2. Find every place that tests the type of an object against a subclass (`is`, `as`,
   `GetType()`). Extract each test into a function ([extract-function.md](extract-function.md)), move it onto
   the superclass ([move-function.md](move-function.md)), and make callers use it. Compile and test after
   each change.
3. Add a field to the superclass that represents what the subclasses differ in, and set it in
   the constructor to the default case. Expose it through the same member the subclasses
   override.
4. Take one subclass. Change the factory so it returns the superclass with the field set to
   that subclass's value, and change the moved type tests to read the field. Compile and test.
5. Delete that subclass. Compile and test.
6. Repeat steps 4 and 5 for each remaining subclass.
7. Optionally make the default case symmetrical with the others (set the field explicitly in
   the factory) if that adds no complexity.

## Example
Before: two subclasses that only return a constant, created from stored records.

```csharp
public record AccountRecord(string Owner, string Kind);

public class Account
{
    public Account(string owner) => Owner = owner;

    public string Owner { get; }
    public virtual string Kind => "basic";
}

public class SavingsAccount : Account
{
    public SavingsAccount(string owner) : base(owner) { }
    public override string Kind => "savings";
}

public class CheckingAccount : Account
{
    public CheckingAccount(string owner) : base(owner) { }
    public override string Kind => "checking";
}

// client
var accounts = new List<Account>();
foreach (var record in records)
{
    switch (record.Kind)
    {
        case "S": accounts.Add(new SavingsAccount(record.Owner)); break;
        case "C": accounts.Add(new CheckingAccount(record.Owner)); break;
        default: accounts.Add(new Account(record.Owner)); break;
    }
}
int savingsCount = accounts.Count(a => a is SavingsAccount);
```

Steps 1 and 2: encapsulate creation in a factory and the type test in a member of the
superclass.

```csharp
public class Account
{
    // ...
    public bool IsSavings => this is SavingsAccount;

    public static Account Create(AccountRecord record) => record.Kind switch
    {
        "S" => new SavingsAccount(record.Owner),
        "C" => new CheckingAccount(record.Owner),
        _ => new Account(record.Owner),
    };
}

// client
var accounts = records.Select(Account.Create).ToList();
int savingsCount = accounts.Count(a => a.IsSavings);
```

Steps 3 to 7: add the field, fold each subclass into the factory, then delete the subclasses.

```csharp
public class Account
{
    private Account(string owner, string kind)
    {
        Owner = owner;
        Kind = kind;
    }

    public string Owner { get; }
    public string Kind { get; }
    public bool IsSavings => Kind == "savings";

    public static Account Create(AccountRecord record) => record.Kind switch
    {
        "S" => new Account(record.Owner, "savings"),
        "C" => new Account(record.Owner, "checking"),
        _ => new Account(record.Owner, "basic"),
    };
}
```

Behavior is unchanged: `Kind` returns the same values, and the client code only changed in the
first two steps, before any subclass disappeared.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
