# Mover Embelezamento para Decorator (Move Embellishment to Decorator)

Kerievsky (2004), cap. 7, p. 144. Padrão: Decorator. Direção: até, rumo a.

## Quando usar
Smells: Complexidade Condicional (Conditional Complexity), Obsessão por Primitivos (Primitive Obsession).

- Uma classe acumulou um embelezamento em torno de seu trabalho central (campos, métodos e flags extras, usados só às vezes, como auditoria ou retentativas), e condicionais decidem se ele é aplicado.
- Cada embelezamento vai para sua própria classe, que envolve um objeto do mesmo tipo. Os clientes os empilham em tempo de execução, só onde são necessários.
- Não use quando a classe tem dezenas de métodos públicos: um Decorator precisa implementar todo método público do tipo que envolve. Considere [replace-conditional-logic-with-strategy.md](replace-conditional-logic-with-strategy.md) no lugar.
- Contra Strategy: um Decorator envolve um objeto e compartilha sua interface, então um decorador pode envolver muitas classes, mas não ser compartilhado entre objetos; uma Strategy vive dentro de um objeto e pode ter qualquer interface, mas a classe hospedeira precisa conhecê-la.
- Desvantagens: o objeto decorado tem identidade diferente (verificações de tipo e casts no original falham), vários decoradores podem interferir uns com os outros dependendo da ordem, e a depuração precisa passar pelos invólucros. Se o embelezamento só protege o acesso, a estrutura é um Protection Proxy.

## Mecânica
Identifique a classe embelezada. Primeiro, confirme que o conjunto de métodos públicos que um decorador precisaria implementar é pequeno. Se não for, reduza-o ou escolha outra refatoração.

1. Encontre ou crie o tipo de envoltório: uma interface (ou classe) que declare todo método público que os clientes usam na classe embelezada. Prefira uma interface, já que uma classe base com estado repassaria esse estado aos decoradores. Crie-a com Unificar Interfaces (Unify Interfaces) ([unify-interfaces.md](../utilities/unify-interfaces.md)) e/ou Extrair Interface (Extract Interface; só na 1ª ed.; sem link). Faça a classe embelezada implementá-la e mude os clientes para depender dela.
2. Remova o condicional que aplica o embelezamento com [replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md), que geralmente começa com [replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md). Se for preciso um método de criação para ocultar o código de tipo, faça-o retornar o tipo de envoltório. Se o embelezamento precisar rodar antes e depois da lógica central, forme primeiro um template method ([form-template-method.md](../generalization/form-template-method.md)). Compile e teste.
3. Cada subclasse do passo 2 agora guarda um embelezamento. Transforme-a em uma classe que delega com Substituir Superclasse por Delegação (Replace Superclass with Delegate) ([replace-superclass-with-delegate.md](../../fowler/inheritance/replace-superclass-with-delegate.md)). A classe delegadora implementa o tipo de envoltório, seu campo delegado tem o tipo de envoltório, e você decide se o embelezamento roda antes ou depois de cada chamada delegada. Se o template method precisar de membros não públicos da classe embelezada, torne-os públicos e unifique a interface de novo. Se um método delegado puder devolver uma instância não decorada, decore-a antes de entregá-la. Compile e teste.
4. A classe delegadora cria o próprio delegado no construtor. Aplique Extrair Parâmetro (Extract Parameter) ([extract-parameter.md](../utilities/extract-parameter.md)) para que o chamador passe o objeto a ser envolvido, e depois remova os parâmetros do construtor que ficaram inúteis com [change-function-declaration.md](../../fowler/first-set/change-function-declaration.md). Compile e teste.

## Exemplo
Antes: uma classe ao mesmo tempo move dinheiro e, opcionalmente, envia notificações de status, decidindo com uma flag em cada método.

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

public class PaymentGateway
{
    private readonly bool _notify;
    private readonly Action<string>? _notifier;

    public PaymentGateway(bool notify, Action<string>? notifier)
    {
        _notify = notify;
        _notifier = notifier;
    }

    public PaymentResult Authorize(string account, decimal amount)
    {
        var result = new PaymentResult(amount > 0, $"auth-{account}-{amount}");
        if (_notify) _notifier!($"authorize {amount} on {account}: approved={result.Approved}");
        return result;
    }

    public PaymentResult Refund(string reference, decimal amount)
    {
        var result = new PaymentResult(amount > 0, reference);
        if (_notify) _notifier!($"refund {amount} of {reference}: approved={result.Approved}");
        return result;
    }
}
```

Depois: a classe central não sabe nada sobre notificações, e `NotifyingPaymentGateway` envolve qualquer `IPaymentGateway`. Os clientes que querem notificações envolvem o gateway na criação: `IPaymentGateway g = new NotifyingPaymentGateway(new PaymentGateway(), messages.Add);`. Um segundo decorator (retentativa, limitação de taxa) envolve o primeiro do mesmo jeito, e então a ordem em que se envolve passa a importar.

```csharp
using System;

public interface IPaymentGateway
{
    PaymentResult Authorize(string account, decimal amount);
    PaymentResult Refund(string reference, decimal amount);
}

public class PaymentGateway : IPaymentGateway
{
    public PaymentResult Authorize(string account, decimal amount) =>
        new(amount > 0, $"auth-{account}-{amount}");

    public PaymentResult Refund(string reference, decimal amount) =>
        new(amount > 0, reference);
}

public class NotifyingPaymentGateway : IPaymentGateway
{
    private readonly IPaymentGateway _inner;
    private readonly Action<string> _notifier;

    public NotifyingPaymentGateway(IPaymentGateway inner, Action<string> notifier)
    {
        _inner = inner;
        _notifier = notifier;
    }

    public PaymentResult Authorize(string account, decimal amount)
    {
        var result = _inner.Authorize(account, amount);
        _notifier($"authorize {amount} on {account}: approved={result.Approved}");
        return result;
    }

    public PaymentResult Refund(string reference, decimal amount)
    {
        var result = _inner.Refund(reference, amount);
        _notifier($"refund {amount} of {reference}: approved={result.Approved}");
        return result;
    }
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A classe sem decorator tem um teste sem nenhuma notificação, e o decorator tem um teste com um gateway interno falso que verifica se as chamadas são repassadas sem alteração.
- Busque `is` / `as` / casts para a classe com embelezamento: esses chamadores quebram quando o objeto é envolvido.
