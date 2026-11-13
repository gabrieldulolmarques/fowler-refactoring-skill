# Compor Método (Compose Method)

Kerievsky (2004), cap. 7, p. 123. Padrão: Composed Method. Direção: até.

## Quando usar
Smells: Método Longo (Long Method).

- Você não consegue entender o que um método faz sem ler cada linha, porque chamadas de alto nível ficam ao lado de laços, condicionais e aritmética de índices.
- O objetivo é um método de cerca de cinco linhas (raramente mais de dez), feito de chamadas a métodos bem nomeados, todos no mesmo nível de detalhe. O nome diz o quê; o corpo diz como.
- Este é o mesmo trabalho de [extract-function.md](../../fowler/first-set/extract-function.md) e [slide-statements.md](../../fowler/moving-features/slide-statements.md), voltado a um único resultado. O livro não dá uma receita fixa, apenas diretrizes.
- Desvantagens: pode deixar muitos métodos privados minúsculos (um sinal para aplicar [extract-class.md](../../fowler/encapsulation/extract-class.md)), e o trabalho real fica mais difícil de achar no depurador. Desempenho não é motivo para parar, a menos que um profiler indique o contrário.

## Mecânica
Siga o procedimento de Extrair Função (Extract Function) em [extract-function.md](../../fowler/first-set/extract-function.md); não há um procedimento separado. O que Kerievsky acrescenta é como conduzi-lo:

1. Remova antes a duplicação e o código morto ([remove-dead-code.md](../../fowler/moving-features/remove-dead-code.md)), para haver menos o que ler.
2. Achate o aninhamento quando ele esconde o caminho principal: [replace-nested-conditional-with-guard-clauses.md](../../fowler/conditional-logic/replace-nested-conditional-with-guard-clauses.md) e [consolidate-conditional-expression.md](../../fowler/conditional-logic/consolidate-conditional-expression.md).
3. Encontre as linhas que estão em um nível de detalhe diferente dos vizinhos (uma condição crua, um laço, uma escrita em array no meio de chamadas). Empurre cada uma para baixo com [extract-function.md](../../fowler/first-set/extract-function.md), nomeada pela sua intenção.
4. Se não achar um bom nome para o que extraiu, você extraiu demais ou de menos. Desfaça com [inline-function.md](../../fowler/first-set/inline-function.md) e corte em outra linha.
5. Troque literais mágicos por constantes nomeadas ([replace-magic-literal.md](../../fowler/organizing-data/replace-magic-literal.md)).
6. Pare quando cada instrução do método disser o quê, e os detalhes estiverem a uma chamada de distância. Compile e teste após cada passo.

## Exemplo
Antes: o método de liquidação aninha duas verificações em volta de código de níveis misturados.

```csharp
using System;
using System.Collections.Generic;

public class Payment
{
    public int Id { get; }
    public decimal Amount { get; }
    public DateTime AuthorizationExpires { get; }

    public Payment(int id, decimal amount, DateTime authorizationExpires)
    {
        Id = id;
        Amount = amount;
        AuthorizationExpires = authorizationExpires;
    }
}

public class SettlementDesk
{
    private readonly List<Payment> _settled = new();
    private readonly List<string> _log = new();

    public bool Closed { get; set; }

    public void Settle(Payment payment)
    {
        if (!Closed)
        {
            if (payment.Amount > 0)
            {
                _settled.Add(payment);
                if (payment.AuthorizationExpires < DateTime.UtcNow.Date)
                    _log.Add($"payment {payment.Id} settled after authorization expired");
                else
                    _log.Add($"payment {payment.Id} settled");
            }
        }
    }
}
```

Depois: primeiro uma cláusula de guarda, depois dois passos no mesmo nível. A regra de expiração ganha um nome.

```csharp
using System;
using System.Collections.Generic;

public class SettlementDesk
{
    private readonly List<Payment> _settled = new();
    private readonly List<string> _log = new();

    public bool Closed { get; set; }

    public void Settle(Payment payment)
    {
        if (Closed || payment.Amount <= 0)
            return;
        Add(payment);
        LogSettlement(payment);
    }

    private void Add(Payment payment) => _settled.Add(payment);

    private void LogSettlement(Payment payment) =>
        _log.Add(IsExpired(payment)
            ? $"payment {payment.Id} settled after authorization expired"
            : $"payment {payment.Id} settled");

    private static bool IsExpired(Payment payment) =>
        payment.AuthorizationExpires < DateTime.UtcNow.Date;
}
```

## Notas (C#)
- Membros com corpo de expressão mantêm as partes extraídas curtas. Use uma função local quando a parte servir a um único método.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Leia o método de cima em voz alta: cada linha deve ser um passo que você nomearia em uma frase, sem operadores nem índices.
