# Builder

Gamma et al. (1995), cap. 3, p. 97. Categoria: criacional de objeto.

## Intenção
Separar o processo passo a passo de montagem de um objeto complexo da representação resultante, para que o mesmo processo possa produzir representações diferentes.

## Quando compensa
- O procedimento que decide quais partes criar e em que ordem deve ser reutilizável e independente de quais são as partes e de como são montadas.
- O mesmo procedimento precisa conseguir produzir saídas diferentes (CSV e JSON do mesmo relatório, por exemplo).
- A construção é uma sequência de passos, e o produto só fica completo no fim; o builder dá mais controle sobre esse processo do que uma única chamada de construtor.
- Mantém o código que monta uma representação em um único lugar, separado do código que decide o que montar.
- Não vale a pena quando um construtor com poucos parâmetros, ou um inicializador de objeto, já é claro. Builders se justificam com muitas partes opcionais ou com várias formas de saída.

## Participantes em C#
- **Builder** (`IReportBuilder`): interface com um método por passo de construção.
- **ConcreteBuilder** (`CsvReportBuilder`, `JsonReportBuilder`): implementa os passos, acumula o resultado e expõe um método para recuperá-lo.
- **Director** (`ReportDirector`): executa os passos de construção sobre qualquer builder que receber.
- **Product** (`string` aqui, mas pode ser qualquer classe): o objeto final. Builders diferentes costumam devolver tipos sem relação entre si, então não é exigida uma interface comum de produto.

## Exemplo (C#)
A exportação de um relatório precisa poder ser gerada como CSV ou JSON a partir das mesmas linhas. O director decide a ordem (título, depois linhas); cada builder decide o formato.

```csharp
using System.Collections.Generic;
using System.Globalization;
using System.Text;

public interface IReportBuilder
{
    void AddTitle(string title);
    void AddRow(string label, decimal value);
}

public class CsvReportBuilder : IReportBuilder
{
    private readonly StringBuilder _text = new();

    public void AddTitle(string title) => _text.AppendLine("# " + title);

    public void AddRow(string label, decimal value) =>
        _text.AppendLine(label + "," + value.ToString(CultureInfo.InvariantCulture));

    public string GetResult() => _text.ToString();
}

public class JsonReportBuilder : IReportBuilder
{
    private string _title = "";
    private readonly List<string> _rows = new();

    public void AddTitle(string title) => _title = title;

    public void AddRow(string label, decimal value) =>
        _rows.Add("{\"label\":\"" + label.Replace("\"", "\\\"") + "\",\"value\":" +
                  value.ToString(CultureInfo.InvariantCulture) + "}");

    public string GetResult() =>
        "{\"title\":\"" + _title.Replace("\"", "\\\"") + "\",\"rows\":[" + string.Join(",", _rows) + "]}";
}

public class ReportDirector
{
    public void Construct(IReportBuilder builder, string title, IEnumerable<(string Label, decimal Value)> rows)
    {
        builder.AddTitle(title);
        foreach (var (label, value) in rows)
            builder.AddRow(label, value);
    }
}

public static class Program
{
    public static void Main()
    {
        var rows = new List<(string Label, decimal Value)> { ("Subscriptions", 1200m), ("Refunds", -80.5m) };
        var director = new ReportDirector();

        var csv = new CsvReportBuilder();
        director.Construct(csv, "Monthly revenue", rows);
        System.Console.WriteLine(csv.GetResult());

        var json = new JsonReportBuilder();
        director.Construct(json, "Monthly revenue", rows);
        System.Console.WriteLine(json.GetResult());
    }
}
```

Uma segunda forma é comum em C#: um builder fluente, sem director, em que quem chama emite os passos e a chamada final produz um objeto imutável. Serve para objetos com muitas configurações opcionais.

```csharp
using System;

public class RetryPolicy
{
    public int MaxAttempts { get; }
    public TimeSpan Delay { get; }
    public bool Exponential { get; }

    public RetryPolicy(int maxAttempts, TimeSpan delay, bool exponential)
    {
        MaxAttempts = maxAttempts;
        Delay = delay;
        Exponential = exponential;
    }
}

public class RetryPolicyBuilder
{
    private int _maxAttempts = 3;
    private TimeSpan _delay = TimeSpan.FromMilliseconds(200);
    private bool _exponential;

    public RetryPolicyBuilder Attempts(int count) { _maxAttempts = count; return this; }
    public RetryPolicyBuilder WaitingBetween(TimeSpan delay) { _delay = delay; return this; }
    public RetryPolicyBuilder WithExponentialBackoff() { _exponential = true; return this; }

    public RetryPolicy Build()
    {
        if (_maxAttempts < 1) throw new InvalidOperationException("At least one attempt is required.");
        return new RetryPolicy(_maxAttempts, _delay, _exponential);
    }
}
```

## Variações
- **Padrões vazios na interface do builder.** Na forma do livro, a classe base do builder implementa cada passo como uma operação vazia, então um builder concreto sobrescreve apenas o que precisa. Em C#, use uma classe abstrata com métodos `virtual` vazios, ou métodos padrão de interface (C# 8), em vez de forçar todo builder a implementar todos os passos.
- **Anexar versus consultar partes anteriores.** A maioria dos builders apenas acrescenta. Se um passo precisa de uma parte construída antes (um vínculo entre dois nós existentes), o builder deve expor uma forma de localizá-la, ou devolver identificadores dos passos anteriores que o director repassa de volta.
- **Sem tipo de produto comum.** Como as saídas podem não ter relação, `GetResult()` é declarado em cada builder concreto, e o cliente que escolheu o builder conhece o seu tipo. Forçar uma classe base comum de produto normalmente não traz ganho.
- **Builder fluente sem director.** A ordem dos passos fica por conta de quem chama; `Build()` valida e devolve um objeto imutável.

## Riscos e alternativas em C#
- Para o caso simples de "muitos parâmetros opcionais", argumentos nomeados e opcionais, ou um inicializador de objeto com propriedades get/set, são mais simples do que uma classe builder.
- Um builder fluente reutilizado depois de `Build()` compartilha estado mutável com o próximo produto. Ou faça `Build()` copiar as coleções que mantém, ou documente o builder como de uso único.
- Valide em `Build()` (ou no construtor do produto), não em cada passo, para que um objeto incompleto não escape.
- Para saída de texto, `StringBuilder` já é um builder; não o encapsule a menos que uma segunda representação seja de fato necessária.
- Com injeção de dependência, builders que guardam estado por chamada devem ser registrados como transient, nunca como singleton.

## Padrões relacionados
- [Abstract Factory](abstract-factory.md): objetivo parecido, mas devolve cada produto imediatamente e foca em famílias, enquanto o Builder constrói um produto complexo passo a passo.
- [Composite](../structural/composite.md): a estrutura que um builder costuma montar.

## Verificação
- O director não contém código específico de formato, e os builders não contêm lógica de ordenação.
- Adicionar um terceiro formato de saída exige um novo builder e nenhuma mudança no director.
- A mesma entrada passada por dois builders gera conteúdo equivalente em duas formas (coberto por um teste por builder).
- Uma montagem incompleta ou inválida falha em `Build()`/`GetResult()`, em vez de produzir um produto meio pronto.
