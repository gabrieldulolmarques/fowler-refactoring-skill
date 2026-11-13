# Remover Argumento de Flag (Remove Flag Argument)

Fowler (2018), cap. 11, p. 314. Antes / também: antes Replace Parameter with Explicit Methods. Inversa: —.

## Quando usar
Smells: Lista Longa de Parâmetros (Long Parameter List).

Um argumento de flag é um parâmetro que o chamador define como um literal (`true`, um membro de enum, uma string) apenas para dizer ao método qual ramo executar. O ponto de chamada então não diz nada sobre o que o valor significa, e a lista de métodos não mostra quais variações existem.

É um argumento de flag somente quando as duas condições valem:
- o chamador passa uma constante que apenas escolhe um ramo, não um valor que se origina em outro lugar do programa;
- o método usa o parâmetro apenas para escolher um caminho, não para repassar ou armazenar.

Não mude chamadores que passam valores calculados. Se alguns chamadores passam literais e outros passam dados, adicione os métodos explícitos, migre apenas os chamadores de literais e mantenha o método original para os chamadores de dados.

Com várias flags independentes, um método por combinação é impraticável, então manter as flags pode ser razoável. Trate-as como um sinal para dividir o método em métodos menores e combináveis.

## Mecânica
1. Crie um método explícito para cada valor do parâmetro, nomeado pelo que aquele valor significa.
   - Se o método original já despacha pelo parâmetro no seu nível mais externo, aplique [decompose-conditional.md](../conditional-logic/decompose-conditional.md): cada ramo vira o corpo de um método explícito, e o original apenas os chama.
   - Se o parâmetro estiver entrelaçado pelo corpo, faça de cada método explícito um invólucro fino que chama o original com um valor fixo.
2. Compile e teste.
3. Substitua cada chamador que passa um literal por uma chamada ao método explícito correspondente. Compile e teste após cada chamador (ou grupo pequeno).
4. Quando nenhum chamador usar mais o parâmetro, apague o método original. Se ele permanecer como alvo dos invólucros, reduza a sua visibilidade ou renomeie-o para sinalizar "interno" (por exemplo, com o sufixo `Core` ou `Impl`).
5. Compile e teste.

## Exemplo
Antes:

```csharp
using System.Collections.Generic;

public class Notifier
{
    private readonly List<string> _sent = new();
    private readonly List<string> _queue = new();

    public void Send(string recipient, string text, bool immediate)
    {
        if (immediate)
        {
            _sent.Add(recipient + ": " + text);
            return;
        }
        _queue.Add(recipient + ": " + text);
    }
}

// chamadores
// notifier.Send("ada@example.com", "Your code is 4821", true);
// notifier.Send("ada@example.com", "Weekly digest", false);
```

Depois:

```csharp
using System.Collections.Generic;

public class Notifier
{
    private readonly List<string> _sent = new();
    private readonly List<string> _queue = new();

    public void SendNow(string recipient, string text)
    {
        _sent.Add(recipient + ": " + text);
    }

    public void Enqueue(string recipient, string text)
    {
        _queue.Add(recipient + ": " + text);
    }
}

// chamadores
// notifier.SendNow("ada@example.com", "Your code is 4821");
// notifier.Enqueue("ada@example.com", "Weekly digest");
```

Quando a flag é usada em vários lugares do corpo, mantenha o original e adicione invólucros. No estado final abaixo, o `Send` original foi renomeado para `SendCore` e tornado privado, o que é possível quando nenhum chamador de literal o usa mais:

```csharp
using System.Collections.Generic;

public class Notifier
{
    private readonly List<string> _sent = new();
    private readonly List<string> _queue = new();

    public void SendNow(string recipient, string text) => SendCore(recipient, text, immediate: true);
    public void Enqueue(string recipient, string text) => SendCore(recipient, text, immediate: false);

    private void SendCore(string recipient, string text, bool immediate)
    {
        var line = immediate ? "[URGENT] " + text : text;
        if (immediate)
        {
            _sent.Add(recipient + ": " + line);
            return;
        }
        _queue.Add(recipient + ": " + line);
    }
}

// chamadores
// notifier.SendNow("ada@example.com", "Your code is 4821");
// notifier.Enqueue("ada@example.com", "Weekly digest");
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Todo chamador de literal agora se lê como o método explícito, e o comportamento para cada valor não mudou.
