# Visitor

Gamma et al. (1995), cap. 5, p. 331. Categoria: comportamental de objeto.

## Intenção
Empacotar uma operação sobre os elementos de uma estrutura de objetos em um objeto separado, para que novas operações possam ser adicionadas sem mudar as classes dos elementos.

## Quando compensa
- Uma estrutura guarda muitas classes com interfaces diferentes, e as operações dependem da classe concreta de cada elemento.
- Muitas operações não relacionadas (preço, renderização, auditoria) poluiriam as classes dos elementos. Cada operação ganha uma classe visitor que mantém seu código e seus dados de trabalho juntos.
- As classes dos elementos raramente mudam, mas novas operações sobre elas são adicionadas com frequência.
- A estrutura é compartilhada por várias aplicações, e cada aplicação deve receber apenas as operações de que precisa.
- Benefícios: uma nova operação é uma nova classe; o código relacionado fica em um lugar, o não relacionado fica separado; um visitor pode acumular estado enquanto percorre a estrutura; ele pode visitar elementos que não compartilham uma classe base comum.
- Custos: adicionar uma nova classe de elemento é caro, porque a interface do visitor e todos os visitors precisam mudar; os elementos geralmente precisam expor estado suficiente para que os visitors funcionem, o que enfraquece o encapsulamento.
- Não vale a pena quando os tipos de elemento mudam mais do que as operações: coloque a operação nos próprios elementos.

## Participantes em C#
- **Visitor** (`IInvoiceVisitor`): interface com um método `Visit` para cada classe de elemento.
- **ConcreteVisitor** (`TotalCalculator`, `TextRenderer`): implementa uma operação sobre a estrutura inteira e mantém seu estado acumulado em campos.
- **Element** (`InvoiceLine`): classe abstrata com `Accept(IInvoiceVisitor)`.
- **ConcreteElement** (`SubscriptionLine`, `UsageLine`, `DiscountLine`): implementa `Accept` chamando o método `Visit` que corresponde ao seu próprio tipo.
- **ObjectStructure** (`Invoice`): a coleção de elementos. Oferece uma forma de entregar um visitor a todos eles.

## Exemplo (C#)
Uma fatura de SaaS é uma lista de linhas de três tipos: uma taxa de assinatura, uso medido e um desconto percentual. Calcular o total e renderizar são dois visitors. Uma terceira operação (um relatório de impostos, por exemplo) seria um novo visitor, sem mudança nas linhas.

```csharp
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

public interface IInvoiceVisitor
{
    void Visit(SubscriptionLine line);
    void Visit(UsageLine line);
    void Visit(DiscountLine line);
}

public abstract class InvoiceLine
{
    public abstract void Accept(IInvoiceVisitor visitor);
}

public sealed class SubscriptionLine : InvoiceLine
{
    public SubscriptionLine(string plan, decimal monthlyPrice)
    {
        Plan = plan;
        MonthlyPrice = monthlyPrice;
    }

    public string Plan { get; }
    public decimal MonthlyPrice { get; }

    public override void Accept(IInvoiceVisitor visitor) => visitor.Visit(this);   // primeiro despacho
}

public sealed class UsageLine : InvoiceLine
{
    public UsageLine(string metric, int units, decimal unitPrice)
    {
        Metric = metric;
        Units = units;
        UnitPrice = unitPrice;
    }

    public string Metric { get; }
    public int Units { get; }
    public decimal UnitPrice { get; }

    public override void Accept(IInvoiceVisitor visitor) => visitor.Visit(this);
}

public sealed class DiscountLine : InvoiceLine
{
    public DiscountLine(string label, decimal percent)
    {
        Label = label;
        Percent = percent;
    }

    public string Label { get; }
    public decimal Percent { get; }

    public override void Accept(IInvoiceVisitor visitor) => visitor.Visit(this);
}

public class Invoice
{
    private readonly List<InvoiceLine> _lines = new();

    public Invoice Add(InvoiceLine line)
    {
        _lines.Add(line);
        return this;
    }

    // A estrutura conduz o percurso.
    public void Accept(IInvoiceVisitor visitor)
    {
        foreach (var line in _lines) line.Accept(visitor);
    }
}

public class TotalCalculator : IInvoiceVisitor
{
    public decimal Total { get; private set; }   // estado acumulado durante o percurso

    public void Visit(SubscriptionLine line) => Total += line.MonthlyPrice;
    public void Visit(UsageLine line) => Total += line.Units * line.UnitPrice;
    public void Visit(DiscountLine line) => Total -= Total * line.Percent / 100m;   // vale para o que veio antes
}

public class TextRenderer : IInvoiceVisitor
{
    private readonly StringBuilder _text = new();

    public string Text => _text.ToString();

    public void Visit(SubscriptionLine line) => _text.AppendLine($"{line.Plan} plan: {Money(line.MonthlyPrice)}");
    public void Visit(UsageLine line) => _text.AppendLine($"{line.Metric}: {line.Units} x {Money(line.UnitPrice)}");
    public void Visit(DiscountLine line) => _text.AppendLine($"{line.Label}: -{line.Percent}%");

    private static string Money(decimal value) => value.ToString("0.00", CultureInfo.InvariantCulture);
}

public static class Program
{
    public static void Main()
    {
        var invoice = new Invoice()
            .Add(new SubscriptionLine("Team", 40m))
            .Add(new UsageLine("api calls (thousands)", 25, 0.8m))
            .Add(new DiscountLine("Annual contract", 10m));

        var totals = new TotalCalculator();
        invoice.Accept(totals);

        var renderer = new TextRenderer();
        invoice.Accept(renderer);

        Console.Write(renderer.Text);
        Console.WriteLine($"Total: {totals.Total.ToString("0.00", CultureInfo.InvariantCulture)}");   // 54.00
    }
}
```

