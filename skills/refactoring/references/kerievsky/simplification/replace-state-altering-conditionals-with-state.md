# Substituir Condicionais que Alteram Estado por State (Replace State-Altering Conditionals with State)

Kerievsky (2004), cap. 7, p. 166. Padrão: State. Direção: até, rumo a.

## Quando usar
Smells: Complexidade Condicional (Conditional Complexity), Classe Grande (Large Class), Obsessão por Primitivos (Primitive Obsession).

- Um objeto tem um campo de status (um enum, constantes, strings) e seus métodos verificam esse campo para decidir o que é permitido e qual é o próximo status. As mesmas verificações se repetem em todo método que move o objeto entre estados, e as transições ficam espalhadas pela classe.
- Cada estado vira uma classe que sabe quais transições permite e para onde elas levam. O objeto (o contexto) repassa as chamadas dependentes de estado ao seu objeto de estado atual e troca de estado apontando para outro. As classes de estado juntas formam um mapa legível de toda a máquina.
- Isto não é Substituir Código de Tipo por Subclasses (Replace Type Code with Subclasses). Ali o tipo é fixo durante a vida do objeto, então subclasses do próprio objeto bastam. Aqui o objeto muda de estado enquanto vive, então a variação precisa morar em um objeto separado que ele possa trocar. Também não é [replace-conditional-logic-with-strategy.md](replace-conditional-logic-with-strategy.md): uma Strategy é escolhida de fora para executar um algoritmo, enquanto os estados escolhem o próprio sucessor.
- Se a lógica de transição ainda é fácil de seguir, não faça. Tente antes [extract-function.md](../../fowler/first-set/extract-function.md). Dois ou três estados com algumas transições costumam ficar melhor como um campo e alguns `if`s. Faça quando a lógica for difícil de seguir, ou quando muitas outras transições estiverem a caminho.
- Desvantagem: mais classes, e as regras de uma transição agora ficam na classe de estado que a inicia, não no contexto.

## Mecânica
O contexto é a classe que possui o campo de status (o campo de estado original). Ele é atribuído ou comparado com um conjunto de constantes conforme as transições acontecem.

1. Aplique Substituir Código de Tipo por Classe (Replace Type Code with Class) ([replace-type-code-with-class.md](../protection/replace-type-code-with-class.md)) ao campo de status, para que o tipo dele seja uma nova classe: a superclasse de estado. Chamadores e todo `switch` sobre o tipo antigo agora comparam com as constantes da classe. Compile.
2. Cada constante agora é uma instância da superclasse de estado. Crie uma subclasse por constante (Substituir Código de Tipo por Subclasses, [replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md), cujo segundo passo é o que o livro chama de Extrair Subclasse (Extract Subclass)), e faça cada constante referenciar a instância da sua subclasse. Declare a superclasse de estado como `abstract`. Compile.
3. Pegue um método do contexto que muda o status de acordo com as regras de transição. Copie-o para a superclasse de estado com as menores mudanças que o façam funcionar (normalmente adicionando o contexto como parâmetro e chamando seus membros por ele). Substitua o corpo do método do contexto por uma chamada à cópia. Compile e teste. Repita para cada método que altera o status.
4. Pegue um estado. Encontre quais dos métodos copiados na superclasse fazem uma transição a partir desse estado. Copie cada um para a subclasse daquele estado (como override) e apague da cópia tudo que não tem relação: a verificação do estado atual e os ramos que pertencem a outros estados. Compile e teste. Repita para cada estado.
5. Substitua o corpo de cada método copiado no passo 3 pelo comportamento padrão: normalmente rejeitar a chamada ou não fazer nada. Compile e teste.
6. Se outros métodos ramificam pelo status (não só os que o alteram), mova-os também, com [replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md): um membro virtual no estado com a resposta comum, sobrescrito pelos estados que diferem.

Dados que pertencem ao objeto (quem está atribuído, quantas vezes foi reaberto) ficam no contexto. Os estados leem e escrevem esses dados pelo contexto que recebem.

## Exemplo
O domínio é um chamado de suporte com quatro estados e estas transições. Qualquer coisa fora da tabela é rejeitada com uma `InvalidOperationException`.

| De | Chamada | Para |
|---|---|---|
| Open | Assign | Assigned |
| Open | Close | Closed |
| Assigned | Unassign | Open |
| Assigned | Resolve | Resolved |
| Resolved | Reopen (no máximo duas vezes) | Assigned |
| Resolved | Close | Closed |
| Closed | (nenhuma) | |

Comentários são aceitos em todo estado, exceto Closed.

Antes: todo método repete uma verificação de status e define o próximo status.

```csharp
using System;

public enum TicketStatus { Open, Assigned, Resolved, Closed }

public class Ticket
{
    private TicketStatus _status = TicketStatus.Open;

    public string? Assignee { get; private set; }
    public int ReopenCount { get; private set; }
    public string StatusName => _status.ToString();
    public bool AcceptsComments => _status != TicketStatus.Closed;

    public void Assign(string agent)
    {
        if (_status != TicketStatus.Open)
            throw new InvalidOperationException($"cannot assign a ticket that is {_status}");
        Assignee = agent;
        _status = TicketStatus.Assigned;
    }

    public void Unassign()
    {
        if (_status != TicketStatus.Assigned)
            throw new InvalidOperationException($"cannot unassign a ticket that is {_status}");
        Assignee = null;
        _status = TicketStatus.Open;
    }

    public void Resolve()
    {
        if (_status != TicketStatus.Assigned)
            throw new InvalidOperationException($"cannot resolve a ticket that is {_status}");
        _status = TicketStatus.Resolved;
    }

    public void Reopen()
    {
        if (_status != TicketStatus.Resolved)
            throw new InvalidOperationException($"cannot reopen a ticket that is {_status}");
        if (ReopenCount >= 2)
            throw new InvalidOperationException("reopen limit reached");
        ReopenCount++;
        _status = TicketStatus.Assigned;
    }

    public void Close()
    {
        if (_status != TicketStatus.Open && _status != TicketStatus.Resolved)
            throw new InvalidOperationException($"cannot close a ticket that is {_status}");
        _status = TicketStatus.Closed;
    }
}
```

