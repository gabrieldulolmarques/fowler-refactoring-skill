# Dividir Laço (Split Loop)

Fowler (2018), cap. 8, p. 227. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smells: Função Longa (Long Function).

- Um laço faz dois ou mais trabalhos sem relação apenas porque eles podem compartilhar uma única passada pelos dados.
- Você quer extrair um desses trabalhos para sua própria função, mas o laço teria que retornar vários valores ou preencher várias variáveis.
- Quem modifica um cálculo precisa entender todos os outros do laço.

Não deixe de dividir só porque os dados são percorridos duas vezes. A clareza vem primeiro; meça depois e junte os laços de volta se a travessia for um gargalo comprovado. Um laço dividido também costuma ser mais fácil de otimizar isoladamente. Deixe o laço em paz se os dois cálculos realmente dependerem um do outro (um lê o que o outro escreve na mesma passada).

## Mecânica
1. Garanta que os testes cubram os resultados do laço.
2. Copie o laço, de modo que a mesma travessia apareça duas vezes em sequência.
3. Em cada cópia, remova as instruções que pertencem à outra responsabilidade, especialmente qualquer coisa com efeitos colaterais (atribuições, acumulação, chamadas que mudam estado). Instruções sem efeitos colaterais podem ficar por enquanto.
4. Compile e execute os testes.
5. Opcionalmente, use Deslocar Instruções (Slide Statements) ([slide-statements.md](slide-statements.md)) para mover a declaração de cada acumulador para junto do seu próprio laço.
6. Considere Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) em cada laço e Substituir Laço por Pipeline (Replace Loop with Pipeline) ([replace-loop-with-pipeline.md](replace-loop-with-pipeline.md)) onde ficar mais legível.

## Exemplo
Antes: uma única passagem calcula ao mesmo tempo o peso total e a entrega mais recente.

```csharp
using System;
using System.Collections.Generic;

public class Delivery
{
    public Delivery(decimal weightKg, DateTime deliveredAt)
    {
        WeightKg = weightKg;
        DeliveredAt = deliveredAt;
    }

    public decimal WeightKg { get; }
    public DateTime DeliveredAt { get; }
}

public static class DeliveryReport
{
    public static string Summarize(IReadOnlyList<Delivery> deliveries)
    {
        decimal totalWeight = 0;
        DateTime latestDelivery = DateTime.MinValue;
        foreach (var delivery in deliveries)
        {
            totalWeight += delivery.WeightKg;
            if (delivery.DeliveredAt > latestDelivery) latestDelivery = delivery.DeliveredAt;
        }

        return $"weight: {totalWeight} kg, last delivery: {latestDelivery:yyyy-MM-dd}";
    }
}
```

Depois: um laço por responsabilidade, e então cada um é extraído para uma função.

```csharp
using System;
using System.Collections.Generic;

public static class DeliveryReport
{
    public static string Summarize(IReadOnlyList<Delivery> deliveries)
    {
        return $"weight: {TotalWeight(deliveries)} kg, last delivery: {LatestDelivery(deliveries):yyyy-MM-dd}";
    }

    private static decimal TotalWeight(IReadOnlyList<Delivery> deliveries)
    {
        decimal totalWeight = 0;
        foreach (var delivery in deliveries)
        {
            totalWeight += delivery.WeightKg;
        }
        return totalWeight;
    }

    private static DateTime LatestDelivery(IReadOnlyList<Delivery> deliveries)
    {
        DateTime latestDelivery = DateTime.MinValue;
        foreach (var delivery in deliveries)
        {
            if (delivery.DeliveredAt > latestDelivery) latestDelivery = delivery.DeliveredAt;
        }
        return latestDelivery;
    }
}
```

O comportamento é o mesmo. Cada função agora tem um único propósito e pode, mais tarde, virar uma expressão LINQ (`deliveries.Sum(d => d.WeightKg)`).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Não misture uma otimização ou uma reescrita em pipeline no mesmo commit da divisão.
