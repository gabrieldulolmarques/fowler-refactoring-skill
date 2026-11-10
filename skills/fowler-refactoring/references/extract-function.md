# Extract Function

Fowler (2018), ch. 6, p. 106. Formerly / aka: Extract Method. Inverse: Inline Function
([inline-function.md](inline-function.md)).

## When to use

Smells: Long Function, Duplicated Code, Comments, Mutable Data, Divergent Change, Feature
Envy, Message Chains, Data Class.

- Reading a fragment forces you to work out what it does. A function named for the purpose
  lets the reader skip the implementation.
- A comment sits above a block to describe it. That comment usually already holds the words
  for the function's name.
- The same or similar logic appears in several places (Duplicated Code).
- Mutable Data: code that writes to shared state is mixed into a longer body. Extracting it
  isolates the update, so it can be found, guarded or replaced.
- Divergent Change: one function serves two different reasons to change. Extract each part so
  they can be separated or moved apart.
- Feature Envy and Message Chains: the fragment mostly works with another object's data.
  Extract it first, then move it to that object.
- Data Class: callers manipulate a record's fields. Extract that behavior, then move it onto
  the class.
- Size is not the test. A single line deserves its own function when the name says more than
  the code does. When the best name you find only repeats the code, keep it inline.
- Do not avoid extraction for fear of call overhead. Measure first.

## Mechanics

1. Pick a name that states the fragment's purpose, not its implementation. If none comes,
   reconsider extracting. The name can be refined later.
2. Create the new function and copy the fragment into it. Leave the original in place for now.
   If the language has nested functions, you may declare the new one inside the source
   function (see the C# notes on local functions).
3. Sort the variables the fragment touches that belong to the source function (parameters and
   temporaries), by what the fragment does with them:
   - Only read, or an object/collection you modify through the reference: pass them in as
     arguments; no return is needed.
   - Declared outside but used only by the fragment: move the declaration into the new
     function. If the declaration sits far from the fragment, Slide Statements
     ([slide-statements.md](slide-statements.md)) brings it next to its use first.
   - Written by the fragment and needed after it: if there is exactly one, make the new
     function return it, as a query.
   - Several written values: do not extract yet. Simplify first with Split Variable
     ([split-variable.md](split-variable.md)) or Replace Temp with Query ([replace-temp-with-query.md](replace-temp-with-query.md)),
     or choose another fragment. As a last resort, return a tuple or a small record.
   - A parameter that the fragment reassigns: apply Split Variable first, so it becomes a
     temporary.
4. Compile. This reveals any variable you missed.
5. Replace the original fragment with a call. If the function returns a value, assign it to
   the variable the fragment used to set.
6. Run the tests.
7. Search for the same or similar code elsewhere and replace it with a call
   ([replace-inline-code-with-function-call.md](replace-inline-code-with-function-call.md)).
8. Optional closing touch: with the call in context, check the name again and tidy the
   extracted function's local names.

## Example

Before: one method mixes a calculation, a mutation and output.

```csharp
using System;
using System.Collections.Generic;

public class CartLine
{
    public string Sku { get; set; } = "";
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
}

public class Cart
{
    public List<CartLine> Lines { get; } = new();
    public bool IsMember { get; set; }
}

public class Warehouse
{
    public Dictionary<string, int> Stock { get; } = new();
}

public class CheckoutService
{
    public void Checkout(Cart cart, Warehouse warehouse)
    {
        decimal subtotal = 0;
        foreach (var line in cart.Lines)
        {
            subtotal += line.Quantity * line.UnitPrice;
        }
        decimal discount = cart.IsMember && subtotal > 100m ? subtotal * 0.1m : 0m;
        decimal payable = subtotal - discount;

        foreach (var line in cart.Lines)
        {
            warehouse.Stock[line.Sku] -= line.Quantity;
        }

        Console.WriteLine($"items: {cart.Lines.Count}");
        Console.WriteLine($"pay: {payable:F2}");
    }
}
```

After: each fragment has a name for its purpose. The pricing fragment writes one variable
the rest of the method needs, so the new function returns it. The stock fragment changes the
warehouse through the object it receives, so it returns nothing.

```csharp
public class CheckoutService
{
    public void Checkout(Cart cart, Warehouse warehouse)
    {
        decimal payable = AmountPayable(cart);
        ReserveStock(cart, warehouse);
        PrintReceipt(cart, payable);
    }

    private static decimal AmountPayable(Cart cart)
    {
        decimal subtotal = 0;
        foreach (var line in cart.Lines)
        {
            subtotal += line.Quantity * line.UnitPrice;
        }
        decimal discount = cart.IsMember && subtotal > 100m ? subtotal * 0.1m : 0m;
        return subtotal - discount;
    }

    private static void ReserveStock(Cart cart, Warehouse warehouse)
    {
        foreach (var line in cart.Lines)
        {
            warehouse.Stock[line.Sku] -= line.Quantity;
        }
    }

    private static void PrintReceipt(Cart cart, decimal payable)
    {
        Console.WriteLine($"items: {cart.Lines.Count}");
        Console.WriteLine($"pay: {payable:F2}");
    }
}
```

Same behavior, and each fragment now has a name and a clear input and output. Extract one
fragment at a time and run the tests between extractions.

## C# notes

- A local function (declared inside the method) is an option for a helper used in one place.
  It can read the enclosing variables without parameters, which removes the out-of-scope
  problem from step 3. Move it to a method later if other code needs it.
- Local functions that capture variables can hide how much state the fragment depends on. For a
  helper you expect to move, extract to a sibling method first so the dependencies show.
- A `static` local function (C# 8+) cannot capture, so its dependencies stay explicit as
  parameters.
- A struct passed by value is not modified through the reference: a fragment that changes
  one changes only a copy. Return the new value, or pass it with `ref`. Prefer returning a
  value or a record/tuple; use `out`/`ref` as a last resort.

## Verification

- Compiles and the tests pass after every step; one commit per refactoring.
- Observable behavior and side effects are unchanged, including the order in which they
  happen.
- The new function's name reveals its purpose, and any duplicates found in step 7 now call it.
