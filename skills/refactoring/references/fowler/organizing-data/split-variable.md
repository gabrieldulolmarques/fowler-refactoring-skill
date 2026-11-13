# Dividir Variável (Split Variable)

Fowler (2018), cap. 9, p. 240. Nome anterior / outro nome: Remove Assignments to Parameters, Split Temp. Inversa: —.

## Quando usar
Smell: Dados Mutáveis (Mutable Data).

Uma variável que guarda o resultado de alguma computação para referência posterior deve ser atribuída uma só vez. Se ela é atribuída uma segunda vez com um valor que significa outra coisa, ela tem dois trabalhos, e o leitor precisa acompanhar qual deles ela tem em cada linha. Dê a cada trabalho a sua própria variável e o seu próprio nome.

Deixe em paz:
- Variáveis de laço, que mudam a cada iteração por natureza.
- Variáveis de coleta, que acumulam um valor (`total = total + x`, construção de string, adição a uma coleção). As atribuições posteriores dependem do valor anterior, então elas têm uma única responsabilidade.

Atribuir a um parâmetro de entrada é um caso comum: o parâmetro é ao mesmo tempo a entrada e o resultado de trabalho. Dividi-lo separa "o que o chamador me deu" de "o que estou calculando".

## Mecânica
1. Escolha o primeiro valor que a variável guarda. Na sua declaração e primeira atribuição, renomeie a variável para um nome que descreva apenas esse primeiro uso.
2. Atualize toda referência que lê esse primeiro valor, parando antes da segunda atribuição.
3. Compile e teste.
4. Na segunda atribuição, declare uma nova variável e nomeie-a para esse segundo uso. Se a linguagem permitir, declare-a como imutÃ¡vel (C# nÃ£o tem variÃ¡veis locais imutÃ¡veis; veja as notas de C#).
5. Repita os passos 2 a 4 para cada atribuição posterior, testando após cada etapa. Na atribuição final o nome original não tem mais referências.
6. Para um parâmetro: declare uma variável local inicializada a partir do parâmetro no início da função, renomeie o parâmetro para dizer que é a entrada original e aponte para o parâmetro as leituras que significam a entrada original. Depois continue com os passos acima na variável local, renomeando-a para dizer o que ela guarda.

## Exemplo
Antes: `value` primeiro guarda a temperatura sem calibração e depois é reutilizada para a calibrada, que é outra grandeza.

```csharp
using System;

public class Sample
{
    public int RawCounts { get; set; }
    public double CountsToCelsius { get; set; }
    public double SelfHeating { get; set; }
}

public class Calibration
{
    public double Offset { get; set; }
    public double Gain { get; set; }
}

public class Report
{
    public double ReportedTemperature(Sample sample, Calibration calibration)
    {
        double value = sample.RawCounts * sample.CountsToCelsius;
        Console.WriteLine($"Uncalibrated: {value}");

        value = (value - calibration.Offset) * calibration.Gain;
        return value - sample.SelfHeating;
    }
}
```

Depois: uma variável por responsabilidade, cada uma nomeada pelo que guarda.

```csharp
public class Report
{
    public double ReportedTemperature(Sample sample, Calibration calibration)
    {
        double uncalibrated = sample.RawCounts * sample.CountsToCelsius;
        Console.WriteLine($"Uncalibrated: {uncalibrated}");

        double calibrated = (uncalibrated - calibration.Offset) * calibration.Gain;
        return calibrated - sample.SelfHeating;
    }
}
```

Caso de parâmetro. Antes, `requested` é ao mesmo tempo a entrada e o intervalo de amostragem efetivo:

```csharp
public class Scheduler
{
    public double EffectiveInterval(double requested, bool lowBattery)
    {
        requested = Math.Max(requested, 0.5) + 0.25;
        if (lowBattery) requested *= 4;
        return requested;
    }
}
```

Intermediário: o parâmetro é renomeado para indicar que é a entrada, e uma variável local assume o valor de trabalho.

```csharp
public class Scheduler
{
    public double EffectiveInterval(double requestedSeconds, bool lowBattery)
    {
        double requested = requestedSeconds;
        requested = Math.Max(requested, 0.5) + 0.25;
        if (lowBattery) requested *= 4;
        return requested;
    }
}
```

Depois: a variável local é renomeada pelo que guarda.

```csharp
public class Scheduler
{
    public double EffectiveInterval(double requestedSeconds, bool lowBattery)
    {
        double interval = Math.Max(requestedSeconds, 0.5) + 0.25;
        if (lowBattery) interval *= 4;
        return interval;
    }
}
```

## Notas (C#)
- C# não tem variáveis locais imutáveis (`const` só serve para constantes de tempo de compilação), então atribua cada nova variável exatamente uma vez.
- Renomear um parâmetro de um método público quebra os chamadores que o passam pelo nome (argumentos nomeados).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhuma variável é atribuída duas vezes para finalidades diferentes; as únicas atribuições repetidas que restam são contadores de laço e variáveis acumuladoras.
