# Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State)

Kerievsky (2004), cap. 7, p. 166. Padrão: State. Direção: até, rumo a.

## Quando usar
Smells: Complexidade Condicional (Conditional Complexity), Classe Grande (Large Class), Obsessão por Primitivos (Primitive Obsession).

- Um objeto tem um campo de status (um enum, constantes, strings) e seus métodos verificam esse campo para decidir o que é permitido e qual é o próximo status. As mesmas verificações se repetem em todo método que move o objeto entre estados, e as transições ficam espalhadas pela classe.
- Cada estado vira uma classe que sabe quais transições permite e para onde elas levam. O objeto (o contexto) repassa as chamadas dependentes de estado ao seu objeto de estado atual e troca de estado apontando para outro. As classes de estado juntas formam um mapa legível de toda a máquina.
- Kerievsky distingue isto do Substituir Código de Tipo por State/Strategy (Replace Type Code with State/Strategy) de Fowler de dois modos: State serve a uma classe que transita entre membros de uma família de classes de estado, enquanto Strategy deixa uma classe entregar um algoritmo a um membro de uma família de classes strategy (veja [replace-conditional-logic-with-strategy.md](replace-conditional-logic-with-strategy.md)); e ele documenta o caminho completo dos condicionais até State, que Fowler deixa para Substituir Condicional por Polimorfismo.
- Se a lógica de transição ainda é fácil de seguir, não faça. Tente antes [extract-function.md](../../fowler/first-set/extract-function.md). Se você ainda consegue seguir a lógica de transição com facilidade, deixe como está, a menos que muitas outras transições estejam planejadas. Faça quando a lógica for difícil de seguir ou difícil de estender.
- Desvantagem: mais classes, e as regras de uma transição agora ficam na classe de estado que a inicia, não no contexto.

## Mecânica
O contexto é a classe que possui o campo de status (o campo de estado original). Ele é atribuído ou comparado com um conjunto de constantes conforme as transições acontecem.

1. Aplique Substituir Código de Tipo por Classe (Replace Type Code with Class) ([replace-type-code-with-class.md](../protection/replace-type-code-with-class.md)) ao campo de status, para que o tipo dele seja uma nova classe: a superclasse de estado. Chamadores e todo `switch` sobre o tipo antigo agora comparam com as constantes da classe. Compile.
2. Cada constante agora é uma instância da superclasse de estado. Crie uma subclasse por constante com Extrair Subclasse (Extract Subclass) (a parte de criação de subclasses de [replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md); pare depois que as subclasses existirem, sem seguir com a remoção de campo nem o empurrar de métodos dessa refatoração), e faça cada constante referenciar a instância da sua subclasse. Declare a superclasse de estado como `abstract`. Compile.
3. Pegue um método do contexto que muda o status de acordo com as regras de transição. Copie-o para a superclasse de estado com as menores mudanças que o façam funcionar (normalmente adicionando o contexto como parâmetro e chamando seus membros por ele). Substitua o corpo do método do contexto por uma chamada à cópia. Compile e teste. Repita para cada método que altera o status.
4. Pegue um estado. Encontre quais dos métodos copiados na superclasse fazem uma transição a partir desse estado. Copie cada um para a subclasse daquele estado (como sobrescrita) e apague da cópia tudo que não tem relação: a verificação do estado atual e os ramos que pertencem a outros estados. Compile e teste. Repita para cada estado.
5. Substitua o corpo de cada método copiado no passo 3 pelo comportamento padrão: normalmente rejeitar a chamada ou não fazer nada. Compile e teste.

**Além do livro:** se outros métodos ramificam pelo status sem alterá-lo, mova-os também, com [replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md): um membro virtual no estado com a resposta comum, sobrescrito pelos estados que diferem. Além disso, a ideia de que um tipo fixo durante a vida do objeto precisa apenas de subclasses do próprio objeto é uma nota desta skill, não o contraste do livro.

Dados que pertencem ao objeto (quem está atribuído, quantas vezes foi reaberto) ficam no contexto. Os estados leem e escrevem esses dados pelo contexto que recebem.

## Exemplo
O domínio é um pagamento instantâneo com quatro estados e estas transições. Qualquer coisa que não esteja na tabela é rejeitada com uma `InvalidOperationException`.

| De | Chamada | Para |
|---|---|---|
| Created | Authorize (no máximo 3 tentativas) | Authorized |
| Authorized | Release | Created |
| Authorized | Settle | Settled |
| Settled | Refund | Refunded |
| Refunded | (nenhuma) | |

A conciliação só é permitida em Settled e Refunded.

Antes: todo método repete uma verificação de status e define o próximo status.

```csharp
using System;

public enum PaymentStatus { Created, Authorized, Settled, Refunded }

public class Payment
{
    private PaymentStatus _status = PaymentStatus.Created;

    public string? AuthCode { get; private set; }
    public int AuthAttempts { get; private set; }
    public string StatusName => _status.ToString();
    public bool AllowsReconciliation => _status == PaymentStatus.Settled || _status == PaymentStatus.Refunded;

    public void Authorize(string code)
    {
        if (_status != PaymentStatus.Created)
            throw new InvalidOperationException($"cannot authorize a payment that is {_status}");
        if (AuthAttempts >= 3)
            throw new InvalidOperationException("authorization attempt limit reached");
        AuthAttempts++;
        AuthCode = code;
        _status = PaymentStatus.Authorized;
    }

    public void Release()
    {
        if (_status != PaymentStatus.Authorized)
            throw new InvalidOperationException($"cannot release a payment that is {_status}");
        AuthCode = null;
        _status = PaymentStatus.Created;
    }

    public void Settle()
    {
        if (_status != PaymentStatus.Authorized)
            throw new InvalidOperationException($"cannot settle a payment that is {_status}");
        _status = PaymentStatus.Settled;
    }

    public void Refund()
    {
        if (_status != PaymentStatus.Settled)
            throw new InvalidOperationException($"cannot refund a payment that is {_status}");
        _status = PaymentStatus.Refunded;
    }
}
```

