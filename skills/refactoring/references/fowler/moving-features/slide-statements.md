# Deslocar Instruções (Slide Statements)

Fowler (2018), cap. 8, p. 223. Nome anterior / outro nome: Consolidate Duplicate Conditional Fragments. Inversa: —.

## Quando usar
Smells: Código Duplicado (Duplicated Code), Dados Mutáveis (Mutable Data) (e como passo dentro de Função Longa (Long Function)).
- Linhas que tocam os mesmos dados estão separadas por linhas que tocam outra coisa.
- Uma variável é declarada bem acima do seu primeiro uso (declare-a logo antes de ser necessária).
- Você quer extrair um grupo de linhas, mas elas estão intercaladas com outro código. Deslocá-las para junto antes torna a extração possível.
- As mesmas instruções aparecem no início ou no fim de todos os ramos de uma condicional.

**Além do livro:** não vale a pena se o deslocamento não puder ser feito com segurança em passos pequenos: faça outra preparação antes (por exemplo, Dividir Variável (Split Variable) em uma variável reutilizada) e volte.

## Mecânica
1. Escolha a posição de destino para o fragmento (a instrução ou o bloco que você vai mover).
2. Verifique se há interferência em cada instrução entre o fragmento e o destino. Desista deste deslocamento se qualquer uma destas condições valer:
   - Subindo: o fragmento passaria pela declaração ou atribuição de algo que ele lê.
   - Descendo: o fragmento passaria por uma instrução que lê algo que o fragmento define ou altera.
   - O fragmento passaria por uma instrução que modifica algo que o fragmento lê ou escreve.
   - O fragmento modifica algo que uma instrução intermediária lê.
   Instruções sem efeitos colaterais podem ser reordenadas livremente. Cuidado com chamadas: só trate uma chamada como livre de efeitos colaterais se você souber que é.
3. Recorte o fragmento e cole-o no destino.
4. Compile e execute os testes.
5. Se um teste falhar, desfaça e tente de novo com um passo menor: desloque por cima de menos instruções ou mova um fragmento menor. Se ainda falhar, o deslocamento talvez ainda não valha a pena.

Deslocando para fora de uma condicional: quando as mesmas instruções terminam (ou começam) todos os ramos e não dependem de qual ramo rodou de um jeito que mude o comportamento, remova-as de cada ramo e ponha uma cópia depois (ou antes) da condicional. Deslocar para dentro de uma condicional é o inverso e repete o fragmento em cada ramo.

## Exemplo
Antes: as linhas do desconto estão misturadas com as da sobretaxa, e `surcharge` é declarada cedo demais.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Courier
{
    public bool IsPartner { get; set; }
}

public class Parcel
{
    public decimal WeightKg { get; set; }
    public decimal RatePerKg { get; set; }
}

public class Shipment
{
    public Courier Courier { get; set; } = new();
    public List<Parcel> Parcels { get; set; } = new();
    public decimal DistanceKm { get; set; }
}

public class CostCalculator
{
    public decimal DeliveryCost(Shipment shipment)
    {
        decimal surcharge;
        var courier = shipment.Courier;
        decimal discount = 0m;
        var baseCost = shipment.Parcels.Sum(p => p.WeightKg * p.RatePerKg);
        surcharge = shipment.DistanceKm * 0.2m;
        if (courier.IsPartner) discount = baseCost * 0.1m;
        if (baseCost > 500m) surcharge = 0m;
        return baseCost - discount + surcharge;
    }
}
```

Depois: cada declaração fica junto do seu uso, e as linhas do desconto ficam adjacentes, prontas para Extrair Função.

```csharp
using System.Linq;

public class CostCalculator
{
    public decimal DeliveryCost(Shipment shipment)
    {
        var baseCost = shipment.Parcels.Sum(p => p.WeightKg * p.RatePerKg);

        var courier = shipment.Courier;
        decimal discount = 0m;
        if (courier.IsPartner) discount = baseCost * 0.1m;

        decimal surcharge = shipment.DistanceKm * 0.2m;
        if (baseCost > 500m) surcharge = 0m;

        return baseCost - discount + surcharge;
    }
}
```

Por que foi seguro: `baseCost` é declarada antes de tudo o que a lê, e as linhas da sobretaxa leem e escrevem apenas `surcharge`, `shipment` e `baseCost`, nenhum dos quais as linhas do desconto alteram.

Caso condicional, antes e depois (mesmo comportamento):

```csharp
using System.Collections.Generic;

public class Route
{
    public bool HasCapacity(Parcel parcel) => parcel.WeightKg <= 20m;
    public void Add(Parcel parcel) { }
    public void Defer(Parcel parcel) { }
}

public class Dispatcher
{
    private readonly List<string> _auditLog = new();

    public void AssignBefore(Route route, Parcel parcel, string trackingCode)
    {
        if (route.HasCapacity(parcel))
        {
            route.Add(parcel);
            _auditLog.Add(trackingCode);
        }
        else
        {
            route.Defer(parcel);
            _auditLog.Add(trackingCode);
        }
    }

    public void AssignAfter(Route route, Parcel parcel, string trackingCode)
    {
        if (route.HasCapacity(parcel))
            route.Add(parcel);
        else
            route.Defer(parcel);
        _auditLog.Add(trackingCode);
    }
}
```

Isso só é válido porque os ramos não mudam o que a entrada de auditoria observa.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Se a cobertura do código movido for fraca, escreva os testes antes: um deslocamento que passa por estado mutável compartilhado é o tipo de mudança que os testes pegam melhor.
