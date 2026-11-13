# Substituir Flag de Controle por Break (Replace Control Flag with Break)

Fowler (2018), só na edição web (não está no livro impresso); resumo em https://refactoring.com/catalog/replaceControlFlagWithBreak.html. Nome anterior / outro nome: Remove Control Flag. Inversa: —.

## Quando usar
Uma variável booleana existe apenas para conduzir o laço: ela é definida quando algo acontece e depois
a condição do laço ou um `if` em torno do corpo a lê para pular o trabalho restante. O leitor
precisa acompanhar a flag ao longo das iterações para ver quando o laço realmente termina.

Smell: nenhum específico (só na edição web).

Substitua a flag por uma saída direta: `break` para sair do laço. Use `return` quando o laço
estiver no fim de uma função (muitas vezes depois de Extrair Função (Extract Function)). `continue` só serve quando a flag
protege o restante de uma única iteração e não as seguintes.
Não use quando a flag for lida depois do laço para um propósito real; então ela é um resultado,
não uma flag de controle, e talvez seja melhor mantida ou retornada por uma função extraída.

## Mecânica
1. Considere extrair o código que usa a flag para uma função própria ([extract-function.md](../first-set/extract-function.md)), para que `return` fique disponível como saída.
2. Para cada lugar que define a flag, substitua a atribuição pela instrução de controle correspondente: em geral `return` ou `break`, e `continue` só quando a flag protegia apenas o restante de uma iteração. Antes de cada mudança, verifique que nada entre a atribuição e o fim da iteração, e nada depois do laço, precisa rodar depois que a flag é definida. Compile e teste após cada uma.
3. Quando nenhum lugar definir mais a flag, tire-a da condição do laço ou do `if` que a protegia, e apague a sua declaração. Compile e teste.

## Exemplo
Antes:

```csharp
using System.Collections.Generic;

public class Promotion
{
    public decimal MinimumSubtotal { get; }
    public Promotion(decimal minimumSubtotal) => MinimumSubtotal = minimumSubtotal;
}

public class Cart
{
    public decimal Subtotal { get; }
    public Cart(decimal subtotal) => Subtotal = subtotal;
}

public interface IPromotionLog
{
    void Apply(Promotion promotion, Cart cart);
}

public class PromotionApplier
{
    public void ApplyFirstEligible(IEnumerable<Promotion> promotions, Cart cart, IPromotionLog log)
    {
        bool applied = false;
        foreach (var promotion in promotions)
        {
            if (!applied)
            {
                if (cart.Subtotal >= promotion.MinimumSubtotal)
                {
                    log.Apply(promotion, cart);
                    applied = true;
                }
            }
        }
    }
}
```

Depois:

```csharp
public class PromotionApplier
{
    public void ApplyFirstEligible(IEnumerable<Promotion> promotions, Cart cart, IPromotionLog log)
    {
        foreach (var promotion in promotions)
        {
            if (cart.Subtotal >= promotion.MinimumSubtotal)
            {
                log.Apply(promotion, cart);
                break;
            }
        }
    }
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda: o laço continua parando no mesmo elemento, e nada após o ponto de saída executava antes.
