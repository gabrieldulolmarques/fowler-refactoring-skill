# Pull Up Constructor Body

Fowler (2018), ch. 12, p. 355. Formerly / aka: —. Inverse: —.

## When to use
Smell: none specific in the book (related: Duplicated Code). Two or more subclasses assign the same fields, or
run the same setup, at the start of their constructors. A constructor cannot be treated
like a regular method: the superclass part must be initialized first and the subclass
constructor calls it explicitly, so the usual "extract, then Pull Up Method" route does not
work directly for the shared initialization. Pull the code into a superclass constructor and
pass what it needs through the call.

If part of the shared code needs values that only the subclass has set by then, it cannot be
hoisted into the base constructor. Handle that part separately, as in step 4. If the whole
thing gets messy, consider Replace Constructor with Factory Function
([replace-constructor-with-factory-function.md](replace-constructor-with-factory-function.md)).

## Mechanics
1. Make sure the superclass has a constructor (create one if needed) and that every subclass
   constructor calls it.
2. In each subclass constructor, use Slide Statements ([slide-statements.md](slide-statements.md)) to reorder
   the shared assignments so they sit immediately after the base call. Test.
3. Move the shared statements into the superclass constructor, delete them from each subclass,
   add a superclass constructor parameter for every value the moved code uses, and pass those
   values from each subclass call. These edits only compile together, so test once at the end.
4. If some common code cannot go at the start (it needs state the subclass sets first),
   Extract Function on it ([extract-function.md](extract-function.md)), then Pull Up Method
   ([pull-up-method.md](pull-up-method.md)), and call it at the end of each subclass constructor.
   If the copies differ only in values, turn those values into parameters of the extracted
   method before pulling it up (Change Function Declaration,
   [change-function-declaration.md](change-function-declaration.md)). Test.

## Example
Before: two kinds of document share a customer and a creation date, each assigned in its own
constructor.

```csharp
using System;

public abstract class Document
{
}

public class Invoice : Document
{
    private readonly string _customer;
    private readonly DateTime _createdOn;
    private readonly decimal _amount;

    public Invoice(string customer, DateTime createdOn, decimal amount)
    {
        _amount = amount;
        _customer = customer;
        _createdOn = createdOn;
    }
}

public class Quote : Document
{
    private readonly string _customer;
    private readonly DateTime _createdOn;
    private readonly int _validDays;

    public Quote(string customer, DateTime createdOn, int validDays)
    {
        _customer = customer;
        _createdOn = createdOn;
        _validDays = validDays;
    }
}
```

After: the shared fields and their assignments live in `Document`. `Invoice` first slid its
assignments next to the base call, then both were moved up.

```csharp
using System;

public abstract class Document
{
    protected readonly string Customer;
    protected readonly DateTime CreatedOn;

    protected Document(string customer, DateTime createdOn)
    {
        Customer = customer;
        CreatedOn = createdOn;
    }
}

public class Invoice : Document
{
    private readonly decimal _amount;

    public Invoice(string customer, DateTime createdOn, decimal amount)
        : base(customer, createdOn)
    {
        _amount = amount;
    }
}

public class Quote : Document
{
    private readonly int _validDays;

    public Quote(string customer, DateTime createdOn, int validDays)
        : base(customer, createdOn)
    {
        _validDays = validDays;
    }
}
```

Common behavior that must run after subclass data is set is extracted into a method, pulled
up, and called as the last line of each subclass constructor. Before, each subclass ended its
constructor with a similar label-building statement:

```csharp
using System;

public abstract class Document
{
    protected readonly string Customer;

    protected Document(string customer)
    {
        Customer = customer;
    }
}

public class Invoice : Document
{
    private readonly decimal _amount;
    public string Label { get; private set; }

    public Invoice(string customer, decimal amount) : base(customer)
    {
        _amount = amount;
        Label = "INV " + Customer + " " + _amount;
    }
}

public class Quote : Document
{
    private readonly int _validDays;
    public string Label { get; private set; }

    public Quote(string customer, int validDays) : base(customer)
    {
        _validDays = validDays;
        Label = "QUO " + Customer + " " + _validDays;
    }
}
```

After: the label-building step is a method in `Document` that reads a subclass-supplied
prefix and detail, and each constructor calls it once its own field is set.

```csharp
using System;

public abstract class Document
{
    protected readonly string Customer;
    public string Label { get; private set; }

    protected Document(string customer)
    {
        Customer = customer;
    }

    protected void Finish(string prefix, object detail)
    {
        Label = prefix + " " + Customer + " " + detail;
    }
}

public class Invoice : Document
{
    private readonly decimal _amount;

    public Invoice(string customer, decimal amount) : base(customer)
    {
        _amount = amount;
        Finish("INV", _amount);
    }
}

public class Quote : Document
{
    private readonly int _validDays;

    public Quote(string customer, int validDays) : base(customer)
    {
        _validDays = validDays;
        Finish("QUO", _validDays);
    }
}
```

## C# notes
- The superclass constructor is reached with `: base(...)` constructor chaining. The base
  constructor runs before the subclass body and before the subclass's own field assignments in
  the constructor body (field initializers of the subclass run even earlier).
- Do not call a `virtual` member from the base constructor to finish construction: it can run
  on a subclass whose fields are not yet set. That is why the late common code goes to a
  method each subclass calls at the end of its own constructor.
- Pulled-up fields are usually `private readonly` plus a `protected`/`public` property, or
  `protected readonly`, depending on who needs them.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The shared assignments no longer appear in any subclass constructor, each subclass passes
  the values through `: base(...)`, and the order of observable side effects during
  construction is unchanged.
