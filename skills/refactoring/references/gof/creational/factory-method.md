# Factory Method

Gamma et al. (1995), cap. 3, p. 107. Também conhecido como: Virtual Constructor. Categoria: criacional de classe.

## Intenção
Dar a uma classe um método sobrescrevível que cria o seu produto, para que cada subclasse escolha a classe concreta e a classe base nunca a nomeie.

## Quando compensa
- Uma classe base sabe quando um objeto é necessário, mas não qual classe concreta criar.
- A classe criadora foi pensada para deixar a escolha do produto a cargo das suas subclasses.
- Uma classe repassa o trabalho a uma entre várias subclasses auxiliares, e você quer manter em um só lugar o conhecimento de qual auxiliar se aplica.
- Dá às subclasses um gancho: um método com uma implementação padrão sensata que uma subclasse pode sobrescrever para fornecer uma versão estendida.
- O código depende apenas da interface do produto, então novos produtos concretos não exigem mudança na classe base.
- Custo: você pode precisar criar uma subclasse do criador só para mudar o produto, o que adiciona um ponto de evolução.
- Não vale a pena quando a classe criada nunca muda. Use `new`, ou um delegate se a escolha é apenas um parâmetro.

## Participantes em C#
- **Product** (`INotification`): interface do que o método de fábrica devolve.
- **ConcreteProduct** (`EmailNotification`, `PushNotification`): implementações.
- **Creator** (`NotificationService`): classe abstrata (ou concreta) que declara o método de fábrica (`CreateNotification`) e o usa na sua própria lógica. Pode fornecer um produto padrão.
- **ConcreteCreator** (`EmailNotificationService`, `PushNotificationService`): sobrescreve o método de fábrica para devolver um produto específico.

## Exemplo (C#)
Um serviço de notificações envia a mensagem "pedido enviado". O fluxo é o mesmo para qualquer canal; só o objeto do canal muda, então a classe base deixa a criação para as subclasses.

```csharp
using System;

public interface INotification
{
    void Send(string recipient, string text);
}

public class EmailNotification : INotification
{
    public void Send(string recipient, string text) =>
        Console.WriteLine($"[email to {recipient}] {text}");
}

public class PushNotification : INotification
{
    public void Send(string recipient, string text) =>
        Console.WriteLine($"[push to device {recipient}] {text}");
}

public abstract class NotificationService
{
    // o método de fábrica
    protected abstract INotification CreateNotification();

    public void NotifyOrderShipped(string recipient, string orderId)
    {
        INotification notification = CreateNotification();
        notification.Send(recipient, $"Your order {orderId} has shipped.");
    }
}

public class EmailNotificationService : NotificationService
{
    protected override INotification CreateNotification() => new EmailNotification();
}

public class PushNotificationService : NotificationService
{
    protected override INotification CreateNotification() => new PushNotification();
}

public static class Program
{
    public static void Main()
    {
        NotificationService service = new PushNotificationService();
        service.NotifyOrderShipped("device-42", "A-1001");
    }
}
```

A forma parametrizada usa um único método de criação com uma chave, então não é necessária uma subclasse por produto. O conjunto de produtos fica fixo em um único `switch`, e uma chave desconhecida falha imediatamente.

```csharp
public static class NotificationFactory
{
    public static INotification Create(string channel) => channel switch
    {
        "email" => new EmailNotification(),
        "push" => new PushNotification(),
        _ => throw new ArgumentException("Unknown channel: " + channel, nameof(channel))
    };
}
```

## Variações
- **Criador abstrato ou implementação padrão.** Com um criador abstrato, as subclasses precisam fornecer o produto, porque não existe implementação padrão razoável. Com um criador concreto, o método de fábrica devolve um produto padrão e existe apenas para que as subclasses possam trocá-lo.
- **Método de fábrica parametrizado.** Um único método cria vários tipos, selecionados por um parâmetro (enum, string, tipo). Uma subclasse pode ampliar o conjunto tratando as suas próprias chaves e delegando o restante ao método base. Todos os produtos voltam como a interface comum, então quem precisar de mais deve fazer um cast.
- **Criador genérico.** Em C#, um `Creator<TProduct> where TProduct : INotification, new()` cria o produto sem uma subclasse por produto. Cobre o caso em que o único trabalho é escolher a classe.
- **Criação preguiçosa.** Não chame um método de fábrica virtual a partir do construtor da base: a classe derivada ainda não foi inicializada. Crie o produto no primeiro uso, por meio de uma propriedade (`Lazy<T>` se encaixa bem).
- **Nomenclatura.** Nomeie os métodos de fábrica para que sejam reconhecidos como tal (`Create...`, `Make...`).

## Riscos e alternativas em C#
- Um `Func<INotification>` passado ao construtor substitui uma hierarquia de subclasse por produto, e muitas vezes é tudo o que é preciso.
- Com injeção de dependência, o contêiner é a fábrica; injete `INotification` (ou uma busca por chave das implementações) em vez de escrever criadores.
- Chamar um método virtual a partir de um construtor é válido em C#, mas roda antes do corpo do construtor da classe derivada, então pode enxergar campos não inicializados. Evite.
- Um `switch` estático `Create(kind)` é mais simples do que uma hierarquia de criadores quando nenhum comportamento varia além da classe; o custo é que o `switch` precisa mudar a cada novo tipo.
- Mantenha os métodos de fábrica `protected` quando só o criador os usa, para que os clientes não sejam tentados a chamá-los.

## Padrões relacionados
- [Abstract Factory](abstract-factory.md): normalmente implementado como um conjunto de métodos de fábrica.
- [Template Method](../behavioral/template-method.md): métodos de fábrica costumam ser chamados a partir de métodos template (`NotifyOrderShipped` acima).
- [Prototype](prototype.md): evita criar subclasses do criador, mas então o produto precisa de uma operação de clonagem e, muitas vezes, de uma etapa de inicialização.

## Verificação
- O código do criador menciona apenas a interface do produto, nunca um produto concreto.
- Um novo produto é adicionado escrevendo uma subclasse (ou um braço de `switch`) sem editar a lógica do criador.
- Nenhum método de fábrica virtual é chamado a partir de um construtor.
- Se as subclasses diferem apenas pela classe que criam, verifique se um delegate ou um genérico seria mais simples.
