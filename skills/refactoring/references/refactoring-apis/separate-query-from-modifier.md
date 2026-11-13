# Separar Consulta de Modificador (Separate Query from Modifier)

Fowler (2018), cap. 11, p. 306. Antes / também: —. Inversa: —.

## Quando usar
Smell: Dados Mutáveis (Mutable Data). Uma função que retorna um valor e também tem efeitos colaterais observáveis
é difícil de confiar: um chamador não pode chamá-la livremente, repeti-la, movê-la ou testá-la sem
disparar o efeito. Uma função sem efeitos colaterais observáveis pode ser chamada qualquer número
de vezes e em qualquer ordem.

Siga a separação comando-consulta: um método que retorna um valor não deve alterar
o estado observável, e um método que altera estado não deve retornar uma resposta calculada. Divida
qualquer método que faça as duas coisas.

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
Antes: um método encontra a conta em atraso e a suspende.

```csharp
public record Account(string Id, int DaysOverdue);

public class CollectionsService
{
    private readonly List<string> _suspended = new();

    public string SuspendFirstOverdue(IEnumerable<Account> accounts)
    {
        foreach (var account in accounts)
        {
            if (account.DaysOverdue > 30)
            {
                _suspended.Add(account.Id);
                return account.Id;
            }
        }
        return "";
    }
}

// chamador
var id = service.SuspendFirstOverdue(accounts);
Console.WriteLine($"Primeira em atraso: {id}");
```

Depois: uma consulta e um comando, com o comando reutilizando a consulta.

```csharp
public class CollectionsService
{
    private readonly List<string> _suspended = new();

    public string FindFirstOverdue(IEnumerable<Account> accounts)
    {
        foreach (var account in accounts)
        {
            if (account.DaysOverdue > 30) return account.Id;
        }
        return "";
    }

    public void SuspendFirstOverdue(IEnumerable<Account> accounts)
    {
        var id = FindFirstOverdue(accounts);
        if (id != "") _suspended.Add(id);
    }
}

// chamador
var id = service.FindFirstOverdue(accounts);
service.SuspendFirstOverdue(accounts);
Console.WriteLine($"Primeira em atraso: {id}");
```

Note que o comando agora executa a busca de novo. Esse é o custo usual da divisão; se
a consulta for cara, aceite-o, faça cache de forma invisível, ou passe o valor encontrado ao
comando em vez disso.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
