# Separar Consulta de Modificador (Separate Query from Modifier)

Fowler (2018), cap. 11, p. 306. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smell: Dados Mutáveis (Mutable Data). Uma função que retorna um valor e também tem efeitos colaterais observáveis
é difícil de confiar: um chamador não pode chamá-la livremente, repeti-la, movê-la ou testá-la sem
disparar o efeito. Uma função sem efeitos colaterais observáveis pode ser chamada qualquer número
de vezes e em qualquer ordem.

Siga a separação comando-consulta, pelo menos na maior parte do tempo: um método que retorna um valor
não deve ter efeitos colaterais observáveis. Divida um método que faça as duas coisas.

Não é uma violação: uma consulta que atualiza um cache privado por velocidade. A mudança não é
observável, já que toda sequência de chamadas retorna os mesmos resultados. Deixe esses casos em paz.

## Mecânica
1. Copie a função e nomeie a cópia pelo que ela retorna (a consulta). Se o seu resultado
   preenche uma variável em um ponto de chamada, o nome dessa variável é uma boa dica.
2. Remova todo efeito colateral da cópia, para que ela apenas calcule e retorne o valor.
3. Rode o compilador ou as verificações estáticas.
4. Encontre cada chamador do original que usa o valor retornado. Substitua a chamada por uma
   chamada à consulta, depois adicione uma chamada ao original logo abaixo. Teste após cada chamador.
5. Remova o valor de retorno do original, para que ele agora seja um comando puro.
6. Teste.
7. A consulta e o comando agora normalmente duplicam lógica. Remova a duplicação, muitas vezes
   fazendo o comando chamar a consulta.

## Exemplo
Antes: um método encontra o primeiro inscrito com bounces e o desativa.

```csharp
using System;
using System.Collections.Generic;

public class Subscriber
{
    public Subscriber(string id, int bounces)
    {
        Id = id;
        Bounces = bounces;
    }

    public string Id { get; }
    public int Bounces { get; }
}

public class MailingListService
{
    private readonly List<string> _disabled = new();

    public string DisableFirstBouncing(IEnumerable<Subscriber> subscribers)
    {
        foreach (var subscriber in subscribers)
        {
            if (subscriber.Bounces > 3)
            {
                _disabled.Add(subscriber.Id);
                return subscriber.Id;
            }
        }
        return "";
    }
}

// chamador
// var id = service.DisableFirstBouncing(subscribers);
// Console.WriteLine($"First bouncing: {id}");
```

Depois: uma consulta e um comando, com o comando reutilizando a consulta.

```csharp
using System;
using System.Collections.Generic;

public class MailingListService
{
    private readonly List<string> _disabled = new();

    public string FindFirstBouncing(IEnumerable<Subscriber> subscribers)
    {
        foreach (var subscriber in subscribers)
        {
            if (subscriber.Bounces > 3) return subscriber.Id;
        }
        return "";
    }

    public void DisableFirstBouncing(IEnumerable<Subscriber> subscribers)
    {
        var id = FindFirstBouncing(subscribers);
        if (id != "") _disabled.Add(id);
    }
}

// chamador
// var id = service.FindFirstBouncing(subscribers);
// service.DisableFirstBouncing(subscribers);
// Console.WriteLine($"First bouncing: {id}");
```

Suposição: nenhum inscrito tem `Id` vazio, já que `""` significa "nenhum encontrado". Observe que o comando agora executa a busca de novo. Esse é o custo usual da separação; se a consulta for cara, aceite isso, faça um cache invisível ou passe o valor encontrado para o comando.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
