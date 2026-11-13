# Substituir Árvore Implícita por Composite (Replace Implicit Tree with Composite)

Kerievsky (2004), cap. 7, p. 178. Direção: até. Padrão: Composite (GoF, p. 163).

## Quando usar
Smells: Obsessão por Primitivos (Primitive Obsession).

- Dados ou lógica formam uma árvore sem serem modelados como tal: laços aninhados que imprimem ou totalizam uma hierarquia, strings montadas com indentação escrita à mão e marcadores de fechamento, tuplas e dicionários fazendo papel de nós. Toda mudança no formato (um nível novo, outro layout) exige editar o código de construção.
- Um Composite dá uma classe a cada parte e permite que os pais tratem todos os filhos por uma única interface, então formatação, totalização e fechamento são feitos uma vez, pelos próprios nós.
- Para lógica condicional (uma árvore de testes `&&` / `||`), o refactoring só compensa quando muitas condições parecidas se acumulam; esse caso é [replace-implicit-language-with-interpreter.md](../generalization/replace-implicit-language-with-interpreter.md).
- Se o cliente precisar montar a mesma árvore em várias formas de saída, adicione depois um Builder por cima ([encapsulate-composite-with-builder.md](../creation/encapsulate-composite-with-builder.md)).
- Deixe árvores pequenas e estáveis implícitas. Desvantagem: complica o design quando montar a árvore à mão é mais simples. Não tem problema começar implícito e refatorar quando o código começar a inchar.

## Mecânica
Dois caminhos funcionam: aplicar refatorações ao código existente (Extrair Classe e afins), ou fazer as novas classes crescerem guiadas por testes e depois substituir o código antigo. Use o segundo quando o código antigo não se presta a extração (por exemplo, texto montado por concatenação).

1. Encontre uma folha implícita: uma parte da árvore que uma classe poderia representar. Crie a classe da folha, por [extract-class.md](../encapsulation/extract-class.md) ou guiado por testes. Se a folha tiver atributos, dê à classe os mesmos atributos, para que a representação completa corresponda à saída antiga. Compile e teste.
2. Substitua cada ocorrência da folha implícita por uma instância da classe da folha. Compile e teste se a árvore ainda se comporta igual.
3. Repita para cada outro tipo de folha. Dê a todas as classes de folha uma interface comum com [extract-superclass.md](../inheritance/extract-superclass.md) ou Extrair Interface (Extract Interface; só na 1ª ed.; sem link).
4. Encontre um pai implícito: uma parte que guarda folhas. Crie a classe do pai, por extração ou guiado por testes. Os clientes adicionam filhos pelo construtor ou por um método `Add`, e o pai trata cada filho apenas pela interface comum. Faça o pai implementar essa interface também se pais precisarem conter pais, ou se os clientes não devem se importar com o tipo de nó que seguram.
5. Substitua cada ocorrência do pai implícito por uma instância de pai contendo as folhas certas. Compile e teste.
6. Repita para os demais pais implícitos. Permita pais dentro de pais só se os pais implícitos realmente se comportarem do mesmo jeito.

## Exemplo
Antes: um relatório sobre uma forma fixa de dois níveis (categorias de despesas) montado com laços e indentação fixa no código. Adicionar uma subcategoria ou mudar o layout exige mexer neste método.

```csharp
using System.Collections.Generic;
using System.Globalization;
using System.Text;

public static class ExpenseReport
{
    public static string Render(IReadOnlyDictionary<string, (string Item, decimal Amount)[]> categories)
    {
        var sb = new StringBuilder();
        decimal total = 0m;
        foreach (var (category, items) in categories)
        {
            sb.AppendLine(category);
            decimal subtotal = 0m;
            foreach (var (item, amount) in items)
            {
                sb.AppendLine($"  {item}: {Money(amount)}");
                subtotal += amount;
            }
            sb.AppendLine($"  subtotal: {Money(subtotal)}");
            total += subtotal;
        }
        sb.AppendLine($"total: {Money(total)}");
        return sb.ToString();
    }

    private static string Money(decimal value) => value.ToString("0.00", CultureInfo.InvariantCulture);
}
```

Depois: `Expense` é a folha e `ExpenseGroup` é o pai, ambos atrás de `IExpenseNode`. Um grupo totaliza e indenta os próprios filhos, e um grupo pode conter outros grupos, então um novo nível não exige mudança no renderizador. Para os mesmos dados de dois níveis, a saída é idêntica à do método antigo.

```csharp
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

public interface IExpenseNode
{
    decimal Amount { get; }
    void Render(StringBuilder sb, int depth);
}

public record Expense(string Item, decimal Amount) : IExpenseNode
{
    public void Render(StringBuilder sb, int depth) =>
        sb.AppendLine($"{ExpenseReport.Indent(depth)}{Item}: {ExpenseReport.Money(Amount)}");
}

public class ExpenseGroup : IExpenseNode
{
    private readonly string _name;
    private readonly List<IExpenseNode> _children = new();

    public ExpenseGroup(string name, params IExpenseNode[] children)
    {
        _name = name;
        _children.AddRange(children);
    }

    public decimal Amount => _children.Sum(c => c.Amount);

    public void Add(IExpenseNode child) => _children.Add(child);

    public void Render(StringBuilder sb, int depth)
    {
        sb.AppendLine($"{ExpenseReport.Indent(depth)}{_name}");
        foreach (var child in _children)
            child.Render(sb, depth + 1);
        sb.AppendLine($"{ExpenseReport.Indent(depth + 1)}subtotal: {ExpenseReport.Money(Amount)}");
    }
}

public static class ExpenseReport
{
    public static string Render(IReadOnlyList<IExpenseNode> roots)
    {
        var sb = new StringBuilder();
        foreach (var root in roots)
            root.Render(sb, 0);
        sb.AppendLine($"total: {Money(roots.Sum(r => r.Amount))}");
        return sb.ToString();
    }

    public static string Indent(int depth) => new string(' ', depth * 2);

    public static string Money(decimal value) => value.ToString("0.00", CultureInfo.InvariantCulture);
}
```

O cliente agora monta a árvore, e aninhar é só mais um `ExpenseGroup` dentro de um grupo:

```csharp
var travel = new ExpenseGroup("Travel",
    new Expense("Flight", 420m),
    new ExpenseGroup("Lodging", new Expense("Hotel", 310.5m)));
string text = ExpenseReport.Render(new IExpenseNode[] { travel });
```

## Notas (C#)
- Um `record` é uma folha conveniente. Uma interface basta para o tipo comum, a menos que folhas e pais compartilhem código.
- Se a árvore precisar ser imutável, receba os filhos só no construtor e exponha-os como `IReadOnlyList<T>`; remova o `Add`.
- A profundidade da recursão é a profundidade da árvore. Para árvores muito profundas, confirme que nenhum nó renderiza recursando sem limite.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Mantenha um teste que compara a saída antiga com a nova para os mesmos dados (o texto "golden"), e rode-o após cada passo.
- Adicione um teste com um pai aninhado, para provar que a árvore realmente compõe.
