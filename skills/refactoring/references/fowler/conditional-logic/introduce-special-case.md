# Introduzir Caso Especial (Introduce Special Case)

Fowler (2018), cap. 10, p. 289. Nome anterior / outro nome: Introduce Null Object. Inversa: —.

## Quando usar
Smells: Campo Temporário (Temporary Field).
- Muitos chamadores de uma estrutura de dados verificam o mesmo valor especial (null, uma string sentinela, um id mágico) e a maioria deles responde do mesmo jeito.
- Você quer essa resposta compartilhada em um só lugar, de modo que os chamadores simplesmente peçam ao objeto o que precisam.
- Null é o valor especial mais comum, daí o nome Null Object, mas a técnica funciona para qualquer caso especial ("desconhecido", "visitante", "sem plano").
- Mantenha uma verificação real onde um chamador realmente precisar de comportamento diferente; algumas exceções são normais.

## Mecânica
Parta de um contêiner (classe ou record) cuja propriedade, o sujeito, pode guardar o valor especial, e de clientes que o comparam com esse valor.

1. Adicione ao sujeito uma propriedade no estilo `IsSpecialCase`, retornando `false`.
2. Crie o tipo de caso especial apenas com essa propriedade, retornando `true`.
3. Aplique Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) à comparação com o valor especial e faça todo cliente chamar a nova função em vez de comparar diretamente. Opcionalmente, faça-a lançar exceção em valores inesperados durante a migração.
4. Faça o contêiner retornar o objeto de caso especial em vez do valor especial bruto (ou adicione-o por um passo de transformação para registros simples).
5. Altere o corpo da verificação extraída para usar a nova propriedade. Compile e teste.
6. Para cada cliente, encontre a reação compartilhada e mova-a para o tipo de caso especial (Combinar Funções em Classe (Combine Functions into Class), [combine-functions-into-class.md](../first-set/combine-functions-into-class.md), ou em Transformação, [combine-functions-into-transform.md](../first-set/combine-functions-into-transform.md)). Substitua a condicional do cliente por uma chamada simples. Teste após cada cliente.
7. Objetos relacionados que o caso especial precisa retornar são eles mesmos casos especiais (por exemplo, um objeto de histórico nulo). Escritas que os clientes costumavam pular viram operações vazias no caso especial.
8. Para os clientes que ainda precisam de comportamento diferente, aplique Internalizar Função (Inline Function) ([inline-function.md](../first-set/inline-function.md)) à verificação extraída, transformando-a em um teste direto da propriedade.
9. Aplique Remover Código Morto (Remove Dead Code) ([remove-dead-code.md](../moving-features/remove-dead-code.md)) à verificação extraída quando ninguém mais a chamar.

Trate o caso especial como um valor: ele não deve mudar após a criação, seja o que for que os objetos reais que ele substitui permitam. Se os clientes só leem, uma instância constante ou literal pode bastar.

## Exemplo
Antes: quatro clientes tratam um carrinho sem promoção. O exemplo pula a etapa de verificação extraída (passo 3) e vai direto para a forma final.

```csharp
public class Promotion
{
    public string Name { get; }
    public decimal DiscountRate { get; }
    public int DaysLeft { get; }
    public virtual int Redemptions { get; set; }

    public Promotion(string name, decimal discountRate, int daysLeft)
    {
        Name = name;
        DiscountRate = discountRate;
        DaysLeft = daysLeft;
    }
}

public class Cart
{
    private readonly Promotion? _promotion;
    public Cart(Promotion? promotion) => _promotion = promotion;
    public Promotion? Promotion => _promotion;
}

public class PromotionClients
{
    public string Label(Cart cart) => cart.Promotion == null ? "no promotion" : cart.Promotion.Name;
    public decimal Rate(Cart cart) => cart.Promotion == null ? 0m : cart.Promotion.DiscountRate;
    public int DaysLeft(Cart cart) => cart.Promotion == null ? 0 : cart.Promotion.DaysLeft;

    public void Redeem(Cart cart)
    {
        if (cart.Promotion != null) cart.Promotion.Redemptions++;
    }
}
```

Depois: a promoção ausente vira um objeto de caso especial.

```csharp
public class Promotion
{
    public virtual bool IsMissing => false;
    public string Name { get; }
    public decimal DiscountRate { get; }
    public int DaysLeft { get; }
    public virtual int Redemptions { get; set; }

    public Promotion(string name, decimal discountRate, int daysLeft)
    {
        Name = name;
        DiscountRate = discountRate;
        DaysLeft = daysLeft;
    }
}

public sealed class MissingPromotion : Promotion
{
    public MissingPromotion() : base("no promotion", 0m, 0) { }
    public override bool IsMissing => true;
    public override int Redemptions { get => 0; set { /* ignorado */ } }
}

public class Cart
{
    private readonly Promotion? _promotion;
    public Cart(Promotion? promotion) => _promotion = promotion;
    public Promotion Promotion => _promotion ?? new MissingPromotion();
}

public class PromotionClients
{
    public string Label(Cart cart) => cart.Promotion.Name;
    public decimal Rate(Cart cart) => cart.Promotion.DiscountRate;
    public int DaysLeft(Cart cart) => cart.Promotion.DaysLeft;
    public void Redeem(Cart cart) => cart.Promotion.Redemptions++;

    // o único cliente que deve se comportar de forma diferente mantém um teste explícito
    public string Banner(Cart cart) =>
        cart.Promotion.IsMissing ? "Join the newsletter for coupons" : $"{cart.Promotion.Name} ends soon";
}
```

`Banner` é um quinto cliente que não está no Antes; ele foi adicionado só para mostrar um cliente que mantém o seu próprio teste explícito. Fora ele, o comportamento é o mesmo: os chamadores recebem os mesmos valores de antes, e a escrita em uma promoção ausente continua sem efeito.

## Notas (C#)
- Com tipos de referência anuláveis ativados, o caso especial remove o `?` e as verificações de null nos pontos de chamada: a propriedade passa a não ser anulável e nunca retorna null.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
