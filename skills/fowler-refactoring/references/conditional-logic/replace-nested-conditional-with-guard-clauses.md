# Substituir Condicional Aninhada por Cláusulas de Guarda (Replace Nested Conditional with Guard Clauses)

Fowler (2018), cap. 10, p. 266. Antes / também: —. Inversa: —.

## Quando usar
- Uma condicional tem um ramo que é o comportamento normal e outros ramos que são casos incomuns
  ou terminais (entrada inválida, dados ausentes, "nada a fazer").
- O aninhamento empurra o trabalho real para a direita, e o leitor precisa manter todas as condições
  envolventes em mente para entendê-lo.
- Uma variável `result` é atribuída em vários ramos apenas para ser retornada no final.

Uma cláusula de guarda marca um caso como um caminho lateral: trate-o e saia. Um if/else apresenta dois
caminhos como igualmente comuns. Escolha o formato que corresponde ao que o código significa.

Não use quando os dois ramos são comportamento normal: mantenha um if/else simples. Saída única é uma
preferência de estilo, então decida pela legibilidade.

## Mecânica
1. Escolha a condição mais externa que protege um caso incomum e reescreva-a como uma cláusula de
   guarda: teste o caso incomum e retorne seu resultado imediatamente. Se a condição protege
   o caso normal, inverta-a primeiro (aplique De Morgan se necessário e simplifique qualquer
   `!` que sobrar) para que o caso incomum se torne o retorno antecipado.
2. Compile e execute os testes.
3. Repita para a próxima condição, avançando para dentro, uma guarda de cada vez.
4. Quando as guardas não precisarem mais da variável de resultado, remova-a e retorne os valores
   diretamente.
5. Se várias guardas retornarem o mesmo valor, una-as com
   Consolidar Expressão Condicional (Consolidate Conditional Expression) ([consolidate-conditional-expression.md](consolidate-conditional-expression.md)).

## Exemplo
Antes: a taxa só é calculada quando o pedido não está cancelado nem vazio.

```csharp
public decimal ShippingFee(Order order)
{
    decimal result;
    if (order.IsCancelled)
    {
        result = 0m;
    }
    else
    {
        if (order.Items.Count == 0)
        {
            result = 0m;
        }
        else
        {
            if (order.Total >= 100m)
            {
                result = 0m;
            }
            else
            {
                result = 7.5m + order.Items.Count * 0.5m;
            }
        }
    }
    return result;
}
```

Depois da primeira guarda (um passo, testes executados):

```csharp
public decimal ShippingFee(Order order)
{
    decimal result;
    if (order.IsCancelled) return 0m;
    if (order.Items.Count == 0)
    {
        result = 0m;
    }
    else
    {
        if (order.Total >= 100m) result = 0m;
        else result = 7.5m + order.Items.Count * 0.5m;
    }
    return result;
}
```

Final, sem a variável e com os resultados iguais consolidados:

```csharp
public decimal ShippingFee(Order order)
{
    if (order.IsCancelled || order.Items.Count == 0 || order.Total >= 100m) return 0m;
    return 7.5m + order.Items.Count * 0.5m;
}
```

Invertendo uma condição: quando um teste com `||` protege o caminho normal, inverta-o (De Morgan
transforma o `||` em `&&`).

```csharp
// antes
public decimal AmountDue(Invoice invoice)
{
    if (invoice.IsOpen || invoice.IsOverdue)
    {
        if (invoice.Customer != null)
            return invoice.Amount - invoice.Paid;
    }
    return 0m;
}

// depois
public decimal AmountDue(Invoice invoice)
{
    if (!invoice.IsOpen && !invoice.IsOverdue) return 0m;
    if (invoice.Customer == null) return 0m;
    return invoice.Amount - invoice.Paid;
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Cada guarda mantém o valor de retorno original para o seu caso, e a ordem das guardas
  corresponde à ordem original de avaliação (uma guarda que chama algo com efeitos colaterais
  não deve passar para antes de outra).