O mesmo total com um `switch` sobre o tipo do elemento, que não precisa de `Accept` nem de interface de visitor:

```csharp
public static class PatternMatchingTotal
{
    public static decimal Of(IEnumerable<InvoiceLine> lines)
    {
        decimal total = 0;
        foreach (var line in lines)
        {
            switch (line)
            {
                case SubscriptionLine s: total += s.MonthlyPrice; break;
                case UsageLine u: total += u.Units * u.UnitPrice; break;
                case DiscountLine d: total -= total * d.Percent / 100m; break;
                default: throw new NotSupportedException(line.GetType().Name);
            }
        }
        return total;
    }
}
```

## Variações
- **Despacho duplo.** A operação que roda depende de dois tipos: o do visitor e o do elemento. `Accept` recebe o visitor e chama a sobrecarga `Visit` correspondente ao tipo do próprio elemento, que é como o código certo é escolhido sem uma verificação de tipo. Linguagens com despacho múltiplo precisam menos do padrão.
- **Quem percorre a estrutura.** Na maioria das vezes, a própria estrutura: uma lista chama `Accept` em cada elemento, e o `Accept` de uma árvore desce nos filhos. Um iterador separado é a outra opção, e o visitor também, o que serve a um percurso irregular ou que depende de resultados anteriores, ao preço de duplicar o percurso em cada visitor.
- **Sobrecargas ou nomes distintos.** `Visit(SubscriptionLine)` com sobrecargas é curto e mostra a simetria entre os casos; nomes como `VisitSubscription` tornam cada ponto de chamada explícito. Escolha um e mantenha.
- **Comportamento padrão.** Um visitor base abstrato pode dar a cada `Visit` um corpo vazio, para que um visitor concreto sobrescreva apenas os tipos de elemento que lhe interessam.
- **Valores de retorno.** Um `IInvoiceVisitor<TResult>` genérico retorna um resultado por elemento, em vez de acumulá-lo em um campo, o que torna o visitor reutilizável e elimina o estado compartilhado.

## Riscos e alternativas em C#
- Pattern matching: instruções `switch` e expressões sobre os tipos de elemento fazem o mesmo trabalho com muito menos código quando o conjunto de tipos de elemento é fechado e vive em um só assembly. O custo é que o compilador não obriga cada operação a tratar um novo elemento: sem um `default` que falhe (como acima), uma nova subclasse é ignorada em silêncio. Uma interface de visitor detecta isso em tempo de compilação, e essa é a principal vantagem que resta ao padrão em C#.
- C# tem despacho `dynamic` (`visitor.Visit((dynamic)element)`), que elimina `Accept`, mas custa velocidade e perde a verificação em tempo de compilação. Evite, exceto em código descartável.
- Toda assinatura `Visit` muda quando você adiciona uma classe de elemento. Se os elementos mudam com frequência, coloque o comportamento neles.
- Visitors leem o estado dos elementos, então propriedades que eram privadas passam a ser públicas. Exponha apenas o que os visitors precisam, como membros somente leitura.
- Um visitor com estado acumulado (como `TotalCalculator`) pode ser usado uma vez. Crie um novo para cada percurso, ou reinicie-o, e não compartilhe um entre threads.
- Estruturas profundas percorridas recursivamente podem estourar a pilha; use uma pilha explícita no percurso se a profundidade for ilimitada.

## Padrões relacionados
- [Composite](../structural/composite.md): visitors aplicam uma operação a uma estrutura montada como composite.
- [Interpreter](interpreter.md): um visitor pode executar a interpretação sobre a árvore sintática.
- [Iterator](iterator.md): pode conduzir o percurso, mas visita apenas elementos que compartilham um tipo; um visitor pode tratar tipos de elemento não relacionados.

## Verificação
- Uma nova operação sobre a estrutura é uma nova classe visitor, e nenhuma classe de elemento mudou.
- As classes de elemento não contêm código específico de operação (nada de preço ou formatação dentro delas).
- Adicionar uma classe de elemento falha na compilação até que cada visitor a trate, ou a alternativa com `switch` tem um `default` que falha e um teste o exercita.
- Cada visitor dá o mesmo resultado quando executado duas vezes sobre a mesma estrutura (o estado é reiniciado ou criado por percurso).
