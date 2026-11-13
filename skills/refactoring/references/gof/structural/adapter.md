# Adapter

Gamma et al. (1995), cap. 4, p. 139. Também conhecido como: Wrapper. Categoria: estrutural de classe e de objeto.

## Intenção
Tornar utilizável, pela interface que o cliente espera, uma classe cuja interface não corresponde a essa expectativa. O adaptador traduz as chamadas, e a classe existente permanece inalterada.

## Quando compensa
- Você precisa reutilizar uma classe existente (um SDK de fornecedor, um serviço legado) cujos membros, unidades ou formatos de dados diferem da interface em que o seu código foi escrito.
- Você escreve um componente reutilizável que deve funcionar com classes que não podem ser previstas, e prefere aceitar uma interface enxuta a impor uma classe base a todos.
- Um único adaptador de objeto pode atender ao adaptado e a todas as suas subclasses. Ele também pode acrescentar um comportamento que o adaptado não tem.
- Custo: o objeto adaptado deixa de ser do tipo adaptado, então o código que espera o tipo original não pode receber o adaptador. Um adaptador de duas vias (que implementa as duas interfaces) resolve isso, ao custo de mais código.
- Dispense quando você controla o adaptado e pode simplesmente alterá-lo, ou quando a tradução é um único ponto de chamada (um lambda ou uma função local bastam).

## Participantes em C#
- **Target** (`IPaymentProcessor`): a interface em que o código cliente é escrito, uma interface C#.
- **Client** (`CheckoutService`): usa apenas o target.
- **Adaptee** (`LegacyGatewayClient`): a classe existente com interface incompatível. Ela permanece intacta.
- **Adapter** (`LegacyGatewayAdapter`): classe que implementa o target e guarda o adaptado em um campo (adaptador de objeto). C# não tem herança múltipla de classes, então a forma de classe é rara.

## Exemplo (C#)
Um checkout cobra por meio de `IPaymentProcessor`, com valores em decimal e um objeto de resultado. Um gateway legado recebe centavos inteiros e devolve uma string de status. O adaptador converte nos dois sentidos.

```csharp
using System;

public class PaymentResult
{
    public bool Approved { get; }
    public string Reference { get; }

    public PaymentResult(bool approved, string reference)
    {
        Approved = approved;
        Reference = reference;
    }
}

public interface IPaymentProcessor
{
    PaymentResult Charge(string customerId, decimal amount, string currency);
}

// Classe existente que não controlamos.
public class LegacyGatewayClient
{
    public string SubmitTransaction(string account, long amountInCents, string currencyCode)
    {
        return amountInCents > 0 ? "OK:" + Guid.NewGuid().ToString("N") : "DECLINED:invalid-amount";
    }
}

public class LegacyGatewayAdapter : IPaymentProcessor
{
    private readonly LegacyGatewayClient _gateway;

    public LegacyGatewayAdapter(LegacyGatewayClient gateway) => _gateway = gateway;

    public PaymentResult Charge(string customerId, decimal amount, string currency)
    {
        long cents = (long)Math.Round(amount * 100m, MidpointRounding.AwayFromZero);
        string raw = _gateway.SubmitTransaction(customerId, cents, currency);
        int separator = raw.IndexOf(':');
        string status = raw.Substring(0, separator);
        string reference = raw.Substring(separator + 1);
        return new PaymentResult(status == "OK", reference);
    }
}

public class CheckoutService
{
    private readonly IPaymentProcessor _payments;

    public CheckoutService(IPaymentProcessor payments) => _payments = payments;

    public string Pay(string customerId, decimal total)
    {
        PaymentResult result = _payments.Charge(customerId, total, "USD");
        return result.Approved ? "paid " + result.Reference : "refused " + result.Reference;
    }
}

public static class Program
{
    public static void Main()
    {
        IPaymentProcessor processor = new LegacyGatewayAdapter(new LegacyGatewayClient());
        var checkout = new CheckoutService(processor);
        Console.WriteLine(checkout.Pay("cust-42", 19.99m));
    }
}
```

## Variações
- **Adaptador de classe**: herda do adaptado e implementa o target. Pode sobrescrever o comportamento do adaptado, mas fica preso a uma classe concreta e não cobre as suas subclasses. Em C# funciona quando o adaptado não é `sealed`, e o adaptador então implementa a interface target sobre a classe base.
- **Quantidade de adaptação**: desde renomear métodos, passando por converter dados, até fornecer operações inteiras que o adaptado não tem (o adaptador então as implementa por conta própria).
- **Adaptador plugável**: um componente reutilizável identifica a interface mais estreita de que precisa a partir do objeto com que trabalha (por exemplo, "dê-me o rótulo de um nó e os seus filhos") e a obtém por uma de três rotas: membros abstratos que as subclasses preenchem, um objeto delegado que implementa uma interface pequena, ou delegates (`Func<>`) passados ao construtor.
- **Adaptador de duas vias**: implementa as duas interfaces, para que o objeto adaptado possa ser usado onde qualquer um dos tipos for esperado.

## Riscos e alternativas em C#
- Quando a adaptação envolve um ou dois membros, passe delegates `Func<>` ao consumidor em vez de definir uma interface e uma classe. Esta é a forma parametrizada do adaptador plugável.
- Coloque o adaptador na fronteira e registre-o no contêiner de injeção de dependência como implementação da interface target. Não deixe o tipo adaptado vazar para o restante do código, ou o adaptador não protege nada.
- Converta unidades, convenções de nulo e estilos de erro (strings de status, códigos de erro) dentro do adaptador, e transforme-os nas exceções ou tipos de resultado que o restante do código usa.
- Não deixe o adaptador crescer com regras de negócio. Quando ele passa a decidir coisas, vira um serviço com uma tradução dentro.

## Padrões relacionados
- [bridge.md](bridge.md): estrutura parecida, mas a Bridge é planejada desde o início para que uma abstração e suas implementações variem de forma independente. O adaptador corrige, depois do fato, uma incompatibilidade entre partes já existentes.
- [decorator.md](decorator.md): mantém a interface e acrescenta comportamento, então é transparente e pode ser empilhado. O adaptador muda a interface.
- [proxy.md](proxy.md): oferece a mesma interface do seu sujeito e controla o acesso a ele. O adaptador oferece uma interface diferente.
- [facade.md](facade.md): define uma interface nova e mais simples sobre um grupo de objetos. O adaptador reutiliza uma interface que já existe do lado do cliente.

## Verificação
- O código cliente compila apenas contra a interface target e não menciona mais o tipo adaptado.
- Um teste alimenta valores de borda (zero, arredondamento, uma resposta de recusa) pelo adaptador e verifica o resultado convertido, não só o caminho feliz.
- A classe adaptada não tem nenhuma mudança no seu código-fonte.
- Se você também injeta um target falso nos testes, os testes do cliente não precisam de adaptador algum.
