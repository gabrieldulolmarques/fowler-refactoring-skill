# Mediator

Gamma et al. (1995), cap. 5, p. 273. Categoria: comportamental de objeto.

## Intenção
Colocar as regras de interação de um grupo de objetos em um único objeto, para que os membros do grupo não se refiram uns aos outros. A interação pode então mudar sem tocar nos membros.

## Quando compensa
- Um conjunto de objetos se comunica de formas bem definidas, mas emaranhadas, e a teia de referências é difícil de acompanhar.
- Um objeto é difícil de reutilizar porque conhece e fala com muitos outros.
- Um comportamento espalhado por várias classes deveria ser customizável sem uma pilha de subclasses.
- Benefícios: os colaboradores se tornam reutilizáveis por conta própria, as ligações muitos-para-muitos viram um-para-muitos, e as regras de cooperação ficam em um único lugar com nome. Mudar as regras significa mudar ou trocar apenas o mediador.
- Passivo: a complexidade migra para o mediador, que pode crescer até virar um monólito. Fique de olho no tamanho dele.
- Não vale a pena para dois objetos, ou quando uma simples inscrição em evento basta.

## Participantes em C#
- **Mediator** (`ISignupMediator`): interface que os colaboradores usam para informar mudanças.
- **ConcreteMediator** (`SignupForm`): conhece seus colaboradores e implementa a coordenação.
- **Colleague** (`PlanSelector`, `CouponField`, `PayButton`): cada um conhece apenas o mediador e informa a ele, em vez de chamar outros colaboradores.

## Exemplo (C#)
Uma tela de cadastro de SaaS: a escolha do plano decide se um cupom é permitido, e o botão de pagamento só fica habilitado quando o formulário é válido. Os widgets não se conhecem. Uma única classe guarda as regras.

```csharp
using System;

public interface ISignupMediator
{
    void Changed(object colleague);
}

public class PlanSelector
{
    private readonly ISignupMediator _mediator;
    private string _plan = "free";

    public PlanSelector(ISignupMediator mediator) => _mediator = mediator;

    public string Plan
    {
        get => _plan;
        set
        {
            _plan = value;
            _mediator.Changed(this);
        }
    }
}

public class CouponField
{
    private readonly ISignupMediator _mediator;
    private string _code = "";

    public CouponField(ISignupMediator mediator) => _mediator = mediator;

    public bool Enabled { get; set; }

    public string Code
    {
        get => _code;
        set
        {
            _code = value;
            _mediator.Changed(this);
        }
    }
}

public class PayButton
{
    public bool Enabled { get; set; }
}

public class SignupForm : ISignupMediator
{
    public PlanSelector Plan { get; }
    public CouponField Coupon { get; }
    public PayButton Pay { get; }

    public SignupForm()
    {
        Plan = new PlanSelector(this);
        Coupon = new CouponField(this);
        Pay = new PayButton();
        Refresh();
    }

    public void Changed(object colleague) => Refresh();

    // All cooperation rules live here.
    private void Refresh()
    {
        bool paid = Plan.Plan != "free";
        Coupon.Enabled = paid;
        if (!paid && Coupon.Code != "") Coupon.Code = "";   // reports back, so guard against looping
        bool couponOk = Coupon.Code == "" || Coupon.Code.StartsWith("PROMO", StringComparison.Ordinal);
        Pay.Enabled = couponOk;
    }
}

public static class Program
{
    public static void Main()
    {
        var form = new SignupForm();
        form.Plan.Plan = "pro";
        form.Coupon.Code = "oops";
        Console.WriteLine(form.Pay.Enabled);   // False
        form.Coupon.Code = "PROMO10";
        Console.WriteLine(form.Pay.Enabled);   // True
    }
}
```

## Variações
- **Omitir o mediador abstrato.** Se os colaboradores só trabalham com um mediador, a interface não acrescenta nada. Mantenha-a quando os colaboradores precisarem ser reutilizados com mediadores diferentes.
- **Como os colaboradores falam com o mediador.** Ou o mediador assina os eventos dos colaboradores (ao estilo Observer, com `event` do C#), ou os colaboradores chamam um método específico do mediador e passam a si mesmos, de modo que o mediador sabe quem mudou. Passar o remetente é direto e fácil de depurar. Eventos mantêm os colaboradores livres de qualquer referência ao mediador.
- **Mediador para coordenar atualizações.** Um mediador pode ficar entre um conjunto de fontes e um conjunto de ouvintes para agrupar notificações e evitar trabalho redundante.

## Riscos e alternativas em C#
- Um mediador que conhece tudo vira uma classe deus. Divida-o por preocupação (um por tela, um por fluxo de trabalho) e mantenha nele decisões, não dados.
- Reentrância: um colaborador alterado pelo mediador pode informar de volta e disparar o mediador de novo. Torne a atualização idempotente ou proteja contra laços, como o exemplo faz.
- Um barramento de mensagens ou um agregador de eventos é um mediador com interface genérica. Ele desacopla mais, mas torna o fluxo mais difícil de rastrear. Use-o quando os participantes forem muitos e desconhecidos de antemão.
- Para um acoplamento simples de mão única (um valor muda, os outros reagem), `event` simples é mais leve do que um mediador.
- Com injeção de dependência, passe aos colaboradores a interface do mediador pelo construtor, como acima.

## Padrões relacionados
- [Facade](../structural/facade.md): também simplifica um grupo de objetos, mas seu protocolo é de mão única (os clientes chamam o subsistema), enquanto um mediador é multidirecional e os colaboradores o conhecem.
- [Observer](observer.md): colaboradores podem notificar o mediador por meio de notificações de observer.

## Verificação
- Nenhuma classe colaboradora se refere a outra classe colaboradora, apenas ao mediador.
- Um colaborador funciona em um teste com um mediador falso.
- Uma mudança de regra (uma nova dependência entre widgets) é feita apenas no mediador.
- O mediador continua de tamanho gerenciável e não guarda dados que pertencem a um colaborador.
