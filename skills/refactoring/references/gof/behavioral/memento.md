# Memento

Gamma et al. (1995), cap. 5, p. 283. Também conhecido como: Token. Categoria: comportamental de objeto.

## Intenção
Capturar o estado interno de um objeto em um objeto separado, sem quebrar o encapsulamento, para que o objeto possa voltar a esse estado depois.

## Quando compensa
- Você precisa guardar um snapshot do estado de um objeto para restaurá-lo depois (desfazer, checkpoints, reversão de uma mudança provisória), e
- ler o estado por uma interface pública exporia detalhes de implementação.
- Benefícios: os detalhes internos do originador permanecem privados, e o originador não precisa gerenciar uma lista de versões, porque quem chama guarda os snapshots.
- Custos: snapshots podem ser caros em memória ou em tempo de cópia. Quem guarda os mementos não consegue saber o tamanho de cada um, então um histórico pode crescer sem ser notado. Em algumas linguagens, é difícil permitir que só o originador leia o memento.
- Não vale a pena quando o estado é meia dúzia de valores públicos (basta copiá-los) ou quando o desfazer pode ser uma operação inversa exata.

## Participantes em C#
- **Memento** (`ChatSettings.Snapshot`, exposto como `IChatSettingsMemento`): guarda o estado salvo. Uma classe aninhada privada dá ao originador a interface ampla. A interface pública vazia dá a todos os demais a interface estreita.
- **Originator** (`ChatSettings`): cria um memento do seu estado e restaura a partir de um.
- **Caretaker** (`SettingsHistory`): guarda os mementos e os devolve, sem nunca olhar por dentro.

## Exemplo (C#)
Um assistente de chat com IA tem configurações (prompt de sistema, temperatura, ferramentas habilitadas). O usuário pode tentar uma mudança e voltar atrás. A classe do snapshot é privada e aninhada, então só `ChatSettings` pode lê-la; o histórico enxerga apenas uma interface opaca.

```csharp
using System;
using System.Collections.Generic;

public interface IChatSettingsMemento
{
    // Interface estreita: nada para ler. Só o originator enxerga o conteúdo.
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
        new Snapshot(_systemPrompt, _temperature, _enabledTools.ToArray());   // copia a lista

    public void Restore(IChatSettingsMemento memento)
    {
        var snapshot = (Snapshot)memento;   // lança exceção para um memento de outra origem
        _systemPrompt = snapshot.SystemPrompt;
        _temperature = snapshot.Temperature;
        _enabledTools.Clear();
        _enabledTools.AddRange(snapshot.EnabledTools);
    }

    // Interface ampla, visível apenas dentro de ChatSettings.
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
        Console.WriteLine(settings.Describe());   // de volta ao primeiro estado
    }
}
```

## Variações
- **Suporte da linguagem para as duas interfaces.** C++ usa classes amigas. Em C#, uma classe aninhada privada que implementa uma interface marcadora pública oferece a mesma divisão. A visibilidade `internal` funciona quando o caretaker está em outro assembly.
- **Mementos incrementais.** Se os mementos são sempre restaurados em uma ordem conhecida (uma pilha de desfazer), cada um pode guardar apenas o que mudou desde o anterior, o que economiza espaço.
- **Snapshots por valor.** Se o estado é imutável ou um valor pequeno, o memento pode ser simplesmente uma cópia dele, e o caretaker pode lê-lo livremente quando o encapsulamento não for uma preocupação.
- **Cursor como memento.** Um marcador de posição em um percurso de coleção é um memento do estado da iteração.

## Riscos e alternativas em C#
- Copie membros mutáveis (listas, dicionários) ao salvar, ou mudanças posteriores alterarão o snapshot. O exemplo copia a lista.
- Históricos sem limite vazam memória. Limite a pilha ou descarte entradas antigas.
- Mementos que guardam referências a outros objetos vivos podem restaurar um grafo inconsistente. Guarde valores, não referências, ou restaure também os objetos relacionados.
- Se existe uma operação inversa exata e barata, um [Command](command.md) com seu próprio `Undo` é mais simples do que snapshots.
- Para persistência entre execuções, serialize o memento (JSON), mas mantenha o formato sob responsabilidade do originador, para que o layout possa mudar em um único lugar.
- Tipos imutáveis tornam os snapshots triviais: mantenha a instância antiga e substitua a referência.

## Padrões relacionados
- [Command](command.md): comandos usam mementos para guardar o estado necessário para desfazer.
- [Iterator](iterator.md): um memento pode guardar o estado de uma iteração.

## Verificação
- Depois de `Save`, uma mudança e `Restore`, cada parte observável do originador é igual ao que era, incluindo as coleções.
- Mudar o originador após um save não altera o memento guardado.
- O caretaker compila sem ler nenhum campo do memento.
- O tamanho do histórico é limitado, ou o caso sem limite é uma decisão documentada.
