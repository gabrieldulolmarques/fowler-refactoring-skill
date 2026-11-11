# Encapsular Variável (Encapsulate Variable)

Fowler (2018), cap. 6, p. 132. Antes / também: Encapsulate Field, Self-Encapsulate Field. Inversa: —.

## Quando usar
Smells: Dados Globais (Global Data), Dados Mutáveis (Mutable Data).

- Os dados só são fáceis de reorganizar quando o acesso a eles passa por funções: uma função pode ser
  movida ou renomeada enquanto uma antiga encaminha para ela, mas dados brutos precisam ser reapontados em todo lugar
  de uma vez. Encapsular primeiro transforma uma movimentação difícil de dados em uma movimentação fácil de função.
- Também dá um só lugar para adicionar validação, efeitos colaterais, registro em log ou rastreamento de mudanças.
- Quanto maior o escopo dos dados mutáveis, mais forte o argumento. Dados usados dentro de uma única função pequena
  raramente precisam disso.
- Dados imutáveis precisam muito menos: nada exige um gancho antes das atualizações, e as cópias são seguras.
- Com código legado, encapsule uma variável sempre que precisar adicionar ou alterar uma referência a ela,
  para que o acoplamento a ela pare de crescer.
- Autoencapsular os campos da própria classe (acessores até dentro da classe) costuma ser
  excessivo. Se uma classe é grande o bastante para precisar disso, divida a classe. Ainda assim é um passo útil
  logo antes de dividir uma.

## Mecânica
1. Crie um getter e um setter (ou uma propriedade) que leiam e escrevam a variável.
2. Faça o build e execute as verificações estáticas.
3. Substitua cada leitura direta pelo getter e cada atribuição direta pelo setter, uma
   referência de cada vez, executando os testes após cada uma.
4. Restrinja a visibilidade da variável (private, ou uma classe separada) para que o compilador
   aponte qualquer referência que você tenha deixado passar e novos acessos diretos não possam surgir.
   Se a visibilidade não puder ser restringida, renomeie-a para um nome deliberadamente chamativo (por
   exemplo `_privateOnly_x`), faça o build e conserte o que quebrar.
5. Execute os testes.
6. Decida até que profundidade vai o encapsulamento (veja abaixo). Se o valor for um registro, considere
   Encapsular Registro (Encapsulate Record) ([encapsulate-record.md](../encapsulation/encapsulate-record.md)).

### Encapsulando o valor, não apenas a referência
Os passos acima controlam a reatribuição da variável, não mudanças no objeto que ela guarda.
Opções quando os chamadores não devem mutar o objeto compartilhado:
- Devolva uma cópia no getter (comum para listas). Os chamadores podem alterar a cópia deles, mas os
  dados compartilhados ficam intactos. Os testes revelam código que dependia de mutar a instância compartilhada.
- Devolva um wrapper somente leitura ou um tipo imutável, para que tentativas de mutação falhem de forma visível. Isso é
  muitas vezes uma boa medida temporária para encontrar todos os mutadores, que você então remove ou transforma em
  métodos de atualização explícitos, antes de trocar o getter para uma cópia.
- Copie também no setter quando a origem não deve continuar ligada aos dados armazenados.
- Cópias e wrappers só protegem um nível de profundidade. Estruturas aninhadas precisam de cópias ou wrappers em cada
  nível.

## Exemplo
Antes: um campo estático lido e escrito a partir de muitas classes.

```csharp
public class Billing
{
    public static decimal TaxRate = 0.18m;
}

public class InvoiceCalculator
{
    public decimal Total(decimal subtotal) => subtotal * (1 + Billing.TaxRate);
}

public class SettingsScreen
{
    public void Apply(decimal rate) => Billing.TaxRate = rate;
}
```

Depois: o campo é renomeado e privado, e uma propriedade com o nome antigo encaminha para ele.
O comportamento não muda.

```csharp
public class Billing
{
    private static decimal _taxRate = 0.18m;

    public static decimal TaxRate
    {
        get => _taxRate;
        set => _taxRate = value;
    }
}

// Os chamadores mantêm a mesma sintaxe: Billing.TaxRate e Billing.TaxRate = rate.
```

Mudança posterior, que não faz parte da refatoração porque altera o comportamento: com o setter
como ponto de entrada único, a validação agora pode ser adicionada em um só lugar, e uma taxa negativa
que antes era aceita agora lança uma exceção.

```csharp
using System;

public class Billing
{
    private static decimal _taxRate = 0.18m;

    public static decimal TaxRate
    {
        get => _taxRate;
        set
        {
            if (value < 0) throw new ArgumentOutOfRangeException(nameof(value));
            _taxRate = value;
        }
    }
}
```

Encapsulando o valor: uma lista compartilhada entregue como cópia.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Customers
{
    private static List<string> _blocked = new();

    public static IReadOnlyList<string> Blocked => _blocked.ToList();
    public static void Block(string id) => _blocked.Add(id);
}
```

## Notas (C#)
- Um campo público vira um campo privado mais uma propriedade. Em C#, trocar um campo por uma
  propriedade mantém a sintaxe de chamada, mas quebra a compatibilidade binária e qualquer coisa que o passe
  por `ref`/`out` ou dependa de reflexão pelo nome do campo, então verifique isso.
- Um campo estático vira uma propriedade estática.
- Uma propriedade com o mesmo nome do campo mantém a sintaxe de chamada, então o passo 3 não tem nada a substituir.
  Renomeie o campo primeiro (`_x`), adicione uma propriedade com o nome antigo e faça o build. Se os chamadores
  precisarem mudar (acessores como métodos, ou um membro renomeado), substitua as referências uma de cada vez
  com testes.
- Código que passa o membro por `ref`/`out` deixa de compilar contra uma propriedade.
- Uma propriedade de tipo struct não pode ser mutada no lugar (`Prop.X = 1` é um erro de compilação);
  leia-a, altere a cópia e atribua de volta.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum membro fora da classe dona referencia o campo (faça o build depois de torná-lo privado),
  e uma busca pelo nome antigo encontra apenas o acessor.
