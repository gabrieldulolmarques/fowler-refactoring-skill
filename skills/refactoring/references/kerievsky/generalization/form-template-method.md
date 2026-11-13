# Form Template Method

Kerievsky (2004), ch. 8, p. 205. Pattern: Template Method. Direction: to.

## When to use
Smells: Duplicated Code.

- Two subclasses implement the same method, and both follow the same steps in the same order, but the steps themselves differ. The skeleton of the algorithm is copied into every subclass.
- Moving the skeleton into the superclass leaves each subclass with only the steps that really vary, and the order of the steps is stated once.
- Fowler's refactoring of the same name is the same idea; Kerievsky's version suits the case where the shared skeleton is hidden inside the bodies, not already visible as repeated statements.
- Do not use it when subclasses would have to implement many small methods just to fill in the skeleton: the hierarchy gets harder to read than the duplication it removed. Keep the number of abstract steps small and make optional steps concrete hooks.

## Mechanics
1. Find a similar method: two subclasses that run similar steps in a similar order. Apply Compose Method ([compose-method.md](../simplification/compose-method.md)) to it in both subclasses, so each step is a method. Steps with the same signature and body in both are identical methods; steps that differ are unique methods. When unsure which kind a step is, ask whether it makes sense for subclasses to inherit or override it as a unique method; if not, extract it as an identical method.
2. Pull up the identical methods with Pull Up Method ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)). Compile and test.
3. Make the similar method's body the same in both subclasses: rename each unique method so both subclasses call the same names, with Change Function Declaration ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)). Compile and test after each rename.
4. If the similar method's signature is not yet identical, change it the same way.
5. Pull up the similar method from one subclass and delete it from the other. Declare an abstract method in the superclass for every unique method. The pulled-up method is now the template. Compile and test.

## Example
Before: two formatters repeat the same sequence (header, one line per message, footer), each with its own formatting.

```csharp
using System.Collections.Generic;
using System.Text;

public class ChatMessage
{
    public string Role { get; }
    public string Text { get; }
    public ChatMessage(string role, string text) { Role = role; Text = text; }
}

public abstract class TranscriptFormatter
{
    public abstract string Format(IReadOnlyList<ChatMessage> messages);
}

public class MarkdownTranscriptFormatter : TranscriptFormatter
{
    public override string Format(IReadOnlyList<ChatMessage> messages)
    {
        var sb = new StringBuilder();
        sb.AppendLine("# Conversation");
        foreach (var m in messages)
            sb.AppendLine($"**{m.Role}**: {m.Text}");
        sb.AppendLine($"messages={messages.Count}");
        return sb.ToString();
    }
}

public class PlainTranscriptFormatter : TranscriptFormatter
{
    public override string Format(IReadOnlyList<ChatMessage> messages)
    {
        var sb = new StringBuilder();
        sb.AppendLine("CONVERSATION");
        foreach (var m in messages)
            sb.AppendLine($"{m.Role}> {m.Text}");
        sb.AppendLine($"messages={messages.Count}");
        return sb.ToString();
    }
}
```

After: the superclass owns the sequence and the identical footer. Each subclass writes only its header and its line.

```csharp
using System.Collections.Generic;
using System.Text;

public class ChatMessage
{
    public string Role { get; }
    public string Text { get; }
    public ChatMessage(string role, string text) { Role = role; Text = text; }
}

public abstract class TranscriptFormatter
{
    public string Format(IReadOnlyList<ChatMessage> messages)
    {
        var sb = new StringBuilder();
        WriteHeader(sb);
        foreach (var m in messages)
            WriteLine(sb, m);
        WriteFooter(sb, messages.Count);
        return sb.ToString();
    }

    protected abstract void WriteHeader(StringBuilder sb);
    protected abstract void WriteLine(StringBuilder sb, ChatMessage message);
    protected virtual void WriteFooter(StringBuilder sb, int count) => sb.AppendLine($"messages={count}");
}

public class MarkdownTranscriptFormatter : TranscriptFormatter
{
    protected override void WriteHeader(StringBuilder sb) => sb.AppendLine("# Conversation");
    protected override void WriteLine(StringBuilder sb, ChatMessage m) => sb.AppendLine($"**{m.Role}**: {m.Text}");
}

public class PlainTranscriptFormatter : TranscriptFormatter
{
    protected override void WriteHeader(StringBuilder sb) => sb.AppendLine("CONVERSATION");
    protected override void WriteLine(StringBuilder sb, ChatMessage m) => sb.AppendLine($"{m.Role}> {m.Text}");
}
```

## C# notes
- `Format` is not `virtual`, so a subclass cannot replace the sequence by accident. A method that was never virtual is the C# equivalent of Java's `final` template.
- Mark required steps `abstract` and optional ones `virtual` with a useful default (the footer above). Use `protected` for both, since callers should only see the template.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Each subclass's output is byte-for-byte the same as before (compare the strings in a test), including the order of the steps.