Depois dos passos 1 e 2, o enum vira uma classe com quatro constantes, cada uma uma instância de uma subclasse aninhada e privada de uma `PaymentState` abstrata. O contexto guarda uma propriedade `State` (agora com setter interno) no lugar de `_status`. Nada mais mudou ainda.

No passo 3, `Authorize` é copiado para a superclasse de estado com o contexto como parâmetro, e o método do contexto apenas delega:

```csharp
// fragment
// em PaymentState
internal virtual void Authorize(Payment payment, string code)
{
    if (payment.State != Created)
        throw new InvalidOperationException($"cannot authorize a payment that is {Name}");
    if (payment.AuthAttempts >= 3)
        throw new InvalidOperationException("authorization attempt limit reached");
    payment.AuthAttempts++;
    payment.AuthCode = code;
    payment.State = Authorized;
}

// em Payment
public void Authorize(string code) => State.Authorize(this, code);
```

No passo 4, `CreatedState` fica com o único ramo que se aplica a ele. A verificação do estado atual e os ramos dos outros estados saem da sobrescrita:

```csharp
// fragment
// em CreatedState
internal override void Authorize(Payment payment, string code)
{
    if (payment.AuthAttempts >= 3)
        throw new InvalidOperationException("authorization attempt limit reached");
    payment.AuthAttempts++;
    payment.AuthCode = code;
    payment.State = Authorized;
}
```

No passo 5, o `Authorize` da base encolhe para o comportamento padrão, `throw NotAllowed("authorize")`. Fazer isso para todos os métodos gera o código final. Cada estado lista exatamente as transições que permite, e um estado que não sobrescreve um método o rejeita.

```csharp
using System;

public class Payment
{
    public PaymentState State { get; internal set; } = PaymentState.Created;
    public string? AuthCode { get; internal set; }
    public int AuthAttempts { get; internal set; }
    public string StatusName => State.Name;
    public bool AllowsReconciliation => State.AllowsReconciliation;

    public void Authorize(string code) => State.Authorize(this, code);
    public void Release() => State.Release(this);
    public void Settle() => State.Settle(this);
    public void Refund() => State.Refund(this);
}

public abstract class PaymentState
{
    public static readonly PaymentState Created = new CreatedState();
    public static readonly PaymentState Authorized = new AuthorizedState();
    public static readonly PaymentState Settled = new SettledState();
    public static readonly PaymentState Refunded = new RefundedState();

    public abstract string Name { get; }
    public virtual bool AllowsReconciliation => false;

    internal virtual void Authorize(Payment payment, string code) => throw NotAllowed("authorize");
    internal virtual void Release(Payment payment) => throw NotAllowed("release");
    internal virtual void Settle(Payment payment) => throw NotAllowed("settle");
    internal virtual void Refund(Payment payment) => throw NotAllowed("refund");

    private InvalidOperationException NotAllowed(string action) =>
        new($"cannot {action} a payment that is {Name}");

    private sealed class CreatedState : PaymentState
    {
        public override string Name => "Created";

        internal override void Authorize(Payment payment, string code)
        {
            if (payment.AuthAttempts >= 3)
                throw new InvalidOperationException("authorization attempt limit reached");
            payment.AuthAttempts++;
            payment.AuthCode = code;
            payment.State = Authorized;
        }
    }

    private sealed class AuthorizedState : PaymentState
    {
        public override string Name => "Authorized";

        internal override void Release(Payment payment)
        {
            payment.AuthCode = null;
            payment.State = Created;
        }

        internal override void Settle(Payment payment) => payment.State = Settled;
    }

    private sealed class SettledState : PaymentState
    {
        public override string Name => "Settled";
        public override bool AllowsReconciliation => true;

        internal override void Refund(Payment payment) => payment.State = Refunded;
    }

    private sealed class RefundedState : PaymentState
    {
        public override string Name => "Refunded";
        public override bool AllowsReconciliation => true;
    }
}
```

Adicionar um estado (digamos, `Disputed`) agora significa uma classe aninhada nova e as transições que levam a ele. Os métodos existentes em `Payment` não mudam.

## Notas (C#)
- Os objetos de estado não guardam dados por pagamento, então as quatro instâncias `static readonly` são compartilhadas por todos os pagamentos. Mantenha assim: se um estado precisar de dados próprios, crie uma instância por contexto em vez de uma constante compartilhada.
- Subclasses aninhadas `private sealed` mantêm as constantes como a única forma de obter um estado. Membros `internal` permitem que os estados alterem o contexto sem expor setters publicamente. Se os estados morarem em outro assembly, use uma pequena interface pública no contexto.
- Se o status for persistido, mantenha um código estável (o `Name`, ou o valor antigo do enum) e converta-o de volta para a constante ao carregar o objeto.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Escreva a tabela de transições como um teste antes do passo 1, cobrindo cada movimento permitido e pelo menos uma chamada rejeitada por estado (incluindo o limite de tentativas), e mantenha-o passando nos cinco passos.
- Depois do passo 4, faça temporariamente os métodos da base lançarem exceção (antecipando o passo 5) em uma branch: qualquer teste que falhar mostra um estado ao qual você esqueceu de sobrescrever.
- Confira que nenhum código fora do contexto e dos estados lê `State` para se ramificar. Isso recriaria o condicional em outro lugar.
