# Extract Adapter

Kerievsky (2004), ch. 8, p. 258. Pattern: Adapter. Direction: to.

## When to use
Smells: Solution Sprawl.

- One class adapts several versions of a component, library or API, so it carries version-specific fields, constructors, methods and conditionals. Comments like "delete when we drop version 1" stay forever, because nobody dares to remove code that something unknown may still use.
- One adapter per version, all behind a common interface, keeps each class responsible for one version. The class name can even carry the version. The program picks the right adapter from configuration or runtime information.
- Adapters also shield you from fast-changing APIs that you do not control.
- Do not do it before the multiple versions actually cause conditionals or maintenance trouble.
- An adapter can hide behavior the client needs, because the client only sees the adapter's interface. If so, widen the interface.
- An adapter wraps one object. If you need to wrap a whole subsystem behind a simpler view, that is a Facade, a different pattern.

## Mechanics
There are several routes. If a class uses conditionals to handle versions, you can usually get one adapter per version by applying Replace Conditional with Polymorphism ([replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md)) repeatedly. The steps below cover the other common case: an existing adapter class with version-specific fields and methods.

1. Identify the overburdened adapter, the class that adapts too many versions.
2. Create a new adapter for one version, by extracting a subclass (Extract Subclass is 1st ed. only; see [replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md)) or by Extract Class ([extract-class.md](../../fowler/encapsulation/extract-class.md)). Move or copy to it every field and method used only by that version. You may have to widen the visibility of some members of the overburdened adapter, and initialize some fields through the new class's constructor, which changes the code that constructs it. Compile and test.
3. Repeat step 2 for each version until the overburdened adapter holds no version-specific code.
4. Remove the duplication among the new adapters with Pull Up Method ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)) and Form Template Method ([form-template-method.md](form-template-method.md)). Compile and test.

## Example
Before: `AssistantModel` adapts two versions of a model provider's API. It has two constructors, one nullable field per version, and a branch in the only method.

```csharp
// Old version of the provider API: a single prompt string in, text out.
public class LegacyCompletionService
{
    public string Complete(string prompt) => $"  reply to [{prompt}]  ";
}

// New version: system and user text are separate, and the answer is an object.
public class ChatReply
{
    public string Text { get; }
    public ChatReply(string text) => Text = text;
}

public class ChatServiceV2
{
    public ChatReply Send(string system, string user) => new ChatReply($"  reply to [{system}/{user}]  ");
}

public class AssistantModel
{
    private readonly LegacyCompletionService? _legacy;
    private readonly ChatServiceV2? _v2;

    public AssistantModel(LegacyCompletionService legacy) => _legacy = legacy;
    public AssistantModel(ChatServiceV2 v2) => _v2 = v2;

    public string Ask(string question)
    {
        var raw = _legacy != null
            ? _legacy.Complete($"User: {question}")
            : _v2!.Send("assistant", question).Text;
        return raw.Trim();
    }
}
```

After: one adapter per version, behind a common interface. The shared trimming stays in a base class (the Form Template Method step), and each adapter implements only how to get the raw reply.

```csharp
public class LegacyCompletionService
{
    public string Complete(string prompt) => $"  reply to [{prompt}]  ";
}

public class ChatReply
{
    public string Text { get; }
    public ChatReply(string text) => Text = text;
}

public class ChatServiceV2
{
    public ChatReply Send(string system, string user) => new ChatReply($"  reply to [{system}/{user}]  ");
}

public interface IAssistantModel
{
    string Ask(string question);
}

public abstract class AssistantModel : IAssistantModel
{
    public string Ask(string question) => RawReply(question).Trim();

    protected abstract string RawReply(string question);
}

public class LegacyAssistantModel : AssistantModel
{
    private readonly LegacyCompletionService _service;
    public LegacyAssistantModel(LegacyCompletionService service) => _service = service;
    protected override string RawReply(string question) => _service.Complete($"User: {question}");
}

public class V2AssistantModel : AssistantModel
{
    private readonly ChatServiceV2 _service;
    public V2AssistantModel(ChatServiceV2 service) => _service = service;
    protected override string RawReply(string question) => _service.Send("assistant", question).Text;
}
```

Clients depend on `IAssistantModel`; startup code (or configuration) chooses `LegacyAssistantModel` or `V2AssistantModel`. When version 1 is retired, delete one class and nothing else.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Each adapter has a test against its own version (or a fake of it), and the old overburdened class has no version fields or branches left before you delete it.
