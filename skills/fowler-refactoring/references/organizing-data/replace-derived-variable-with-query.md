# Substituir Variável Derivada por Consulta (Replace Derived Variable with Query)

Fowler (2018), cap. 9, p. 248. Antes / também: —. Inversa: —.

## Quando usar
Smell: Dados Mutáveis (Mutable Data). Uma variável guarda um valor totalmente determinado por outros dados
(um total corrente, uma contagem, uma soma em cache), e todo lugar que altera os dados de origem também
precisa lembrar de atualizar a variável. Esqueça uma atualização e as duas divergem. Calcular o
valor quando ele é lido elimina toda essa classe de bugs e muitas vezes deixa claro o que o valor significa.

Não aplique quando os dados de origem são imutáveis e o resultado derivado também pode ser imutável:
construir uma nova estrutura a partir deles uma vez só é aceitável. Reconsidere também quando o
cálculo é caro e lido com muita frequência; meça antes de abrir mão do valor armazenado.

## Mecânica
1. Encontre todo lugar que atribui ou atualiza a variável. Se uma variável mistura várias
   origens (por exemplo, um valor inicial mais mudanças acumuladas), aplique antes Dividir Variável (Split Variable)
   ([split-variable.md](split-variable.md)) para que cada parte tenha um significado e uma origem.
2. Escreva uma função ou propriedade que calcule o valor a partir dos dados de origem.
3. Em cada leitura da variável, afirme que ela é igual ao cálculo (Introduzir Asserção (Introduce Assertion),
   [introduce-assertion.md](../conditional-logic/introduce-assertion.md)). Se não houver um único lugar para pôr a asserção, aplique antes
   Encapsular Variável (Encapsulate Variable) ([encapsulate-variable.md](../first-set/encapsulate-variable.md)).
4. Rode os testes. Se a asserção falhar, a hipótese está errada ou a divisão do passo 1 está
   incompleta; corrija isso antes de continuar.
5. Substitua cada leitura da variável por uma chamada ao cálculo.
6. Rode os testes.
7. Remova a declaração e toda atualização da variável (Remover Código Morto (Remove Dead Code),
   [remove-dead-code.md](../moving-features/remove-dead-code.md)), junto com a asserção. Internalize o cálculo
   ([inline-function.md](../first-set/inline-function.md)) se uma função auxiliar separada não for mais útil.
8. Rode os testes.

## Exemplo
Antes: `AmountPaid` é uma segunda cópia de uma informação que já está em `Payments`.

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

public record Payment(decimal Amount);

public class Invoice
{
    private readonly List<Payment> _payments = new();
    private decimal _amountPaid;

    public Invoice(decimal total) => Total = total;

    public decimal Total { get; }
    public decimal AmountPaid => _amountPaid;
    public decimal Outstanding => Total - AmountPaid;

    public void Register(Payment payment)
    {
        _payments.Add(payment);
        _amountPaid += payment.Amount;
    }
}
```

Passo intermediário: afirme contra o cálculo, rode os testes e então troque o leitor.

```csharp
public decimal AmountPaid
{
    get
    {
        Debug.Assert(_amountPaid == CalculatedAmountPaid);
        return CalculatedAmountPaid;
    }
}

private decimal CalculatedAmountPaid => _payments.Sum(p => p.Amount);
```

Depois: o campo e a sua atualização sumiram.

```csharp
public class Invoice
{
    private readonly List<Payment> _payments = new();

    public Invoice(decimal total) => Total = total;

    public decimal Total { get; }
    public decimal AmountPaid => _payments.Sum(p => p.Amount);
    public decimal Outstanding => Total - AmountPaid;

    public void Register(Payment payment) => _payments.Add(payment);
}
```

Se o campo tivesse começado com um valor inicial diferente de zero, a asserção falharia. Divida-o
primeiro em `_openingPaid` e um acumulador, e calcule apenas a parte do acumulador.

## Notas (C#)
- O cálculo cabe em uma propriedade somente leitura calculada (`=> ...`).
- `Debug.Assert` é removido dos builds Release, então rode os testes em Debug para exercitá-lo.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
