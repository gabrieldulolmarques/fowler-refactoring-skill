# Extrair Classe (Extract Class)

Fowler (2018), cap. 7, p. 182. Antes / também: —. Inversa: Internalizar Classe (Inline Class)
([inline-class.md](inline-class.md)).

## Quando usar
Smells: Classe Grande (Large Class), Alteração Divergente (Divergent Change), Agrupamentos de Dados (Data Clumps), Obsessão por Primitivos (Primitive Obsession), Campo Temporário (Temporary Field).

- Uma classe cresceu até ter muitos campos e métodos, e parte dela pode ser entendida isoladamente.
- Um subconjunto dos campos e métodos pertence junto: os campos mudam juntos ou dependem uns dos outros.
- Teste: remova mentalmente um campo ou método. Se outros membros perderem o sentido, eles pertencem à mesma classe extraída.
- Subtipagem ou variação afeta apenas alguns recursos da classe, ou recursos diferentes variam de maneiras diferentes.

Não use quando as partes estiverem muito emaranhadas com o resto e não houver uma
responsabilidade clara para nomear. Também não divida uma classe pequena e coesa.

## Mecânica
1. Decida qual responsabilidade separar e dê um nome a ela.
2. Crie a nova classe, vazia. Se o nome da original não descrever mais o que sobrou, renomeie-a.
3. Dê à original uma instância da nova classe, criada em seu construtor, e guarde-a em um campo privado.
4. Mova os campos um de cada vez ([move-field.md](../moving-features/move-field.md)). Os membros da original agora delegam para a nova classe. Compile e teste após cada campo.
5. Mova os métodos um de cada vez ([move-function.md](../moving-features/move-function.md)), começando pelos de nível mais baixo (os que são chamados, e não os que chamam). Compile e teste após cada método.
6. Revise as duas interfaces públicas: remova métodos que não são mais necessários e renomeie membros para se adequarem ao novo contexto (a nova classe não precisa dos prefixos ou qualificadores antigos).
7. Decida se vai expor o novo objeto aos clientes. Se sim, considere torná-lo antes um objeto de valor ([change-reference-to-value.md](../organizing-data/change-reference-to-value.md)).

## Exemplo
Antes: uma classe de fatura que também guarda os dados do endereço de cobrança.

```csharp
public class Invoice
{
    private decimal _amount;
    private string _billingStreet;
    private string _billingCity;
    private string _billingZip;

    public Invoice(decimal amount, string street, string city, string zip)
    {
        _amount = amount;
        _billingStreet = street;
        _billingCity = city;
        _billingZip = zip;
    }

    public decimal Amount => _amount;
    public string BillingStreet => _billingStreet;
    public string BillingCity => _billingCity;
    public string BillingZip => _billingZip;

    public string BillingLabel => $"{_billingStreet}, {_billingCity} {_billingZip}";
}
```

Depois: os dados e o comportamento do endereço vivem em `Address`; `Invoice` mantém seus membros públicos
como delegadores, então os chamadores não mudam.

```csharp
public class Address
{
    public Address(string street, string city, string zip)
    {
        Street = street;
        City = city;
        Zip = zip;
    }

    public string Street { get; }
    public string City { get; }
    public string Zip { get; }

    public override string ToString() => $"{Street}, {City} {Zip}";
}

public class Invoice
{
    private readonly decimal _amount;
    private readonly Address _billingAddress;

    public Invoice(decimal amount, string street, string city, string zip)
    {
        _amount = amount;
        _billingAddress = new Address(street, city, zip);
    }

    public decimal Amount => _amount;
    public string BillingStreet => _billingAddress.Street;
    public string BillingCity => _billingAddress.City;
    public string BillingZip => _billingAddress.Zip;

    public string BillingLabel => _billingAddress.ToString();
}
```

Um passo posterior pode expor `Address` aos clientes e eliminar os delegadores `Billing*`.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda: os membros públicos da classe original retornam os mesmos valores de antes.
