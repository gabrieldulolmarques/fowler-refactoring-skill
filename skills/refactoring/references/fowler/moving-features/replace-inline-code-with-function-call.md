# Substituir Código Internalizado por Chamada de Função (Replace Inline Code with Function Call)

Fowler (2018), cap. 8, p. 222. Antes / também: —. Inversa: —.

## Quando usar
- O código inline faz o mesmo trabalho de uma função que já existe na base de código ou na
  biblioteca padrão (um laço manual que busca, soma, junta ou testa pertinência).
- A mesma lógica está copiada em vários lugares e uma das cópias já vive em uma função nomeada.
- Duplicação é o sintoma usual (veja Código Duplicado (Duplicated Code) em [smells.md](../../smells.md)).

Antes de substituir, leia o nome da função no lugar do código inline. Se o nome soar
natural ali, substitua. Se não soar, ou o nome é ruim (corrija com
[change-function-declaration.md](../first-set/change-function-declaration.md)) ou a função tem um propósito diferente e a
semelhança é coincidência. Nesse caso, deixe o código em paz: se você mudaria o
corpo da função sem querer que este código mudasse, eles não são a mesma coisa.

## Mecânica
1. Confirme que a função existente faz exatamente o que o código inline faz, incluindo casos
   extremos (entrada vazia, null, ordenação, sensibilidade a maiúsculas e minúsculas, efeitos colaterais).
2. Substitua o código inline por uma chamada à função.
3. Compile e execute os testes.
4. Repita para as outras cópias, uma de cada vez, testando após cada uma.

## Exemplo
Antes:

```csharp
public class ShippingPolicy
{
    private static readonly string[] RestrictedCountries = { "KP", "IR", "SY" };

    public bool IsRestricted(string countryCode)
    {
        bool restricted = false;
        foreach (var code in RestrictedCountries)
        {
            if (code == countryCode)
            {
                restricted = true;
            }
        }
        return restricted;
    }
}
```

Depois:

```csharp
public class ShippingPolicy
{
    private static readonly string[] RestrictedCountries = { "KP", "IR", "SY" };

    public bool IsRestricted(string countryCode)
    {
        return RestrictedCountries.Contains(countryCode);
    }
}
```

(`Contains` em um array vem de `System.Linq`; adicione `using System.Linq;` onde necessário.)
O comportamento não muda: ambos retornam true quando o código está na lista.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
