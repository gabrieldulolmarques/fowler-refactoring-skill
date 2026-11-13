# Substituir Parâmetro por Consulta (Replace Parameter with Query)

Fowler (2018), cap. 11, p. 324. Nome anterior / outro nome: Replace Parameter with Method. Inversa: Substituir Consulta por Parâmetro (Replace Query with Parameter) ([replace-query-with-parameter.md](replace-query-with-parameter.md)).

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
public class Recipient
{
    public string CountryCode { get; }

    public Recipient(string countryCode) => CountryCode = countryCode;
}

public class SmsBilling
{
    private readonly int _monthlyVolume;
    private readonly Recipient _recipient;

    public SmsBilling(int monthlyVolume, Recipient recipient)
    {
        _monthlyVolume = monthlyVolume;
        _recipient = recipient;
    }

    public decimal MessageFee()
    {
        decimal baseFee = _monthlyVolume > 1000 ? 0.04m : 0.06m;
        bool international = _recipient.CountryCode != "BR";
        return AddSurcharge(baseFee, international);
    }

    private decimal AddSurcharge(decimal baseFee, bool international)
    {
        return international ? baseFee + 0.10m : baseFee;
    }
}
```

Passo 1: transforme a variável local `international` em uma consulta ([replace-temp-with-query.md](../encapsulation/replace-temp-with-query.md)), o que dá ao parâmetro uma única fonte:

```csharp
// fragment
    public decimal MessageFee()
    {
        decimal baseFee = _monthlyVolume > 1000 ? 0.04m : 0.06m;
        return AddSurcharge(baseFee, IsInternational);
    }

    private bool IsInternational => _recipient.CountryCode != "BR";
```

Passo 2: dentro de `AddSurcharge`, use `IsInternational` no lugar do parâmetro. Passo 3: remova o parâmetro.

Depois:

```csharp
public class SmsBilling
{
    private readonly int _monthlyVolume;
    private readonly Recipient _recipient;

    public SmsBilling(int monthlyVolume, Recipient recipient)
    {
        _monthlyVolume = monthlyVolume;
        _recipient = recipient;
    }

    public decimal MessageFee()
    {
        decimal baseFee = _monthlyVolume > 1000 ? 0.04m : 0.06m;
        return AddSurcharge(baseFee);
    }

    private bool IsInternational => _recipient.CountryCode != "BR";

    private decimal AddSurcharge(decimal baseFee)
    {
        return IsInternational ? baseFee + 0.10m : baseFee;
    }
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
