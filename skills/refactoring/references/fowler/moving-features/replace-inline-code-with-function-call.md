# Substituir Código Internalizado por Chamada de Função (Replace Inline Code with Function Call)

Fowler (2018), cap. 8, p. 222. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
- O código internalizado faz o mesmo trabalho de uma função que já existe na base de código ou na
  biblioteca padrão (um laço manual que busca, soma, junta ou testa pertinência).
- A mesma lógica está copiada em vários lugares e uma das cópias já vive em uma função nomeada.
- Duplicação é o sintoma usual (veja Código Duplicado (Duplicated Code) em [smells.md](../smells.md)).

Antes de substituir, leia o nome da função no lugar do código internalizado. Se o nome soar
natural ali, substitua. Se não soar, ou o nome é ruim (corrija com
[change-function-declaration.md](../first-set/change-function-declaration.md)) ou a função tem um propósito diferente e a
semelhança é coincidência. Nesse caso, deixe o código em paz: se você mudaria o
corpo da função sem querer que este código mudasse, eles não são a mesma coisa.

## Mecânica
1. Confirme que a função existente faz exatamente o que o código internalizado faz, incluindo casos
   extremos (entrada vazia, null, ordenação, sensibilidade a maiúsculas e minúsculas, efeitos colaterais).
2. Substitua o código internalizado por uma chamada à função.
3. Compile e execute os testes.
4. Repita para as outras cópias, uma de cada vez, testando após cada uma.

## Exemplo
Antes:

```csharp
public class CourierCoverage
{
    private static readonly string[] ServiceAreas = { "north", "central", "harbor" };

    public bool Covers(string zone)
    {
        bool covered = false;
        foreach (var area in ServiceAreas)
        {
            if (area == zone)
            {
                covered = true;
            }
        }
        return covered;
    }
}
```

Depois:

```csharp
using System.Linq;

public class CourierCoverage
{
    private static readonly string[] ServiceAreas = { "north", "central", "harbor" };

    public bool Covers(string zone)
    {
        return ServiceAreas.Contains(zone);
    }
}
```

(`Contains` em um array vem de `System.Linq`; adicione `using System.Linq;` onde for preciso.)
O comportamento não muda: os dois retornam verdadeiro quando a zona está na lista.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
