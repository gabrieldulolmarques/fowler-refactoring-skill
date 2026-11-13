# Substituir Construtores por Métodos de Criação (Replace Constructors with Creation Methods)

Kerievsky (2004), cap. 6, p. 57. Padrão: Creation Method. Direção: até.

## Quando usar
Smells: Código Duplicado (Duplicated Code), Obsessão por Primitivos (Primitive Obsession).

- Uma classe tem vários construtores, e os chamadores precisam ler listas de parâmetros ou corpos de construtores para escolher o certo. Uma chamada como `new ClientOptions("https://api.example.com", 30, 1.5)` não diz que tipo de cliente configura.
- Dois tipos de instância precisam dos mesmos tipos de parâmetro, então o segundo construtor não pode ser escrito. Métodos com nome não têm esse limite.
- Construtores que ninguém chama tendem a sobreviver porque são difíceis de buscar. Um método de criação com nome é fácil de buscar, então código de criação morto fica mais fácil de achar e apagar.
- Um Creation Method é qualquer método estático ou de instância que devolve uma nova instância. Todo Factory Method é um, mas o inverso não vale (veja [introduce-polymorphic-creation-with-factory-method.md](introduce-polymorphic-creation-with-factory-method.md)).
- Relação com Fowler: [replace-constructor-with-factory-function.md](../../fowler/refactoring-apis/replace-constructor-with-factory-function.md) é a versão de construtor único do mesmo movimento (um construtor, uma factory com nome). Este arquivo serve para uma classe com muitos construtores: você escolhe quais tipos de instância merecem um nome, faz todos passarem por um único construtor geral, e esconde o resto.
- Desvantagem: a criação fica não padronizada, porque algumas classes usam `new` e outras usam um Creation Method. Se a classe tem construtores demais porque faz coisas demais, aplique antes Extrair Classe (Extract Class) ([extract-class.md](../../fowler/encapsulation/extract-class.md)). Se a maioria das instâncias usa só uma pequena parte de seus campos, considere dividi-la com subclasses. Uma classe que precisaria de dezenas de Creation Methods pode manter alguns construtores públicos para casos raros, ou receber parâmetros nos seus Creation Methods.
- Se os Creation Methods começarem a ofuscar o propósito real da classe, mova-os para uma factory separada (o livro chama isso de Extrair Factory (Extract Factory); veja [move-creation-knowledge-to-factory.md](move-creation-knowledge-to-factory.md)).

## Mecânica
1. Encontre o construtor geral, o completo, para o qual os outros delegam. Se não existir, crie-o com Encadear Construtores (Chain Constructors) ([chain-constructors.md](../utilities/chain-constructors.md)).
2. Escolha um cliente que chame um construtor para obter um tipo de instância. Aplique Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) sobre essa chamada para obter um método estático público, e depois Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)) para colocá-lo na classe que possui o construtor. Dê a ele o nome do tipo de instância que devolve. Compile e teste.
3. Troque cada outro chamador desse construtor que quer o mesmo tipo de instância para chamar o Creation Method. Compile e teste.
4. Se o construtor escolhido delega a outro, faça o Creation Method chamar o delegado diretamente e internalize o construtor escolhido (como Internalizar Função (Inline Function), [inline-function.md](../../fowler/first-set/inline-function.md), aplicada a um construtor). Compile e teste.
5. Repita os passos 2 a 4 para cada construtor que quiser substituir.
6. Torne não público todo construtor que não tenha chamadores fora da classe. Compile.

## Exemplo
Antes: quatro construtores que diferem apenas nos valores padrão que preenchem. Dois deles recebem um único número, então quem chama precisa observar o tipo (`int` ou `double`) para obter o certo.

```csharp
public class ClientOptions
{
    private readonly string _baseUrl;
    private readonly int _timeoutSeconds;
    private readonly double _backoffFactor;

    public ClientOptions(string baseUrl) : this(baseUrl, 30, 2.0) { }
    public ClientOptions(string baseUrl, int timeoutSeconds) : this(baseUrl, timeoutSeconds, 2.0) { }
    public ClientOptions(string baseUrl, double backoffFactor) : this(baseUrl, 30, backoffFactor) { }
    public ClientOptions(string baseUrl, int timeoutSeconds, double backoffFactor)
    {
        _baseUrl = baseUrl; _timeoutSeconds = timeoutSeconds; _backoffFactor = backoffFactor;
    }

    public string Describe() => $"{_baseUrl} timeout={_timeoutSeconds}s backoff={_backoffFactor}";
}

public static class Caller
{
    public static void Run()
    {
        var a = new ClientOptions("https://api.example.test", 10);
        var b = new ClientOptions("https://api.example.test", 1.5);
    }
}
```

Depois: só sobra o construtor geral, privado. Cada tipo de opções tem um nome.

```csharp
public class ClientOptions
{
    private readonly string _baseUrl;
    private readonly int _timeoutSeconds;
    private readonly double _backoffFactor;

    private ClientOptions(string baseUrl, int timeoutSeconds, double backoffFactor)
    {
        _baseUrl = baseUrl; _timeoutSeconds = timeoutSeconds; _backoffFactor = backoffFactor;
    }

    public static ClientOptions Default(string baseUrl) => new(baseUrl, 30, 2.0);
    public static ClientOptions WithTimeout(string baseUrl, int timeoutSeconds) => new(baseUrl, timeoutSeconds, 2.0);
    public static ClientOptions WithBackoff(string baseUrl, double backoffFactor) => new(baseUrl, 30, backoffFactor);

    public string Describe() => $"{_baseUrl} timeout={_timeoutSeconds}s backoff={_backoffFactor}";
}

public static class Caller
{
    public static void Run()
    {
        var a = ClientOptions.WithTimeout("https://api.example.test", 10);
        var b = ClientOptions.WithBackoff("https://api.example.test", 1.5);
    }
}
```

## Notas (C#)
- Parâmetros opcionais ou inicializadores de objeto podem substituir alguns construtores encadeados, mas não dão nome ao tipo de instância. Use-os quando as variantes diferem apenas por um valor opcional, e Creation Methods quando as variantes significam coisas diferentes.
- Um `record` com construtor privado mais métodos estáticos funciona do mesmo jeito (C# 9+; no Unity ele precisa de um shim de `IsExternalInit`).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Uma busca pelo construtor não encontra nenhum chamador fora da classe, e nenhum Creation Method fica sem uso.
- O nome de cada Creation Method diz o que difere do valor padrão (timeout, backoff), não como os argumentos estão dispostos.
