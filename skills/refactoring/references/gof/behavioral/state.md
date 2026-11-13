# State

Gamma et al. (1995), cap. 5, p. 305. Também conhecido como: Objects for States. Categoria: comportamental de objeto.

## Intenção
Permitir que um objeto mude seu comportamento quando seu estado interno muda, delegando a um objeto separado por estado. Para quem chama, o objeto parece mudar de classe.

## Quando compensa
- O comportamento depende do estado atual e precisa mudar em tempo de execução.
- Várias operações repetem o mesmo `if` ou `switch` grande sobre um campo de status. Cada ramo vira uma classe e os switches desaparecem.
- Benefícios: o comportamento de cada estado fica em um só lugar; as transições são explícitas; uma transição é uma única atribuição de referência, então o contexto nunca fica pela metade; objetos de estado sem dados podem ser compartilhados.
- Custos: mais classes do que uma grande classe única. Vale a pena com muitos estados ou muitas operações dependentes de estado, e não com dois estados e uma operação.
- Não vale a pena quando os estados e as transições são apenas dados, sem comportamento; um enum e uma tabela de transições (veja Variações) bastam.

## Participantes em C#
- **Context** (`Ride`): o tipo que os clientes usam. Guarda o objeto de estado atual e repassa as chamadas dependentes de estado a ele.
- **State** (`RideState`): classe abstrata que declara um método para cada operação dependente de estado. Sua implementação padrão rejeita a operação, então cada estado concreto sobrescreve apenas o que permite. Uma interface também funciona quando não há implementações padrão.
- **ConcreteState** (`RequestedState`, `AcceptedState`, `InProgressState`, `CompletedState`): comportamento e transições de saída de um estado.

## Exemplo (C#)
Uma corrida de transporte por aplicativo passa por quatro estados: Requested, depois Accepted (um motorista assumiu), depois InProgress (o passageiro embarcou), depois Completed (a tarifa é cobrada). Cada estado permite apenas o próprio próximo passo; qualquer outra coisa lança exceção. Os estados não guardam dados, então cada um tem uma única instância compartilhada, e cada um decide o seu sucessor.

```csharp
using System;

public class Ride
{
    public RideState State { get; private set; } = RequestedState.Instance;
    public string? DriverId { get; private set; }
    public decimal Fare { get; private set; }

    // Operações repassadas ao estado atual.
    public void Accept(string driverId) => State.Accept(this, driverId);
    public void Start() => State.Start(this);
    public void Complete(decimal fare) => State.Complete(this, fare);

    // Usado pelos estados, para mudar de estado e registrar dados.
    public void TransitionTo(RideState next) => State = next;
    public void AssignDriver(string driverId) => DriverId = driverId;
    public void Charge(decimal fare) => Fare = fare;
}

public abstract class RideState
{
    public string Name => GetType().Name.Replace("State", "");

    public virtual void Accept(Ride ride, string driverId) => throw Reject("accept");
    public virtual void Start(Ride ride) => throw Reject("start");
    public virtual void Complete(Ride ride, decimal fare) => throw Reject("complete");

    private InvalidOperationException Reject(string action) =>
        new($"Cannot {action} a ride that is {Name}.");
}

public sealed class RequestedState : RideState
{
    public static readonly RequestedState Instance = new();
    private RequestedState() { }

    public override void Accept(Ride ride, string driverId)
    {
        ride.AssignDriver(driverId);
        ride.TransitionTo(AcceptedState.Instance);
    }
}

public sealed class AcceptedState : RideState
{
    public static readonly AcceptedState Instance = new();
    private AcceptedState() { }

    public override void Start(Ride ride) => ride.TransitionTo(InProgressState.Instance);
}

public sealed class InProgressState : RideState
{
    public static readonly InProgressState Instance = new();
    private InProgressState() { }

    public override void Complete(Ride ride, decimal fare)
    {
        ride.Charge(fare);
        ride.TransitionTo(CompletedState.Instance);
    }
}

public sealed class CompletedState : RideState
{
    public static readonly CompletedState Instance = new();
    private CompletedState() { }
    // Terminal: toda operação é rejeitada pela classe base.
}

public static class Program
{
    public static void Main()
    {
        var ride = new Ride();
        ride.Accept("driver-7");
        ride.Start();
        ride.Complete(18.50m);
        Console.WriteLine($"{ride.State.Name} {ride.DriverId} {ride.Fare}");   // Completed driver-7 18.50

        try { ride.Start(); }
        catch (InvalidOperationException e) { Console.WriteLine(e.Message); }  // Cannot start a ride that is Completed.
    }
}
```

