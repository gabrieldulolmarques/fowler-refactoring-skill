# Ocultar Delegação (Hide Delegate)

Fowler (2018), cap. 7, p. 189. Nome anterior / outro nome: —. Inversa: Remover Intermediário (Remove Middle Man)
([remove-middle-man.md](remove-middle-man.md)).

## Quando usar
Smells: Cadeias de Mensagens (Message Chains), Troca de Informações Privilegiadas (Insider Trading).

- O código cliente alcança, através de um servidor, um objeto que ele guarda (`order.Customer.Region.Manager`),
  então o cliente conhece como o servidor é construído e qual objeto é dono dos dados.
- Se a interface do delegado mudar, todo cliente do servidor que toca o delegado
  também precisa mudar. Um método de encaminhamento no servidor confina essa mudança a um só lugar.
- Não continue adicionando encaminhadores para todo membro do delegado por hábito. Quando o servidor
  vira uma lista de métodos de repasse, ocultar custa mais do que rende: veja Remover
  Intermediário. Até onde ocultar é uma decisão que você pode revisar depois.

## Mecânica
1. Para cada membro do delegado que um cliente usa, adicione um método de encaminhamento simples no servidor.
2. Compile e teste.
3. Altere um cliente de cada vez para chamar o servidor em vez de passar pelo delegado.
   Compile e teste após cada cliente.
4. Quando o último cliente parar de passar pelo servidor até o delegado, remova o
   getter público que o expõe (apague-o ou reduza sua visibilidade).
5. Compile e teste.

## Exemplo

Antes: o cliente navega pela assinatura até o preço mensal do plano.

```csharp
public class Plan
{
    public decimal MonthlyPrice { get; set; }
}

public class Subscription
{
    public Plan Plan { get; set; } = null!;
}

public static class Client
{
    public static decimal Price(Subscription subscription)
    {
        decimal price = subscription.Plan.MonthlyPrice;
        return price;
    }
}
```

Depois: `Subscription` oculta `Plan`.

```csharp
public class Subscription
{
    private Plan _plan = null!;

    public Plan Plan { get => _plan; set => _plan = value; } // removido no passo 4
    public decimal MonthlyPrice => _plan.MonthlyPrice;
}

public static class Client
{
    public static decimal Price(Subscription subscription)
    {
        decimal price = subscription.MonthlyPrice;
        return price;
    }
}
```

Quando todos os clientes usarem `MonthlyPrice`, apague o acessor público `Plan` (ou torne-o
privado), para que a delegação não possa mais ser alcançada de fora.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum cliente ainda referencia o tipo delegado através do servidor.
