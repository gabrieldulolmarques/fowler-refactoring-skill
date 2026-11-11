# Substituir Variável Temporária por Consulta (Replace Temp with Query)

Fowler (2018), cap. 7, p. 178. Antes / também: —. Inversa: —.

## Quando usar
Smells: Função Longa (Long Function).

- Uma variável temporária captura o resultado de uma expressão, e o código posterior apenas a lê. Substituí-la por uma
  consulta dá um nome ao cálculo e permite que outros métodos o reutilizem.
- Você está quebrando um método longo e as temporárias forçam cada trecho extraído a receber parâmetros extras. Quando as temporárias
  viram consultas, os trechos podem ser extraídos livremente.
- O mesmo valor é calculado da mesma forma em vários métodos de uma classe.

Não use quando:
- A variável é um instantâneo de um valor que muda depois (um "valor antigo" mantido de propósito). A
  consulta retornaria um resultado diferente no ponto de uso.
- A variável é atribuída de um jeito que não pode ser reunido em um único cálculo.
- O código está fora de uma classe e a consulta precisaria de muitos parâmetros; o ganho desaparece.
- O cálculo é caro e usado muitas vezes em um caminho crítico; meça primeiro ou mantenha a temporária.

## Mecânica
1. Garanta que o valor esteja definido antes da primeira leitura e que não possa ser diferente em uma leitura posterior
   do mesmo cálculo.
2. Se a variável for atribuída mais de uma vez, reestruture para que tenha uma única atribuição, ou
   confirme que todas as atribuições irão para a consulta. C# não tem variável local somente leitura, então
   confirme lendo o código ou pelos avisos do compilador. Use `const` apenas para valores
   de tempo de compilação. Compile e teste.
3. Extraia o cálculo da variável para um novo método ou propriedade. Se o nome que você quer
   colidir com a variável, escolha um nome provisório para o método. Onde várias atribuições
   constroem o valor, o método extraído deve conter todas elas.
4. Garanta que o novo método não tenha efeitos colaterais. Se tiver, aplique antes Separar Consulta de Modificador (Separate Query from Modifier)
   ([separate-query-from-modifier.md](../refactoring-apis/separate-query-from-modifier.md)).
5. Compile e teste.
6. Aplique Internalizar Variável (Inline Variable) ([inline-variable.md](../first-set/inline-variable.md)) para remover a temporária, substituindo cada leitura por uma
   chamada à consulta. Compile e teste.
7. Repita para a próxima temporária.

## Exemplo
Antes:

```csharp
public class Invoice
{
    private readonly int _hours;
    private readonly Consultant _consultant;

    public Invoice(int hours, Consultant consultant)
    {
        _hours = hours;
        _consultant = consultant;
    }

    public decimal Total()
    {
        var fees = _hours * _consultant.HourlyRate;
        var surchargeRate = 0.02m;
        if (fees > 5000m) surchargeRate = 0.05m;
        return fees + fees * surchargeRate;
    }
}

public record Consultant(decimal HourlyRate);
```

Passo a passo: `fees` já é atribuída uma só vez, então extraia seu
lado direito para `Fees` e internalize a variável. Depois extraia `surchargeRate`, mantendo as duas
atribuições dentro do novo método, e internalize-a.

Depois:

```csharp
public class Invoice
{
    private readonly int _hours;
    private readonly Consultant _consultant;

    public Invoice(int hours, Consultant consultant)
    {
        _hours = hours;
        _consultant = consultant;
    }

    public decimal Total() => Fees + Fees * SurchargeRate;

    private decimal Fees => _hours * _consultant.HourlyRate;

    private decimal SurchargeRate => Fees > 5000m ? 0.05m : 0.02m;
}

public record Consultant(decimal HourlyRate);
```

O comportamento é o mesmo. `Fees` agora é reutilizável por outros métodos, e `Total` não carrega mais
temporárias que bloqueariam extrações futuras.

## Notas de C#
- Uma propriedade somente leitura (`private decimal Fees => ...`) serve para cálculos baratos e sem efeitos colaterais.
- Mantenha as consultas caras como métodos (`ComputeFees()`), para que o custo fique visível no ponto de chamada.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A consulta retorna o mesmo valor em todos os pontos onde a temporária era lida (sem mudanças de estado
  entre eles).
