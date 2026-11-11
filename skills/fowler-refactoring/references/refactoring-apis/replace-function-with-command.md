# Substituir Função por Comando (Replace Function with Command)

Fowler (2018), cap. 11, p. 337. Antes / também: Replace Method with Method Object. Inversa:
Substituir Comando por Função (Replace Command with Function) ([replace-command-with-function.md](replace-command-with-function.md)).

## Quando usar
Smell: Função Longa (Long Function). O gatilho típico é uma função cujas variáveis locais e parâmetros estão tão
entrelaçados que Extrair Função (Extract Function) precisaria de listas longas de parâmetros ou retornaria vários valores.
Transformar a função em um objeto faz dessas variáveis locais campos, para que as partes possam compartilhá-los.

Um comando também ajuda quando a operação precisa de mais do que uma chamada pode oferecer: desfazer, ser enfileirada ou
registrada em log, parâmetros fornecidos em etapas, personalização por subclasse ou gancho, ou testes voltados aos seus
passos internos.

Não use por padrão. Um comando é estrutura extra; uma função simples (ou delegado) é a
melhor escolha na maior parte do tempo. Recorra a um comando apenas quando um dispositivo mais simples não der a você
o que você precisa.

## Mecânica
1. Crie uma classe vazia com o nome da função (siga a convenção de nomes da linguagem para
   comandos).
2. Aplique Mover Função (Move Function) ([move-function.md](../moving-features/move-function.md)) para mover o corpo da função para a classe como um
   único método. Use o nome da convenção para ele, ou um genérico como `Execute`.
   Deixe a função original no lugar como um encaminhador que cria o comando e o chama;
   mantenha-a até o fim.
3. Compile e teste.
4. Mova os argumentos para o construtor um de cada vez: adicione um campo e um parâmetro de
   construtor, passe-o a partir do encaminhador, remova-o da lista de parâmetros do método e
   atualize os seus usos no corpo. Compile e teste após cada um.
5. Opcionalmente, para permitir a decomposição: promova as variáveis locais a campos, uma de cada vez,
   compilando e testando após cada uma.
6. Agora aplique Extrair Função ([extract-function.md](../first-set/extract-function.md)) ao corpo; os novos métodos leem
   e escrevem os campos diretamente.

## Exemplo
Antes: uma função que calcula o preço de uma fatura, com várias variáveis locais que interagem.

```csharp
public record Customer(string Region, bool IsPreferred);
public record Order(int Units, decimal UnitPrice);
public interface ITaxTable { decimal RateFor(string region); }

public static class Billing
{
    public static decimal InvoiceTotal(Order order, Customer customer, ITaxTable taxes)
    {
        decimal subtotal = order.Units * order.UnitPrice;
        decimal discount = 0m;
        if (order.Units > 100)
            discount += subtotal * 0.05m;
        if (customer.IsPreferred)
            discount += subtotal * 0.02m;
        decimal taxable = subtotal - discount;
        decimal tax = taxable * taxes.RateFor(customer.Region);
        return taxable + tax;
    }
}
```

Depois dos passos 1 a 4 (o encaminhador permanece, o comando é dono dos argumentos):

```csharp
public static class Billing
{
    public static decimal InvoiceTotal(Order order, Customer customer, ITaxTable taxes)
        => new InvoiceTotalCalculator(order, customer, taxes).Execute();
}

public class InvoiceTotalCalculator
{
    private readonly Order _order;
    private readonly Customer _customer;
    private readonly ITaxTable _taxes;

    public InvoiceTotalCalculator(Order order, Customer customer, ITaxTable taxes)
    {
        _order = order;
        _customer = customer;
        _taxes = taxes;
    }

    public decimal Execute()
    {
        decimal subtotal = _order.Units * _order.UnitPrice;
        decimal discount = 0m;
        if (_order.Units > 100)
            discount += subtotal * 0.05m;
        if (_customer.IsPreferred)
            discount += subtotal * 0.02m;
        decimal taxable = subtotal - discount;
        decimal tax = taxable * _taxes.RateFor(_customer.Region);
        return taxable + tax;
    }
}
```

Depois dos passos 5 e 6 (variáveis locais promovidas a campos, depois partes extraídas):

```csharp
public class InvoiceTotalCalculator
{
    private readonly Order _order;
    private readonly Customer _customer;
    private readonly ITaxTable _taxes;
    private decimal _subtotal;
    private decimal _discount;

    public InvoiceTotalCalculator(Order order, Customer customer, ITaxTable taxes)
    {
        _order = order;
        _customer = customer;
        _taxes = taxes;
    }

    public decimal Execute()
    {
        _subtotal = _order.Units * _order.UnitPrice;
        ApplyDiscounts();
        decimal taxable = _subtotal - _discount;
        return taxable + taxable * _taxes.RateFor(_customer.Region);
    }

    private void ApplyDiscounts()
    {
        _discount = 0m;
        if (_order.Units > 100)
            _discount += _subtotal * 0.05m;
        if (_customer.IsPreferred)
            _discount += _subtotal * 0.02m;
    }
}
```

O comportamento é o mesmo em cada etapa. Note que `Execute` agora altera campos, então uma instância
de comando é de uso único, a menos que os campos sejam reiniciados no começo de `Execute`.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
