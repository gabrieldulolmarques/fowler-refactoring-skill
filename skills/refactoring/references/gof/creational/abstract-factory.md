# Abstract Factory

Gamma et al. (1995), cap. 3, p. 87. Também conhecido como: Kit. Categoria: criacional de objeto.

## Intenção
Oferecer uma interface para criar uma família inteira de objetos relacionados, para que o código cliente nunca nomeie as classes concretas dessa família.

## Quando compensa
- O sistema não deve depender de como seus produtos são criados, compostos ou representados.
- O sistema precisa funcionar com uma entre várias famílias de produtos (por exemplo, um conjunto de classes por região ou por provedor) e não pode depender de qual delas está em uso.
- Os produtos de uma família só fazem sentido juntos, e você quer que o compilador e a fábrica, e não a disciplina da equipe, impeçam que sejam misturados.
- Você distribui uma biblioteca de produtos e quer expor apenas as interfaces deles, não as implementações.
- Trocar a família é uma decisão única, em um só lugar: a fábrica concreta é criada uma vez e entregue ao código que precisa dos produtos.
- Isola as classes concretas: os nomes dos produtos aparecem apenas dentro das fábricas concretas.
- Custo: adicionar um novo tipo de produto altera a interface da fábrica e todas as fábricas concretas.
- Não vale a pena quando existe apenas uma família, ou quando a "família" é um único produto (um [Factory Method](factory-method.md) simples ou um `Func<T>` bastam).

## Participantes em C#
- **AbstractFactory** (`ICheckoutFactory`): interface com um método de criação por tipo de produto.
- **ConcreteFactory** (`BrazilCheckoutFactory`, `GermanyCheckoutFactory`): classes que implementam a interface, cada uma devolvendo os produtos de uma família.
- **AbstractProduct** (`ITaxCalculator`, `IInvoiceFormatter`): uma interface por tipo de produto.
- **ConcreteProduct** (`BrazilTaxCalculator`, `GermanyInvoiceFormatter`, ...): as classes que uma fábrica concreta instancia.
- **Client** (`CheckoutService`): recebe um `ICheckoutFactory` e usa apenas as interfaces.

## Exemplo (C#)
Um checkout online precisa calcular o imposto e formatar a nota fiscal de acordo com o país do comprador. As regras de imposto e o layout da nota andam juntos, então cada país tem uma fábrica que cria os dois.

```csharp
using System;
using System.Globalization;

public interface ITaxCalculator
{
    decimal TaxFor(decimal amount);
}

public interface IInvoiceFormatter
{
    string Format(string orderId, decimal amount, decimal tax);
}

public interface ICheckoutFactory
{
    ITaxCalculator CreateTaxCalculator();
    IInvoiceFormatter CreateInvoiceFormatter();
}

public class BrazilTaxCalculator : ITaxCalculator
{
    public decimal TaxFor(decimal amount) => amount * 0.17m;
}

public class BrazilInvoiceFormatter : IInvoiceFormatter
{
    public string Format(string orderId, decimal amount, decimal tax) =>
        string.Format(new CultureInfo("pt-BR"), "Pedido {0}: total {1:N2}, imposto {2:N2}", orderId, amount + tax, tax);
}

public class GermanyTaxCalculator : ITaxCalculator
{
    public decimal TaxFor(decimal amount) => amount * 0.19m;
}

public class GermanyInvoiceFormatter : IInvoiceFormatter
{
    public string Format(string orderId, decimal amount, decimal tax) =>
        string.Format(new CultureInfo("de-DE"), "Bestellung {0}: Summe {1:N2}, MwSt. {2:N2}", orderId, amount + tax, tax);
}

public class BrazilCheckoutFactory : ICheckoutFactory
{
    public ITaxCalculator CreateTaxCalculator() => new BrazilTaxCalculator();
    public IInvoiceFormatter CreateInvoiceFormatter() => new BrazilInvoiceFormatter();
}

public class GermanyCheckoutFactory : ICheckoutFactory
{
    public ITaxCalculator CreateTaxCalculator() => new GermanyTaxCalculator();
    public IInvoiceFormatter CreateInvoiceFormatter() => new GermanyInvoiceFormatter();
}

public class CheckoutService
{
    private readonly ITaxCalculator _tax;
    private readonly IInvoiceFormatter _invoice;

    public CheckoutService(ICheckoutFactory factory)
    {
        _tax = factory.CreateTaxCalculator();
        _invoice = factory.CreateInvoiceFormatter();
    }

    public string Close(string orderId, decimal amount) =>
        _invoice.Format(orderId, amount, _tax.TaxFor(amount));
}

public static class Program
{
    public static void Main()
    {
        // o país é decidido uma única vez, no ponto de composição
        ICheckoutFactory factory = new GermanyCheckoutFactory();
        var checkout = new CheckoutService(factory);
        Console.WriteLine(checkout.Close("A-1001", 100m));
    }
}
```

