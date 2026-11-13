# Strategy

Gamma et al. (1995), ch. 5, p. 315. Also known as: Policy. Category: object behavioral.

## Intent
Put each algorithm of a family in its own object behind a common interface, so the code that uses the algorithm can switch between them and the algorithm can change without touching that code.

## When it pays off
- Several classes differ only in how they do one thing, or one class picks among behaviors with a chain of conditionals.
- You need variants of the same algorithm, such as a fast one that uses more memory and a slow one that uses less.
- An algorithm needs data or helper structures that its callers should not see.
- Benefits: families of interchangeable algorithms; an alternative to subclassing the context; the conditionals go away; the choice can be made at run time.
- Liabilities: the client must know the strategies well enough to pick one; the shared interface may pass data some strategies ignore; more objects.
- Skip it when there is one algorithm, or the variation never matters to the caller. A `switch` that has two arms and never grows is fine.

## Participants in C#
- **Strategy** (`IRetryPolicy`): interface (or a delegate type) that all algorithms implement.
- **ConcreteStrategy** (`NoRetry`, `FixedDelay`, `ExponentialBackoff`): one algorithm each.
- **Context** (`ApiCaller`): holds a strategy, forwards the decision to it, and passes the data it needs.
- **Client** (`Program`): chooses the strategy and gives it to the context, usually once.

## Example (C#)
An HTTP API client decides how long to wait between retries of a failed call. The retry policy is a strategy: the caller loops and runs the operation, the policy answers "wait this long, or stop".

```csharp
using System;
using System.Threading.Tasks;

public interface IRetryPolicy
{
    // Delay before retry number `attempt` (1 for the first retry), or null to stop.
    TimeSpan? NextDelay(int attempt);
}

public sealed class NoRetry : IRetryPolicy
{
    public TimeSpan? NextDelay(int attempt) => null;
}

public sealed class FixedDelay : IRetryPolicy
{
    private readonly TimeSpan _delay;
    private readonly int _maxRetries;

    public FixedDelay(TimeSpan delay, int maxRetries)
    {
        _delay = delay;
        _maxRetries = maxRetries;
    }

    public TimeSpan? NextDelay(int attempt) => attempt <= _maxRetries ? _delay : null;
}

public sealed class ExponentialBackoff : IRetryPolicy
{
    private readonly TimeSpan _initial;
    private readonly TimeSpan _cap;
    private readonly int _maxRetries;

    public ExponentialBackoff(TimeSpan initial, TimeSpan cap, int maxRetries)
    {
        _initial = initial;
        _cap = cap;
        _maxRetries = maxRetries;
    }

    public TimeSpan? NextDelay(int attempt)
    {
        if (attempt > _maxRetries) return null;
        var ms = _initial.TotalMilliseconds * Math.Pow(2, attempt - 1);
        return TimeSpan.FromMilliseconds(Math.Min(ms, _cap.TotalMilliseconds));
    }
}

public class ApiCaller
{
    private readonly IRetryPolicy _policy;

    public ApiCaller(IRetryPolicy policy) => _policy = policy;

    public async Task<T> CallAsync<T>(Func<Task<T>> operation)
    {
        for (int attempt = 1; ; attempt++)
        {
            try
            {
                return await operation();
            }
            catch (TimeoutException)
            {
                var delay = _policy.NextDelay(attempt);
                if (delay is null) throw;      // policy says stop
                await Task.Delay(delay.Value);
            }
        }
    }
}

public static class Program
{
    public static async Task Main()
    {
        var calls = 0;
        Task<string> Flaky()
        {
            calls++;
            if (calls < 3) throw new TimeoutException();
            return Task.FromResult("ok");
        }

        var caller = new ApiCaller(new ExponentialBackoff(
            TimeSpan.FromMilliseconds(10), TimeSpan.FromSeconds(1), maxRetries: 5));

        Console.WriteLine(await caller.CallAsync(Flaky));   // ok, after two waits
    }
}
```

## Variations
- **How data reaches the strategy.** Pass what it needs as arguments (the example passes the attempt number): the pair stays decoupled, but the context may pass values some strategies ignore. Or pass the context itself, or let the strategy hold a reference to it: the strategy can ask for exactly what it needs, but the context must expose more of itself and the two are coupled.
- **Compile-time selection with generics.** When the strategy is fixed at build time and never changes, a generic parameter with an interface constraint (`ApiCaller<TPolicy> where TPolicy : IRetryPolicy`) binds it statically and, with structs, can avoid a virtual call.
- **Optional strategy.** Let the context have a default when none is supplied, so most clients never see the pattern. In the example, a missing policy could mean `NoRetry`.
- **Stateless and shared.** Strategies without fields can be shared by many contexts. Anything that varies per call stays in the context and travels in the arguments.

## Risks and C# alternatives
- When the interface has one method, a delegate is the strategy: `Func<int, TimeSpan?>` replaces `IRetryPolicy`, and a lambda replaces each class. Keep the interface when strategies have configuration, a name, several methods or need to be registered in a container.
- With dependency injection, register the implementations and inject the one you want (or an `IEnumerable<IRetryPolicy>` plus a selector). The choice of strategy becomes configuration.
- A strategy that keeps state between calls (a counter, a circuit-breaker window) is not safe to share across callers or threads. Either keep it per context or guard the state.
- Strategies for randomness or time (jitter, `DateTime.Now`) are hard to test. Take a clock or random source as a dependency.
- A strategy interface shaped for the most complex algorithm forces the simple ones to accept parameters they never use. Review the interface when a new strategy needs data it does not carry.

## Related patterns
- [Flyweight](../structural/flyweight.md): strategy objects without state make good flyweights.
- [Template Method](template-method.md): varies part of an algorithm by inheritance, where Strategy varies the whole algorithm by delegation.

**Beyond the book:** [State](state.md) has the same structure, but a state is replaced by the object as it moves through its life, and a strategy is chosen from outside.

## Verification
- The context contains no branching on which algorithm is in use, and names no concrete strategy.
- Adding a variant means adding one class (or one lambda) and no change to the context.
- Each strategy can be tested alone, without the context.
- The strategy interface carries only data that every strategy really needs, or the extra data is justified.
