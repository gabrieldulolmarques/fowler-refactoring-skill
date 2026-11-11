# Substituir Consulta por Parâmetro (Replace Query with Parameter)

Fowler (2018), cap. 11, p. 327. Antes / também: —. Inversa: Substituir Parâmetro por Consulta
([replace-parameter-with-query.md](replace-parameter-with-query.md)).

## Quando usar
- Uma função lê algo de fora do seu próprio escopo (um global, um singleton, um membro estático, um
  elemento de um módulo que você planeja afastar) e você quer que a função deixe de depender disso.
- A função é difícil de testar ou de raciocinar sobre porque o seu resultado muda com estado oculto. Mover
  a busca para um parâmetro faz com que ela retorne o mesmo resultado para os mesmos argumentos (transparência
  referencial), de modo que a lógica pode ficar em um núcleo puro envolvido por código que trata de E/S e estado
  compartilhado.
- Contrapartida: o chamador agora precisa encontrar e passar o valor, então os pontos de chamada ficam mais pesados e
  as listas de parâmetros mais longas. Se muitos chamadores repetem a mesma busca, ou a dependência é inofensiva,
  mantenha a consulta dentro (a refatoração inversa). Decida por onde a responsabilidade pertence; a
  escolha é reversível.

## Mecânica
1. Aplique Extrair Variável (Extract Variable) ([extract-variable.md](../first-set/extract-variable.md)) à expressão da consulta, para que ela fique em uma
   variável local separada do resto do corpo. Compile e teste.
2. Aplique Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) a tudo, exceto a linha que realiza
   a consulta. A nova função recebe a variável como parâmetro. Dê a ela um nome temporário e fácil de
   buscar. Compile e teste.
3. Aplique Internalizar Variável (Inline Variable) ([inline-variable.md](../first-set/inline-variable.md)) à variável do passo 1, para que a função
   original apenas chame a nova com a expressão da consulta como argumento. Compile e teste.
4. Aplique Internalizar Função (Inline Function) ([inline-function.md](../first-set/inline-function.md)) à função original, para que todo chamador agora
   chame a nova função e passe a própria consulta. Compile e teste.
5. Renomeie a nova função para o nome original, usando o nome temporário pesquisável para encontrar
   todo uso. Compile e teste.

## Exemplo
Antes: o método lê um relógio estático.

```csharp
public class Invoice
{
    private readonly decimal _amount;
    private readonly DateTime _dueDate;
    private readonly decimal _dailyPenaltyRate;

    public Invoice(decimal amount, DateTime dueDate, decimal dailyPenaltyRate)
    {
        _amount = amount;
        _dueDate = dueDate;
        _dailyPenaltyRate = dailyPenaltyRate;
    }

    public decimal Penalty()
    {
        var daysLate = (DateTime.Today - _dueDate).Days;
        return daysLate > 0 ? _amount * _dailyPenaltyRate * daysLate : 0m;
    }
}

// chamador
var penalty = invoice.Penalty();
```

Depois: o chamador fornece a data, e `Penalty` depende apenas dos seus argumentos e dos
campos imutáveis.

```csharp
public class Invoice
{
    private readonly decimal _amount;
    private readonly DateTime _dueDate;
    private readonly decimal _dailyPenaltyRate;

    public Invoice(decimal amount, DateTime dueDate, decimal dailyPenaltyRate)
    {
        _amount = amount;
        _dueDate = dueDate;
        _dailyPenaltyRate = dailyPenaltyRate;
    }

    public decimal Penalty(DateTime today)
    {
        var daysLate = (today - _dueDate).Days;
        return daysLate > 0 ? _amount * _dailyPenaltyRate * daysLate : 0m;
    }
}

// chamador
var penalty = invoice.Penalty(DateTime.Today);
```

Um teste agora pode passar qualquer data e obter um resultado repetível.

## Notas de C#
- Útil para remover uma dependência de um estático ou singleton (`DateTime.Today`, uma classe estática de
  configuração, um service locator) e tornar o código testável.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Todo chamador passa o valor que a antiga consulta interna retornava, então o comportamento não muda.