As instâncias compartilhadas são campos estáticos apenas porque os estados não carregam dados. Se um estado precisar de dados por corrida, crie um novo objeto a cada transição e guarde esses dados nele.

Uma versão dirigida por tabela da mesma máquina, para quando só as transições variam e não há comportamento por estado:

```csharp
using System.Collections.Generic;

public enum RideStatus { Requested, Accepted, InProgress, Completed }
public enum RideEvent { Accept, Start, Complete }

public class RideMachine
{
    private static readonly Dictionary<(RideStatus, RideEvent), RideStatus> Transitions = new()
    {
        [(RideStatus.Requested, RideEvent.Accept)] = RideStatus.Accepted,
        [(RideStatus.Accepted, RideEvent.Start)] = RideStatus.InProgress,
        [(RideStatus.InProgress, RideEvent.Complete)] = RideStatus.Completed,
    };

    public RideStatus Status { get; private set; } = RideStatus.Requested;

    public bool TryFire(RideEvent e)
    {
        if (!Transitions.TryGetValue((Status, e), out var next)) return false;
        Status = next;
        return true;
    }
}
```

## Variações
- **Quem decide o próximo estado.** Se as regras são fixas, o contexto pode guardá-las. Costuma ser mais flexível deixar cada estado escolher o seu sucessor, como acima. O custo é que os estados passam a conhecer uns aos outros.
- **Máquina dirigida por tabela.** Uma tabela mapeia (estado, evento) para o próximo estado. As regras viram dados e são fáceis de ler como um todo, mas a consulta é mais lenta do que uma chamada virtual, a lógica fica menos explícita, e associar ações às transições exige trabalho extra. State modela o comportamento por estado; uma tabela modela apenas as transições.
- **Criar ou reutilizar objetos de estado.** Criar sob demanda serve a estados que carregam muitos dados e mudam pouco. Criar uma vez e reutilizar serve a transições frequentes, mas o contexto precisa conseguir alcançar todos os estados.
- **Compartilhamento.** Um estado sem campos de instância, cujo significado é dado inteiramente pelo seu tipo, pode ser compartilhado por todos os contextos, passando o contexto como argumento para que ele possa agir sobre ele.
- **Mudar de classe em tempo de execução.** Poucas linguagens permitem que um objeto troque de classe. Delegar a um objeto de estado substituível produz o mesmo efeito em C#.

## Riscos e alternativas em C#
- Para poucos estados e uma ou duas operações, uma expressão `switch` sobre um enum é mais curta e mais fácil de seguir. Passe para State quando o mesmo `switch` aparecer em vários métodos ou quando cada ramo crescer.
- Um `Instance` estático em cada estado é um singleton. Isso é aceitável para objetos sem estado, mas esconde a dependência. Passar as instâncias a partir do contexto, ou de um pequeno registro, facilita os testes.
- Objetos de estado que alteram o contexto por métodos públicos (`TransitionTo`, `AssignDriver`) enfraquecem os invariantes do contexto. Mantenha esses métodos `internal` quando os tipos compartilham um assembly, ou exponha apenas o que os estados precisam.
- Transições que envolvem I/O ou precisam ser seguras para threads exigem uma trava (lock) ou serialização em volta da mudança de estado. Uma atribuição de referência é atômica, mas a sequência ler-e-agir não é.
- As implementações padrão da classe base que lançam exceção transformam uma operação proibida em erro de execução. Se quem chama deve poder perguntar antes, adicione um método no estilo `CanStart` ou retorne um tipo de resultado em vez de lançar exceção.

## Padrões relacionados
- [Flyweight](../structural/flyweight.md): trata das condições e da técnica para compartilhar objetos de estado.
- [Singleton](../creational/singleton.md): objetos de estado compartilhados e sem estado costumam ser singletons.

**Além do livro:** o [Strategy](strategy.md) tem a mesma estrutura (um contexto que delega a um objeto substituível), mas intenção diferente. Uma estratégia é escolhida de fora e raramente muda sozinha; um estado se substitui a si mesmo à medida que o objeto avança em sua vida.

## Verificação
- Nenhum método do contexto contém `switch` ou `if` sobre um valor de status; cada chamada dependente de estado é um único repasse ao estado.
- Adicionar um estado significa adicionar uma classe e alterar apenas os estados que levam até ele.
- Cada transição ilegal é coberta por um teste que espera a rejeição, e cada transição legal por um teste que verifica o próximo estado.
- O contexto nunca fica com uma transição aplicada pela metade: o estado muda por uma única atribuição, depois que o trabalho do estado termina.
