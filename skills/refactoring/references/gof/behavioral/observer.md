# Observer

Gamma et al. (1995), cap. 5, p. 293. Também conhecido como: Dependents, Publish-Subscribe. Categoria: comportamental de objeto.

## Intenção
Permitir que um objeto (o sujeito) anuncie suas mudanças a qualquer número de dependentes (os observadores), sem conhecer quem são eles nem o que fazem com a notícia.

## Quando compensa
- Um aspecto de uma abstração depende de outro, e você quer variar e reutilizar cada um separadamente (um sensor e as telas que o mostram).
- Uma mudança em um objeto precisa chegar a outros, e o número de receptores é desconhecido ou muda em tempo de execução.
- O sujeito não deve presumir nada sobre os receptores, para que eles possam viver em camadas superiores sem quebrar a arquitetura em camadas.
- Benefícios: acoplamento mínimo e abstrato; difusão sem endereçamento; observadores podem ser adicionados ou removidos sem tocar no sujeito.
- Passivos: observadores não sabem uns dos outros, então uma mudança inocente pode disparar uma longa cascata de atualizações, difícil de rastrear. Um sinal genérico de "algo mudou" também obriga os observadores a descobrir o que mudou.
- Evite quando há um único receptor fixo: uma chamada direta ou um parâmetro delegate é mais claro.

## Participantes em C#
- **Subject** (`TemperatureSensor`): mantém a lista de observadores e oferece anexar e desanexar. Em C#, isso é um campo `event`, cujos `+=` e `-=` são as operações de anexar e desanexar.
- **Observer** (`EventHandler<ReadingChangedEventArgs>`): a interface de atualização. Um tipo delegate substitui a interface de um método.
- **ConcreteSubject** (`TemperatureSensor`): guarda o estado de interesse e dispara o evento quando ele muda.
- **ConcreteObserver** (`Dashboard`, `OverheatAlert`): assina um sujeito, lê do evento ou do remetente o que precisa e mantém o próprio estado consistente.

## Exemplo (C#)
Um sensor de temperatura em um sistema IoT dispara um evento a cada nova leitura. Um painel e uma regra de alerta assinam de forma independente. Ambos se desligam ao serem descartados, para que o sensor nunca os mantenha vivos por mais tempo do que o necessário.

```csharp
using System;
using System.Collections.Generic;

public class ReadingChangedEventArgs : EventArgs
{
    public ReadingChangedEventArgs(string sensorId, double celsius)
    {
        SensorId = sensorId;
        Celsius = celsius;
    }

    public string SensorId { get; }
    public double Celsius { get; }
}

public class TemperatureSensor
{
    private double _celsius;

    public TemperatureSensor(string id) => Id = id;

    public string Id { get; }

    // Subject side: subscribers attach with += and detach with -=.
    public event EventHandler<ReadingChangedEventArgs>? ReadingChanged;

    public void Report(double celsius)
    {
        if (celsius == _celsius) return;   // no change, no notification
        _celsius = celsius;                // state is consistent before notifying
        ReadingChanged?.Invoke(this, new ReadingChangedEventArgs(Id, celsius));
    }
}

public class Dashboard : IDisposable
{
    private readonly TemperatureSensor _sensor;
    private readonly Dictionary<string, double> _latest = new();

    public Dashboard(TemperatureSensor sensor)
    {
        _sensor = sensor;
        _sensor.ReadingChanged += OnReading;
    }

    public double? Latest(string sensorId) => _latest.TryGetValue(sensorId, out var v) ? v : null;

    private void OnReading(object? sender, ReadingChangedEventArgs e) => _latest[e.SensorId] = e.Celsius;

    public void Dispose() => _sensor.ReadingChanged -= OnReading;   // matches the +=
}

public class OverheatAlert : IDisposable
{
    private readonly TemperatureSensor _sensor;
    private readonly double _limit;

    public OverheatAlert(TemperatureSensor sensor, double limit)
    {
        _sensor = sensor;
        _limit = limit;
        _sensor.ReadingChanged += OnReading;
    }

    public bool Tripped { get; private set; }

    private void OnReading(object? sender, ReadingChangedEventArgs e)
    {
        if (e.Celsius > _limit) Tripped = true;
    }

    public void Dispose() => _sensor.ReadingChanged -= OnReading;
}

public static class Program
{
    public static void Main()
    {
        var sensor = new TemperatureSensor("freezer-1");
        using var dashboard = new Dashboard(sensor);
        using var alert = new OverheatAlert(sensor, limit: -10);

        sensor.Report(-18);
        sensor.Report(-5);

        Console.WriteLine($"{dashboard.Latest("freezer-1")} {alert.Tripped}");   // -5 True
    }
}
```

