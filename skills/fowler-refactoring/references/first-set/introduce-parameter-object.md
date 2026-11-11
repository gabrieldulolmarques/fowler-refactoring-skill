# Introduzir Objeto de Parâmetros (Introduce Parameter Object)

Fowler (2018), cap. 6, p. 140. Antes / também: —. Inversa: —.

## Quando usar
Smells: Agrupamentos de Dados (Data Clumps), Lista Longa de Parâmetros (Long Parameter List), Função Longa (Long Function), Obsessão por Primitivos (Primitive Obsession).

- O mesmo grupo de valores aparece como parâmetros em várias funções, geralmente com os mesmos
  nomes, ou com nomes ligeiramente diferentes para a mesma ideia.
- Dar nome ao grupo torna explícita a relação entre os valores, encurta as assinaturas e
  faz todas as funções chegarem aos valores do mesmo jeito.
- Quando o grupo vira um objeto, o comportamento que trabalha sobre ele
  (validação, comparação, verificações de pertinência, formatação) ganha um lugar natural para viver, e o
  objeto muitas vezes se torna um conceito de domínio de verdade.
- Prefira Preservar Objeto Inteiro (Preserve Whole Object) ([preserve-whole-object.md](../refactoring-apis/preserve-whole-object.md)) quando os valores já são
  campos de um objeto existente que a função chamada pode simplesmente receber.

## Mecânica
1. Se não existir uma estrutura adequada, crie uma. Prefira um tipo que possa guardar comportamento depois, e
   torne-o imutável com igualdade por valor (um objeto de valor).
2. Execute os testes.
3. Use Mudar Declaração de Função (Change Function Declaration) ([change-function-declaration.md](change-function-declaration.md)) para adicionar à função um parâmetro do
   novo tipo. Onde a linguagem exigir um valor, passe `null` ou um padrão nos
   chamadores por enquanto.
4. Execute os testes.
5. Atualize cada chamador para construir e passar a instância certa. Execute os testes após cada chamador.
6. Para cada valor do grupo, um de cada vez: substitua os usos do parâmetro original dentro
   da função pelo membro correspondente do novo objeto, remova esse parâmetro da
   assinatura e de todos os chamadores, e execute os testes.
7. Procure comportamento que possa ir para o novo tipo (Mover Função (Move Function), [move-function.md](../moving-features/move-function.md))
   e outros lugares em que o mesmo grupo apareça, e use o novo tipo lá também.

## Exemplo
Antes: três valores viajam juntos por duas funções.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public record Order(string Id, decimal Total, DateTime PlacedOn);

public class OrderReport
{
    public decimal TotalBetween(IEnumerable<Order> orders, DateTime from, DateTime to) =>
        orders.Where(o => o.PlacedOn >= from && o.PlacedOn <= to).Sum(o => o.Total);

    public int CountBetween(IEnumerable<Order> orders, DateTime from, DateTime to) =>
        orders.Count(o => o.PlacedOn >= from && o.PlacedOn <= to);
}

// chamador
// var total = report.TotalBetween(orders, quarter.Start, quarter.End);
// var count = report.CountBetween(orders, quarter.Start, quarter.End);
```

Depois: o par vira um `DateRange`, e a verificação de pertinência foi movida para dentro dele.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public record Order(string Id, decimal Total, DateTime PlacedOn);

public record DateRange(DateTime From, DateTime To)
{
    public bool Contains(DateTime value) => value >= From && value <= To;
}

public class OrderReport
{
    public decimal TotalBetween(IEnumerable<Order> orders, DateRange range) =>
        orders.Where(o => range.Contains(o.PlacedOn)).Sum(o => o.Total);

    public int CountBetween(IEnumerable<Order> orders, DateRange range) =>
        orders.Count(o => range.Contains(o.PlacedOn));
}

// chamador
// var period = new DateRange(quarter.Start, quarter.End);
// var total = report.TotalBetween(orders, period);
// var count = report.CountBetween(orders, period);
```

O comportamento não muda. Os estados intermediários (com os parâmetros antigos e o novo na
assinatura) compilaram e passaram nos testes a cada passo.

## Notas (C#)
- O novo tipo pode ser uma classe, um `record` ou um `record struct`. Um `record` dá igualdade por valor
  e imutabilidade (`init` ou propriedades posicionais) de graça, o que combina com um objeto de valor.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum chamador ainda passa os valores individuais antigos, e nenhuma função os lê de outro lugar
  que não seja o novo objeto.
