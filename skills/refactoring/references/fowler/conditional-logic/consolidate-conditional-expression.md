# Consolidar Expressão Condicional (Consolidate Conditional Expression)

Fowler (2018), cap. 10, p. 263. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
- Vários `if` seguidos, cada um com um teste diferente mas o mesmo resultado (mesmo valor de retorno, mesma ação).
- `if` aninhados sem `else`, em que só o mais interno faz algo.
- Você quer dar nome à regra combinada ("é elegível", "está bloqueado") extraindo-a depois ([extract-function.md](../first-set/extract-function.md)).

Não use quando as verificações forem responsabilidades independentes que apenas compartilham um resultado hoje. Fundi-las esconde que cada uma pode mudar por conta própria. Decomponha em vez disso, ou deixe-as separadas.

## Mecânica
1. Verifique que nenhuma das condições tem efeitos colaterais (sem escritas, sem chamadas que mudem estado ou consumam entrada). Se alguma tiver, separe antes a consulta do modificador ([separate-query-from-modifier.md](../refactoring-apis/separate-query-from-modifier.md)).
2. Escolha duas verificações adjacentes que compartilhem o resultado e una suas condições em um único `if`. Verificações consecutivas se unem com `||`; verificações aninhadas se unem com `&&`.
3. Compile e execute os testes.
4. Repita com a próxima verificação até restar uma única condição.
5. Considere extrair a condição combinada para uma função com um nome que revele a intenção ([extract-function.md](../first-set/extract-function.md)).

A ordem importa quando as condições podem lançar exceção ou são custosas: `||` e `&&` fazem curto-circuito como a sequência original fazia, então mantenha a ordem original da esquerda para a direita.

## Exemplo
Antes:

```csharp
using System;

public class Cart
{
    public decimal Subtotal { get; }
    public bool ContainsGiftCard { get; }

    public Cart(decimal subtotal, bool containsGiftCard)
    {
        Subtotal = subtotal;
        ContainsGiftCard = containsGiftCard;
    }
}

public class Coupon
{
    public DateTime ExpiresOn { get; }
    public decimal MinimumSubtotal { get; }
    public decimal Percentage { get; }
    public bool IsSingleUse { get; }

    public Coupon(DateTime expiresOn, decimal minimumSubtotal, decimal percentage, bool isSingleUse)
    {
        ExpiresOn = expiresOn;
        MinimumSubtotal = minimumSubtotal;
        Percentage = percentage;
        IsSingleUse = isSingleUse;
    }
}

public class CouponService
{
    public decimal Discount(Cart cart, Coupon coupon, DateTime today)
    {
        if (today > coupon.ExpiresOn) return 0m;
        if (cart.Subtotal < coupon.MinimumSubtotal) return 0m;
        if (cart.ContainsGiftCard) return 0m;

        return cart.Subtotal * coupon.Percentage;
    }
}
```

Depois de unir e depois extrair:

```csharp
public class CouponService
{
    public decimal Discount(Cart cart, Coupon coupon, DateTime today)
    {
        if (IsNotApplicable(cart, coupon, today)) return 0m;

        return cart.Subtotal * coupon.Percentage;
    }

    private static bool IsNotApplicable(Cart cart, Coupon coupon, DateTime today) =>
        today > coupon.ExpiresOn
        || cart.Subtotal < coupon.MinimumSubtotal
        || cart.ContainsGiftCard;
}
```

Forma aninhada, unida com `&&`:

```csharp
public class CouponBadge
{
    public void ShowBefore(Cart cart, Coupon coupon)
    {
        if (coupon.IsSingleUse)
            if (cart.Subtotal >= coupon.MinimumSubtotal)
                ShowBadge(cart);
    }

    public void ShowAfter(Cart cart, Coupon coupon)
    {
        if (coupon.IsSingleUse && cart.Subtotal >= coupon.MinimumSubtotal)
            ShowBadge(cart);
    }

    private void ShowBadge(Cart cart) { }
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
