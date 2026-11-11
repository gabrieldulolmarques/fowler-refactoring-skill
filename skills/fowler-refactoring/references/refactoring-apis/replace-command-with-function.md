# Substituir Comando por Função (Replace Command with Function)

Fowler (2018), cap. 11, p. 344. Antes / também: —. Inversa: Substituir Função por Comando
([replace-function-with-command.md](replace-function-with-command.md)).

## Quando usar
Converta quando a classe apenas recebe as suas entradas, executa uma computação e retorna o resultado,
e a lógica é simples o bastante para ser lida como uma função (ou algumas funções pequenas). Não converta
quando os chamadores dependem de desfazer, enfileiramento, vários pontos de entrada ou configuração incremental.

## Mecânica
1. Extraia uma função que envolva a criação do comando e a chamada ao seu método execute ([extract-function.md](../first-set/extract-function.md)). Esta será a função substituta, e os chamadores agora passam por ela.
2. Para cada função auxiliar que o método execute chama, internalize-a no método execute ([inline-function.md](../first-set/inline-function.md)). Se a auxiliar retorna um valor, primeiro extraia essa chamada para uma variável ([extract-variable.md](../first-set/extract-variable.md)), depois internalize.
3. Mude a assinatura do método execute para que ele receba todos os parâmetros do construtor ([change-function-declaration.md](../first-set/change-function-declaration.md)). Atualize a função invólucro para passá-los.
4. No método execute, substitua cada uso de um campo pelo parâmetro correspondente, um campo de cada vez, testando após cada um. Remova também a atribuição do campo no construtor, para que um uso esquecido falhe de forma evidente. O construtor e os seus campos agora estão mortos, mas permanecem até que o passo 7 apague a classe.
5. Internalize a chamada ao construtor e a chamada a execute na função invólucro, para que ela contenha a lógica diretamente.
6. Teste.
7. Apague a classe de comando agora sem uso ([remove-dead-code.md](../moving-features/remove-dead-code.md)).

## Exemplo
Antes:

```csharp
public class InvoiceTotalCalculator
{
    private readonly Customer _customer;
    private readonly int _units;
    private readonly ShippingPolicy _shipping;

    public InvoiceTotalCalculator(Customer customer, int units, ShippingPolicy shipping)
    {
        _customer = customer;
        _units = units;
        _shipping = shipping;
    }

    private decimal Subtotal() => _customer.UnitPrice * _units;

    public decimal Execute()
    {
        return Subtotal() + _shipping.Fee;
    }
}

// chamador
decimal total = new InvoiceTotalCalculator(customer, units, shipping).Execute();
```

Passo 1, envolva a chamada:

```csharp
public static decimal InvoiceTotal(Customer customer, int units, ShippingPolicy shipping)
    => new InvoiceTotalCalculator(customer, units, shipping).Execute();
```

Passos 2 a 4, `Subtotal` internalizado, parâmetros movidos para `Execute`, campos não mais usados. O
invólucro estático do passo 1 vive na mesma classe ou em uma classe auxiliar estática, e agora chama
`new InvoiceTotalCalculator(customer, units, shipping).Execute(customer, units, shipping)`.
O construtor ainda recebe os seus três argumentos, mas não os armazena mais; ele vai embora
com a classe no passo 7:

```csharp
public decimal Execute(Customer customer, int units, ShippingPolicy shipping)
{
    var subtotal = customer.UnitPrice * units;
    return subtotal + shipping.Fee;
}
```

Passos 5 a 7, lógica internalizada no invólucro, classe apagada:

```csharp
public static decimal InvoiceTotal(Customer customer, int units, ShippingPolicy shipping)
{
    var subtotal = customer.UnitPrice * units;
    return subtotal + shipping.Fee;
}

// chamador
decimal total = InvoiceTotal(customer, units, shipping);
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
