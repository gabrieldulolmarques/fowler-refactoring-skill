# Chain of Responsibility

Gamma et al. (1995), cap. 5, p. 223. Categoria: comportamental de objeto.

## Intenção
Dar a vários objetos a chance de tratar uma requisição, para que o remetente não precise saber qual deles vai tratá-la. Os receptores são encadeados, e a requisição percorre os elos até que um deles a aceite.

## Quando compensa
- Mais de um objeto pode tratar uma requisição, e qual deles fará isso só se sabe em tempo de execução.
- Você quer enviar uma requisição sem nomear o receptor, ou o conjunto de possíveis receptores deve ser configurável.
- Benefício: remetente e receptores ficam desacoplados. Cada handler guarda uma única referência (seu sucessor) em vez de conhecer todos os candidatos, e a cadeia pode ser reordenada ou estendida em tempo de execução.
- Custo: nada garante que a requisição será tratada. Ela pode cair no fim da cadeia, ou a cadeia pode ser montada de forma errada. Decida o que significa uma requisição não tratada e torne isso visível.
- Não vale a pena quando o receptor é conhecido estaticamente, ou quando cada etapa precisa sempre rodar (isso é um pipeline, não uma cadeia: veja Variações).

## Participantes em C#
- **Handler** (`PaymentRoute`): classe abstrata (ou interface) que declara o método de tratamento e, opcionalmente, guarda o vínculo com o sucessor e o encaminhamento padrão.
- **ConcreteHandler** (`BrlInstantRoute`, `EurInstantRoute`, `ManualReviewRoute`): decide se a requisição é de sua competência. Se for, a trata; caso contrário, chama o sucessor.
- **Client** (`Program` no exemplo): monta a cadeia e envia a requisição ao primeiro handler.

## Exemplo (C#)
Uma requisição de pagamento instantâneo é encaminhada ao trilho que atende a sua moeda. Exatamente um handler assume cada requisição: a primeira rota que aceita a moeda, ou a rota de revisão manual, no fim da cadeia, como reserva. A requisição é um objeto, então novos dados não mudam a assinatura do handler.

```csharp
using System;

public class PaymentRequest
{
    public PaymentRequest(string payerId, decimal amount, string currency)
    {
        PayerId = payerId;
        Amount = amount;
        Currency = currency;
    }

    public string PayerId { get; }
    public decimal Amount { get; }
    public string Currency { get; }
}

public class PaymentDecision
{
    public PaymentDecision(bool approved, string reason)
    {
        Approved = approved;
        Reason = reason;
    }

    public bool Approved { get; }
    public string Reason { get; }
}

public abstract class PaymentRoute
{
    private PaymentRoute? _next;

    // Devolve o handler recebido, para que as chamadas possam ser encadeadas na montagem.
    public PaymentRoute SetNext(PaymentRoute next)
    {
        _next = next;
        return next;
    }

    public virtual PaymentDecision Handle(PaymentRequest request)
    {
        if (CanHandle(request))
        {
            return Process(request);
        }

        return _next != null
            ? _next.Handle(request)
            : new PaymentDecision(false, "no route accepts the payment");
    }

    protected abstract bool CanHandle(PaymentRequest request);

    protected abstract PaymentDecision Process(PaymentRequest request);
}

public class BrlInstantRoute : PaymentRoute
{
    protected override bool CanHandle(PaymentRequest request) => request.Currency == "BRL";

    protected override PaymentDecision Process(PaymentRequest request) =>
        new PaymentDecision(true, "sent through the domestic instant rail");
}

public class EurInstantRoute : PaymentRoute
{
    private readonly decimal _maxAmount;

    public EurInstantRoute(decimal maxAmount) => _maxAmount = maxAmount;

    protected override bool CanHandle(PaymentRequest request) =>
        request.Currency == "EUR" && request.Amount <= _maxAmount;

    protected override PaymentDecision Process(PaymentRequest request) =>
        new PaymentDecision(true, "sent through the euro instant rail");
}

// Reserva: aceita tudo o que as rotas anteriores não aceitaram.
public class ManualReviewRoute : PaymentRoute
{
    protected override bool CanHandle(PaymentRequest request) => true;

    protected override PaymentDecision Process(PaymentRequest request) =>
        new PaymentDecision(false, "queued for manual review");
}

public static class Program
{
    public static void Main()
    {
        var first = new BrlInstantRoute();
        first.SetNext(new EurInstantRoute(100_000m))
             .SetNext(new ManualReviewRoute());

        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 300m, "BRL")).Reason); // trilho instantâneo doméstico
        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 300m, "EUR")).Reason); // trilho instantâneo em euro
        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 300m, "JPY")).Reason); // revisão manual
    }
}
```

