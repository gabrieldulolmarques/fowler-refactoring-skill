# Introduzir Caso Especial (Introduce Special Case)

Fowler (2018), cap. 10, p. 289. Antes / também: Introduce Null Object. Inversa: —.

## Quando usar
Smells: Campo Temporário (Temporary Field).
- Muitos chamadores de uma estrutura de dados verificam o mesmo valor especial (null, uma string sentinela, um id mágico) e a maioria deles responde do mesmo jeito.
- Você quer essa resposta compartilhada em um só lugar, de modo que os chamadores simplesmente peçam ao objeto o que precisam.
- Null é o valor especial mais comum, daí o nome Null Object, mas a técnica funciona para qualquer caso especial ("desconhecido", "visitante", "sem plano").
- Mantenha uma verificação real onde um chamador realmente precisar de comportamento diferente; algumas exceções são normais.

## Mecânica
Parta de um contêiner (classe ou record) cuja propriedade, o sujeito, pode guardar o valor especial, e de clientes que o comparam com esse valor.

1. Adicione ao sujeito uma propriedade no estilo `IsSpecialCase`, retornando `false`.
2. Crie o tipo de caso especial apenas com essa propriedade, retornando `true`.
3. Aplique Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) à comparação com o valor especial e faça todo cliente chamar a nova função em vez de comparar diretamente. Opcionalmente, faça-a lançar exceção em valores inesperados durante a migração.
4. Faça o contêiner retornar o objeto de caso especial em vez do valor especial bruto (ou adicione-o por um passo de transformação para registros simples).
5. Altere o corpo da verificação extraída para usar a nova propriedade. Compile e teste.
6. Para cada cliente, encontre a reação compartilhada e mova-a para o tipo de caso especial (Combinar Funções em Classe (Combine Functions into Class), [combine-functions-into-class.md](../first-set/combine-functions-into-class.md), ou em Transformação, [combine-functions-into-transform.md](../first-set/combine-functions-into-transform.md)). Substitua a condicional do cliente por uma chamada simples. Teste após cada cliente.
7. Objetos relacionados que o caso especial precisa retornar são eles mesmos casos especiais (por exemplo, um objeto de histórico nulo). Escritas que os clientes costumavam pular viram operações vazias no caso especial.
8. Para os clientes que ainda precisam de comportamento diferente, aplique Internalizar Função (Inline Function) ([inline-function.md](../first-set/inline-function.md)) à verificação extraída, transformando-a em um teste direto da propriedade.
9. Aplique Remover Código Morto (Remove Dead Code) ([remove-dead-code.md](../moving-features/remove-dead-code.md)) à verificação extraída quando ninguém mais a chamar.

Trate o caso especial como um valor: ele não deve mudar após a criação, seja o que for que os objetos reais que ele substitui permitam. Se os clientes só leem, uma instância constante ou literal pode bastar.

## Exemplo
Antes: quatro clientes tratam um cliente ausente em uma conta. O exemplo pula a etapa da verificação extraída (passo 3) e vai direto à forma final.

```csharp
public class Account
{
    private readonly Customer? _customer;
    public Account(Customer? customer) => _customer = customer;
    public Customer? Customer => _customer;
}

public class Customer
{
    public string Name { get; init; } = "";
    public string PlanCode { get; set; } = "";
    public int LateInvoicesLastYear { get; init; }
}

// clientes
string label = account.Customer == null ? "guest" : account.Customer.Name;
string plan = account.Customer == null ? "basic" : account.Customer.PlanCode;
if (account.Customer != null) account.Customer.PlanCode = newPlan;
int late = account.Customer == null ? 0 : account.Customer.LateInvoicesLastYear;
```

Depois: o cliente ausente é um objeto de caso especial.

```csharp
public class Customer
{
    public virtual bool IsMissing => false;
    public virtual string Name { get; init; } = "";
    public virtual string PlanCode { get; set; } = "";
    public virtual int LateInvoicesLastYear { get; init; }
}

public sealed class MissingCustomer : Customer
{
    public override bool IsMissing => true;
    public override string Name { get => "guest"; init { } }
    public override string PlanCode { get => "basic"; set { /* ignorado */ } }
    public override int LateInvoicesLastYear { get => 0; init { } }
}

public class Account
{
    private readonly Customer? _customer;
    public Account(Customer? customer) => _customer = customer;
    public Customer Customer => _customer ?? new MissingCustomer();
}

// clientes
string label = account.Customer.Name;
string plan = account.Customer.PlanCode;
account.Customer.PlanCode = newPlan;
int late = account.Customer.LateInvoicesLastYear;

// o único cliente que precisa se comportar de forma diferente mantém um teste explícito
string greeting = account.Customer.IsMissing ? "Welcome, new tenant" : $"Hello, {account.Customer.Name}";
```

Mesmo comportamento: os chamadores recebem os mesmos valores de antes, e a escrita em um cliente ausente continua sendo uma operação vazia.

## Notas de C#
- Com tipos de referência anuláveis habilitados, o caso especial remove `?` e as verificações de null nos pontos de chamada: a propriedade passa a ser não anulável e nunca retorna null.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
