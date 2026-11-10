# Encapsulate Record

Fowler (2018), ch. 7, p. 162. Formerly / aka: Replace Record with Data Class.
Inverse: —.

## When to use
Smells: Data Class.

- Mutable data lives in a bare record and many places read and write its fields directly.
  A class can serve a derived value through the same property as a stored one, and can keep
  a deprecated alias while callers migrate to a new name.
- The record is a free-form map with implicit fields: to know whether it holds
  `price`/`currency` or just `amount`, you have to read every place that builds or uses it.
  This costs more as the scope grows. A class makes the fields explicit.
- The data is a nested structure of lists and maps, often from JSON or XML. It can be
  encapsulated too, which protects you from format changes and from updates that are hard to
  trace.

Not needed for an immutable value used in a small scope: there, adding or copying a field
is cheap and a plain record is fine.

## Mechanics
1. Apply Encapsulate Variable ([encapsulate-variable.md](../first-set/encapsulate-variable.md)) to the variable that holds the
   record. Give the getter a temporary, grep-friendly name such as `GetRawContact`; it is
   removed in step 5.
2. Introduce a small class that holds the record, and store an instance of it in the variable.
   Give it a property that exposes the underlying record (a `RawData` property in the C#
   example) and point the encapsulating functions at that property. Compile and test.
3. Add new functions that return the class instance instead of the raw record.
4. Move the callers one at a time from the raw-record function to the object-returning
   function. For each use, call an accessor on the object, creating it if it does not exist
   yet (a setter for a write, a getter for a read; for a deep access, first apply Extract
   Function and Move Function so the digging happens inside the class). Compile and test
   after each caller.
   - For a nested record, convert the writers first: gathering all updates in one place is
     the most valuable part. Readers can then get a copy or a read-only view.
   - To check that no writer was missed, temporarily make the raw accessor return a deep copy
     (or a frozen copy): a test fails if some code still updates the original.
5. When no caller uses them any more, delete the raw accessor and the searchable functions.
   Compile and test.
6. Optionally, fold the wrapped record into individual fields of the class. This breaks the
   link to the input data, so a stray reference elsewhere cannot bypass the class. If you
   keep the record inside, copy it when you assign it.
7. If a field is itself a structure, apply Encapsulate Record or Encapsulate Collection
   ([encapsulate-collection.md](encapsulate-collection.md)) to it, recursively, when the control is worth the effort.

For readers of a large nested structure there are three options: extract each read into a
method on the class (an explicit API, but possibly a lot of special cases); hand out a copy of
the data (simple, but costs time and surprises callers who expect to modify the original, so
measure first); or recurse into smaller classes (most control, most work). A mix is fine.

## Example
Before: a shared contact record kept as a dictionary.

```csharp
using System.Collections.Generic;

public static class Billing
{
    public static Dictionary<string, string> Contact =
        new() { ["name"] = "Ana Souza", ["email"] = "ana@example.com" };
}

public static class InvoiceHeader
{
    public static string Render() => $"Bill to: {Billing.Contact["name"]}";
}

public static class ContactForm
{
    public static void ChangeEmail(string email) => Billing.Contact["email"] = email;
}
```

Intermediate state (steps 1 to 3): wrapper class, raw accessor, object accessor. Step 1 also
makes `InvoiceHeader` and `ContactForm` call the raw accessor.

```csharp
using System.Collections.Generic;

public class BillingContact
{
    private readonly Dictionary<string, string> _data;
    public BillingContact(Dictionary<string, string> data) => _data = data;
    public Dictionary<string, string> RawData => _data;
}

public static class Billing
{
    private static BillingContact _contact = new(
        new() { ["name"] = "Ana Souza", ["email"] = "ana@example.com" });

    public static Dictionary<string, string> GetRawContact() => _contact.RawData;
    public static BillingContact GetContact() => _contact;
}

public static class InvoiceHeader
{
    public static string Render() => $"Bill to: {Billing.GetRawContact()["name"]}";
}

public static class ContactForm
{
    public static void ChangeEmail(string email) => Billing.GetRawContact()["email"] = email;
}
```

After (steps 4 to 6): callers use the object, the raw accessors are gone, the dictionary is
folded into properties.

```csharp
using System.Collections.Generic;

public class BillingContact
{
    public BillingContact(Dictionary<string, string> data)
    {
        Name = data["name"];
        Email = data["email"];
    }

    public string Name { get; set; }
    public string Email { get; set; }
}

public static class Billing
{
    private static BillingContact _contact = new(
        new() { ["name"] = "Ana Souza", ["email"] = "ana@example.com" });

    public static BillingContact GetContact() => _contact;
}

public static class InvoiceHeader
{
    public static string Render() => $"Bill to: {Billing.GetContact().Name}";
}

public static class ContactForm
{
    public static void ChangeEmail(string email) => Billing.GetContact().Email = email;
}
```

## C# notes
- Dictionary, tuple, anonymous or `dynamic` data becomes a class or `record` with properties.
  Anonymous types cannot cross method boundaries as a typed value, which is a good reason to
  convert them.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- After step 5, grep for the raw accessor names and for direct indexing of the old variable.
  Expect zero hits.
