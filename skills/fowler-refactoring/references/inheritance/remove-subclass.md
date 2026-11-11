# Remover Subclasse (Remove Subclass)

Fowler (2018), cap. 12, p. 369. Antes / também: antes Replace Subclass with Fields.
Inversa: Substituir Código de Tipo por Subclasses (Replace Type Code with Subclasses) ([replace-type-code-with-subclasses.md](replace-type-code-with-subclasses.md)).

## Quando usar
Smell: nenhum específico no livro (relacionados: Elemento Ocioso (Lazy Element), Generalidade Especulativa (Speculative Generality)).

- Uma subclasse foi adicionada para uma variação que nunca cresceu: ela sobrescreve um ou dois membros para retornar uma
  constante, e nada mais depende do seu tipo. A classe custa atenção dos leitores e
  não devolve nada.
- O comportamento que justificava a subclasse foi para outro lugar ou foi apagado, deixando um toco.
- Normalmente aplicada a um grupo inteiro de subclasses irmãs. Prepare todas primeiro
  (fábrica, testes de tipo), depois incorpore-as uma de cada vez.
- Antes de apagar, olhe os clientes em busca de comportamento que dependa da subclasse. Se ele
  pertenceria à subclasse, ela ainda pode valer a pena ser mantida.
- Não use quando as subclasses carregam comportamento polimórfico real ou estrutura de dados
  diferente. Essa variação é para o que a herança serve.

## Mecânica
1. Encapsule a construção: aplique Substituir Construtor por Função de Fábrica (Replace Constructor with Factory Function)
   ([replace-constructor-with-factory-function.md](../refactoring-apis/replace-constructor-with-factory-function.md)) a cada construtor de subclasse. Se os
   chamadores escolhem a subclasse a partir de um valor de dados (um código, um campo de registro), mova essa lógica
   de seleção para a fábrica. Compile e teste.
2. Encontre todo lugar que testa o tipo de um objeto contra uma subclasse (`is`, `as`,
   `GetType()`). Extraia cada teste para uma função ([extract-function.md](../first-set/extract-function.md)), mova-a para
   a superclasse ([move-function.md](../moving-features/move-function.md)) e faça os chamadores usá-la. Compile e teste após
   cada mudança.
3. Adicione à superclasse um campo que represente aquilo em que as subclasses diferem, e defina-o no
   construtor com o caso padrão. Exponha-o pelo mesmo membro que as subclasses
   sobrescrevem.
4. Pegue uma subclasse. Mude a fábrica para que ela retorne a superclasse com o campo definido com
   o valor daquela subclasse, e mude os testes de tipo movidos para lerem o campo. Compile e teste.
5. Apague essa subclasse. Compile e teste.
6. Repita os passos 4 e 5 para cada subclasse restante.
7. Opcionalmente, torne o caso padrão simétrico aos outros (defina o campo explicitamente na
   fábrica) se isso não acrescentar complexidade.

## Exemplo
Antes: duas subclasses que apenas retornam uma constante, criadas a partir de registros armazenados.

```csharp
public record AccountRecord(string Owner, string Kind);

public class Account
{
    public Account(string owner) => Owner = owner;

    public string Owner { get; }
    public virtual string Kind => "básica";
}

public class SavingsAccount : Account
{
    public SavingsAccount(string owner) : base(owner) { }
    public override string Kind => "poupança";
}

public class CheckingAccount : Account
{
    public CheckingAccount(string owner) : base(owner) { }
    public override string Kind => "corrente";
}

// cliente
var accounts = new List<Account>();
foreach (var record in records)
{
    switch (record.Kind)
    {
        case "S": accounts.Add(new SavingsAccount(record.Owner)); break;
        case "C": accounts.Add(new CheckingAccount(record.Owner)); break;
        default: accounts.Add(new Account(record.Owner)); break;
    }
}
int savingsCount = accounts.Count(a => a is SavingsAccount);
```

Passos 1 e 2: encapsule a criação em uma fábrica e o teste de tipo em um membro da
superclasse.

```csharp
public class Account
{
    // ...
    public bool IsSavings => this is SavingsAccount;

    public static Account Create(AccountRecord record) => record.Kind switch
    {
        "S" => new SavingsAccount(record.Owner),
        "C" => new CheckingAccount(record.Owner),
        _ => new Account(record.Owner),
    };
}

// cliente
var accounts = records.Select(Account.Create).ToList();
int savingsCount = accounts.Count(a => a.IsSavings);
```

Passos 3 a 7: adicione o campo, incorpore cada subclasse na fábrica e depois apague as subclasses.

```csharp
public class Account
{
    private Account(string owner, string kind)
    {
        Owner = owner;
        Kind = kind;
    }

    public string Owner { get; }
    public string Kind { get; }
    public bool IsSavings => Kind == "poupança";

    public static Account Create(AccountRecord record) => record.Kind switch
    {
        "S" => new Account(record.Owner, "poupança"),
        "C" => new Account(record.Owner, "corrente"),
        _ => new Account(record.Owner, "básica"),
    };
}
```

O comportamento não muda: `Kind` retorna os mesmos valores, e o código do cliente só mudou nos
dois primeiros passos, antes de qualquer subclasse desaparecer.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
