# Decompor Condicional (Decompose Conditional)

Fowler (2018), cap. 10, p. 260. Nome anterior / outro nome: —. Inversa: —. É Extrair Função (Extract Function)
([extract-function.md](../first-set/extract-function.md)) aplicada às partes de uma condicional.

## Quando usar
Smells: Função Longa (Long Function) (lógica condicional que esconde a intenção).

- A condição é uma expressão booleana composta e o leitor precisa descobrir o que ela significa.
- Os ramos guardam cálculos ou sequências de instruções cujo propósito não é óbvio.
- Um comentário acima do `if` explica a condição, ou comentários rotulam cada ramo.

O ponto é dar nomes: a condição ganha um nome para a pergunta de negócio que faz, e cada
ramo ganha um nome para o que produz. Pule quando a condição e os ramos já forem
de uma linha e lerem como a intenção.

## Mecânica
1. Extraia a condição para sua própria função (ou propriedade) com o nome da pergunta que ela faz.
   Compile e teste.
2. Extraia o corpo do ramo `then` para uma função com o nome do seu resultado. Compile e
   teste.
3. Extraia o corpo do ramo `else` da mesma forma. Compile e teste.
4. Para uma cadeia de `else if`, trate cada condição e ramo seguintes do mesmo jeito, um de cada vez.
5. Opcionalmente, quando cada ramo apenas atribui ou retorna um valor, reescreva a instrução como uma
   expressão ternária (`x = Condition() ? A() : B();`). Compile e teste.

## Exemplo
Antes:

```csharp
using System;

public class Parcel
{
    public decimal WeightKg { get; }
    public int Zone { get; }
    public decimal Subtotal { get; }

    public Parcel(decimal weightKg, int zone, decimal subtotal)
    {
        WeightKg = weightKg;
        Zone = zone;
        Subtotal = subtotal;
    }
}

public class Campaign
{
    public DateTime Start { get; }
    public DateTime End { get; }
    public decimal MinimumSubtotal { get; }
    public decimal FlatRate { get; }

    public Campaign(DateTime start, DateTime end, decimal minimumSubtotal, decimal flatRate)
    {
        Start = start;
        End = end;
        MinimumSubtotal = minimumSubtotal;
        FlatRate = flatRate;
    }
}

public class ShippingCalculator
{
    public decimal Cost(Parcel parcel, Campaign campaign, DateTime today)
    {
        decimal cost;
        if (today >= campaign.Start && today <= campaign.End && parcel.Subtotal >= campaign.MinimumSubtotal)
            cost = campaign.FlatRate;
        else
            cost = 4m + parcel.Zone * 1.5m + parcel.WeightKg * 0.8m;
        return cost;
    }
}
```

Depois:

```csharp
public class ShippingCalculator
{
    public decimal Cost(Parcel parcel, Campaign campaign, DateTime today)
    {
        return QualifiesForCampaign(parcel, campaign, today)
            ? CampaignRate(campaign)
            : ZoneAndWeightRate(parcel);
    }

    private static bool QualifiesForCampaign(Parcel parcel, Campaign campaign, DateTime today) =>
        today >= campaign.Start
        && today <= campaign.End
        && parcel.Subtotal >= campaign.MinimumSubtotal;

    private static decimal CampaignRate(Campaign campaign) =>
        campaign.FlatRate;

    private static decimal ZoneAndWeightRate(Parcel parcel) =>
        4m + parcel.Zone * 1.5m + parcel.WeightKg * 0.8m;
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
