# Retornar Valor Modificado (Return Modified Value)

Fowler, catálogo online: https://refactoring.com/catalog/returnModifiedValue.html (só na edição web, sem seção no livro). Antes / também: —. Inversa: —.

## Quando usar
Smell: nenhum específico (apenas catálogo web; relacionados: Dados Mutáveis (Mutable Data), Função Longa (Long Function)).
- Uma função lê algumas entradas, calcula um valor e o armazena em uma variável declarada fora dela (um campo, uma variável local capturada pelo chamador, um acumulador compartilhado), sem retornar nada.
- Quem lê o código chamador não consegue saber que a chamada produz um valor, nem qual variável ela alimenta.
- Você quer extrair, mover ou reordenar esse código e a escrita oculta torna isso arriscado.

Pule quando a função atualiza várias variáveis de uma vez (retorne um pequeno registro, ou divida a função primeiro) ou quando alterar estado compartilhado é o objetivo inteiro da operação.

## Mecânica
A página de origem mostra apenas um par de código antes/depois, então os smells, a condição para pular e estes passos são derivados desse par, não de passos publicados.

1. Identifique a única variável externa que a função atualiza, e todo lugar que a lê ou escreve antes e depois da chamada.
2. Declare uma variável local dentro da função. Escolha o seu valor inicial conforme o caso:
   - A função parte de um valor fixo (o caso usual, e o do exemplo): inicie a variável local nesse valor.
   - A função acumula sobre um valor deixado por chamadas anteriores: inicie a variável local no valor identidade (`0` para uma soma, uma coleção vazia para uma lista), e depois faça o chamador combinar o valor retornado com a variável externa.
3. Substitua toda escrita na variável externa no corpo da função por uma escrita na variável local, e ao final da função atribua a variável local à variável externa (combinando-a com o valor existente no caso de acumulação), para que o comportamento permaneça o mesmo. Compile e teste.
4. Faça a função retornar a variável local (mude o tipo de retorno de `void`). Compile e teste.
5. Em cada ponto de chamada, use o valor retornado no lugar de ler a variável externa (idealmente atribuindo-o a uma variável declarada ali, somente leitura se nada mais a altera). Compile e teste.
6. Remova da função a atribuição final à variável externa, e remova a variável externa se nada mais precisar dela. Renomeie a função se o seu nome descrevia uma ação em vez do valor. Compile e teste.

## Exemplo
Antes:

```csharp
public class InvoiceReport
{
    private decimal _totalDiscount;

    private void CalculateDiscount(IReadOnlyList<InvoiceLine> lines)
    {
        foreach (var line in lines)
        {
            if (line.Discount > 0)
                _totalDiscount += line.Discount;
        }
    }

    public decimal Summarize(IReadOnlyList<InvoiceLine> lines)
    {
        _totalDiscount = 0;
        CalculateDiscount(lines);
        return _totalDiscount;
    }
}

public record InvoiceLine(decimal Price, decimal Discount);
```

Depois:

```csharp
public class InvoiceReport
{
    private decimal CalculateDiscount(IReadOnlyList<InvoiceLine> lines)
    {
        var result = 0m;
        foreach (var line in lines)
        {
            if (line.Discount > 0)
                result += line.Discount;
        }
        return result;
    }

    public decimal Summarize(IReadOnlyList<InvoiceLine> lines)
    {
        return CalculateDiscount(lines);
    }
}

public record InvoiceLine(decimal Price, decimal Discount);
```

Mesmo comportamento, inclusive em chamadas repetidas (o "antes" reinicia o campo no começo de `Summarize`), com o campo eliminado e o fluxo de dados visível na chamada.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
