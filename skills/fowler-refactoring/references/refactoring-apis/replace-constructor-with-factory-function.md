# Substituir Construtor por Função de Fábrica (Replace Constructor with Factory Function)

Fowler (2018), cap. 11, p. 334. Antes / também: antes Replace Constructor with Factory Method. Inversa: —.

## Quando usar
- Construtores têm limites: não podem ser renomeados a cada uso, então `new Account(id, 'S')` diz pouco sobre o que é criado. Uma fábrica nomeada (`Account.CreateSavings(id)`) diz.
- Os chamadores passam um código de tipo literal ou uma flag apenas para escolher uma variante. Isso é um smell em si, e a fábrica pode esconder o código atrás de um nome descritivo.
- A criação pode precisar retornar uma subclasse, uma instância compartilhada ou em cache, ou um objeto de caso especial. Um construtor sempre retorna uma nova instância exatamente da sua própria classe.
- Não se incomode quando o construtor já é claro e tem uma única forma óbvia de ser chamado.

## Mecânica
1. Crie uma função de fábrica cujo corpo apenas chame o construtor com os mesmos argumentos.
2. Substitua uma chamada ao construtor por uma chamada à fábrica. Compile e teste.
3. Repita o passo 2 para cada chamador, um de cada vez.
4. Onde um chamador passa um código literal, adicione uma fábrica mais específica que embuta essa escolha no seu nome, e mude o chamador para ela.
5. Reduza a visibilidade do construtor o máximo possível (`private` ou `protected`), para que código novo não possa contornar a fábrica. Compile e teste.

## Exemplo
Antes:

```csharp
using System;

public class Invoice
{
    public string Customer { get; }
    public string KindCode { get; }

    public Invoice(string customer, string kindCode)
    {
        Customer = customer;
        KindCode = kindCode;
    }

    public string Kind => KindCode switch
    {
        "R" => "Recorrente",
        "O" => "Avulsa",
        _ => throw new ArgumentException("Tipo desconhecido")
    };
}

// chamadores
var a = new Invoice(row.Customer, row.KindCode);
var b = new Invoice("Acme", "R");
```

Depois:

```csharp
using System;

public class Invoice
{
    public string Customer { get; }
    public string KindCode { get; }

    private Invoice(string customer, string kindCode)
    {
        Customer = customer;
        KindCode = kindCode;
    }

    public static Invoice Create(string customer, string kindCode) =>
        new Invoice(customer, kindCode);

    public static Invoice CreateRecurring(string customer) =>
        new Invoice(customer, "R");

    public string Kind => KindCode switch
    {
        "R" => "Recorrente",
        "O" => "Avulsa",
        _ => throw new ArgumentException("Tipo desconhecido")
    };
}

// chamadores
var a = Invoice.Create(row.Customer, row.KindCode);
var b = Invoice.CreateRecurring("Acme");
```

O comportamento é o mesmo; o código literal não aparece mais no ponto de chamada de `b`.

## Notas (C#)
- A fábrica é um método de fábrica estático. Torne o construtor `private` (ou `protected` se as subclasses precisarem chamá-lo) quando todos os chamadores tiverem migrado.
- Se a fábrica precisa retornar uma subclasse, um construtor `private` na base impede que subclasses externas derivem dela. Aninhe as subclasses na classe base, ou torne o construtor da base `protected` ou `private protected`. Mantenha os construtores das subclasses `internal` ou `private` para que só a fábrica os alcance.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
