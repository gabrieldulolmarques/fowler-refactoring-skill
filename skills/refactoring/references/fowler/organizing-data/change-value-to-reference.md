# Mudar Valor para Referência (Change Value to Reference)

Fowler (2018), cap. 9, p. 256. Antes / também: —. Inversa: Mudar Referência para Valor (Change Reference to Value)
([change-reference-to-value.md](change-reference-to-value.md)).

## Quando usar
- Vários objetos hospedeiros (faturas, pedidos) guardam cada um a sua própria cópia da mesma entidade lógica
  (uma conta, um cliente), construída com `new` a partir do mesmo identificador.
- A entidade é atualizada ou enriquecida ao longo do tempo, então toda cópia precisa ser encontrada e alterada. Uma cópia
  esquecida deixa os dados inconsistentes.
- A entidade tem identidade real: dois objetos com o mesmo id são a mesma coisa, não apenas
  valores iguais.

Não vale a pena quando a entidade nunca é atualizada: as cópias são então inofensivas, e um valor é mais simples
(sem repositório, sem ciclo de vida para gerenciar). Memória duplicada, por si só, raramente é motivo.

## Mecânica
1. Crie um repositório (ou registro) que guarde uma instância por identificador, se o código ainda não
   tiver um. Reutilize um existente, se houver.
2. Garanta que o código que constrói o objeto hospedeiro tenha o que precisa para localizar a instância
   correta, normalmente o identificador que já está presente na sua entrada.
3. Mude o construtor do hospedeiro (ou o código que o cria) para pedir a instância ao repositório
   em vez de chamar `new`. Compile e teste após cada construtor que você mudar.
4. Decida como o repositório é preenchido: criado no primeiro pedido, ou pré-carregado de modo que um
   id desconhecido seja um erro. Faça o comportamento do hospedeiro corresponder a essa escolha.
5. Se o repositório for global, considere passá-lo como parâmetro do construtor para que o hospedeiro
   não fique acoplado a estado compartilhado.

## Exemplo
Antes: toda fatura constrói a sua própria `Account`, então duas faturas da mesma conta guardam dois
objetos separados.

```csharp
public class Account
{
    public Account(string id) { Id = id; }
    public string Id { get; }
    public decimal CreditLimit { get; set; }
}

public class Invoice
{
    public Invoice(string number, string accountId)
    {
        Number = number;
        Account = new Account(accountId);
    }

    public string Number { get; }
    public Account Account { get; }
}
```

Aumentar o limite de crédito por meio de uma fatura não afeta a outra.

Depois: um repositório entrega uma `Account` por id, e `Invoice` o utiliza.

```csharp
using System.Collections.Generic;

public class AccountRepository
{
    private readonly Dictionary<string, Account> _accounts = new();

    public Account GetOrRegister(string id)
    {
        if (!_accounts.TryGetValue(id, out var account))
        {
            account = new Account(id);
            _accounts[id] = account;
        }
        return account;
    }

    public Account? Find(string id) =>
        _accounts.TryGetValue(id, out var account) ? account : null;
}

public class Invoice
{
    public Invoice(string number, string accountId, AccountRepository accounts)
    {
        Number = number;
        Account = accounts.GetOrRegister(accountId);
    }

    public string Number { get; }
    public Account Account { get; }
}
```

Agora `a.Account` e `b.Account` são o mesmo objeto para o mesmo id, então uma mudança feita por meio de uma
fatura é vista por todas. Aqui o repositório é passado como parâmetro em vez de lido de um global.

## Notas (C#)
- Um repositório ou registro que entrega a instância compartilhada é a forma usual: um
  dicionário indexado por id, dentro de uma classe pequena.
- Se o repositório for compartilhado entre threads, use uma estrutura thread-safe (por exemplo
  `ConcurrentDictionary.GetOrAdd`) para que dois chamadores não possam criar duas instâncias para um mesmo id.
- A igualdade por referência é o padrão de uma classe, que é o que você quer aqui: não adicione igualdade
  por valor à entidade compartilhada.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Adicione um teste de que dois hospedeiros construídos a partir do mesmo id retornam a mesma instância
  (`Assert.Same`), e de que uma mudança feita por um é visível pelo outro.
