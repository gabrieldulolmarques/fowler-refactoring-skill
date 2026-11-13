# Combinar Funções em Transformação (Combine Functions into Transform)

Fowler (2018), cap. 6, p. 149. Nome anterior / outro nome: —. Inversa: —. Alternativa:
Combinar Funções em Classe (Combine Functions into Class) ([combine-functions-into-class.md](combine-functions-into-class.md)).

## Quando usar
Smells: Cirurgia com Espingarda (Shotgun Surgery), Dados Mutáveis (Mutable Data).

- Vários clientes derivam valores (um total, uma cobrança, um status) do mesmo registro de origem, e
  as fórmulas são repetidas ou ficam em auxiliares que ninguém conhece.
- Você quer um só lugar para consultar e alterar cada derivação: a transformação.
- Os dados de origem são somente leitura na prática (um relatório, um view model, uma entrada que só é lida).

Não use quando os clientes modificam a origem depois da transformação. Os campos derivados são
armazenados na cópia, então uma mudança posterior na origem os deixa desatualizados. Nesse caso use
Combinar Funções em Classe, em que os valores derivados são calculados sob demanda.

Escolha entre transformação e classe principalmente pelo estilo que a base de código já usa, com essa
única exceção.

## Mecânica
1. Crie uma função de transformação que receba o registro de origem e devolva uma cópia com os mesmos
   valores. Faça a cópia profunda se o registro guardar dados aninhados mutáveis.
2. Adicione um teste de que a transformação não altera o registro recebido.
3. Escolha uma derivação. Se a lógica dela ainda não for uma função, aplique antes Extrair Função (Extract Function).
4. Mova o corpo para a transformação, de modo que ele preencha um novo campo na cópia. Mova também qualquer auxiliar de que o
   corpo precise, ou torne-o acessível a partir da transformação.
5. Faça um cliente chamar a transformação e ler o novo campo em vez de calcular.
6. Compile e teste.
7. Repita os passos 3 a 6 para cada derivação restante e cada cliente restante. Uma derivação
   que se apoia em outra deve ler o campo da outra.
8. Quando nenhum cliente chamar mais o auxiliar antigo, apague-o ou aninhe-o na transformação. Internalize
   as variáveis que agora só copiam um campo.

## Exemplo

Antes: dois lugares calculam o mesmo subtotal.

```csharp
using System;

public class Cart
{
    public string Customer { get; }
    public int Units { get; }
    public decimal UnitPrice { get; }
    public bool IsMember { get; }

    public Cart(string customer, int units, decimal unitPrice, bool isMember)
    {
        Customer = customer;
        Units = units;
        UnitPrice = unitPrice;
        IsMember = isMember;
    }
}

public static class Reports
{
    private static decimal DiscountThreshold(bool isMember) => isMember ? 50m : 100m;

    public static decimal ItemsTotal(Cart cart)
    {
        var subtotal = cart.Units * cart.UnitPrice;
        return subtotal;
    }

    public static decimal DiscountGiven(Cart cart)
    {
        var subtotal = cart.Units * cart.UnitPrice;
        var discountable = Math.Max(0, subtotal - DiscountThreshold(cart.IsMember));
        return discountable * 0.2m;
    }
}
```

Depois: uma transformação guarda as duas derivações; os clientes leem campos.

```csharp
using System;

public class Cart
{
    public string Customer { get; }
    public int Units { get; }
    public decimal UnitPrice { get; }
    public bool IsMember { get; }

    public Cart(string customer, int units, decimal unitPrice, bool isMember)
    {
        Customer = customer;
        Units = units;
        UnitPrice = unitPrice;
        IsMember = isMember;
    }
}

public class EnrichedCart : Cart
{
    public decimal Subtotal { get; }
    public decimal DiscountableAmount { get; }

    public EnrichedCart(Cart source, decimal subtotal, decimal discountableAmount)
        : base(source.Customer, source.Units, source.UnitPrice, source.IsMember)
    {
        Subtotal = subtotal;
        DiscountableAmount = discountableAmount;
    }
}

public static class CartEnricher
{
    private static decimal DiscountThreshold(bool isMember) => isMember ? 50m : 100m;

    public static EnrichedCart Enrich(Cart cart)
    {
        var subtotal = cart.Units * cart.UnitPrice;
        var discountable = Math.Max(0, subtotal - DiscountThreshold(cart.IsMember));
        return new EnrichedCart(cart, subtotal, discountable);
    }
}

public static class Reports
{
    public static decimal ItemsTotal(Cart cart) => CartEnricher.Enrich(cart).Subtotal;

    public static decimal DiscountGiven(Cart cart) => CartEnricher.Enrich(cart).DiscountableAmount * 0.2m;
}
```

O comportamento é o mesmo. As fórmulas agora ficam em `Enrich`; um novo valor derivado é mais um
campo ali. `EnrichedCart` deriva de `Cart` e passa os valores da origem ao construtor base,
então pode ser usado onde um `Cart` é esperado. Se ele não deve herdar, torne-o um tipo independente
que repete os campos.

## Notas (C#)
- Esta refatoração é idiomática em JavaScript. Em C#, a transformação costuma ser uma função que
  devolve um `record` enriquecido novo (construído com um construtor, ou com um construtor de cópia
  quando deriva do record de origem; `with` só serve quando o tipo enriquecido é o mesmo tipo),
  então o original nunca é mutado e não é preciso cópia profunda (C# 9+; no Unity, um `record`
  posicional precisa de um shim de `IsExternalInit`).
- Records são rasos: se a origem guarda coleções ou objetos mutáveis, copie-os também.
- Se os dados de fato forem mutados, ou se as derivações precisarem do comportamento do objeto, prefira
  Combinar Funções em Classe (Combine Functions into Class).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A transformação deixa sua entrada inalterada (o teste do passo 2).
