# Introduzir Criação Polimórfica com Factory Method (Introduce Polymorphic Creation with Factory Method)

Kerievsky (2004), cap. 6, p. 88. Padrão: Factory Method. Direção: até.

## Quando usar
Smells: Código Duplicado (Duplicated Code).

- Classes em uma hierarquia implementam um método quase de forma idêntica, e a única diferença é qual classe elas instanciam. O resto do método é o mesmo.
- Um Factory Method precisa de três coisas: um tipo (interface ou classe base) para o que é criado, as classes que implementam esse tipo, e várias classes que decidem localmente qual delas criar.
- Costuma aparecer onde um Template Method chama um Factory Method para seu único passo variável. Remover métodos duplicados em uma hierarquia costuma terminar nessa combinação.
- Frameworks usam do mesmo jeito: declaram um método de criação e deixam sua subclasse sobrescrevê-lo para encaixar o seu próprio objeto.
- Custos: a assinatura é compartilhada por todos os implementadores, então alguns deles podem receber parâmetros de que não precisam. O padrão é mais difícil de montar do que `new`, mas o código que o usa é mais curto do que os métodos duplicados que substitui.
- Compare com [replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md): um Creation Method comum não é polimórfico; um Factory Method é.

## Mecânica
Isto cobre o caso de subclasses irmãs com um *método semelhante*. Uma superclasse e uma subclasse é o mesmo, com menos passos.
1. Em uma subclasse, altere o método semelhante para que a criação aconteça em um *método de instanciação* separado (aplique Extrair Função (Extract Function), [extract-function.md](../../fowler/first-set/extract-function.md)). Use um nome genérico (`CreateReport`) e devolva o tipo que todas as irmãs podem compartilhar. Compile e teste.
2. Faça o mesmo em cada irmã. Os métodos de instanciação devem acabar com a mesma assinatura. Compile e teste.
3. Garanta que as irmãs tenham uma superclasse comum que você possa alterar. Se não tiverem, aplique Extrair Superclasse (Extract Superclass) ([extract-superclass.md](../../fowler/inheritance/extract-superclass.md)). Esta classe desempenha o papel de Creator no padrão. Compile e teste.
4. Aplique Formar Template Method (Form Template Method) ([form-template-method.md](../generalization/form-template-method.md)) ao método semelhante. Isso usa Subir Método (Pull Up Method) ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)), e o método de instanciação se torna um método abstrato na superclasse: esse é o factory method. Cada irmã agora é um ConcreteCreator. Compile e teste.
5. Repita para outros métodos semelhantes nas irmãs que possam usar o mesmo factory method.
6. Se a maioria das subclasses cria a mesma classe, dê ao método da superclasse um corpo padrão que cria essa classe, e deixe as outras sobrescrevê-lo. Compile e teste.

## Exemplo
Antes: dois clientes repetem o mesmo método. Só a classe de parser muda.

```csharp
using System.Collections.Generic;
using System.Linq;

public interface IItemParser { IReadOnlyList<string> Parse(string body); }
public class CsvItemParser : IItemParser
{
    public IReadOnlyList<string> Parse(string body) => body.Split(',').Select(s => s.Trim()).ToList();
}
public class LineItemParser : IItemParser
{
    public IReadOnlyList<string> Parse(string body) => body.Split('\n').Select(s => s.Trim()).ToList();
}

public class CsvApiClient
{
    public IReadOnlyList<string> GetItems(string rawBody)
    {
        var body = rawBody.Trim();
        var parser = new CsvItemParser();
        return parser.Parse(body).Where(i => i.Length > 0).ToList();
    }
}
public class LineApiClient
{
    public IReadOnlyList<string> GetItems(string rawBody)
    {
        var body = rawBody.Trim();
        var parser = new LineItemParser();
        return parser.Parse(body).Where(i => i.Length > 0).ToList();
    }
}
```

Depois: `GetItems` existe uma única vez em `ApiClient`. Ele chama `CreateParser`, e cada subclasse decide o que construir.

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class ApiClient
{
    public IReadOnlyList<string> GetItems(string rawBody)
    {
        var body = rawBody.Trim();
        var parser = CreateParser();
        return parser.Parse(body).Where(i => i.Length > 0).ToList();
    }

    protected abstract IItemParser CreateParser();
}

public class CsvApiClient : ApiClient
{
    protected override IItemParser CreateParser() => new CsvItemParser();
}

public class LineApiClient : ApiClient
{
    protected override IItemParser CreateParser() => new LineItemParser();
}
```

## Notas (C#)
- Torne o factory method `protected abstract`, a menos que chamadores fora da hierarquia precisem dele. Uma implementação padrão é `protected virtual`.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- O método parecido agora existe em um único lugar, e nenhuma subclasse repete o seu corpo.
- Cada subclasse sobrescreve apenas a etapa de criação.
