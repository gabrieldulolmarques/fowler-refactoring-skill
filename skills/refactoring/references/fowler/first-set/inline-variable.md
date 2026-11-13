# Internalizar Variável (Inline Variable)

Fowler (2018), cap. 6, p. 123. Antes / também: Inline Temp. Inversa: Extrair Variável (Extract Variable)
([extract-variable.md](extract-variable.md)).

## Quando usar
- O nome da variável não acrescenta nada além do que a expressão já diz, então é apenas
  uma linha a mais para ler.
- A variável está entre você e outra refatoração: por exemplo, ela é lida dentro de um
  bloco que você quer extrair ou mover, e mantê-la força um parâmetro ou valor de retorno extra.
- Não internalize quando o nome explica uma expressão pouco óbvia, ou quando a expressão é
  cara e a variável é lida muitas vezes. Nesses casos a variável se justifica.

## Mecânica
1. Verifique se o lado direito não tem efeitos colaterais. Se tiver, pare.
2. Como precaução extra, verifique se nada entre a atribuição e as leituras pode mudar
   aquilo que o lado direito avalia. Se puder, pare.
3. Confirme que a variável é atribuída exatamente uma vez. Em C# essa verificação é manual: um local `const`
   só aceita constante de tempo de compilação, então, para outros valores, o compilador não garante a atribuição única. Procure no método outras atribuições, inclusive `out`, `ref`, `+=` e `++`.
   Se o valor for uma constante, um `const` temporário faz o compilador verificar; para um campo,
   `readonly` faz o mesmo. Execute os testes.
4. Substitua a primeira leitura da variável pelo lado direito. Faça o build e teste.
5. Repita para cada leitura restante, testando pelo caminho.
6. Apague a declaração e a atribuição. Faça o build e teste.

## Exemplo

Antes:

```csharp
using System.Collections.Generic;
using System.Linq;

public class CartLine
{
    public string Sku { get; }
    public int Quantity { get; }

    public CartLine(string sku, int quantity)
    {
        Sku = sku;
        Quantity = quantity;
    }
}

public class Cart
{
    public List<CartLine> Lines { get; } = new();
}

public class WholesalePolicy
{
    public bool QualifiesForWholesale(Cart cart)
    {
        int units = cart.Lines.Sum(l => l.Quantity);
        return units > 20;
    }
}
```

Depois:

```csharp
using System.Linq;

public class WholesalePolicy
{
    public bool QualifiesForWholesale(Cart cart)
    {
        return cart.Lines.Sum(l => l.Quantity) > 20;
    }
}
```

O comportamento é o mesmo: a expressão é avaliada uma vez, no mesmo ponto, sem efeitos colaterais.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Depois que a última leitura é substituída, a variável não tem mais referências; o compilador falha se a
  declaração tiver sido apagada cedo demais.
