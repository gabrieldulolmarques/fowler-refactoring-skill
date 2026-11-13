# Memento

Gamma et al. (1995), ch. 5, p. 283. Also known as: Token. Category: object behavioral.

## Intent
Capture an object's internal state in a separate object, without breaking encapsulation, so the object can go back to that state later.

## When it pays off
- You must save a snapshot of an object's state to restore it later (undo, checkpoints, rollback of a tentative change), and
- reading the state through a public interface would expose implementation details.
- Benefits: the originator's internals stay private, and the originator does not have to manage a list of versions itself because the caller keeps the snapshots.
- Liabilities: snapshots can be expensive in memory or copy time. The caretaker cannot tell how big a memento is, so a history may grow unnoticed. In some languages it is hard to let only the originator read the memento.
- Not worth it when the state is a couple of public values (just copy them) or when the undo can be an exact inverse operation.

## Participants in C#
- **Memento** (`ChatSettings.Snapshot`, exposed as `IChatSettingsMemento`): holds the saved state. A private nested class gives the originator the wide interface. The empty public interface gives everyone else the narrow one.
- **Originator** (`ChatSettings`): creates a memento of its state and restores from one.
- **Caretaker** (`SettingsHistory`): stores mementos and hands them back, never looking inside.

## Example (C#)
An AI chat assistant has settings (system prompt, temperature, enabled tools). The user can try a change and go back. The snapshot class is private and nested, so only `ChatSettings` can read it; the history sees only an opaque interface.

```csharp
using System;
using System.Collections.Generic;

public interface IChatSettingsMemento
{
    // Narrow interface: nothing to read. Only the originator can see inside.
}

public class ChatSettings
{
    private string _systemPrompt = "You are a helpful assistant.";
    private double _temperature = 0.7;
    private readonly List<string> _enabledTools = new();

    public void SetPrompt(string prompt) => _systemPrompt = prompt;
    public void SetTemperature(double value) => _temperature = value;
    public void EnableTool(string tool) => _enabledTools.Add(tool);

    public string Describe() =>
        $"{_systemPrompt} | t={_temperature} | tools=[{string.Join(", ", _enabledTools)}]";

    public IChatSettingsMemento Save() =>
        new Snapshot(_systemPrompt, _temperature, _enabledTools.ToArray());   // copies the list

    public void Restore(IChatSettingsMemento memento)
    {
        var snapshot = (Snapshot)memento;   // throws for a foreign memento
        _systemPrompt = snapshot.SystemPrompt;
        _temperature = snapshot.Temperature;
        _enabledTools.Clear();
        _enabledTools.AddRange(snapshot.EnabledTools);
    }

    // Wide interface, visible only inside ChatSettings.
    private sealed class Snapshot : IChatSettingsMemento
    {
        public Snapshot(string systemPrompt, double temperature, string[] enabledTools)
        {
            SystemPrompt = systemPrompt;
            Temperature = temperature;
            EnabledTools = enabledTools;
        }

        public string SystemPrompt { get; }
        public double Temperature { get; }
        public string[] EnabledTools { get; }
    }
}

public class SettingsHistory
{
    private readonly Stack<IChatSettingsMemento> _saved = new();

    public void Checkpoint(ChatSettings settings) => _saved.Push(settings.Save());

    public void Undo(ChatSettings settings)
    {
        if (_saved.Count > 0) settings.Restore(_saved.Pop());
    }
}

public static class Program
{
    public static void Main()
    {
        var settings = new ChatSettings();
        var history = new SettingsHistory();

        history.Checkpoint(settings);
        settings.SetTemperature(1.4);
        settings.EnableTool("web-search");
        Console.WriteLine(settings.Describe());

        history.Undo(settings);
        Console.WriteLine(settings.Describe());   // back to the first state
    }
}
```

## Variations
- **Language support for the two interfaces.** C++ uses friend classes. In C#, a private nested class that implements a public marker interface gives the same split. `internal` visibility works when the caretaker lives in another assembly.
- **Incremental mementos.** If mementos are always restored in a known order (an undo stack), each can store only what changed since the previous one, which saves space.
- **Value snapshots.** If the state is immutable or a small value, the memento can simply be a copy of it, and the caretaker can read it freely when encapsulation is not a concern.
- **Cursor as a memento.** A position marker in a collection traversal is a memento of the iteration state.

## Risks and C# alternatives
- Copy mutable members (lists, dictionaries) when saving, or later changes will alter the snapshot. The example copies the list.
- Unbounded histories leak memory. Cap the stack or drop old entries.
- Mementos that hold references to other live objects can restore an inconsistent graph. Snapshot values, not references, or restore the related objects too.
- If an exact inverse operation exists and is cheap, a [Command](command.md) with its own `Undo` is simpler than snapshots.
- For persistence across runs, serialize the memento (JSON) but keep the format owned by the originator, so the layout can change in one place.
- Immutable types make snapshots trivial: keep the old instance and replace the reference.

## Related patterns
- [Command](command.md): commands use mementos to hold the state needed to undo.
- [Iterator](iterator.md): a memento can store the state of an iteration.

## Verification
- After `Save`, change, `Restore`, every observable part of the originator equals what it was, including collections.
- Changing the originator after a save does not alter the stored memento.
- The caretaker compiles without reading any field of the memento.
- The history size is bounded, or the unbounded case is a documented decision.
