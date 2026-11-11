# Substituir Flag de Controle por Break (Replace Control Flag with Break)

Fowler, catálogo online: https://refactoring.com/catalog/replaceControlFlagWithBreak.html. Antes / também: Remove Control Flag. Inversa: —.

## Quando usar
Uma variável booleana existe apenas para conduzir o laço: ela é definida quando algo acontece e depois
a condição do laço ou um `if` em torno do corpo a lê para pular o trabalho restante. O leitor
precisa acompanhar a flag ao longo das iterações para ver quando o laço realmente termina.

Smell: nenhum específico (apenas no catálogo web).

Substitua a flag por uma saída direta: `break` para sair do laço. Use `return` quando o laço
estiver no fim de uma função (muitas vezes depois de Extrair Função (Extract Function)). `continue` só serve quando a flag
protege o restante de uma única iteração e não as seguintes.
Não use quando a flag for lida depois do laço para um propósito real; então ela é um resultado,
não uma flag de controle, e talvez seja melhor mantida ou retornada por uma função extraída.

## Mecânica
O catálogo online dá apenas um exemplo antes/depois; estes passos são uma derivação genérica.
1. Encontre a flag: a variável que é definida dentro do laço e testada para decidir se continua trabalhando ou continua o laço. Verifique que nada depois do laço depende do seu valor.
2. Encontre o lugar onde a flag é definida com seu valor de "parar".
3. Verifique o que roda entre essa atribuição e o fim da iteração. Garanta que nada disso precise rodar depois que a flag for definida; será pulado após a saída. Verifique também as instruções depois do laço: nenhuma pode depender de o laço ter rodado até o fim.
4. Ponha um `break` ou `return` logo após a atribuição; ambos interrompem todas as iterações seguintes. Use `continue` apenas quando a flag era redefinida a cada iteração, de modo que protegia só o restante de uma iteração. Compile e teste.
5. Remova a flag da condição do laço ou do `if` que protegia o corpo. Compile e teste.
6. Remova a atribuição à flag e sua declaração. Compile e teste.

## Exemplo
Pressupõe que `Customer` e `IMailer` existam.

Antes:

```csharp
using System.Collections.Generic;

public void NotifyOverdue(IEnumerable<Customer> customers, IMailer mailer)
{
    bool notified = false;
    foreach (var customer in customers)
    {
        if (!notified)
        {
            if (customer.Balance < 0)
            {
                mailer.SendReminder(customer);
                notified = true;
            }
        }
    }
}
```

Depois:

```csharp
public void NotifyOverdue(IEnumerable<Customer> customers, IMailer mailer)
{
    foreach (var customer in customers)
    {
        if (customer.Balance < 0)
        {
            mailer.SendReminder(customer);
            break;
        }
    }
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda: o laço ainda para no mesmo elemento e nada depois do ponto de saída costumava rodar.
