# Consolidar Expressão Condicional (Consolidate Conditional Expression)

Fowler (2018), cap. 10, p. 263. Antes / também: —. Inversa: —.

## Quando usar
- Vários `if` seguidos, cada um com um teste diferente mas o mesmo resultado (mesmo valor de retorno, mesma ação).
- `if` aninhados sem `else`, em que só o mais interno faz algo.
- Você quer dar nome à regra combinada ("é elegível", "está bloqueado") extraindo-a depois ([extract-function.md](../first-set/extract-function.md)).

Não use quando as verificações forem responsabilidades independentes que apenas compartilham um resultado hoje. Fundi-las esconde que cada uma pode mudar por conta própria. Decomponha em vez disso, ou deixe-as separadas.

## Mecânica
1. Verifique que nenhuma das condições tem efeitos colaterais (sem escritas, sem chamadas que mudem estado ou consumam entrada). Se alguma tiver, separe antes a consulta do modificador ([separate-query-from-modifier.md](../refactoring-apis/separate-query-from-modifier.md)).
2. Escolha duas verificações adjacentes que compartilhem o resultado e una suas condições em um único `if`. Verificações consecutivas se unem com `||`; verificações aninhadas se unem com `&&`.
3. Compile e execute os testes.
4. Repita com a próxima verificação até restar uma única condição.
5. Considere extrair a condição combinada para uma função com um nome que revele a intenção ([extract-function.md](../first-set/extract-function.md)).

A ordem importa quando as condições podem lançar exceção ou são custosas: `||` e `&&` fazem curto-circuito como a sequência original fazia, então mantenha a ordem original da esquerda para a direita.

## Exemplo
Antes:

```csharp
public decimal RefundAmount(Order order)
{
    if (order.IsDigital) return 0m;
    if (order.DaysSinceDelivery > 30) return 0m;
    if (order.IsFinalSale) return 0m;

    return order.Total - order.RestockingFee;
}
```

Depois de fundir e depois extrair:

```csharp
public decimal RefundAmount(Order order)
{
    if (IsNotRefundable(order)) return 0m;

    return order.Total - order.RestockingFee;
}

private static bool IsNotRefundable(Order order) =>
    order.IsDigital
    || order.DaysSinceDelivery > 30
    || order.IsFinalSale;
```

Forma aninhada, fundida com `&&`:

```csharp
// antes
if (customer.IsActive)
    if (customer.Balance > 0m)
        SendReminder(customer);

// depois
if (customer.IsActive && customer.Balance > 0m)
    SendReminder(customer);
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
