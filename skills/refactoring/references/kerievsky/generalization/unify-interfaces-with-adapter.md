# Unify Interfaces with Adapter

Kerievsky (2004), ch. 8, p. 247. Pattern: Adapter. Direction: to, towards.

## When to use
Smells: Alternative Classes with Different Interfaces, Oddball Solution, Duplicated Code.

- Two classes do the same or similar work through different interfaces, and a client that uses both has to be written twice.
- The client would be simpler if both looked the same.
- You cannot just rename or move methods until they match, because one class belongs to a third-party library, to a framework with many other clients, or you lack its source.
- Once both classes sit behind one interface, the duplicated client code can be merged with refactorings such as Form Template Method ([form-template-method.md](form-template-method.md)) or Introduce Polymorphic Creation with Factory Method ([introduce-polymorphic-creation-with-factory-method.md](../creation/introduce-polymorphic-creation-with-factory-method.md)).
- Do not use it when you can change one of the interfaces directly: renaming is cheaper than adding a class.

## Mechanics
The adaptee is the class whose interface the client does not prefer. The adapter is the class that will wrap it.

1. Extract a common interface from the class whose interface the client prefers (Extract Interface, 1st ed. only). If that class has methods taking its own type, change them to take the interface. Compile and test.
2. In the client that uses the adaptee, apply Extract Class ([extract-class.md](../../fowler/encapsulation/extract-class.md)) to create a primitive adapter: a class with an adaptee field, a getter for it, and a constructor (or setter) that receives it.
3. Change the client's fields, locals and parameters of the adaptee type to the adapter type. Each call now first gets the adaptee from the adapter. Compile and test.
4. For each distinct adaptee call in the client, apply Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) to make an invocation method that takes the adapter as a parameter and calls the adaptee through it. Compile and test after each.
5. Move each invocation method into the adapter with Move Function ([move-function.md](../../fowler/moving-features/move-function.md)), shaping it like the matching method of the common interface. If the moved body needs a value from the client, pass it in the adapter's constructor, or give the adapter a reference it can query, rather than adding a parameter that would make the signature differ. If a parameter is unavoidable, change the interface method to match. Compile and test; repeat until the adapter has every method of the interface.
6. Declare that the adapter implements the common interface, and change adapter methods that take an adapter to take the interface. Compile and test.
7. Change the client to use the interface everywhere instead of the adapter type. Compile and test. The client now talks to both classes through one type.

## Example
Before: a batch answerer sends questions to our own `InHouseModel` and, with a separate copy of the logic, to a third-party `RemoteCompletionApi` that we cannot change.

```csharp
using System.Collections.Generic;

public class InHouseModel
{
    public string Reply(string prompt, int maxTokens) => $"in-house({maxTokens}): {prompt}";
}

public class CompletionRequest
{
    public string Prompt { get; }
    public int MaxTokens { get; }
    public CompletionRequest(string prompt, int maxTokens) { Prompt = prompt; MaxTokens = maxTokens; }
}

public class CompletionResponse
{
    public string Text { get; }
    public CompletionResponse(string text) => Text = text;
}

// Third party: cannot be changed.
public sealed class RemoteCompletionApi
{
    public CompletionResponse Complete(CompletionRequest request) =>
        new CompletionResponse($"remote({request.MaxTokens}): {request.Prompt}");
}

public class BatchAnswerer
{
    public List<string> AnswerInHouse(IEnumerable<string> questions, InHouseModel model)
    {
        var answers = new List<string>();
        foreach (var q in questions)
            answers.Add(model.Reply($"Answer briefly: {q}", 256));
        return answers;
    }

    public List<string> AnswerRemote(IEnumerable<string> questions, RemoteCompletionApi api)
    {
        var answers = new List<string>();
        foreach (var q in questions)
            answers.Add(api.Complete(new CompletionRequest($"Answer briefly: {q}", 256)).Text);
        return answers;
    }
}
```

After: both providers sit behind `IChatModel`. The adapter wraps the remote API, and the answerer has one loop.

```csharp
using System.Collections.Generic;

public interface IChatModel
{
    string Reply(string prompt, int maxTokens);
}

public class InHouseModel : IChatModel
{
    public string Reply(string prompt, int maxTokens) => $"in-house({maxTokens}): {prompt}";
}

public class CompletionRequest
{
    public string Prompt { get; }
    public int MaxTokens { get; }
    public CompletionRequest(string prompt, int maxTokens) { Prompt = prompt; MaxTokens = maxTokens; }
}

public class CompletionResponse
{
    public string Text { get; }
    public CompletionResponse(string text) => Text = text;
}

// Third party: cannot be changed.
public sealed class RemoteCompletionApi
{
    public CompletionResponse Complete(CompletionRequest request) =>
        new CompletionResponse($"remote({request.MaxTokens}): {request.Prompt}");
}

public class RemoteModelAdapter : IChatModel
{
    private readonly RemoteCompletionApi _api;
    public RemoteModelAdapter(RemoteCompletionApi api) => _api = api;

    public string Reply(string prompt, int maxTokens) =>
        _api.Complete(new CompletionRequest(prompt, maxTokens)).Text;
}

public class BatchAnswerer
{
    public List<string> Answer(IEnumerable<string> questions, IChatModel model)
    {
        var answers = new List<string>();
        foreach (var q in questions)
            answers.Add(model.Reply($"Answer briefly: {q}", 256));
        return answers;
    }
}
```

The third-party class is untouched: only the adapter knows its request and response types. Adding another provider means one more adapter, not another loop.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The same inputs produce the same outbound messages through both channels as before (compare the returned answers), and no client code still names the adaptee type.
