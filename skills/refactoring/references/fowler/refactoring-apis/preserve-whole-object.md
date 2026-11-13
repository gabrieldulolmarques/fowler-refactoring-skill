# Preservar Objeto Inteiro (Preserve Whole Object)

Fowler (2018), cap. 11, p. 319. Antes / também: —. Inversa: —.

## Quando usar
Smells: Função Longa (Long Function), Lista Longa de Parâmetros (Long Parameter List), Agrupamentos de Dados (Data Clumps).

- Os chamadores leem dois ou mais valores de um objeto e os repassam. Passe o objeto no lugar.
- A assinatura deixa de mudar quando a função mais tarde precisa de outro campo desse objeto.
- Vários chamadores repetem a mesma lógica sobre as partes desempacotadas. Essa lógica muitas vezes pertence ao objeto inteiro (Inveja de Recursos (Feature Envy); veja [move-function.md](../moving-features/move-function.md)).
- Comum logo depois de Introduzir Objeto de Parâmetros (Introduce Parameter Object) ([introduce-parameter-object.md](../first-set/introduce-parameter-object.md)): procure os pontos de chamada restantes que ainda desempacotam os dados.
- Se vários chamadores só usam sempre o mesmo subconjunto dos membros do objeto, considere [extract-class.md](../encapsulation/extract-class.md).
- Um objeto que chama outro objeto com vários dos seus próprios valores pode passar `this`.

Não use quando a função chamada não deve depender do tipo do objeto inteiro, tipicamente porque elas vivem em módulos ou camadas diferentes. Então mantenha os parâmetros primitivos, ou passe um objeto menor.

## Mecânica
1. Declare um novo método vazio com a assinatura que você quer (o objeto inteiro como parâmetro). Dê a ele um nome temporário único e fácil de buscar.
2. Faça o seu corpo chamar o método antigo, mapeando do objeto inteiro para os parâmetros antigos.
3. Compile (verificações estáticas).
4. Mude os chamadores um por vez para usar o novo método, compilando e testando após cada um. Variáveis locais que só alimentavam os argumentos antigos podem ficar mortas; remova-as ([remove-dead-code.md](../moving-features/remove-dead-code.md)).
5. Quando não restar nenhum chamador do método antigo, internalize o método antigo no novo ([inline-function.md](../first-set/inline-function.md)).
6. Renomeie o novo método para o nome original e atualize os seus chamadores (o nome temporário único permite que uma busca de texto simples encontre todos os pontos de chamada a atualizar).

Variação: se você preferir construir o novo método a partir de outras refatorações, use [extract-variable.md](../first-set/extract-variable.md) na chamada e na expressão do objeto em um chamador, depois [extract-function.md](../first-set/extract-function.md) na chamada, e [move-function.md](../moving-features/move-function.md) se ele pertencer à classe da função chamada. Continue a partir do passo 4.

## Exemplo
Antes:

```csharp
using System;
using System.Collections.Generic;

public class TimeWindow
{
    public TimeWindow(TimeSpan start, TimeSpan end)
    {
        Start = start;
        End = end;
    }

    public TimeSpan Start { get; }
    public TimeSpan End { get; }
}

public class ScheduledNotification
{
    public ScheduledNotification(TimeWindow window)
    {
        Window = window;
    }

    public TimeWindow Window { get; }
}

public class QuietHoursPolicy
{
    private readonly TimeWindow _allowed = new(TimeSpan.FromHours(8), TimeSpan.FromHours(21));

    public bool Allows(TimeSpan start, TimeSpan end) =>
        start >= _allowed.Start && end <= _allowed.End;
}

public class NotificationAuditor
{
    public void Audit(ScheduledNotification notification, QuietHoursPolicy policy, List<string> findings)
    {
        var from = notification.Window.Start;
        var to = notification.Window.End;
        if (!policy.Allows(from, to))
            findings.Add("delivery window falls inside quiet hours");
    }
}
```

Intermediário (passos 1 e 2; o novo método delega ao antigo):

```csharp
// fragment
public bool xxNewAllows(TimeWindow window) => Allows(window.Start, window.End);
```

Depois (chamadores migrados, método antigo internalizado, nome temporário removido):

```csharp
public class QuietHoursPolicy
{
    private readonly TimeWindow _allowed = new(TimeSpan.FromHours(8), TimeSpan.FromHours(21));

    public bool Allows(TimeWindow window) =>
        window.Start >= _allowed.Start && window.End <= _allowed.End;
}

public class NotificationAuditor
{
    public void Audit(ScheduledNotification notification, QuietHoursPolicy policy, List<string> findings)
    {
        if (!policy.Allows(notification.Window))
            findings.Add("delivery window falls inside quiet hours");
    }
}
```

O comportamento é o mesmo; as variáveis locais `from` e `to` sumiram.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Depois do passo 5, uma busca pelo nome do método antigo não encontra nenhum chamador restante. Depois do passo 6, uma busca pelo prefixo temporário (`xx`) não encontra nada.
