# Remover Intermediário (Remove Middle Man)

Fowler (2018), cap. 7, p. 192. Antes / também: —. Inversa: Ocultar Delegação (Hide Delegate) ([hide-delegate.md](hide-delegate.md)).

## Quando usar
Smell: Intermediário (Middle Man). Uma classe oculta um delegado atrás de métodos de encaminhamento e, com o tempo, a maioria
de seus membros não faz nada além de chamar o mesmo membro no delegado. Cada novo recurso do delegado
exige mais um encaminhador, e a classe não acrescenta comportamento próprio.

Gatilho típico: ocultação aplicada com entusiasmo demais, em nome de "nunca fale com estranhos". Quanto
ocultar é uma decisão de julgamento que muda conforme o sistema evolui, então é normal reverter uma
Ocultar Delegação anterior.

Não é motivo para remover tudo: alguns encaminhadores que os clientes usam constantemente podem ficar. Também
é normal manter a ocultação onde o delegado provavelmente será substituído ou sua estrutura
provavelmente mudará, já que os chamadores ficariam protegidos dessa mudança.

## Mecânica
1. Adicione um getter (um acessor) no servidor que exponha o objeto delegado.
2. Escolha um método de encaminhamento. Em cada cliente que o chama, substitua a chamada por uma
   chamada encadeada pelo novo acessor (`server.Delegate.Member`). Compile e teste após cada
   substituição.
3. Quando não restar nenhum chamador desse método de encaminhamento, apague-o. Compile e teste.
4. Repita os passos 2 e 3 para os outros encaminhadores que você quer remover.

Se sua ferramenta permitir, um atalho é aplicar Encapsular Variável (Encapsulate Variable) ao campo do delegado
para que os encaminhadores passem pelo acessor público e depois Internalizar Função (Inline Function) em cada encaminhador para
substituir todos os seus chamadores de uma vez ([encapsulate-variable.md](../first-set/encapsulate-variable.md), [inline-function.md](../first-set/inline-function.md)).

## Exemplo
Antes: `Customer` oculta sua `Account` e encaminha para ela.

```csharp
public class Account
{
    public string Manager { get; }
    public decimal CreditLimit { get; }

    public Account(string manager, decimal creditLimit)
    {
        Manager = manager;
        CreditLimit = creditLimit;
    }
}

public class Customer
{
    private readonly Account _account;

    public Customer(Account account) => _account = account;

    public string Manager => _account.Manager;
    public decimal CreditLimit => _account.CreditLimit;
}

// cliente
string manager = customer.Manager;
```

Passo 1: exponha o delegado.

```csharp
public class Customer
{
    private readonly Account _account;

    public Customer(Account account) => _account = account;

    public Account Account => _account;
    public string Manager => _account.Manager;
    public decimal CreditLimit => _account.CreditLimit;
}
```

Passos 2 e 3: atualize cada cliente e depois apague os encaminhadores que não são mais usados.

```csharp
// cliente
string manager = customer.Account.Manager;

public class Customer
{
    public Customer(Account account) => Account = account;

    public Account Account { get; }
}
```

O comportamento é o mesmo; `Customer` não precisa mais de um novo membro cada vez que `Account` ganha um.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
