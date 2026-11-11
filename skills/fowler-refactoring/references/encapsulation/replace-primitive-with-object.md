# Substituir Primitivo por Objeto (Replace Primitive with Object)

Fowler (2018), cap. 7, p. 174. Antes / também: Replace Data Value with Object, Replace Type Code with Class. Inversa: —.

## Quando usar
Smell: Obsessão por Primitivos (Primitive Obsession). Um simples `string` ou `int` representa um conceito de domínio, e a lógica sobre ele (validação, formatação, comparação, extração de partes) começa a aparecer ou está duplicada pela base de código. Encapsular o valor dá a essa lógica um lugar só dela.

Faça isso assim que quiser fazer mais com o valor do que imprimir ou armazenar. A primeira versão do tipo pode ser um wrapper simples, já que dá ao comportamento futuro um lugar para pousar. É uma decisão de julgamento: se o valor só é repassado e nunca inspecionado, um wrapper pode não valer a pena.

## Mecânica
1. Se o valor for um campo simples, aplique antes Encapsular Variável (Encapsulate Variable) ([encapsulate-variable.md](../first-set/encapsulate-variable.md)), para que todas as leituras e escritas passem por um único getter e setter.
2. Crie um pequeno tipo de valor que receba o primitivo existente em seu construtor e o exponha (em C#, `ToString()` ou uma conversão explícita costuma ler melhor do que uma propriedade genérica `Value`).
3. Faça o build e execute as verificações estáticas.
4. Altere o setter para construir o novo tipo e armazená-lo, mudando o tipo do campo.
5. Altere o getter para retornar o primitivo obtido do novo tipo, de modo que os chamadores ainda vejam o tipo antigo.
6. Faça o build e teste.
7. Renomeie os acessores originais ([change-function-declaration.md](../first-set/change-function-declaration.md)) se agora enganarem, por exemplo um getter que retorna uma string de descrição em vez do conceito.
8. Decida se é um objeto de valor ou um objeto de referência ([change-reference-to-value.md](../organizing-data/change-reference-to-value.md), [change-value-to-reference.md](../organizing-data/change-value-to-reference.md)).

A seguir, opcionalmente: adicione um acessor que retorne o novo objeto e migre os chamadores para ele um de cada vez, depois mova a validação, a comparação e a formatação para o tipo, tornando-o imutável com igualdade por valor. Cada uma dessas é uma pequena mudança testada por si só.

## Exemplo
Antes: o telefone de um cliente é uma string, e os chamadores a destrinchan.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Customer
{
    public string Phone { get; set; } = "";
}

public static class Reports
{
    public static int CountInArea(IEnumerable<Customer> customers, string areaCode) =>
        customers.Count(c => c.Phone.StartsWith(areaCode));
}
```

Depois: um tipo de valor é dono da validação e do código de área.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public sealed record PhoneNumber
{
    private readonly string _digits;

    public PhoneNumber(string value)
    {
        if (value is null || value.Length != 10 || !value.All(char.IsDigit))
            throw new ArgumentException($"'{value}' is not a 10-digit phone number");
        _digits = value;
    }

    public string AreaCode => _digits[..2];
    public string Formatted() => $"({AreaCode}) {_digits[2..6]}-{_digits[6..]}";
    public override string ToString() => _digits;
}

public class Customer
{
    private PhoneNumber _phone;

    public Customer(string phone) => _phone = new PhoneNumber(phone);

    public PhoneNumber Phone => _phone;

    // Acessor antigo mantido para os chamadores existentes, renomeado porque agora retorna texto.
    public string PhoneText
    {
        get => _phone.ToString();
        set => _phone = new PhoneNumber(value);
    }
}

public static class Reports
{
    public static int CountInArea(IEnumerable<Customer> customers, string areaCode) =>
        customers.Count(c => c.Phone.AreaCode == areaCode);
}
```

O mesmo comportamento para entradas válidas de 10 dígitos; um número malformado agora é rejeitado quando é atribuído, e não descoberto depois. O cliente é sempre construído com um telefone, então `Phone` nunca é nulo.

## Notas de C#
- Uma `string` ou `int` com significado vira seu próprio tipo: um `record`, ou um `readonly record struct` para valores pequenos. Se os valores legais forem um conjunto fechado e fixo, sem comportamento extra, um `enum` pode bastar.
- Um `record` dá igualdade por valor de graça; mantenha o estado imutável.
- Um `readonly record struct` pode ser `default`, o que pula o construtor e sua validação. Uma expressão `with` em um record também copia o estado sem executar a validação. Use uma `sealed class` quando qualquer um dos dois importar.
- Um `enum` é mais fraco que um wrapper: qualquer inteiro pode ser convertido para ele sem verificação.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Faça grep pelas comparações e parsing brutos do primitivo antigo (literais de string, `StartsWith`, `Substring`); nenhum deve restar fora do novo tipo.
- Todo ponto de construção passa pelo construtor que valida.
