# Substituir Variável Derivada por Consulta (Replace Derived Variable with Query)

Fowler (2018), cap. 9, p. 248. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smell: Dados Mutáveis (Mutable Data). Uma variável guarda um valor totalmente determinado por outros dados
(um total corrente, uma contagem, uma soma em cache), e todo lugar que altera os dados de origem também
precisa lembrar de atualizar a variável. Esqueça uma atualização e as duas divergem. Calcular o
valor quando ele é lido elimina toda essa classe de bugs e muitas vezes deixa claro o que o valor significa.

A exceção é quando os dados de origem são imutáveis e o resultado derivado também pode ser imutável:
construir uma nova estrutura a partir deles uma vez só é aceitável.

**Além do livro:** reconsidere quando o cálculo é caro e lido com muita frequência; meça antes de abrir mão do valor armazenado.

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
Antes: `UsedKwh` é uma segunda cópia de informação que já está nas leituras.

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

public class EnergyReading
{
    public EnergyReading(double kwh) => Kwh = kwh;
    public double Kwh { get; }
}

public class EnergyMeter
{
    private readonly List<EnergyReading> _readings = new();
    private double _usedKwh;

    public EnergyMeter(double budgetKwh) => BudgetKwh = budgetKwh;

    public double BudgetKwh { get; }
    public double UsedKwh => _usedKwh;
    public double RemainingKwh => BudgetKwh - UsedKwh;

    public void Record(EnergyReading reading)
    {
        _readings.Add(reading);
        _usedKwh += reading.Kwh;
    }
}
```

Passo intermediário: adicione uma asserção contra o cálculo, rode os testes e então troque o leitor.

```csharp
// fragment
public double UsedKwh
{
    get
    {
        Debug.Assert(_usedKwh == CalculatedUsedKwh);
        return _usedKwh;
    }
}

private double CalculatedUsedKwh => _readings.Sum(r => r.Kwh);
```

Depois: o campo e a atualização dele sumiram.

```csharp
public class EnergyMeter
{
    private readonly List<EnergyReading> _readings = new();

    public EnergyMeter(double budgetKwh) => BudgetKwh = budgetKwh;

    public double BudgetKwh { get; }
    public double UsedKwh => _readings.Sum(r => r.Kwh);
    public double RemainingKwh => BudgetKwh - UsedKwh;

    public void Record(EnergyReading reading) => _readings.Add(reading);
}
```

Se o campo tivesse começado com um valor inicial diferente de zero, a asserção falharia. Separe-o antes em `_openingUsedKwh` e um acumulador, e calcule apenas a parte do acumulador.

## Notas (C#)
- O cálculo cabe em uma propriedade somente leitura calculada (`=> ...`).
- `Debug.Assert` é removido das compilações Release, então rode os testes em Debug para exercitá-lo.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
