# Substituir Notificações Fixas no Código por Observer (Replace Hard-Coded Notifications with Observer)

Kerievsky (2004), cap. 8, p. 236. Padrão: Observer. Direção: até, rumo a.

## Quando usar
Smells: —.

- Uma classe (o notificador) mantém uma referência direta a outra classe (o receptor) e a chama sempre que algo acontece. Para exatamente um receptor esse acoplamento é aceitável, e é o ponto de partida certo.
- Agora uma segunda parte precisa saber dos mesmos eventos, ou o receptor deveria ser outra classe em algumas configurações. Subclasses que existem só para conectar um receptor específico à classe base são o sintoma típico.
- Com uma interface de observador, o sujeito sabe apenas que há algo escutando, nunca quem é. Qualquer classe que implemente a interface pode se inscrever.
- Não introduza isso cedo. Uma chamada direta simples é mais simples, e você pode evoluir para Observer quando o segundo ouvinte realmente chegar.
- Atente para dois problemas. Notificações em cascata (um observador que também é sujeito, notificando outros, e assim por diante) são difíceis de depurar; considere um Mediator. Vazamentos acontecem quando um sujeito de vida longa mantém a referência a um observador que já deveria ter saído, então cada inscrição precisa de uma desinscrição correspondente.

## Mecânica
Termos: o notificador é a classe que chama o receptor; o receptor é a classe que está sendo chamada. Depois da refatoração, a superclasse do notificador é o sujeito, e cada receptor é um observador.

1. Se o notificador faz trabalho próprio em nome do seu receptor (formatar, decidir, traduzir) em vez de apenas notificar, mova esse trabalho para o receptor com Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)). Depois disso, os métodos do notificador apenas repassam o evento. Faça isso para cada notificador. Compile e teste.
2. Crie a interface de observador extraindo uma interface de um receptor, mantendo apenas os métodos que o seu notificador chama (Extrair Interface (Extract Interface), só na 1ª ed.). Se outros notificadores chamam métodos do receptor que faltam na interface, acrescente-os para que uma única interface sirva a todos os receptores. Compile.
3. Faça cada receptor implementar a interface, e faça cada notificador falar com o seu receptor apenas por meio dela. Cada receptor agora é um observador. Compile e teste.
4. Para um notificador, suba os seus métodos de notificação para a superclasse com Subir Método (Pull Up Method) ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)), incluindo o campo que guarda o observador e o código que o define. A superclasse agora é o sujeito. Repita para cada notificador. Compile.
5. Mude cada observador para se registrar diretamente no sujeito, e não no notificador, e depois apague a subclasse notificadora. Compile e teste.
6. Mude o sujeito para guardar uma coleção de observadores em vez de um só: acrescente um método de inscrição (e, se observadores puderem sair, um de desinscrição), e faça cada notificação chegar a todos os observadores da coleção. Compile e teste.
7. Faça cada inscrição ter uma desinscrição correspondente no momento certo (quando o observador for descartado, fechado ou substituído), e itere sobre uma cópia da coleção ao notificar, para que um observador que se desinscreva dentro do seu callback não quebre o laço.

## Exemplo
Antes: `TokenMeter` mede o uso de tokens de uma conversa em relação ao seu orçamento. `DashboardTokenMeter` é uma subclasse cujo único trabalho é reportar cada medição a um `UsageDashboard`, e também monta a linha de texto que o painel mostra.

```csharp
using System.Collections.Generic;

public class UsageReport
{
    public string Conversation { get; }
    public int Tokens { get; }
    public bool OverBudget { get; }
    public UsageReport(string conversation, int tokens, bool overBudget)
    {
        Conversation = conversation;
        Tokens = tokens;
        OverBudget = overBudget;
    }
}

public class TokenMeter
{
    public UsageReport Record(string conversation, int tokens)
    {
        var report = new UsageReport(conversation, tokens, tokens > 4000);
        OnRecorded(report);
        return report;
    }

    protected virtual void OnRecorded(UsageReport report) { }
}

public class UsageDashboard
{
    public List<string> Lines { get; } = new();
    public void Add(string line) => Lines.Add(line);
}

public class DashboardTokenMeter : TokenMeter
{
    private readonly UsageDashboard _dashboard;
    public DashboardTokenMeter(UsageDashboard dashboard) => _dashboard = dashboard;

    protected override void OnRecorded(UsageReport r)
    {
        var line = $"{r.Conversation}: {r.Tokens} tokens {(r.OverBudget ? "over budget" : "ok")}";
        _dashboard.Add(line);
    }
}
```

