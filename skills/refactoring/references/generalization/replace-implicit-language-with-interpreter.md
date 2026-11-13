# Substituir Linguagem Implícita por Interpreter (Replace Implicit Language with Interpreter)

Kerievsky (2004), cap. 8, p. 269. Direção: até. Padrão: Interpreter (GoF, p. 243).

## Quando usar
Smells: Explosão Combinatória (Combinatorial Explosion), Classe Grande (Large Class), Obsessão por Primitivos (Primitive Obsession), Código Duplicado (Duplicated Code).

- Uma classe tem muitos métodos que são, na prática, combinações de algumas ideias: `ByStatus`, `ByMinTotal`, `ByStatusAndMinTotal`, `ByCustomerAndStatus`... A linguagem de "encontre pedidos que são X e Y, mas não Z" está ali, mas nunca foi escrita como tal. Cada nova combinação exige um novo método, e os métodos repetem o mesmo código de filtragem.
- Modelar a linguagem com algumas classes pequenas (os critérios, mais and/or/not) permite que os chamadores montem qualquer combinação em tempo de execução, sem código novo, e permite configurar o comportamento dinamicamente, por exemplo a partir de um formulário de busca.
- Isso é o padrão Specification e o padrão Query Object, que são interpretadores para seleção de objetos.
- Serve para gramáticas pequenas (menos de cerca de uma dúzia de classes). Para uma linguagem grande, um gerador de parsers é melhor. Para uma linguagem pequena e uniforme, código simples pode bastar.
- Há um custo inicial: definir as classes e mudar os chamadores para compô-las. Ele se paga quando a alternativa é uma lista crescente de métodos quase duplicados.

## Mecânica
Estes passos assumem seleção de objetos: vários métodos percorrem uma coleção e escolhem os objetos que casam.

1. Encontre um método de seleção que use um argumento de critério (por exemplo, um total mínimo). Crie uma classe de especificação concreta para esse critério: o construtor recebe o valor e expõe um getter. No método de seleção, crie uma instância e leia o critério pelo getter. Dê à classe o nome do que ela faz (`MinTotalSpec`). Se um método usa vários critérios, faça os passos 1 e 2 para cada um. Compile e teste se a seleção ainda funciona.
2. Aplique Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) à condição dentro do laço, criando um método booleano `IsSatisfiedBy`, e mova-o para a especificação concreta com Mover Função (Move Function) ([move-function.md](../moving-features/move-function.md)). Se ainda não existir uma superclasse de especificação, crie uma com Extrair Superclasse (Extract Superclass) ([extract-superclass.md](../inheritance/extract-superclass.md)), abstrata, declarando apenas `IsSatisfiedBy`. Compile e teste.
3. Repita os passos 1 e 2 para os outros métodos de seleção.
4. Para um método de seleção que agora monta várias especificações concretas, crie uma especificação composta que as contenha (via construtor ou método `Add`), mova a condição combinada para o seu `IsSatisfiedBy` e faça-a estender a superclasse de especificação (veja [replace-one-many-distinctions-with-composite.md](replace-one-many-distinctions-with-composite.md) e [extract-composite.md](extract-composite.md)). Acrescente especificações `Or` e `Not` quando os chamadores precisarem delas.
5. Todo método de seleção agora recebe uma única especificação, e os métodos são idênticos, exceto pela forma como a especificação é montada. Extraia o laço compartilhado para `SelectBy(spec)` e faça cada método de seleção chamá-lo. Compile e teste após cada passo.
6. Internalize os métodos de seleção antigos com Internalizar Função (Inline Function) ([inline-function.md](../first-set/inline-function.md)), para que os chamadores montem a especificação e chamem `SelectBy`. Compile e teste.

## Exemplo
Antes: um localizador de pedidos, com um método por combinação.

