# Unificar Interfaces (Unify Interfaces)

Kerievsky (2004), cap. 11, p. 343. Padrão: —. Direção: —.

## Quando usar
Smells: Código Duplicado (Duplicated Code) (a contracapa interna do livro lista Unificar Interfaces com Adapter (Unify Interfaces with Adapter) ali; este utilitário é o passo de baixo nível em que ela se apoia).

- Uma superclasse ou interface não tem métodos públicos que uma subclasse tem, então o código não consegue tratar todos da mesma forma e recorre a verificações de tipo ou casts.
- Adicione os métodos que faltam ao tipo base, com comportamento vazio (null) em uma classe, para que a subclasse possa sobrescrevê-los e os chamadores possam usar o tipo base em qualquer lugar.
- O livro precisou disso duas vezes: quando um Decorator precisava da mesma interface da classe que embeleza ([move-embellishment-to-decorator.md](../simplification/move-embellishment-to-decorator.md)), e quando um Visitor precisava que suas fontes o aceitassem polimorficamente ([move-accumulation-to-visitor.md](../accumulation/move-accumulation-to-visitor.md)).
- Muitas vezes é um passo temporário. Refatorações posteriores podem permitir remover de novo os métodos acrescentados, ou você pode extrair uma interface independente, para que os implementadores não herdem os campos da classe base.

## Mecânica
Para cada *método faltante*, ou seja, um método público na subclasse que a superclasse ou interface não declara:

1. Adicione uma cópia do método à superclasse ou interface. Na superclasse, dê a ele um corpo que não faz nada, ou que devolve um valor padrão inofensivo. Compile.
2. Repita até que os dois compartilhem a mesma interface pública.
3. Teste tudo que usa a superclasse.

## Exemplo
Antes: só a subclasse arquivada pode avisar sobre o vencimento da retenção, então um laço sobre os arquivos armazenados precisa testar o tipo.

```csharp
using System.Collections.Generic;

public interface IUploadNotifier { void Send(string message); }

public class StoredFile
{
    public string Name { get; }

    public StoredFile(string name) => Name = name;

    public virtual decimal MonthlyCostPerGb() => 0.02m;
}

public class ArchivedFile : StoredFile
{
    public ArchivedFile(string name) : base(name) { }

    public override decimal MonthlyCostPerGb() => 0.004m;
    public void NotifyExpiry(IUploadNotifier notifier) => notifier.Send($"File {Name} is close to its retention limit");
}
```

Depois: `NotifyExpiry` é declarado na classe base com comportamento nulo e sobrescrito na subclasse, então os chamadores usam apenas `StoredFile`.

```csharp
public class StoredFile
{
    public string Name { get; }

    public StoredFile(string name) => Name = name;

    public virtual decimal MonthlyCostPerGb() => 0.02m;
    public virtual void NotifyExpiry(IUploadNotifier notifier) { }
}

public class ArchivedFile : StoredFile
{
    public ArchivedFile(string name) : base(name) { }

    public override decimal MonthlyCostPerGb() => 0.004m;
    public override void NotifyExpiry(IUploadNotifier notifier) => notifier.Send($"File {Name} is close to its retention limit");
}

public static class Demo
{
    public static void NotifyAll(IEnumerable<StoredFile> files, IUploadNotifier notifier)
    {
        foreach (var f in files) f.NotifyExpiry(notifier);
    }
}
```

## Notas (C#)
- O método da base precisa ser `virtual` (ou `abstract`) e o da subclasse `override`. Um método da subclasse com o mesmo nome sem `override` oculta o da base, e chamar `NotifyExpiry` por uma referência a `StoredFile` não faria nada.
- Para uma interface, acrescentar um membro quebra todas as implementações existentes. Implementações padrão de interface (C# 8) permitem acrescentá-lo com corpo, mas só são acessíveis pelo tipo da interface, não pela classe.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os testes de tipo ou casts que a unificação deveria remover agora podem ser apagados, e os testes que usam apenas o tipo base continuam passando para cada subclasse.
