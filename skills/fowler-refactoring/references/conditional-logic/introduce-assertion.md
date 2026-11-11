# Introduzir Asserção (Introduce Assertion)

Fowler (2018), cap. 10, p. 302. Antes / também: —. Inversa: —.

## Quando usar
Smell: Comentários (Comments). Um comentário que diz "isto deve ser positivo" ou "x nunca é nulo aqui" é
uma suposição escrita só para humanos. Uma asserção afirma a mesma coisa em código, de modo que
o leitor a vê e o runtime pode verificá-la.

Uma asserção marca um erro de programador: uma condição que deve valer se o resto do
sistema estiver correto. Reserve as asserções para invariantes das quais o design depende. Pule as
meramente plausíveis, porque cada asserção é mais uma condição a manter.

Entradas de fora do programa (arquivos, rede, usuários, outros sistemas) podem legitimamente estar
erradas, então precisam de validação e tratamento de erros de verdade, não de uma asserção. Uma falha de asserção
significa um bug. Nada deve tratá-la como um resultado normal.

## Mecânica
1. Encontre uma condição que o código assume ser verdadeira neste ponto.
2. Quando necessário: se o formato do código não permitir uma instrução ali (por exemplo, uma expressão
   ternária), reformule-o antes em instruções `if` simples. Teste.
3. Adicione a asserção nesse ponto. O comportamento não muda desde que a asserção não tenha
   efeitos colaterais e que o programa funcione do mesmo jeito com todas as asserções removidas. Ela só
   é avaliada em builds Debug, então teste em Debug. Teste.
4. Quando necessário: pergunte onde o valor ruim entraria primeiro. Muitas vezes o melhor lugar é o setter,
   construtor ou fábrica que o produz, de modo que uma falha aponte para a origem e não para
   o código que o usa depois. Mova ou adicione a asserção ali. Teste.
5. Quando necessário: se a mesma condição aparecer em várias asserções, extraia-a para uma função nomeada
   ([extract-function.md](../first-set/extract-function.md)) para que seja alterada em um só lugar.
6. Remova o comentário que a asserção substitui.

## Exemplo
Antes:

```csharp
public class Customer
{
    public string? Email { get; }
    public string? Phone { get; }

    public Customer(string? email, string? phone)
    {
        Email = email;
        Phone = phone;
    }

    public string PreferredContact()
    {
        // email e telefone nunca são ambos vazios
        return string.IsNullOrEmpty(Email) ? Phone! : Email;
    }
}
```

Depois (a verificação vive no construtor, onde um par ruim entraria primeiro):

```csharp
using System.Diagnostics;

public class Customer
{
    public string? Email { get; }
    public string? Phone { get; }

    public Customer(string? email, string? phone)
    {
        Debug.Assert(
            !string.IsNullOrEmpty(email) || !string.IsNullOrEmpty(phone),
            "o cliente precisa de um e-mail ou de um telefone");
        Email = email;
        Phone = phone;
    }

    public string PreferredContact()
    {
        return string.IsNullOrEmpty(Email) ? Phone! : Email;
    }
}
```

## Notas de C#
- `Debug.Assert` (`System.Diagnostics`) é removido dos builds Release, o que combina com a regra
  de que o programa deve se comportar do mesmo jeito sem asserções. Não ponha efeitos colaterais na
  expressão asserida.
- `Debug.Assert` não altera a análise de fluxo de nulos, então o `!` em `PreferredContact`
  permanece e ainda esconde um possível nulo quando `Email` está vazio. A asserção documenta a
  invariante; ela não a prova ao compilador.
- Se uma verificação também precisar rodar em produção, ela não é uma asserção: use validação de verdade
  (por exemplo, lançar `ArgumentException`).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Execute os testes em um build Debug para que a nova asserção seja de fato avaliada.