## Variações
- **Onde os observadores ficam guardados.** Uma lista dentro de cada sujeito é o mais simples. Se há muitos sujeitos e poucos observadores, uma tabela compartilhada de sujeito para observadores economiza memória, ao custo de um acesso mais lento.
- **Vários sujeitos por observador.** A atualização carrega o remetente (o argumento `sender` de `EventHandler`), então um único handler pode saber qual sujeito disparou.
- **Quem dispara a notificação.** Ou os métodos que mudam o estado notificam por conta própria (clientes não podem esquecer, mas uma rajada de mudanças gera uma rajada de atualizações), ou o cliente chama um método de notificação depois de um lote (menos atualizações, mas fácil de esquecer).
- **Push ou pull.** Push envia os detalhes nos dados do evento (o exemplo faz isso). Pull envia quase nada, e o observador lê o sujeito. Push acopla o sujeito ao que os observadores precisam; pull pode fazer os observadores trabalharem a mais.
- **Interesse por tipo de evento.** Exponha vários eventos (`ReadingChanged`, `Offline`) ou um filtro por tópico, para que os observadores recebam apenas o que pediram.
- **Estado autoconsistente primeiro.** Notifique como último passo de uma operação, depois que todos os campos foram atualizados. Em uma hierarquia de classes, dispare o evento a partir de um método não sobrescrevível que chama um passo sobrescrevível, para que uma subclasse não notifique no meio do caminho.
- **Um gerenciador de mudanças.** Quando muitos sujeitos e observadores dependem uns dos outros, um objeto separado pode coletar as mudanças e notificar cada observador uma única vez. Isso é um mediador para atualizações.
- **Sujeito que deixa de existir.** O sujeito pode disparar um evento final para que os observadores soltem sua referência.

## Riscos e alternativas em C#
- Use o recurso da linguagem: `event EventHandler<T>` para sujeito e observador, e `Action<T>` ou um delegate simples quando não for preciso um tipo de dados de evento. Escreva seu próprio par `ISubject`/`IObserver` apenas quando precisar de ordenação, filtragem ou estado por assinante. `IObservable<T>`/`IObserver<T>` existem na biblioteca base e servem a fluxos que também terminam ou falham.
- **Cada `+=` precisa de um `-=` correspondente.** O sujeito mantém uma referência forte ao alvo de cada handler. Um sujeito de vida longa (um sensor, um serviço singleton, um evento estático) mantém vivo todo assinante depois que o dono já não precisa dele: um vazamento de memória, e o objeto morto continua recebendo chamadas. Desassine em `Dispose`, em um gancho de ciclo de vida ou quando a tela fechar. Cuidado com lambdas, que não podem ser desanexadas a menos que você guarde o delegate em uma variável.
- **Handlers rodam de forma síncrona**, na thread que disparou o evento, um após o outro, antes de a chamada que disparou retornar. Um handler lento atrasa o sujeito; uma exceção em um handler interrompe os seguintes e aparece para quem disparou. Mantenha os handlers curtos, capture exceções dentro deles, ou repasse o trabalho a uma fila ou a um `Channel<T>`. Um handler `async void` retorna já no primeiro `await`, então o sujeito não pode esperá-lo nem ver suas exceções.
- Handlers podem anexar, desanexar ou alterar o sujeito enquanto o evento está sendo disparado. `?.Invoke` copia o delegate, então uma mudança de assinatura não corrompe a chamada em andamento, mas um handler removido durante a chamada ainda pode ser chamado uma vez.
- Em várias threads, a cópia do delegate é segura, mas os handlers rodam na thread que disparou. Redirecione para o contexto certo (uma thread de UI, por exemplo) dentro do handler.
- Cascatas: se um handler altera o sujeito, ou outro sujeito que realimenta o primeiro, podem surgir laços. Documente quais operações notificam.

## Padrões relacionados
- [Mediator](mediator.md): um gerenciador de mudanças que guarda as relações sujeito-observador atua como mediador. Observer espalha a comunicação entre objetos; Mediator a centraliza em um só.
- [Singleton](../creational/singleton.md): um gerenciador de mudanças costuma ser único e global, mas passe-o como parâmetro em vez de buscá-lo em uma variável global.

## Verificação
- O sujeito compila e roda com zero assinantes, e seu código não cita nenhum tipo concreto de observador.
- Adicionar um novo observador não exige mudança no sujeito nem nos outros observadores.
- Toda assinatura tem uma desassinatura em um caminho que realmente executa; depois do dispose, a lista de handlers do sujeito não referencia mais o observador.
- O sujeito está em estado consistente no momento em que cada notificação é disparada, e as operações que notificam estão documentadas.