```csharp
using System.Collections.Generic;

public enum Status { Open, Paid, Shipped }
public record Order(string Id, string Customer, Status Status, decimal Total);

public class OrderFinder
{
    private readonly List<Order> _orders;
    public OrderFinder(List<Order> orders) => _orders = orders;

    public List<Order> ByStatus(Status status)
    {
        var found = new List<Order>();
        foreach (var o in _orders)
            if (o.Status == status) found.Add(o);
        return found;
    }

    public List<Order> ByMinTotal(decimal min)
    {
        var found = new List<Order>();
        foreach (var o in _orders)
            if (o.Total >= min) found.Add(o);
        return found;
    }

    public List<Order> ByStatusAndMinTotal(Status status, decimal min)
    {
        var found = new List<Order>();
        foreach (var o in _orders)
            if (o.Status == status && o.Total >= min) found.Add(o);
        return found;
    }

    public List<Order> ByCustomerNotStatus(string customer, Status status)
    {
        var found = new List<Order>();
        foreach (var o in _orders)
            if (o.Customer == customer && o.Status != status) found.Add(o);
        return found;
    }
}
```

Depois: um pequeno conjunto de classes de especificação e um único `SelectBy`. Qualquer combinação é montada pelo chamador.

```csharp
using System.Collections.Generic;
using System.Linq;

public enum Status { Open, Paid, Shipped }
public record Order(string Id, string Customer, Status Status, decimal Total);

public abstract class OrderSpec
{
    public abstract bool IsSatisfiedBy(Order order);
}

public class StatusSpec : OrderSpec
{
    private readonly Status _status;
    public StatusSpec(Status status) => _status = status;
    public override bool IsSatisfiedBy(Order o) => o.Status == _status;
}

public class MinTotalSpec : OrderSpec
{
    private readonly decimal _min;
    public MinTotalSpec(decimal min) => _min = min;
    public override bool IsSatisfiedBy(Order o) => o.Total >= _min;
}

public class CustomerSpec : OrderSpec
{
    private readonly string _customer;
    public CustomerSpec(string customer) => _customer = customer;
    public override bool IsSatisfiedBy(Order o) => o.Customer == _customer;
}

public class AndSpec : OrderSpec
{
    private readonly OrderSpec[] _specs;
    public AndSpec(params OrderSpec[] specs) => _specs = specs;
    public override bool IsSatisfiedBy(Order o) => _specs.All(s => s.IsSatisfiedBy(o));
}

public class OrSpec : OrderSpec
{
    private readonly OrderSpec[] _specs;
    public OrSpec(params OrderSpec[] specs) => _specs = specs;
    public override bool IsSatisfiedBy(Order o) => _specs.Any(s => s.IsSatisfiedBy(o));
}

public class NotSpec : OrderSpec
{
    private readonly OrderSpec _spec;
    public NotSpec(OrderSpec spec) => _spec = spec;
    public override bool IsSatisfiedBy(Order o) => !_spec.IsSatisfiedBy(o);
}

public class OrderFinder
{
    private readonly List<Order> _orders;
    public OrderFinder(List<Order> orders) => _orders = orders;

    public List<Order> SelectBy(OrderSpec spec) => _orders.Where(spec.IsSatisfiedBy).ToList();
}

// O antigo ByCustomerNotStatus(c, s) agora é:
//   finder.SelectBy(new AndSpec(new CustomerSpec(c), new NotSpec(new StatusSpec(s))));
```

## Notas (C#)
- Em C#, um `Func<Order, bool>` (e combinadores sobre ele) ou o `Where` do LINQ costumam bastar para filtragem em memória. Classes se justificam quando os critérios precisam ser inspecionados, impressos, serializados ou traduzidos (por exemplo, para SQL).
- Se o alvo é um banco de dados, `Expression<Func<T, bool>>` permite que o provedor traduza os critérios; criar as suas próprias classes de especificação duplicaria o que o provedor já faz.
- Faça as especificações imutáveis e baratas de construir; elas são valores que descrevem uma pergunta, não serviços.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Para cada método antigo do localizador, um teste monta a especificação equivalente e confirma que ela retorna os mesmos pedidos, na mesma ordem, antes de o método antigo ser internalizado.
