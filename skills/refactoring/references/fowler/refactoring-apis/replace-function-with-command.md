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
Antes: uma função que precifica uma campanha, com várias variáveis locais que interagem entre si.

```csharp
public class Campaign
{
    public Campaign(string channel, int recipients, int optedOut)
    {
        Channel = channel;
        Recipients = recipients;
        OptedOut = optedOut;
    }

    public string Channel { get; }
    public int Recipients { get; }
    public int OptedOut { get; }
}

public class Account
{
    public Account(string region, bool isPrepaid)
    {
        Region = region;
        IsPrepaid = isPrepaid;
    }

    public string Region { get; }
    public bool IsPrepaid { get; }
}

public interface IRateTable
{
    decimal PricePerMessage(string channel);
    decimal TaxRate(string region);
}

public static class Billing
{
    public static decimal CampaignCost(Campaign campaign, Account account, IRateTable rates)
    {
        int deliverable = campaign.Recipients - campaign.OptedOut;
        decimal subtotal = deliverable * rates.PricePerMessage(campaign.Channel);
        decimal discount = 0m;
        if (deliverable > 10000)
            discount += subtotal * 0.05m;
        if (account.IsPrepaid)
            discount += subtotal * 0.02m;
        decimal taxable = subtotal - discount;
        decimal tax = taxable * rates.TaxRate(account.Region);
        return taxable + tax;
    }
}
```

Depois dos passos 1 a 4 (o encaminhador permanece, o comando passa a ser dono dos argumentos):

```csharp
public static class Billing
{
    public static decimal CampaignCost(Campaign campaign, Account account, IRateTable rates)
        => new CampaignCostCalculator(campaign, account, rates).Execute();
}

public class CampaignCostCalculator
{
    private readonly Campaign _campaign;
    private readonly Account _account;
    private readonly IRateTable _rates;

    public CampaignCostCalculator(Campaign campaign, Account account, IRateTable rates)
    {
        _campaign = campaign;
        _account = account;
        _rates = rates;
    }

    public decimal Execute()
    {
        int deliverable = _campaign.Recipients - _campaign.OptedOut;
        decimal subtotal = deliverable * _rates.PricePerMessage(_campaign.Channel);
        decimal discount = 0m;
        if (deliverable > 10000)
            discount += subtotal * 0.05m;
        if (_account.IsPrepaid)
            discount += subtotal * 0.02m;
        decimal taxable = subtotal - discount;
        decimal tax = taxable * _rates.TaxRate(_account.Region);
        return taxable + tax;
    }
}
```

Depois dos passos 5 e 6 (variáveis locais promovidas a campos, depois partes extraídas):

```csharp
public class CampaignCostCalculator
{
    private readonly Campaign _campaign;
    private readonly Account _account;
    private readonly IRateTable _rates;
    private int _deliverable;
    private decimal _subtotal;
    private decimal _discount;

    public CampaignCostCalculator(Campaign campaign, Account account, IRateTable rates)
    {
        _campaign = campaign;
        _account = account;
        _rates = rates;
    }

    public decimal Execute()
    {
        _deliverable = _campaign.Recipients - _campaign.OptedOut;
        _subtotal = _deliverable * _rates.PricePerMessage(_campaign.Channel);
        ApplyDiscounts();
        decimal taxable = _subtotal - _discount;
        return taxable + taxable * _rates.TaxRate(_account.Region);
    }

    private void ApplyDiscounts()
    {
        _discount = 0m;
        if (_deliverable > 10000)
            _discount += _subtotal * 0.05m;
        if (_account.IsPrepaid)
            _discount += _subtotal * 0.02m;
    }
}
```

O comportamento é o mesmo em todas as etapas. Observe que `Execute` agora altera campos, então uma instância do comando só serve para um uso, a menos que os campos sejam zerados no início de `Execute`.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
