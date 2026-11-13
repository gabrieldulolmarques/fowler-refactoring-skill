# Introduzir Asserção (Introduce Assertion)

Fowler (2018), cap. 10, p. 302. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smell: Comentários (Comments). Um comentário que diz "isto deve ser positivo" ou "x nunca é nulo aqui" é
uma suposição escrita só para humanos. Uma asserção afirma a mesma coisa em código, de modo que
o leitor a vê e o ambiente de execução pode verificá-la.

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
public class Promotion
{
    public string? Code { get; }
    public string? SeasonName { get; }

    public Promotion(string? code, string? seasonName)
    {
        Code = code;
        SeasonName = seasonName;
    }

    public string Label()
    {
        // uma promoção sempre tem um código de cupom ou um nome de temporada
        return string.IsNullOrEmpty(Code) ? SeasonName! : Code;
    }
}
```

Depois (a verificação fica no construtor, onde um par inválido entraria primeiro):

```csharp
using System.Diagnostics;

public class Promotion
{
    public string? Code { get; }
    public string? SeasonName { get; }

    public Promotion(string? code, string? seasonName)
    {
        Debug.Assert(
            !string.IsNullOrEmpty(code) || !string.IsNullOrEmpty(seasonName),
            "a promotion needs a coupon code or a season name");
        Code = code;
        SeasonName = seasonName;
    }

    public string Label()
    {
        return string.IsNullOrEmpty(Code) ? SeasonName! : Code;
    }
}
```

## Notas (C#)
- `Debug.Assert` (`System.Diagnostics`) é removido das compilações Release, o que combina com a regra de que o programa deve se comportar igual sem asserções. Não coloque efeitos colaterais na expressão verificada.
- `Debug.Assert` não muda a análise de fluxo de nulos do compilador, então o `!` em `Label` continua e ainda oculta um possível null quando `Code` estiver vazio. A asserção documenta o invariante; ela não o prova para o compilador.
- Se a verificação também precisar rodar em produção, ela não é uma asserção: use validação de verdade (por exemplo, lançar `ArgumentException`).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Rode os testes em uma compilação Debug para que a nova asserção de fato seja avaliada.