Depois, forma clássica: a formatação foi movida para o painel (passo 1), a interface `IUsageObserver` foi extraída (passos 2 e 3), a notificação foi subida e a subclasse apagada (passos 4 e 5), e o sujeito agora mantém uma lista (passo 6). Um segundo observador, `BudgetAlarm`, se inscreve sem nenhuma mudança em `TokenMeter`.

```csharp
using System.Collections.Generic;

public class UsageReport
{
    public string Conversation { get; }
    public int Tokens { get; }
    public bool OverBudget { get; }
    public UsageReport(string conversation, int tokens, bool overBudget)
    {
        Conversation = conversation;
        Tokens = tokens;
        OverBudget = overBudget;
    }
}

public interface IUsageObserver
{
    void Recorded(UsageReport report);
}

public class TokenMeter
{
    private readonly List<IUsageObserver> _observers = new();

    public void Subscribe(IUsageObserver observer) => _observers.Add(observer);
    public void Unsubscribe(IUsageObserver observer) => _observers.Remove(observer);

    public UsageReport Record(string conversation, int tokens)
    {
        var report = new UsageReport(conversation, tokens, tokens > 4000);
        foreach (var observer in _observers.ToArray())
            observer.Recorded(report);
        return report;
    }
}

public class UsageDashboard : IUsageObserver
{
    public List<string> Lines { get; } = new();

    public void Recorded(UsageReport r) =>
        Lines.Add($"{r.Conversation}: {r.Tokens} tokens {(r.OverBudget ? "over budget" : "ok")}");
}

public class BudgetAlarm : IUsageObserver
{
    public int Overruns { get; private set; }
    public void Recorded(UsageReport r) { if (r.OverBudget) Overruns++; }
}

// Conexão e desconexão, sempre em par:
//   var meter = new TokenMeter();
//   var dashboard = new UsageDashboard();
//   meter.Subscribe(dashboard);
//   meter.Record("chat-1", 1200);
//   meter.Unsubscribe(dashboard);
```

Depois, C# idiomático: o mesmo desenho, com um `event` no lugar da interface e de dois métodos. A interface de observador vira o tipo delegate `EventHandler<UsageReport>`, e a lista, `Subscribe` e `Unsubscribe` viram `event`, `+=` e `-=`.

```csharp
using System;
using System.Collections.Generic;

public class UsageReport
{
    public string Conversation { get; }
    public int Tokens { get; }
    public bool OverBudget { get; }
    public UsageReport(string conversation, int tokens, bool overBudget)
    {
        Conversation = conversation;
        Tokens = tokens;
        OverBudget = overBudget;
    }
}

public class TokenMeter
{
    public event EventHandler<UsageReport>? Recorded;

    public UsageReport Record(string conversation, int tokens)
    {
        var report = new UsageReport(conversation, tokens, tokens > 4000);
        Recorded?.Invoke(this, report);
        return report;
    }
}

public class UsageDashboard
{
    public List<string> Lines { get; } = new();

    public void Attach(TokenMeter meter) => meter.Recorded += OnRecorded;
    public void Detach(TokenMeter meter) => meter.Recorded -= OnRecorded;

    private void OnRecorded(object? sender, UsageReport r) =>
        Lines.Add($"{r.Conversation}: {r.Tokens} tokens {(r.OverBudget ? "over budget" : "ok")}");
}
```

## Notas (C#)
- A forma idiomática é um `event` do C# (`event EventHandler<T>`, ou `Action<T>` em casos simples). Use uma interface de observador apenas quando um observador precisar de vários callbacks diferentes ou quando você quiser passá-lo como uma unidade.
- Todo `+=` precisa de um `-=` correspondente, e o sujeito costuma sobreviver ao assinante; assim, um handler que nunca é removido mantém o assinante vivo. Desinscreva em `Dispose`, em um método de fechamento ou quando o observador for substituído. Para um assinante que implementa `IDisposable`, coloque o `-=` ali.
- Inscrever uma lambda ou método anônimo é fácil, mas `-=` com uma lambda nova e textualmente idêntica não a remove. Guarde o delegate em um campo se você precisar se desinscrever.
- Só a classe que declara um `event` pode disparé-lo; código externo só pode usar `+=` e `-=`. Isso geralmente é o que você quer. Use `?.Invoke` para que um `event` sem assinantes não lance exceção.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Um teste com dois observadores verifica que ambos recebem cada evento, na ordem esperada, e que um observador não vê nada depois de se desinscrever.
- Procure cada `Subscribe` ou `+=`: cada um deve ter um `Unsubscribe` ou `-=` alcançável. Depois que o último observador sai, o sujeito não guarda mais nenhuma referência a ele.
