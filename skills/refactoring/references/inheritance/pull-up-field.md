# Subir Campo (Pull Up Field)

Fowler (2018), cap. 12, p. 353. Antes / também: —. Inversa: Descer Campo (Push Down Field)
([push-down-field.md](push-down-field.md)).

## Quando usar
Remove declarações de dados duplicadas em subclasses irmãs. Nenhum smell do catálogo se liga
diretamente a ela.

- Comece lendo como as subclasses irmãs usam os seus campos. Se duas delas guardam os mesmos
  dados para o mesmo propósito, o campo é um candidato, qualquer que seja o nome de cada um.
- Uma vez na superclasse, a declaração duplicada some e o código que a usa
  pode acompanhar (veja [pull-up-method.md](pull-up-method.md)).
- Não use quando os campos apenas se parecem mas significam coisas diferentes, ou quando apenas algumas
  das subclasses precisam dos dados. Então o campo pertence ao lugar onde está, ou a uma nova
  classe intermediária.
- Em linguagens em que os campos aparecem na primeira atribuição, sem declaração na classe,
  o mesmo efeito vem de [pull-up-constructor-body.md](pull-up-constructor-body.md).

## Mecânica
1. Inspecione todo uso de cada campo candidato e confirme que todos desempenham o mesmo papel
   (mesmo significado, mesma unidade, mesmo tempo de vida).
2. Se os nomes diferem, renomeie-os para um só nome com [rename-field.md](../organizing-data/rename-field.md). Compile e teste.
3. Declare o campo na superclasse, com uma visibilidade que as subclasses possam alcançar
   (`protected`, ou privado com uma propriedade se você preferir encapsulá-lo).
4. Apague o campo das subclasses, um de cada vez se forem muitas.
5. Compile e rode os testes.

## Exemplo
Antes: dois tipos de fatura mantêm cada um o seu próprio `customerName`.

```csharp
public abstract class Invoice
{
    public abstract decimal Total();
}

public class ServiceInvoice : Invoice
{
    private string customerName;
    private decimal hours;
    private decimal rate;

    public ServiceInvoice(string customerName, decimal hours, decimal rate)
    {
        this.customerName = customerName;
        this.hours = hours;
        this.rate = rate;
    }

    public string Describe() => $"Serviço para {customerName}";
    public override decimal Total() => hours * rate;
}

public class ProductInvoice : Invoice
{
    private string customerName;
    private decimal unitPrice;
    private int quantity;

    public ProductInvoice(string customerName, decimal unitPrice, int quantity)
    {
        this.customerName = customerName;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
    }

    public string Describe() => $"Produtos para {customerName}";
    public override decimal Total() => unitPrice * quantity;
}
```

Depois: o campo é declarado uma só vez em `Invoice`. Os construtores das subclasses ainda o atribuem,
o que [pull-up-constructor-body.md](pull-up-constructor-body.md) pode então arrumar. O inicializador `= ""`
evita o aviso CS8618 quando os tipos de referência anuláveis estão habilitados; ele pode sair quando
a atribuição for para dentro de um construtor de `Invoice`.

```csharp
public abstract class Invoice
{
    protected string customerName = "";

    public abstract decimal Total();
}

public class ServiceInvoice : Invoice
{
    private decimal hours;
    private decimal rate;

    public ServiceInvoice(string customerName, decimal hours, decimal rate)
    {
        this.customerName = customerName;
        this.hours = hours;
        this.rate = rate;
    }

    public string Describe() => $"Serviço para {customerName}";
    public override decimal Total() => hours * rate;
}

public class ProductInvoice : Invoice
{
    private decimal unitPrice;
    private int quantity;

    public ProductInvoice(string customerName, decimal unitPrice, int quantity)
    {
        this.customerName = customerName;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
    }

    public string Describe() => $"Produtos para {customerName}";
    public override decimal Total() => unitPrice * quantity;
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Todo construtor de subclasse ainda compila depois que o seu próprio campo é apagado, e a saída de
  `Describe()` e `Total()` não muda.
