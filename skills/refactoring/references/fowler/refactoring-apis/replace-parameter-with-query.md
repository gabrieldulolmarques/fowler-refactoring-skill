# Substituir Parâmetro por Consulta (Replace Parameter with Query)

Fowler (2018), cap. 11, p. 324. Antes / também: antes Replace Parameter with Method. Inversa: Substituir Consulta por Parâmetro (Replace Query with Parameter) ([replace-query-with-parameter.md](replace-query-with-parameter.md)).

## Quando usar
Smell: Lista Longa de Parâmetros (Long Parameter List). Um chamador passa um valor que a função poderia obter com a mesma facilidade por conta própria, normalmente a partir do receptor ou de outro parâmetro. O chamador faz trabalho extra e a lista de parâmetros repete informação que ela já tem. O caso mais seguro é um parâmetro calculado puramente a partir de outro parâmetro da mesma lista: passar os dois não acrescenta nada.

Não use quando a remoção dá à função uma dependência indesejada: uma chamada a algo que ela não deveria conhecer, ou acesso a algo que você planeja tirar dali mais tarde. Evite também quando a função é determinística (mesmas entradas, mesmo resultado) e a consulta leria estado global mutável, porque isso perde a propriedade e torna a função mais difícil de testar.

## Mecânica
1. Se o valor é calculado por uma expressão ou várias instruções no chamador, extraia esse cálculo para a sua própria função ou propriedade ([extract-function.md](../first-set/extract-function.md)), de modo que haja uma única consulta a chamar.
2. Dentro do corpo da função, substitua cada uso do parâmetro por uma chamada a essa consulta. Compile e teste após cada substituição.
3. Remova o parâmetro agora sem uso da declaração e de todos os chamadores ([change-function-declaration.md](../first-set/change-function-declaration.md)). Compile e teste.

## Exemplo
Antes:

```csharp
public class Customer
{
    public string Country { get; }

    public Customer(string country) => Country = country;
}

public class Account
{
    private readonly decimal _balance;
    private readonly Customer _customer;

    public Account(decimal balance, Customer customer)
    {
        _balance = balance;
        _customer = customer;
    }

    public decimal MonthlyFee()
    {
        decimal baseFee = _balance < 1000m ? 12m : 0m;
        bool abroad = _customer.Country != "BR";
        return AddSurcharge(baseFee, abroad);
    }

    private decimal AddSurcharge(decimal baseFee, bool abroad)
    {
        return abroad ? baseFee + 25m : baseFee;
    }
}
```

Passo 1: transforme a variável local `abroad` em uma consulta ([replace-temp-with-query.md](../encapsulation/replace-temp-with-query.md)), o que dá ao parâmetro uma única fonte:

```csharp
    public decimal MonthlyFee()
    {
        decimal baseFee = _balance < 1000m ? 12m : 0m;
        return AddSurcharge(baseFee, IsAbroad);
    }

    private bool IsAbroad => _customer.Country != "BR";
```

Passo 2: dentro de `AddSurcharge`, use `IsAbroad` em vez do parâmetro. Passo 3: descarte o parâmetro.

Depois:

```csharp
    public decimal MonthlyFee()
    {
        decimal baseFee = _balance < 1000m ? 12m : 0m;
        return AddSurcharge(baseFee);
    }

    private bool IsAbroad => _customer.Country != "BR";

    private decimal AddSurcharge(decimal baseFee)
    {
        return IsAbroad ? baseFee + 25m : baseFee;
    }
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
