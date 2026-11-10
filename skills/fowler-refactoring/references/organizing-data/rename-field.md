# Rename Field

Fowler (2018), ch. 9, p. 244. Formerly / aka: —. Inverse: —.

## When to use
Smell: Mysterious Name. Data structures carry most of a program's meaning, so their field
names deserve the same care as function names. As you learn the domain, put the better
understanding into the name. The idea applies to bare records and to classes: the property
(or getter and setter pair) that callers see is the field, so rename it with the same care.

The cost depends on reach. A field used in one small scope can be renamed in one pass. A field
read and written all over a code base needs the gradual route below.

## Mechanics
1. If the record is only used in a small scope (one function, one class), rename every access
   to the field in one pass, run the tests, and stop here.
2. Otherwise, make sure the data is behind accessors. If it is a bare record that callers touch
   directly, apply Encapsulate Record first ([encapsulate-record.md](../encapsulation/encapsulate-record.md)).
3. Rename the private backing field inside the class and fix the internal members that use it.
   Build and test. If the constructor copied the input straight into the backing field, split
   them first so the internal name can change on its own.
4. If a constructor, factory or initializer takes a record or options object keyed by the old
   field name, let it accept the new name too and prefer the new one when both appear. Move the
   callers over one at a time, testing as you go, then drop the old name. Use Change Function
   Declaration ([change-function-declaration.md](../first-set/change-function-declaration.md)) for this step.
   With plain positional parameters there is nothing to accept twice: renaming the parameter
   is enough, and only named-argument callers notice.
5. Rename the accessors (getter and setter) to the new name, again with Change Function
   Declaration, so callers move over in small steps.
6. Build and test. Search for string-based uses (reflection, configuration, serialized
   payloads, query strings) that the compiler cannot see.

If the data is immutable, you can skip encapsulation: add the new name holding the same value,
move the users over gradually, then delete the old name. Never keep two copies of mutable data.

If the tests break during a one-pass rename, undo it and use the gradual route.

## Example
Before: `Customer` exposes a public field named `Tag` that actually holds the billing
reference, and many callers use it.

```csharp
public class Customer
{
    public string Tag;       // actually the billing reference
    public string Country;
}

// caller
var customer = new Customer { Tag = "INV-2041", Country = "BR" };
Console.WriteLine(customer.Tag);
```

Step 1, encapsulate and give the backing field its own name. The object initializer in the
caller keeps compiling because it goes through the property setters:

```csharp
public class Customer
{
    private string _billingReference;
    private string _country;

    public string Tag
    {
        get => _billingReference;
        set => _billingReference = value;
    }

    public string Country
    {
        get => _country;
        set => _country = value;
    }
}
```

Step 2, rename the property and update the callers. This class has no constructor, so
mechanics step 4 has nothing to do here:

```csharp
public class Customer
{
    private string _billingReference;
    private string _country;

    public string BillingReference
    {
        get => _billingReference;
        set => _billingReference = value;
    }

    public string Country
    {
        get => _country;
        set => _country = value;
    }
}

// caller
var customer = new Customer { BillingReference = "INV-2041", Country = "BR" };
Console.WriteLine(customer.BillingReference);
```

Behavior is unchanged; only the name moved.

## C# notes
- A serialized or persisted field keeps its wire name only with a mapping attribute (for
  example `[JsonPropertyName("oldName")]`) or a migration. Renaming the property without one
  changes the JSON, the column or the stored data.
- Turning a public field into a property changes the member itself: reflection and binary
  consumers break, and serializers may treat the two differently.
- The compiler finds direct usages, not reflection, data binding by string or configuration keys.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
