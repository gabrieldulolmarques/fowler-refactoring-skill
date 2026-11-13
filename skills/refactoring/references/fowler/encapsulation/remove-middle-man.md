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

Antes: `Workspace` oculta a sua `BillingAccount` e encaminha chamadas para ela.

```csharp
public class BillingAccount
{
    public string BillingEmail { get; }
    public decimal CreditBalance { get; }

    public BillingAccount(string billingEmail, decimal creditBalance)
    {
        BillingEmail = billingEmail;
        CreditBalance = creditBalance;
    }
}

public class Workspace
{
    private readonly BillingAccount _billingAccount;

    public Workspace(BillingAccount billingAccount) => _billingAccount = billingAccount;

    public string BillingEmail => _billingAccount.BillingEmail;
    public decimal CreditBalance => _billingAccount.CreditBalance;
}

public static class Client
{
    public static string Email(Workspace workspace)
    {
        string email = workspace.BillingEmail;
        return email;
    }
}
```

Passo 1: exponha o delegado.

```csharp
public class Workspace
{
    private readonly BillingAccount _billingAccount;

    public Workspace(BillingAccount billingAccount) => _billingAccount = billingAccount;

    public BillingAccount BillingAccount => _billingAccount;
    public string BillingEmail => _billingAccount.BillingEmail;
    public decimal CreditBalance => _billingAccount.CreditBalance;
}
```

Passos 2 e 3: atualize cada cliente e depois apague os encaminhadores que não são mais usados.

```csharp
public class Workspace
{
    public Workspace(BillingAccount billingAccount) => BillingAccount = billingAccount;

    public BillingAccount BillingAccount { get; }
}

public static class Client
{
    public static string Email(Workspace workspace)
    {
        string email = workspace.BillingAccount.BillingEmail;
        return email;
    }
}
```

O comportamento é o mesmo; `Workspace` não precisa mais de um membro novo cada vez que `BillingAccount` ganha um.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
