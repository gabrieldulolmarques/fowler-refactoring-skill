# Extrair Adapter (Extract Adapter)

Kerievsky (2004), cap. 8, p. 258. Padrão: Adapter. Direção: até.

## Quando usar
Smells: Solução Espalhada (Solution Sprawl).

- Uma classe adapta várias versões de um componente, biblioteca ou API, então carrega campos, construtores, métodos e condicionais específicos de cada versão. Comentários como "apague quando deixarmos a versão 1" ficam para sempre, porque ninguém se arrisca a remover código que algo desconhecido ainda pode usar.
- Um adaptador por versão, todos atrás de uma interface comum, mantém cada classe responsável por uma versão. O nome da classe pode até trazer a versão. O programa escolhe o adaptador certo a partir da configuração ou de informações de tempo de execução.
- Adaptadores também protegem você de APIs que mudam rápido e que você não controla.
- Não faça isso antes de as múltiplas versões realmente causarem condicionais ou problemas de manutenção.
- Um adaptador pode esconder um comportamento que o cliente precisa, porque o cliente só enxerga a interface do adaptador. Se for o caso, amplie a interface.
- Um adaptador envolve um único objeto. Se você precisa envolver um subsistema inteiro atrás de uma visão mais simples, isso é um Facade, que é outro padrão.

## Mecânica
Há várias formas de fazer isso. Se uma classe usa condicionais para tratar versões, normalmente você obtém um adaptador por versão aplicando repetidamente Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism) ([replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md)). Os passos abaixo cobrem o outro caso comum: uma classe adaptadora existente, com campos e métodos específicos de versão.

1. Identifique o adaptador sobrecarregado, a classe que adapta versões demais.
2. Crie um novo adaptador para uma versão, por Extrair Subclasse (Extract Subclass) (só na 1ª ed.; veja [replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md)) ou por Extrair Classe (Extract Class) ([extract-class.md](../../fowler/encapsulation/extract-class.md)). Mova ou copie para ele cada campo e método usado apenas por essa versão. Talvez seja preciso ampliar a visibilidade de alguns membros do adaptador sobrecarregado e inicializar alguns campos pelo construtor da nova classe, o que muda o código que a constrói. Compile e teste.
3. Repita o passo 2 para cada versão, até que o adaptador sobrecarregado não contenha mais código específico de versão.
4. Remova a duplicação entre os novos adaptadores com Subir Método (Pull Up Method) ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)) e Formar Template Method (Form Template Method) ([form-template-method.md](form-template-method.md)). Compile e teste.

## Exemplo
Antes: `AssistantModel` adapta duas versões da API de um provedor de modelos. Tem dois construtores, um campo anulável por versão e um desvio no único método.

```csharp
// Versão antiga da API do provedor: um prompt de texto na entrada, texto na saída.
public class LegacyCompletionService
{
    public string Complete(string prompt) => $"  reply to [{prompt}]  ";
}

// Nova versão: os textos de sistema e de usuário são separados, e a resposta é um objeto.
public class ChatReply
{
    public string Text { get; }
    public ChatReply(string text) => Text = text;
}

public class ChatServiceV2
{
    public ChatReply Send(string system, string user) => new ChatReply($"  reply to [{system}/{user}]  ");
}

public class AssistantModel
{
    private readonly LegacyCompletionService? _legacy;
    private readonly ChatServiceV2? _v2;

    public AssistantModel(LegacyCompletionService legacy) => _legacy = legacy;
    public AssistantModel(ChatServiceV2 v2) => _v2 = v2;

    public string Ask(string question)
    {
        var raw = _legacy != null
            ? _legacy.Complete($"User: {question}")
            : _v2!.Send("assistant", question).Text;
        return raw.Trim();
    }
}
```

Depois: um adaptador por versão, atrás de uma interface comum. A limpeza compartilhada (o `Trim`) fica em uma classe base (o passo de Formar Template Method), e cada adaptador implementa apenas como obter a resposta bruta.

```csharp
public class LegacyCompletionService
{
    public string Complete(string prompt) => $"  reply to [{prompt}]  ";
}

public class ChatReply
{
    public string Text { get; }
    public ChatReply(string text) => Text = text;
}

public class ChatServiceV2
{
    public ChatReply Send(string system, string user) => new ChatReply($"  reply to [{system}/{user}]  ");
}

public interface IAssistantModel
{
    string Ask(string question);
}

public abstract class AssistantModel : IAssistantModel
{
    public string Ask(string question) => RawReply(question).Trim();

    protected abstract string RawReply(string question);
}

public class LegacyAssistantModel : AssistantModel
{
    private readonly LegacyCompletionService _service;
    public LegacyAssistantModel(LegacyCompletionService service) => _service = service;
    protected override string RawReply(string question) => _service.Complete($"User: {question}");
}

public class V2AssistantModel : AssistantModel
{
    private readonly ChatServiceV2 _service;
    public V2AssistantModel(ChatServiceV2 service) => _service = service;
    protected override string RawReply(string question) => _service.Send("assistant", question).Text;
}
```

Os clientes dependem de `IAssistantModel`; o código de inicialização (ou a configuração) escolhe `LegacyAssistantModel` ou `V2AssistantModel`. Quando a versão 1 for aposentada, apague uma classe e nada mais.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Cada adaptador tem um teste contra a sua própria versão (ou um fake dela), e a classe sobrecarregada antiga não tem mais campos nem desvios de versão antes de você apagá-la.