## Variações
- **Métodos de fábrica dentro da fábrica.** A forma usual: cada método de criação é um método de fábrica, e uma fábrica concreta os implementa. Simples, mas exige uma classe de fábrica por família.
- **Fábrica baseada em protótipos.** A fábrica guarda um protótipo de cada produto e o clona sob demanda (veja [prototype.md](prototype.md)). Uma nova família é então apenas um novo conjunto de protótipos, sem nova classe de fábrica.
- **Criação parametrizada.** Um único método `Create(kind)` substitui a interface com um método por produto, então novos tipos de produto não exigem mudança na interface. O preço é a segurança de tipos: todo resultado volta como o tipo base comum, e quem precisar de mais deve fazer um cast.
- **Uma fábrica por família, normalmente uma instância.** A fábrica costuma ser criada uma vez e compartilhada. Recebê-la pelo construtor, como acima, basta; ela não precisa ser um [Singleton](singleton.md).

## Riscos e alternativas em C#
- Se a família é apenas "qual implementação desta interface", registre as implementações em um contêiner de injeção de dependência, escolhidas por configuração (país, tenant). O contêiner passa a ser a fábrica abstrata e nenhuma interface de fábrica precisa ser escrita à mão.
- Quando os tipos de produto são poucos e estáveis, um par de delegates (`Func<ITaxCalculator>`, `Func<IInvoiceFormatter>`) passado ao cliente faz o mesmo trabalho com menos cerimônia.
- Quando as famílias são escolhidas em tempo de execução por chave, mantenha um `Dictionary<string, ICheckoutFactory>` e falhe de forma explícita com uma chave desconhecida na fronteira, em vez de cair em uma família padrão.
- Não deixe os clientes receberem uma fábrica e depois ignorá-la, instanciando classes concretas em outro lugar; isso quebra a garantia de que uma família nunca é misturada.
- Adicionar um tipo de produto depois obriga a editar todas as fábricas. Se isso acontece com frequência, a fronteira da família provavelmente está errada.

## Padrões relacionados
- [Factory Method](factory-method.md): uma fábrica concreta costuma ser um conjunto de métodos de fábrica.
- [Prototype](prototype.md): uma forma alternativa de implementar a fábrica concreta, por clonagem.
- [Singleton](singleton.md): uma fábrica concreta costuma ser uma única instância compartilhada.
- [Builder](builder.md): também cria objetos complexos, mas passo a passo, e devolve o produto no fim; o Abstract Factory devolve cada produto de imediato e enfatiza famílias.

## Verificação
- Nenhum código cliente fora do ponto de composição cita uma classe de produto concreto ou de fábrica concreta.
- Trocar a família exige alterar uma única linha (o lugar onde a fábrica é criada).
- Um teste cria cada fábrica concreta e verifica se seus produtos pertencem juntos (mesma região, mesmas regras).
- Adicionar uma segunda família exigiu apenas classes novas, sem edições no cliente.
