# Replace Type Code with Subclasses

Fowler (2018), ch. 12, p. 362. Formerly / aka: subsumes Replace Type Code with State/Strategy and Extract Subclass. Inverse: Remove Subclass ([remove-subclass.md](remove-subclass.md)).

## When to use
Smells: Primitive Obsession, Large Class.

- Several methods branch on the same type code. Subclasses let you finish with Replace Conditional with Polymorphism ([replace-conditional-with-polymorphism.md](replace-conditional-with-polymorphism.md)).
- Some fields or methods only apply to certain values of the code. A subclass holds them explicitly, instead of relying on checks that the code has the right value ([push-down-field.md](push-down-field.md), [push-down-method.md](push-down-method.md)).

Choose where the subclasses go:

- **Direct inheritance:** subclass the class itself (`Engineer : Employee`). Simplest, but it does not work if that class already needs subclasses for another axis, or if an object must change its kind during its life.
- **Indirect inheritance:** first apply Replace Primitive with Object ([replace-primitive-with-object.md](replace-primitive-with-object.md)) to the code, producing a small type class, then subclass that class. The owner holds a reference to it, so the kind can change at runtime. This is what the old State/Strategy refactoring amounts to.

Do not use it when the code is only data that no behavior depends on; a plain enum is enough there.

## Mechanics
1. Self-encapsulate the type code: all reads go through one getter.
2. Pick one code value. Create a subclass for it whose getter returns that literal value.
3. Add selection logic that maps the incoming code to the subclass. With direct inheritance, make construction a factory ([replace-constructor-with-factory-function.md](replace-constructor-with-factory-function.md)) and put the selection there. With indirect inheritance, the selection can stay in the owner's constructor or setter. While some codes still lack a subclass, keep the base class concrete and let the selection fall back to it.
4. Build and test. To be sure the tests exercise the new subclass, change its returned value for a moment and check that a test fails, then restore it.
5. Repeat steps 2 to 4 for each remaining code value, testing after each. The base class stays concrete until the last one is done.
6. Once every value has a subclass, remove the stored type code field and the base getter. Make unknown codes fail in the selection logic (default branch throws), then drop any separate validation. Build and test.
7. Remove the now unused code parameter from the constructor ([change-function-declaration.md](change-function-declaration.md)).
8. For each method that uses the type getter, push it down into the subclasses and replace the conditional with polymorphism. When nothing reads the getter any more, delete it ([remove-dead-code.md](remove-dead-code.md)). Test after each method.

With indirect inheritance, a mutable kind means a setter that re-runs the selection and swaps the type object. With it, the empty type base class may stay: it documents the family and is a natural home for logic shared by the kinds.

## Example
Before: an account whose behavior depends on a string kind.

```csharp
using System;

public class Account
{
    private readonly string _owner;
    private readonly string _kind;

    public Account(string owner, string kind)
    {
        if (kind != "checking" && kind != "savings")
            throw new ArgumentException($"Unknown account kind: {kind}");
        _owner = owner;
        _kind = kind;
    }

    public string Kind => _kind;

    public decimal MonthlyFee() => _kind == "checking" ? 5m : 0m;

    public override string ToString() => $"{_owner} ({_kind})";
}
```

After steps 1 to 8 (`MonthlyFee` pushed down and made polymorphic; `Kind` kept only for `ToString`):

```csharp
using System;

public abstract class Account
{
    private readonly string _owner;

    protected Account(string owner) => _owner = owner;

    public static Account Create(string owner, string kind) => kind switch
    {
        "checking" => new CheckingAccount(owner),
        "savings" => new SavingsAccount(owner),
        _ => throw new ArgumentException($"Unknown account kind: {kind}")
    };

    public abstract string Kind { get; }

    public abstract decimal MonthlyFee();

    public override string ToString() => $"{_owner} ({Kind})";
}

public class CheckingAccount : Account
{
    public CheckingAccount(string owner) : base(owner) { }
    public override string Kind => "checking";
    public override decimal MonthlyFee() => 5m;
}

public class SavingsAccount : Account
{
    public SavingsAccount(string owner) : base(owner) { }
    public override string Kind => "savings";
    public override decimal MonthlyFee() => 0m;
}
```

Behavior is unchanged: callers now use `Account.Create(owner, kind)`, and `MonthlyFee` no longer branches on the code. `Kind` stays only because `ToString` and possibly outside callers read it; delete it (step 8) once nothing does.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Every code value that existed before maps to a subclass, and unknown values still fail the way they did.
