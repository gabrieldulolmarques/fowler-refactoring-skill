# Substituir Código de Tipo por Subclasses (Replace Type Code with Subclasses)

Fowler (2018), cap. 12, p. 362. Antes / também: engloba Replace Type Code with State/Strategy e Extract Subclass. Inversa: Remover Subclasse (Remove Subclass) ([remove-subclass.md](remove-subclass.md)).

## Quando usar
Smells: Obsessão por Primitivos (Primitive Obsession), Classe Grande (Large Class).

- Vários métodos ramificam pelo mesmo código de tipo. As subclasses permitem terminar com Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism) ([replace-conditional-with-polymorphism.md](../conditional-logic/replace-conditional-with-polymorphism.md)).
- Alguns campos ou métodos só se aplicam a certos valores do código. Uma subclasse os guarda de forma explícita, em vez de depender de verificações de que o código tem o valor certo ([push-down-field.md](push-down-field.md), [push-down-method.md](push-down-method.md)).

Escolha onde as subclasses ficam:

- **Herança direta:** crie subclasses da própria classe (`Engineer : Employee`). É o mais simples, mas não funciona se essa classe já precisa de subclasses para outro eixo, ou se um objeto deve mudar de tipo durante a sua vida.
- **Herança indireta:** aplique primeiro Substituir Primitivo por Objeto (Replace Primitive with Object) ([replace-primitive-with-object.md](../encapsulation/replace-primitive-with-object.md)) ao código, produzindo uma pequena classe de tipo, e então crie subclasses dessa classe. O dono guarda uma referência a ela, então o tipo pode mudar em tempo de execução. É nisso que a antiga refatoração State/Strategy se resume.

Não use quando o código é apenas dado do qual nenhum comportamento depende; um enum simples basta ali.

## Mecânica
1. Autoencapsule o código de tipo: todas as leituras passam por um único getter.
2. Escolha um valor de código. Crie uma subclasse para ele cujo getter retorne esse valor literal.
3. Adicione lógica de seleção que mapeie o código recebido para a subclasse. Com herança direta, faça da construção uma fábrica ([replace-constructor-with-factory-function.md](../refactoring-apis/replace-constructor-with-factory-function.md)) e ponha a seleção ali. Com herança indireta, a seleção pode ficar no construtor ou no setter do dono. Enquanto alguns códigos ainda não têm subclasse, mantenha a classe base concreta e deixe a seleção recorrer a ela.
4. Compile e teste. Para ter certeza de que os testes exercitam a nova subclasse, mude por um instante o valor que ela retorna e verifique que um teste falha, depois restaure-o.
5. Repita os passos 2 a 4 para cada valor de código restante, testando após cada um. A classe base permanece concreta até que o último esteja feito.
6. Quando todo valor tiver uma subclasse, remova o campo armazenado do código de tipo e o getter da base. Faça os códigos desconhecidos falharem na lógica de seleção (o ramo padrão lança uma exceção), depois descarte qualquer validação separada. Compile e teste.
7. Remova o parâmetro de código agora sem uso do construtor ([change-function-declaration.md](../first-set/change-function-declaration.md)).
8. Para cada método que usa o getter de tipo, desça-o para as subclasses e substitua o condicional por polimorfismo. Quando nada mais ler o getter, apague-o ([remove-dead-code.md](../moving-features/remove-dead-code.md)). Teste após cada método.

Com herança indireta, um tipo mutável significa um setter que reexecuta a seleção e troca o objeto de tipo. Com isso, a classe base vazia do tipo pode permanecer: ela documenta a família e é um lugar natural para a lógica compartilhada entre os tipos.

## Exemplo
Antes: um arquivo de mídia cujo comportamento depende de um tipo em string.

```csharp
using System;

public class MediaFile
{
    private readonly string _title;
    private readonly string _kind;

    public MediaFile(string title, string kind)
    {
        if (kind != "audio" && kind != "video")
            throw new ArgumentException($"Unknown media kind: {kind}");
        _title = title;
        _kind = kind;
    }

    public string Kind => _kind;

    public int MegabytesPerMinute() => _kind == "video" ? 8 : 1;

    public override string ToString() => $"{_title} ({_kind})";
}
```

Depois dos passos 1 a 8 (`MegabytesPerMinute` descido e tornado polimórfico; `Kind` mantido apenas para `ToString`):

```csharp
using System;

public abstract class MediaFile
{
    private readonly string _title;

    protected MediaFile(string title) => _title = title;

    public static MediaFile Create(string title, string kind) => kind switch
    {
        "audio" => new AudioFile(title),
        "video" => new VideoFile(title),
        _ => throw new ArgumentException($"Unknown media kind: {kind}")
    };

    public abstract string Kind { get; }

    public abstract int MegabytesPerMinute();

    public override string ToString() => $"{_title} ({Kind})";
}

public class AudioFile : MediaFile
{
    public AudioFile(string title) : base(title) { }
    public override string Kind => "audio";
    public override int MegabytesPerMinute() => 1;
}

public class VideoFile : MediaFile
{
    public VideoFile(string title) : base(title) { }
    public override string Kind => "video";
    public override int MegabytesPerMinute() => 8;
}
```

O comportamento não muda: os chamadores agora usam `MediaFile.Create(title, kind)`, e `MegabytesPerMinute`
não ramifica mais pelo código. `Kind` permanece apenas porque `ToString` e possivelmente chamadores externos
o leem; apague-o (passo 8) quando nada mais o fizer.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Todo valor de código que existia antes mapeia para uma subclasse, e valores desconhecidos ainda falham do
  mesmo modo que antes.
