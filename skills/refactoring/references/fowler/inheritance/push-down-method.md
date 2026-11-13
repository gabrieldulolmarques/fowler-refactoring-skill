# Push Down Method

Fowler (2018), ch. 12, p. 359. Formerly / aka: —. Inverse: Pull Up Method
([pull-up-method.md](pull-up-method.md)).

## When to use
Smell: Refused Bequest. A method defined on a base class is relevant to just one subclass,
or to a small share of them. Leaving it on the base class suggests every subclass supports it
and makes the hierarchy harder to read. Moving it down puts the behavior where it belongs.

Precondition: the code that calls the method must already hold a reference typed as that
specific subclass. If callers use the base type and rely on the method being available on all
subclasses, pushing it down breaks them. In that case, keep it on the base class and use
Replace Conditional with Polymorphism ([replace-conditional-with-polymorphism.md](../conditional-logic/replace-conditional-with-polymorphism.md)), with a
neutral default implementation on the base class.

## Mechanics
1. Find every caller of the method and confirm each one works with the specific subclass type
   (or can be changed to).
2. Copy the method into each subclass that needs it.
3. Remove the method from the superclass.
4. Compile and run the tests. Fix any caller the compiler flags by giving it the subclass type.
5. If a subclass that does not need the method still ends up with a copy (or an override),
   remove it there.
6. Compile and run the tests again.

## Example
Before: `Subscriber` offers a download allowance, but only premium subscribers can download.

```csharp
public abstract class Subscriber
{
    public string Name { get; set; } = "";

    public int RemainingDownloads(int used)
    {
        return used >= 50 ? 0 : 50 - used;
    }
}

public class PremiumSubscriber : Subscriber { }

public class FreeSubscriber : Subscriber { }

public class OfflineLibrary
{
    public bool CanDownload(PremiumSubscriber subscriber, int used)
    {
        return subscriber.RemainingDownloads(used) > 0;
    }
}
```

After: the method lives only on `PremiumSubscriber`. `OfflineLibrary` already used that type,
so it needs no change.

```csharp
public abstract class Subscriber
{
    public string Name { get; set; } = "";
}

public class PremiumSubscriber : Subscriber
{
    public int RemainingDownloads(int used)
    {
        return used >= 50 ? 0 : 50 - used;
    }
}

public class FreeSubscriber : Subscriber { }

public class OfflineLibrary
{
    public bool CanDownload(PremiumSubscriber subscriber, int used)
    {
        return subscriber.RemainingDownloads(used) > 0;
    }
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