Depois dos passos 1 e 2, o enum é uma classe com quatro constantes, cada uma instância de uma subclasse aninhada privada de um `TicketState` abstrato. O contexto mantém uma propriedade `State` (agora com setter interno) no lugar de `_status`. Nada mais mudou ainda.

No passo 3, `Assign` é copiado para a superclasse de estado com o contexto como parâmetro, e o método do contexto apenas delega:

```csharp
// em TicketState
internal virtual void Assign(Ticket ticket, string agent)
{
    if (ticket.State != Open)
        throw new InvalidOperationException($"cannot assign a ticket that is {Name}");
    ticket.Assignee = agent;
    ticket.State = Assigned;
}

// em Ticket
public void Assign(string agent) => State.Assign(this, agent);
```

No passo 4, `OpenState` recebe apenas o ramo que se aplica a ele. A verificação e os ramos dos outros estados saem do override:

```csharp
// em OpenState
internal override void Assign(Ticket ticket, string agent)
{
    ticket.Assignee = agent;
    ticket.State = Assigned;
}
```

No passo 5, o `Assign` base encolhe para o padrão, `throw NotAllowed("assign")`. Fazendo isso para todos os métodos, chega-se ao código final. Cada estado lista exatamente as transições que permite, e um estado que não sobrescreve um método o rejeita.

```csharp
using System;

public class Ticket
{
    public TicketState State { get; internal set; } = TicketState.Open;
    public string? Assignee { get; internal set; }
    public int ReopenCount { get; internal set; }
    public string StatusName => State.Name;
    public bool AcceptsComments => State.AcceptsComments;

    public void Assign(string agent) => State.Assign(this, agent);
    public void Unassign() => State.Unassign(this);
    public void Resolve() => State.Resolve(this);
    public void Reopen() => State.Reopen(this);
    public void Close() => State.Close(this);
}

public abstract class TicketState
{
    public static readonly TicketState Open = new OpenState();
    public static readonly TicketState Assigned = new AssignedState();
    public static readonly TicketState Resolved = new ResolvedState();
    public static readonly TicketState Closed = new ClosedState();

    public abstract string Name { get; }
    public virtual bool AcceptsComments => true;

    internal virtual void Assign(Ticket ticket, string agent) => throw NotAllowed("assign");
    internal virtual void Unassign(Ticket ticket) => throw NotAllowed("unassign");
    internal virtual void Resolve(Ticket ticket) => throw NotAllowed("resolve");
    internal virtual void Reopen(Ticket ticket) => throw NotAllowed("reopen");
    internal virtual void Close(Ticket ticket) => throw NotAllowed("close");

    private InvalidOperationException NotAllowed(string action) =>
        new($"cannot {action} a ticket that is {Name}");

    private sealed class OpenState : TicketState
    {
        public override string Name => "Open";

        internal override void Assign(Ticket ticket, string agent)
        {
            ticket.Assignee = agent;
            ticket.State = Assigned;
        }

        internal override void Close(Ticket ticket) => ticket.State = Closed;
    }

    private sealed class AssignedState : TicketState
    {
        public override string Name => "Assigned";

        internal override void Unassign(Ticket ticket)
        {
            ticket.Assignee = null;
            ticket.State = Open;
        }

        internal override void Resolve(Ticket ticket) => ticket.State = Resolved;
    }

    private sealed class ResolvedState : TicketState
    {
        public override string Name => "Resolved";

        internal override void Reopen(Ticket ticket)
        {
            if (ticket.ReopenCount >= 2)
                throw new InvalidOperationException("reopen limit reached");
            ticket.ReopenCount++;
            ticket.State = Assigned;
        }

        internal override void Close(Ticket ticket) => ticket.State = Closed;
    }

    private sealed class ClosedState : TicketState
    {
        public override string Name => "Closed";
        public override bool AcceptsComments => false;
    }
}
```

Acrescentar um estado (digamos, `Escalated`) agora significa uma nova classe aninhada e as transições que levam a ele. Os métodos existentes em `Ticket` não mudam.

## Notas (C#)
- Os objetos de estado não guardam dados por ticket, então as quatro instâncias `static readonly` são compartilhadas por todos os tickets. Mantenha assim: se um estado precisar de dados próprios, crie uma instância por contexto em vez de uma constante compartilhada.
- Subclasses aninhadas `private sealed` mantêm as constantes como única forma de obter um estado. Membros `internal` permitem que os estados alterem o contexto sem expor setters publicamente. Se os estados morarem em outro assembly, use uma pequena interface pública no contexto.
- Se o status for persistido, mantenha um código estável (o `Name`, ou o valor antigo do enum) e mapeie-o de volta para a constante ao carregar o objeto.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Escreva a tabela de transições como teste antes do passo 1, cobrindo cada movimento permitido e pelo menos uma chamada rejeitada por estado (incluindo o limite de reabertura), e mantenha-a passando pelos cinco passos.
- Após o passo 4, faça temporariamente os métodos base lançarem exceção (o passo 5 antecipado) em uma branch: qualquer teste que falhar aponta um estado para o qual você esqueceu um override.
- Confirme que nenhum código fora do contexto e dos estados lê `State` para ramificar. Isso recriaria o condicional em outro lugar.
