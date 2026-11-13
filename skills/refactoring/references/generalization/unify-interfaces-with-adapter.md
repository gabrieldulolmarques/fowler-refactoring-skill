# Unificar Interfaces com Adapter (Unify Interfaces with Adapter)

Kerievsky (2004), cap. 8, p. 247. Direção: até, rumo a. Padrão: Adapter (GoF, p. 139).

## Quando usar
Smells: Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces), Solução Destoante (Oddball Solution), Código Duplicado (Duplicated Code).

- Duas classes fazem o mesmo trabalho, ou um trabalho parecido, por interfaces diferentes, e um cliente que usa as duas precisa ser escrito duas vezes.
- O cliente seria mais simples se as duas tivessem a mesma aparência.
- Você não pode simplesmente renomear ou mover métodos até que eles coincidam, porque uma das classes pertence a uma biblioteca de terceiros, a um framework com muitos outros clientes, ou porque você não tem o código-fonte dela.
- Depois que as duas classes estão atrás de uma interface comum, o código duplicado do cliente pode ser unificado com refatorações como Formar Template Method (Form Template Method) ([form-template-method.md](form-template-method.md)) ou Introduzir Criação Polimórfica com Factory Method (Introduce Polymorphic Creation with Factory Method) ([introduce-polymorphic-creation-with-factory-method.md](../creation/introduce-polymorphic-creation-with-factory-method.md)).
- Não use quando você pode alterar diretamente uma das interfaces: renomear é mais barato do que acrescentar uma classe.

## Mecânica
O adaptado é a classe cuja interface o cliente não prefere. O adaptador é a classe que vai envolvê-la.

1. Extraia uma interface comum da classe cuja interface o cliente prefere (Extrair Interface (Extract Interface), só na 1ª ed.). Se essa classe tem métodos que recebem o próprio tipo, altere-os para receber a interface. Compile e teste.
2. No cliente que usa o adaptado, aplique Extrair Classe (Extract Class) ([extract-class.md](../encapsulation/extract-class.md)) para criar um adaptador primitivo: uma classe com um campo para o adaptado, um getter para ele e um construtor (ou setter) que o recebe.
3. Troque os campos, variáveis locais e parâmetros do cliente que são do tipo adaptado pelo tipo adaptador. Cada chamada agora primeiro obtém o adaptado a partir do adaptador. Compile e teste.
4. Para cada chamada distinta ao adaptado no cliente, aplique Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) para criar um método de invocação que recebe o adaptador como parâmetro e chama o adaptado por ele. Compile e teste após cada um.
5. Mova cada método de invocação para o adaptador com Mover Função (Move Function) ([move-function.md](../moving-features/move-function.md)), moldando-o como o método correspondente da interface comum. Se o corpo movido precisar de um valor do cliente, passe-o pelo construtor do adaptador, ou dê ao adaptador uma referência que ele possa consultar, em vez de acrescentar um parâmetro que tornaria a assinatura diferente. Se um parâmetro for inevitável, altere o método da interface para casar. Compile e teste; repita até o adaptador ter todos os métodos da interface.
6. Declare que o adaptador implementa a interface comum, e altere os métodos do adaptador que recebem um adaptador para receber a interface. Compile e teste.
7. Mude o cliente para usar a interface em todos os pontos, no lugar do tipo adaptador. Compile e teste. O cliente agora fala com as duas classes por um único tipo.

## Exemplo
Antes: um notificador envia recibos pelo nosso próprio `EmailSender` e, com uma cópia separada da lógica, pelo `SmsGateway` de terceiros, que não podemos alterar.

```csharp
using System.Collections.Generic;

public record Customer(string Name, string Email, string Phone);
public record SmsMessage(string Number, string Text);

public class EmailSender
{
    public List<string> Sent { get; } = new();
    public void Send(string to, string subject, string body) => Sent.Add($"{to}|{subject}|{body}");
}

// Terceiro: não pode ser alterado.
public sealed class SmsGateway
{
    public List<SmsMessage> Outbox { get; } = new();
    public void Transmit(SmsMessage message) => Outbox.Add(message);
}

public class ReceiptNotifier
{
    public void ByEmail(IEnumerable<Customer> customers, EmailSender sender, string orderId)
    {
        foreach (var c in customers)
            sender.Send(c.Email, "Receipt", $"Dear {c.Name}, order {orderId} is paid.");
    }

    public void BySms(IEnumerable<Customer> customers, SmsGateway gateway, string orderId)
    {
        foreach (var c in customers)
            gateway.Transmit(new SmsMessage(c.Phone, $"Dear {c.Name}, order {orderId} is paid."));
    }
}
```

Depois: os dois canais ficam atrás de `IMessageSender`. O adaptador envolve o gateway, e o notificador tem um único laço.

```csharp
using System.Collections.Generic;

public record Customer(string Name, string Email, string Phone);
public record SmsMessage(string Number, string Text);

public interface IMessageSender
{
    void Send(string to, string subject, string body);
}

public class EmailSender : IMessageSender
{
    public List<string> Sent { get; } = new();
    public void Send(string to, string subject, string body) => Sent.Add($"{to}|{subject}|{body}");
}

// Terceiro: não pode ser alterado.
public sealed class SmsGateway
{
    public List<SmsMessage> Outbox { get; } = new();
    public void Transmit(SmsMessage message) => Outbox.Add(message);
}

public class SmsGatewayAdapter : IMessageSender
{
    private readonly SmsGateway _gateway;
    public SmsGatewayAdapter(SmsGateway gateway) => _gateway = gateway;

    // SMS não tem assunto; o endereço é o número de telefone.
    public void Send(string to, string subject, string body) =>
        _gateway.Transmit(new SmsMessage(to, body));
}

public class ReceiptNotifier
{
    public void Notify(IEnumerable<Customer> customers, IMessageSender sender, bool useEmail, string orderId)
    {
        foreach (var c in customers)
            sender.Send(useEmail ? c.Email : c.Phone, "Receipt", $"Dear {c.Name}, order {orderId} is paid.");
    }
}
```

A flag `useEmail` mostra o que ainda é diferente: como obter o endereço. Se isso incomodar, dê à interface um membro que escolha o endereço, ou deixe o chamador passar a lista de endereços. Isso é um passo separado.

## Notas (C#)
- Prefira composição (um campo que guarda o adaptado, como acima) a herdar da classe de terceiros, que pode ser `sealed` e prende você à API dela.
- Mantenha o construtor do adaptador rigoroso: valide que o adaptado não é nulo, e coloque a tradução (nomes, unidades, tratamento de erros) no adaptador, não no cliente.
- Se a interface deve ser implementada por muitas classes que você controla, uma interface é o certo. Se você só precisa de um formato de função, `Action<...>` ou `Func<...>` podem substituir uma interface de um método.
- Registre o adaptador e a interface no seu container de DI, se usar um, para que os clientes recebam `IMessageSender` e nunca vejam o adaptado.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- As mesmas entradas produzem as mesmas mensagens de saída pelos dois canais que antes (compare `Sent` e `Outbox`), e nenhum código do cliente ainda cita o tipo adaptado.
