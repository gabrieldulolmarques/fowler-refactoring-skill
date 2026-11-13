# Substituir Primitivo por Objeto (Replace Primitive with Object)

Fowler (2018), cap. 7, p. 174. Nome anterior / outro nome: Replace Data Value with Object, Replace Type Code with Class. Inversa: —.

## Quando usar
Smell: Obsessão por Primitivos (Primitive Obsession). Um simples `string` ou `int` representa um conceito de domínio, e a lógica sobre ele (validação, formatação, comparação, extração de partes) começa a aparecer ou está duplicada pela base de código. Encapsular o valor dá a essa lógica um lugar só dela.

Faça isso assim que quiser fazer mais com o valor do que imprimir ou armazenar. A primeira versão do tipo pode ser um invólucro (wrapper) simples, já que dá ao comportamento futuro um lugar onde ficar. É uma questão de julgamento: se o valor só é repassado e nunca inspecionado, um invólucro pode não valer a pena.

## Mecânica
1. Se o valor for um campo simples, aplique antes Encapsular Variável (Encapsulate Variable) ([encapsulate-variable.md](../first-set/encapsulate-variable.md)), para que todas as leituras e escritas passem por um único getter e setter.
2. Crie um pequeno tipo de valor que receba o primitivo existente em seu construtor e o exponha (em C#, `ToString()` ou uma conversão explícita costuma ler melhor do que uma propriedade genérica `Value`).
3. Faça o build e execute as verificações estáticas.
4. Altere o setter para construir o novo tipo e armazená-lo, mudando o tipo do campo.
5. Altere o getter para retornar o primitivo obtido do novo tipo, de modo que os chamadores ainda vejam o tipo antigo.
6. Faça o build e teste.
7. Renomeie os acessores originais ([change-function-declaration.md](../first-set/change-function-declaration.md)) se agora enganarem, por exemplo um getter que retorna uma string de descrição em vez do conceito.
8. Decida se é um objeto de valor ou um objeto de referência ([change-reference-to-value.md](../organizing-data/change-reference-to-value.md), [change-value-to-reference.md](../organizing-data/change-value-to-reference.md)).

A seguir, opcionalmente: adicione um acessor que retorne o novo objeto e migre os chamadores para ele um de cada vez, depois mova a validação, a comparação e a formatação para o tipo, tornando-o imutável com igualdade por valor. Cada uma dessas é uma pequena mudança testada por si só.

## Exemplo

Antes: o cupom de uma assinatura é uma string, e os chamadores a desmontam.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Subscription
{
    public string Coupon { get; set; } = "";
}

public static class Reports
{
    public static int CountByCampaign(IEnumerable<Subscription> subscriptions, string campaign) =>
        subscriptions.Count(s => s.Coupon.StartsWith(campaign + "-"));
}
```

Depois: um tipo de valor passa a cuidar da validação e da campanha.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public sealed class CouponCode
{
    private readonly string _value;

    public CouponCode(string value)
    {
        var parts = (value ?? "").Split('-');
        if (parts.Length != 2 || parts[0].Length == 0
            || !int.TryParse(parts[1], out var percent) || percent < 1 || percent > 100)
            throw new ArgumentException($"'{value}' is not a coupon code like SPRING-15");
        _value = value!;
        Campaign = parts[0];
        PercentOff = percent;
    }

    public string Campaign { get; }
    public int PercentOff { get; }
    public override string ToString() => _value;
}

public class Subscription
{
    private CouponCode _coupon;

    public Subscription(string coupon) => _coupon = new CouponCode(coupon);

    public CouponCode Coupon => _coupon;

    // Acessor antigo mantido para os chamadores existentes, renomeado porque agora devolve texto.
    public string CouponText
    {
        get => _coupon.ToString();
        set => _coupon = new CouponCode(value);
    }
}

public static class Reports
{
    public static int CountByCampaign(IEnumerable<Subscription> subscriptions, string campaign) =>
        subscriptions.Count(s => s.Coupon.Campaign == campaign);
}
```

Mesmo comportamento para códigos válidos; um código malformado agora é rejeitado no momento da
atribuição, e não descoberto mais tarde. A assinatura sempre é criada com um cupom, então `Coupon` nunca é nulo.

## Notas (C#)
- Um `string` ou `int` com significado vira um tipo próprio: um `record`, ou um `readonly record struct` para
  valores pequenos (C# 9+ para `record`, C# 10 para `readonly record struct`; no Unity precisa de um shim de
  `IsExternalInit`). Se os valores legais forem um conjunto fechado fixo, sem comportamento extra, um `enum`
  pode bastar.
- Um `record` oferece igualdade por valor de graça; mantenha o estado imutável.
- Um `readonly record struct` pode ser `default`, o que pula o construtor e a sua validação. Uma expressão
  `with` em um record também copia o estado sem rodar a validação. Use uma `sealed class` quando qualquer um
  desses casos importar.
- Um `enum` é mais fraco que um invólucro: qualquer inteiro pode ser convertido para ele sem verificação.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Faça uma busca pelas comparações e análises brutas do primitivo antigo (literais de string, `StartsWith`,
  `Substring`); nenhuma deve restar fora do novo tipo.
- Todo ponto de construção passa pelo construtor que valida.
