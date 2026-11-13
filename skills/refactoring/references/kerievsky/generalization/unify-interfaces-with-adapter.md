# Unificar Interfaces com Adapter (Unify Interfaces with Adapter)

Kerievsky (2004), cap. 8, p. 247. Padrão: Adapter. Direção: até, rumo a.

## Quando usar
Smells: Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces), Solução Destoante (Oddball Solution), Código Duplicado (Duplicated Code).

- Duas classes fazem o mesmo trabalho, ou um trabalho parecido, por interfaces diferentes, e um cliente que usa as duas precisa ser escrito duas vezes.
- O cliente seria mais simples se as duas tivessem a mesma aparência.
- Você não pode simplesmente renomear ou mover métodos até que eles coincidam, porque uma das classes pertence a uma biblioteca de terceiros, a um framework com muitos outros clientes, ou porque você não tem o código-fonte dela.
- Depois que as duas classes estão atrás de uma interface comum, o código duplicado do cliente pode ser unificado com refatorações como Formar Template Method (Form Template Method) ([form-template-method.md](form-template-method.md)) ou Introduzir Criação Polimórfica com Factory Method (Introduce Polymorphic Creation with Factory Method) ([introduce-polymorphic-creation-with-factory-method.md](../creation/introduce-polymorphic-creation-with-factory-method.md)).
- Não use quando você pode alterar diretamente uma das interfaces: renomear é mais barato do que acrescentar uma classe.

## Mecânica
O adaptado é a classe cuja interface o cliente não prefere. O adaptador é a classe que vai envolvê-la.

1. Extraia uma interface comum da classe cuja interface o cliente prefere (Extrair Interface (Extract Interface), só na 1ª ed.). Se essa classe tem métodos que recebem o próprio tipo, altere-os para receber a interface. Compile e teste.
2. No cliente que usa o adaptado, aplique Extrair Classe (Extract Class) ([extract-class.md](../../fowler/encapsulation/extract-class.md)) para criar um adaptador primitivo: uma classe com um campo para o adaptado, um getter para ele e um construtor (ou setter) que o recebe.
3. Troque os campos, variáveis locais e parâmetros do cliente que são do tipo adaptado pelo tipo adaptador. Cada chamada agora primeiro obtém o adaptado a partir do adaptador. Compile e teste.
4. Para cada chamada distinta ao adaptado no cliente, aplique Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) para criar um método de invocação que recebe o adaptador como parâmetro e chama o adaptado por ele. Compile e teste após cada um.
5. Mova cada método de invocação para o adaptador com Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)), moldando-o como o método correspondente da interface comum. Se o corpo movido precisar de um valor do cliente, passe-o pelo construtor do adaptador, ou dê ao adaptador uma referência que ele possa consultar, em vez de acrescentar um parâmetro que tornaria a assinatura diferente. Se um parâmetro for inevitável, altere o método da interface para casar. Compile e teste; repita até o adaptador ter todos os métodos da interface.
6. Declare que o adaptador implementa a interface comum, e altere os métodos do adaptador que recebem um adaptador para receber a interface. Compile e teste.
7. Mude o cliente para usar a interface em todos os pontos, no lugar do tipo adaptador. Compile e teste. O cliente agora fala com as duas classes por um único tipo.

## Exemplo
Antes: um respondedor em lote envia perguntas ao nosso próprio `InHouseModel` e, com uma cópia separada da lógica, à `RemoteCompletionApi` de terceiros, que não podemos alterar.

```csharp
using System.Collections.Generic;

public class InHouseModel
{
    public string Reply(string prompt, int maxTokens) => $"in-house({maxTokens}): {prompt}";
}

public class CompletionRequest
{
    public string Prompt { get; }
    public int MaxTokens { get; }
    public CompletionRequest(string prompt, int maxTokens) { Prompt = prompt; MaxTokens = maxTokens; }
}

public class CompletionResponse
{
    public string Text { get; }
    public CompletionResponse(string text) => Text = text;
}

// Terceiro: não pode ser alterado.
public sealed class RemoteCompletionApi
{
    public CompletionResponse Complete(CompletionRequest request) =>
        new CompletionResponse($"remote({request.MaxTokens}): {request.Prompt}");
}

public class BatchAnswerer
{
    public List<string> AnswerInHouse(IEnumerable<string> questions, InHouseModel model)
    {
        var answers = new List<string>();
        foreach (var q in questions)
            answers.Add(model.Reply($"Answer briefly: {q}", 256));
        return answers;
    }

    public List<string> AnswerRemote(IEnumerable<string> questions, RemoteCompletionApi api)
    {
        var answers = new List<string>();
        foreach (var q in questions)
            answers.Add(api.Complete(new CompletionRequest($"Answer briefly: {q}", 256)).Text);
        return answers;
    }
}
```

Depois: os dois provedores ficam atrás de `IChatModel`. O adaptador envolve a API remota, e o respondedor tem um único laço.

```csharp
using System.Collections.Generic;

public interface IChatModel
{
    string Reply(string prompt, int maxTokens);
}

public class InHouseModel : IChatModel
{
    public string Reply(string prompt, int maxTokens) => $"in-house({maxTokens}): {prompt}";
}

public class CompletionRequest
{
    public string Prompt { get; }
    public int MaxTokens { get; }
    public CompletionRequest(string prompt, int maxTokens) { Prompt = prompt; MaxTokens = maxTokens; }
}

public class CompletionResponse
{
    public string Text { get; }
    public CompletionResponse(string text) => Text = text;
}

// Terceiro: não pode ser alterado.
public sealed class RemoteCompletionApi
{
    public CompletionResponse Complete(CompletionRequest request) =>
        new CompletionResponse($"remote({request.MaxTokens}): {request.Prompt}");
}

public class RemoteModelAdapter : IChatModel
{
    private readonly RemoteCompletionApi _api;
    public RemoteModelAdapter(RemoteCompletionApi api) => _api = api;

    public string Reply(string prompt, int maxTokens) =>
        _api.Complete(new CompletionRequest(prompt, maxTokens)).Text;
}

public class BatchAnswerer
{
    public List<string> Answer(IEnumerable<string> questions, IChatModel model)
    {
        var answers = new List<string>();
        foreach (var q in questions)
            answers.Add(model.Reply($"Answer briefly: {q}", 256));
        return answers;
    }
}
```

O componente de terceiros não muda: só o adaptador conhece os tipos de requisição e de resposta dele. Adicionar outro provedor significa mais um adaptador, não mais um laço.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- As mesmas entradas produzem as mesmas respostas pelos dois caminhos que antes (compare as respostas devolvidas), e nenhum código do cliente ainda cita o tipo adaptado.
