# Bridge

Gamma et al. (1995), cap. 4, p. 151. Também conhecido como: Handle/Body. Categoria: estrutural de objeto.

## Intenção
Separar uma abstração da sua implementação em duas hierarquias ligadas por uma referência, para que cada uma possa ser estendida por conta própria.

## Quando compensa
- Você tem duas dimensões independentes de variação (por exemplo, o que uma mensagem significa e como ela é entregue), e criar uma subclasse para cada par multiplicaria as classes (`UrgentEmail`, `UrgentPush`, `ReminderEmail`, ...).
- A implementação deve poder ser escolhida ou trocada em tempo de execução, ou ocultada do código cliente.
- Benefícios: implementação e abstração podem ser estendidas separadamente, os clientes dependem apenas da abstração, e a implementação pode mudar sem tocar neles.
- Custo: mais uma camada de indireção, e a divisão precisa ser feita no ponto certo. O padrão é planejado desde o início; não é uma correção para duas classes que, por acaso, são incompatíveis.
- Não vale a pena quando há uma só implementação e nenhum sinal de que haverá mais. Uma interface simples basta, e a bridge pode vir depois.

## Participantes em C#
- **Abstraction** (`Notification`): classe abstrata que guarda uma referência ao implementador e define a operação de alto nível em termos dele.
- **RefinedAbstraction** (`SecurityAlert`, `DeliveryReminder`): subclasses que variam o comportamento de alto nível.
- **Implementor** (`IChannel`): interface com as operações primitivas de que a abstração precisa. Não precisa parecer com a interface da abstração.
- **ConcreteImplementor** (`EmailChannel`, `PushChannel`, `WebhookChannel`): classes que implementam `IChannel` para um meio de entrega específico.

## Exemplo (C#)
Notificações têm tipos (alerta de segurança, lembrete de entrega) e canais (e-mail, push, webhook). Cada tipo monta o seu texto e o envia pelo canal que recebeu. Adicionar um canal ou um tipo mexe em um só lugar.

```csharp
using System;

public interface IChannel
{
    void Send(string recipient, string title, string body);
}

public class EmailChannel : IChannel
{
    public void Send(string recipient, string title, string body) =>
        Console.WriteLine($"[email to {recipient}] {title}: {body}");
}

public class PushChannel : IChannel
{
    public void Send(string recipient, string title, string body) =>
        Console.WriteLine($"[push to device of {recipient}] {title}");
}

public class WebhookChannel : IChannel
{
    private readonly string _url;

    public WebhookChannel(string url) => _url = url;

    public void Send(string recipient, string title, string body) =>
        Console.WriteLine($"[POST {_url}] {{\"to\":\"{recipient}\",\"title\":\"{title}\"}}");
}

public abstract class Notification
{
    protected IChannel Channel { get; }

    protected Notification(IChannel channel) => Channel = channel;

    public abstract void Notify(string recipient);
}

public class SecurityAlert : Notification
{
    private readonly string _location;

    public SecurityAlert(IChannel channel, string location) : base(channel) => _location = location;

    public override void Notify(string recipient) =>
        Channel.Send(recipient, "New sign-in", $"A sign-in from {_location} was detected.");
}

public class DeliveryReminder : Notification
{
    private readonly DateTime _eta;

    public DeliveryReminder(IChannel channel, DateTime eta) : base(channel) => _eta = eta;

    public override void Notify(string recipient) =>
        Channel.Send(recipient, "Your package arrives soon", $"Expected at {_eta:HH:mm}.");
}

public static class Program
{
    public static void Main()
    {
        Notification a = new SecurityAlert(new EmailChannel(), "Lisbon");
        Notification b = new DeliveryReminder(new PushChannel(), new DateTime(2026, 1, 5, 14, 30, 0));
        Notification c = new SecurityAlert(new WebhookChannel("https://hooks.example/ops"), "Oslo");
        a.Notify("ana");
        b.Notify("ana");
        c.Notify("ops");
    }
}
```

## Variações
- **Implementador único**: quando há só uma implementação, o implementador abstrato pode ser descartado. A separação ainda permite que essa implementação mude sem tocar nos clientes.
- **Escolha do implementador**: a abstração pode escolhê-lo no construtor a partir de parâmetros, começar com uma implementação padrão e trocar depois (por exemplo, pelo tamanho ou pela carga), ou pedir a uma fábrica para nunca citar uma classe concreta. Em C#, a forma mais simples é a injeção pelo construtor, com a escolha feita na raiz de composição ou por um contêiner de DI.
- **Implementadores compartilhados**: vários objetos de abstração podem guardar a mesma instância de implementador. Os implementadores costumam ser sem estado ou seguros para threads, para que o compartilhamento seja seguro.
- **Referência de volta**: o implementador pode precisar avisar a abstração sobre eventos (uma mensagem foi rejeitada); dê a ele um evento ou um callback, não o tipo concreto.

## Riscos e alternativas em C#
- Se o implementador precisa de apenas uma operação, um delegate (`Action<string, string, string>`) pode substituir a interface. Mantenha a interface quando ela tiver vários membros ou precisar de estado e testes próprios.
- A injeção de dependência já oferece a bridge de graça: a abstração recebe a interface no construtor. O padrão serve principalmente para enxergar os dois eixos e mantê-los separados.
- Não deixe as subclasses de `Notification` testar o tipo do canal (`if (Channel is EmailChannel)`). Isso anula o desacoplamento; coloque a diferença na interface.
- Separar cedo demais adiciona interfaces que ninguém usa. Faça isso quando o segundo eixo aparecer, não antes.

## Padrões relacionados
- [abstract-factory.md](../creational/abstract-factory.md): pode criar e configurar uma bridge específica, para que as abstrações não citem implementadores concretos.
- [adapter.md](adapter.md): parece parecido, mas reconcilia classes existentes e não relacionadas, depois do fato. A Bridge é uma decisão de design tomada de antemão.

## Verificação
- Adicionar um canal não exige mudança em `Notification` nem em suas subclasses; adicionar um tipo não exige mudança nos canais.
- O número de classes cresce como tipos mais canais, não como tipos vezes canais.
- Nenhuma abstração refinada verifica o tipo concreto do seu implementador.
- Os testes de um tipo usam um `IChannel` falso e verificam o que foi enviado.
