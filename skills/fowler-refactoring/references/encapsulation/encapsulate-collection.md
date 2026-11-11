# Encapsular Coleção (Encapsulate Collection)

Fowler (2018), cap. 7, p. 170. Antes / também: —. Inversa: —.

## Quando usar
Smell: nenhum específico no livro (relacionado: Dados Mutáveis (Mutable Data)). A motivação é encapsular
dados mutáveis, para que a coleção não possa ser alterada de qualquer lugar.

- Uma classe tem uma propriedade que retorna sua coleção interna, então qualquer chamador pode adicionar, remover
  ou reordenar itens e o dono nunca fica sabendo.
- O dono tem regras sobre os membros da coleção (limites, totais, validação, notificações de mudança)
  que os chamadores podem contornar hoje.
- Um setter permite que os chamadores substituam a coleção inteira, e eles guardam uma referência a ela.

Uma propriedade sobre o campo protege quem é o dono da lista, não quem a edita.

Evite esconder as coleções por completo (`CountOfLines`, `LineAt(i)`): os chamadores perdem o LINQ. Retorne uma
coleção segura e escolha uma única proteção (cópia ou visão somente leitura) para todos os getters.

## Mecânica
1. Se o campo ainda não estiver atrás de uma propriedade ou de um acessor, aplique antes Encapsular Variável (Encapsulate Variable)
   ([encapsulate-variable.md](../first-set/encapsulate-variable.md)).
2. Adicione métodos no dono para adicionar e remover itens individuais. Decida o que a remoção de um item
   inexistente faz (ignorar, lançar exceção ou deixar o chamador escolher) e registre isso no método.
3. Se houver um setter para a coleção inteira, remova-o quando possível
   ([remove-setting-method.md](../refactoring-apis/remove-setting-method.md)). Se ele precisar ficar, faça-o copiar a coleção recebida
   para o campo em vez de guardar a referência do chamador.
4. Faça o build e execute os testes.
5. Encontre todos os usos da propriedade da coleção. Altere cada chamada que a modifica (`Add`,
   `Remove`, `Clear`, atribuição por indexador, `Sort` in-place) para usar os novos métodos. Teste após
   cada alteração.
6. Procure qualquer `Add`/`Remove` restante no getter e então altere-o para retornar uma
   visão protegida: uma cópia ou um wrapper somente leitura. Com uma cópia, uma escrita perdida some
   em silêncio, e é por isso que a busca vem primeiro.
7. Execute os testes. Qualquer código que ainda tentava modificar a coleção agora falha na compilação
   ou falha de forma explícita.

## Exemplo
Antes:

```csharp
public class OrderLine
{
    public OrderLine(string sku, int quantity) { Sku = sku; Quantity = quantity; }
    public string Sku { get; }
    public int Quantity { get; }
}

public class Order
{
    public List<OrderLine> Lines { get; set; } = new();
}

// chamadores
order.Lines.Add(new OrderLine("A-1", 2));
order.Lines = LoadLines(id);
var total = order.Lines.Sum(l => l.Quantity);
```

Depois:

```csharp
public class Order
{
    private readonly List<OrderLine> _lines = new();

    public IReadOnlyList<OrderLine> Lines => _lines.ToArray();

    public void AddLine(OrderLine line) => _lines.Add(line);

    public void RemoveLine(OrderLine line)
    {
        if (!_lines.Remove(line))
            throw new InvalidOperationException("O pedido não contém esta linha.");
    }

    public void ReplaceLines(IEnumerable<OrderLine> lines)
    {
        var copy = lines.ToList();
        _lines.Clear();
        _lines.AddRange(copy);
    }
}

// chamadores (usings e LoadLines omitidos, como em Antes)
order.AddLine(new OrderLine("A-1", 2));
order.ReplaceLines(LoadLines(id)); // o setter sumiu
var total = order.Lines.Sum(l => l.Quantity);
```

As leituras continuam funcionando com LINQ. As escritas agora passam por `Order`, então uma regra como "no máximo
50 linhas" tem um único lugar para viver.

## Notas de C#
- Exponha `IReadOnlyList<T>` ou `IReadOnlyCollection<T>`, com métodos `Add`/`Remove` no
  dono.
- Uma interface somente leitura não impede que um chamador faça o cast de volta para `List<T>` e a modifique.
  Onde isso importar, retorne uma cópia (`ToArray()`, `ToList()`) ou um wrapper como
  `AsReadOnly()`.
- Uma cópia é um instantâneo: mudanças posteriores no dono não aparecem nela. Um wrapper é uma visão
  ao vivo. Escolha um e seja consistente. Para coleções grandes lidas com frequência, um wrapper
  evita o custo da cópia.
- Operações que mutam uma coleção que você não possui ainda podem causar problemas: `List<T>.Sort()` e
  `Reverse()` alteram a lista in-place, então copie antes ao ordenar o que um getter retornou.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum chamador modifica a coleção a não ser pelos métodos do dono.