## Variações
- **Onde fica o vínculo.** A classe base do handler pode ter o campo do sucessor (como acima), ou cada handler concreto pode definir o seu. Quando os objetos já formam uma hierarquia (um nó e seu pai), a referência ao pai que já existe pode servir como sucessor, em vez de um vínculo novo.
- **Representação da requisição.** Um método fixo por tipo de requisição é simples e seguro quanto a tipos, mas fechado. Um código (string ou enum) com um switch é aberto, mas perde a segurança de tipos nos parâmetros. Um objeto de requisição, possivelmente com subclasses, agrupa os parâmetros e é o meio-termo usual. Os handlers testam o tipo com casamento de padrões (pattern matching) e repassam o que não conhecem.
- **Estender por herança.** Uma subclasse pode tratar as requisições que lhe interessam e chamar `base.Handle` para as demais, estendendo o tratamento da superclasse em vez de substituí-lo.
- **Tratada versus repassada.** Na forma clássica, o primeiro handler que aceita encerra o percurso. Uma variante deixa todos os handlers agirem e sempre repassarem (um pipeline). Escolha uma e nomeie-a com clareza, porque quem chama raciocina de forma diferente sobre cada uma.

## Riscos e alternativas em C#
- O fim silencioso da cadeia é a principal fonte de bugs. Retorne um resultado que diga "não tratada" (como a implementação padrão em `PaymentRoute` faz) ou lance uma exceção, em vez de não retornar nada.
- Um ciclo nos vínculos de sucessor faz o percurso rodar para sempre. Monte a cadeia em um único lugar.
- Para uma lista curta e fixa, um laço sobre `IEnumerable<PaymentRoute>` que retorna o primeiro resultado não nulo é mais simples do que handlers encadeados, e a ordem fica visível em uma linha. Use objetos encadeados quando os handlers precisarem decidir dinamicamente se repassam, ou quando a cadeia reaproveitar uma hierarquia já existente.
- Com injeção de dependência, registre os handlers em ordem e monte a cadeia na raiz de composição.
- Delegates também funcionam: uma lista de `Func<PaymentRequest, PaymentDecision?>` substitui a classe por etapa quando os handlers não têm estado próprio.

## Padrões relacionados
- [Composite](../structural/composite.md): o pai de um componente costuma ser o seu sucessor, então os dois são usados juntos.
- [Command](command.md): um objeto de requisição em uma cadeia costuma ser um comando.

**Além do livro:** o [Decorator](../structural/decorator.md) é estruturalmente parecido (um objeto seguinte envolvido), mas um decorator sempre adiciona comportamento e repassa, enquanto um handler pode interromper a requisição.

## Verificação
- Uma requisição que cada handler deve tratar é tratada exatamente por esse handler, com um teste por handler.
- Uma requisição que ninguém trata produz um resultado explícito de "não tratada", e não silêncio nem uma exceção vinda de um sucessor nulo.
- O remetente guarda referência apenas ao primeiro handler e compila sem se referir a nenhum handler concreto.
- Reordenar ou remover um handler muda o comportamento sem editar os outros handlers.
