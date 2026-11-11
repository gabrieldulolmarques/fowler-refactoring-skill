# Substituir Código de Erro por Exceção (Replace Error Code with Exception)

https://refactoring.com/catalog/replaceErrorCodeWithException.html. Antes / também: —. Inversa: —.
Relacionada: Substituir Exceção por Verificação Prévia (Replace Exception with Precheck) ([replace-exception-with-precheck.md](replace-exception-with-precheck.md)).

## Quando usar
Uma função reporta falha pelo seu valor de retorno: um número mágico, `null`, `false` ou um objeto de
status. Os chamadores precisam verificá-lo após cada chamada, e quem esquece deixa o programa
continuar com estado ruim. Lançar uma exceção tira o sinal do caminho normal de retorno e o deixa
chegar à camada que souber tratá-lo.

Use apenas para falhas que sejam realmente excepcionais. Se a condição é rotineira e se espera
que os chamadores ramifiquem por ela (uma busca que muitas vezes não encontra nada, uma entrada frequentemente inválida),
mantenha um resultado baseado em retorno ou ofereça uma verificação prévia; veja [replace-exception-with-precheck.md](replace-exception-with-precheck.md).

## Mecânica
1. Escolha ou crie um tipo de exceção para a falha. Dê a ele a informação que o código de erro
   carregava (o código, um motivo, o valor problemático).
2. Encontre todo chamador da função e, em cada ponto de chamada, envolva a chamada de modo que a
   exceção lançada seja tratada onde o código antigo tratava o código de erro. Faça isso antes de
   mudar a função, mantendo o ramo antigo funcionando. Compile e teste.
3. Na função, substitua o `return <código de erro>` por `throw new <Exception>(...)`.
   Compile e teste.
4. Em cada chamador, remova a verificação agora morta do código de erro. Compile e teste.
5. Se alguns chamadores não conseguem tratar a exceção, deixe-a propagar até uma camada que consiga; não
   a capture apenas para transformá-la de volta em um código.
6. Se o tipo de retorno da função existia apenas para carregar o código (um status `int`, um `bool`),
   simplifique-o, por exemplo para `void`, como um passo separado com [change-function-declaration.md](../first-set/change-function-declaration.md).

## Exemplo
Antes: `Reserve` retorna um código, e o chamador precisa interpretá-lo.

```csharp
using System;
using System.Collections.Generic;

public class Inventory
{
    private readonly Dictionary<string, int> _stock = new();

    public int Reserve(string sku, int quantity)
    {
        if (!_stock.TryGetValue(sku, out var available)) return -1; // sku desconhecido
        if (available < quantity) return -2;                        // estoque insuficiente
        _stock[sku] = available - quantity;
        return 0;
    }
}

public class OrderService
{
    private readonly Inventory _inventory = new();

    public string Place(string sku, int quantity)
    {
        var result = _inventory.Reserve(sku, quantity);
        if (result == -1) return "produto desconhecido";
        if (result == -2) return "sem estoque";
        return "realizado";
    }
}
```

Depois: as falhas são exceções e o chamador as trata onde escolher.

```csharp
using System;
using System.Collections.Generic;

public class ReservationException : Exception
{
    public ReservationException(string message) : base(message) { }
}

public class Inventory
{
    private readonly Dictionary<string, int> _stock = new();

    public void Reserve(string sku, int quantity)
    {
        if (!_stock.TryGetValue(sku, out var available))
            throw new ReservationException("produto desconhecido");
        if (available < quantity)
            throw new ReservationException("sem estoque");
        _stock[sku] = available - quantity;
    }
}

public class OrderService
{
    private readonly Inventory _inventory = new();

    public string Place(string sku, int quantity)
    {
        try
        {
            _inventory.Reserve(sku, quantity);
            return "realizado";
        }
        catch (ReservationException e)
        {
            return e.Message;
        }
    }
}
```

## Notas de C#
- Não use exceções para fluxo de controle esperado: elas são lentas em comparação com um desvio e
  escondem os caminhos normais do programa. Reserve-as para falhas que o chamador não consiga razoavelmente
  evitar verificando antes.
- Prefira um tipo de exceção específico (ou um embutido como `ArgumentException` ou
  `InvalidOperationException` onde couber) a um `Exception` genérico, e capture o tipo mais estreito.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Adicione um teste por antigo código de erro que afirme que a exceção é lançada com os dados certos.
- Procure chamadores fora da solução (reflexão, outros assemblies) que ainda esperem o código.
