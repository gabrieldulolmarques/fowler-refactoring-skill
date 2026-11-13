# Substituir Notificações Fixas no Código por Observer (Replace Hard-Coded Notifications with Observer)

Kerievsky (2004), cap. 8, p. 236. Direção: até, rumo a. Padrão: Observer (GoF, p. 293).

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
Antes: `PaymentProcessor` decide o resultado de uma cobrança. `DashboardPaymentProcessor` é uma subclasse cujo único trabalho é reportar cada cobrança a um `PaymentDashboard`, e também monta a linha de texto que o painel mostra.

```csharp
using System.Collections.Generic;

public record ChargeResult(string Account, decimal Amount, bool Approved);

public class PaymentProcessor
{
    public ChargeResult Charge(string account, decimal amount)
    {
        var result = new ChargeResult(account, amount, amount <= 1000m);
        OnCharged(result);
        return result;
    }

    protected virtual void OnCharged(ChargeResult result) { }
}

public class PaymentDashboard
{
    public List<string> Lines { get; } = new();
    public void Add(string line) => Lines.Add(line);
}

public class DashboardPaymentProcessor : PaymentProcessor
{
    private readonly PaymentDashboard _dashboard;
    public DashboardPaymentProcessor(PaymentDashboard dashboard) => _dashboard = dashboard;

    protected override void OnCharged(ChargeResult r)
    {
        var line = $"{r.Account}: {r.Amount:F2} {(r.Approved ? "approved" : "declined")}";
        _dashboard.Add(line);
    }
}
```

Depois, forma clássica: a formatação foi movida para o painel (passo 1), `IChargeObserver` foi extraída (passos 2 e 3), a notificação foi subida e a subclasse apagada (passos 4 e 5), e o sujeito agora mantém uma lista (passo 6). Um segundo observador, `FraudMonitor`, se inscreve sem nenhuma mudança em `PaymentProcessor`.

```csharp
using System.Collections.Generic;

public record ChargeResult(string Account, decimal Amount, bool Approved);

public interface IChargeObserver
{
    void Charged(ChargeResult result);
}

public class PaymentProcessor
{
    private readonly List<IChargeObserver> _observers = new();

    public void Subscribe(IChargeObserver observer) => _observers.Add(observer);
    public void Unsubscribe(IChargeObserver observer) => _observers.Remove(observer);

    public ChargeResult Charge(string account, decimal amount)
    {
        var result = new ChargeResult(account, amount, amount <= 1000m);
        foreach (var observer in _observers.ToArray())
            observer.Charged(result);
        return result;
    }
}

public class PaymentDashboard : IChargeObserver
{
    public List<string> Lines { get; } = new();

    public void Charged(ChargeResult r) =>
        Lines.Add($"{r.Account}: {r.Amount:F2} {(r.Approved ? "approved" : "declined")}");
}

public class FraudMonitor : IChargeObserver
{
    public int Declines { get; private set; }
    public void Charged(ChargeResult r) { if (!r.Approved) Declines++; }
}

// Conexão e desconexão, sempre em par:
//   var processor = new PaymentProcessor();
//   var dashboard = new PaymentDashboard();
//   processor.Subscribe(dashboard);
//   processor.Charge("acc-1", 50m);
//   processor.Unsubscribe(dashboard);
```

Depois, C# idiomático: o mesmo desenho, com um `event` no lugar da interface e de dois métodos. O tipo de interface de observador vira o delegate `EventHandler<ChargeResult>`, e a lista, `Subscribe` e `Unsubscribe` viram `event`, `+=` e `-=`.

```csharp
using System;
using System.Collections.Generic;

public record ChargeResult(string Account, decimal Amount, bool Approved);

public class PaymentProcessor
{
    public event EventHandler<ChargeResult>? Charged;

    public ChargeResult Charge(string account, decimal amount)
    {
        var result = new ChargeResult(account, amount, amount <= 1000m);
        Charged?.Invoke(this, result);
        return result;
    }
}

public class PaymentDashboard
{
    public List<string> Lines { get; } = new();

    public void Attach(PaymentProcessor processor) => processor.Charged += OnCharged;
    public void Detach(PaymentProcessor processor) => processor.Charged -= OnCharged;

    private void OnCharged(object? sender, ChargeResult r) =>
        Lines.Add($"{r.Account}: {r.Amount:F2} {(r.Approved ? "approved" : "declined")}");
}
```

## Notas (C#)
- A forma idiomática é um `event` do C# (`event EventHandler<T>`, ou `Action<T>` em casos simples). Use uma interface de observador apenas quando um observador precisar de vários callbacks diferentes ou quando você quiser passá-lo como uma unidade.
- Todo `+=` precisa de um `-=` correspondente, e o sujeito costuma sobreviver ao assinante; assim, um handler que nunca é removido mantém o assinante vivo. Desinscreva em `Dispose`, em um método de fechamento ou quando o observador for substituído. Para um assinante que implementa `IDisposable`, coloque o `-=` ali.
- Inscrever uma lambda ou método anônimo é fácil, mas `-=` com uma lambda nova e textualmente idêntica não a remove. Guarde o delegate em um campo se você precisar se desinscrever.
- Só a classe que declara um `event` pode dispará-lo; código externo só pode usar `+=` e `-=`. Isso geralmente é o que você quer. Use `?.Invoke` para que um event sem assinantes não lance exceção.
- Handlers rodam de forma síncrona, na ordem de inscrição, na thread de quem chamou. Se um deles lançar exceção, os demais são pulados, e um handler lento deixa `Charge` lento. Mantenha os handlers curtos, ou capture e reporte o erro dentro do método que dispara se um observador ruim não puder impedir os outros.
- Um handler que se desinscreve (ou se inscreve) durante a notificação é seguro com events, porque delegates são imutáveis e `Invoke` trabalha sobre um snapshot. Na versão com lista manual, itere sobre uma cópia, como acima.
- Se o sujeito precisar viver muito mais que os observadores e você não puder garantir a desinscrição, um padrão de weak event ou um desenho diferente (polling, um barramento de mensagens) é mais seguro do que depender de disciplina.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Um teste com dois observadores verifica que ambos recebem cada evento, na ordem esperada, e que um observador não vê nada depois de se desinscrever.
- Procure cada `Subscribe` ou `+=`: cada um deve ter um `Unsubscribe` ou `-=` alcançável. Depois que o último observador sai, o sujeito não guarda mais nenhuma referência a ele.
