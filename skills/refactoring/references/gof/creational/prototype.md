# Prototype

Gamma et al. (1995), cap. 3, p. 117. Categoria: criacional de objeto.

## Intenção
Criar objetos novos copiando uma instância já configurada (o protótipo), para que um cliente possa produzir objetos sem conhecer suas classes nem como foram configurados.

## Quando compensa
- As classes a criar são escolhidas em tempo de execução, ou você quer evitar uma hierarquia de fábricas que espelha a hierarquia de produtos.
- As instâncias de uma classe diferem apenas em algumas combinações de estado, então é mais fácil manter algumas instâncias prontas e clonar do que construir cada uma do zero.
- Novos tipos de objeto podem ser definidos registrando uma instância configurada, incluindo e removendo em tempo de execução, sem nenhuma classe nova.
- Reduz a herança, e os usuários podem definir "novos tipos" variando valores ou estrutura.
- Custo: toda classe protótipo precisa implementar uma clonagem correta, o que pode ser difícil quando o objeto mantém recursos compartilhados ou referências circulares.
- Não vale a pena quando construir o objeto é barato e óbvio, ou quando os objetos são imutáveis (compartilhe a mesma instância).

## Participantes em C#
- **Prototype** (`IPrototype<T>`): interface que declara `Clone()`. `ICloneable` existe, mas devolve `object`, então uma interface tipada é melhor.
- **ConcretePrototype** (`BillingPlan`): implementa `Clone()`.
- **Client** (`PlanCatalog`): guarda protótipos sob chaves e cria objetos novos clonando-os.

## Exemplo (C#)
Um sistema de cobrança SaaS oferece alguns planos base. O comercial cria planos personalizados para clientes como cópias de um plano base com preço alterado, e o catálogo nunca precisa conhecer mais do que o tipo do plano.

```csharp
using System;
using System.Collections.Generic;

public interface IPrototype<T>
{
    T Clone();
}

public class BillingPlan : IPrototype<BillingPlan>
{
    public string Name { get; set; }
    public decimal MonthlyPrice { get; set; }
    public List<string> Features { get; }

    public BillingPlan(string name, decimal monthlyPrice, IEnumerable<string> features)
    {
        Name = name;
        MonthlyPrice = monthlyPrice;
        Features = new List<string>(features);
    }

    // cópia profunda: o clone possui sua própria lista de recursos
    public BillingPlan Clone() => new BillingPlan(Name, MonthlyPrice, Features);
}

public class PlanCatalog
{
    private readonly Dictionary<string, BillingPlan> _prototypes = new();

    public void Register(string key, BillingPlan prototype) => _prototypes[key] = prototype;

    public bool Unregister(string key) => _prototypes.Remove(key);

    public BillingPlan Create(string key)
    {
        if (!_prototypes.TryGetValue(key, out var prototype))
            throw new KeyNotFoundException("No plan registered as " + key);
        return prototype.Clone();
    }
}

public static class Program
{
    public static void Main()
    {
        var catalog = new PlanCatalog();
        catalog.Register("starter", new BillingPlan("Starter", 9m, new[] { "1 project" }));
        catalog.Register("team", new BillingPlan("Team", 49m, new[] { "10 projects", "SSO" }));

        BillingPlan custom = catalog.Create("team");
        custom.Name = "Team (Acme)";
        custom.MonthlyPrice = 39m;
        custom.Features.Add("Priority support");

        Console.WriteLine(catalog.Create("team").Features.Count); // 2: o protótipo permanece intacto
    }
}
```

## Variações
- **Gerenciador de protótipos.** Quando os protótipos entram e saem em tempo de execução, mantenha um registro (`PlanCatalog`) que cadastra, remove e busca por chave, para que os clientes não gerenciem os protótipos diretamente.
- **Cópia rasa versus cópia profunda.** Decida o que é compartilhado e o que é copiado. `MemberwiseClone()` faz uma cópia rasa: campos de referência (como `Features`) ficariam compartilhados. Copie toda referência mutável que o clone precisa possuir.
- **Inicializando o clone.** O clone muitas vezes precisa de valores (nome do cliente, um identificador). Parâmetros em `Clone()` quebram a interface uniforme, então defina propriedades depois de clonar, ou adicione um método `Initialize(...)` na classe concreta.
- **Cópia por serialização.** Se o objeto já pode ser serializado e desserializado, um ciclo de ida e volta produz uma cópia profunda de graça, ao custo de desempenho.
- **Fábrica baseada em protótipos.** Uma fábrica que mantém um protótipo por produto e o clona (veja [abstract-factory.md](abstract-factory.md)).

## Riscos e alternativas em C#
- Esquecer de copiar em profundidade um campo mutável gera dois objetos que se alteram em silêncio. Teste se mudar o clone deixa o protótipo intacto (veja Verificação).
- Um construtor de cópia (`new BillingPlan(other)`) é uma alternativa comum e explícita a um método `Clone()`, e não precisa de interface de clonagem.
- Para objetos imutáveis não há o que proteger: compartilhe uma instância e crie variações com um método que devolve um objeto novo (`plan.WithPrice(39m)`).
- Evite `ICloneable`: seu contrato não diz se a cópia é rasa ou profunda, e ele devolve `object`.
- Tipos por valor (`struct`) já são copiados na atribuição; um protótipo só é necessário para tipos de referência.

## Padrões relacionados
- [Abstract Factory](abstract-factory.md): concorrente e parceiro; uma fábrica pode guardar protótipos e devolver clones.
- [Factory Method](factory-method.md): outra forma de variar as classes criadas, por meio de subclasses do criador.
- [Composite](../structural/composite.md) e [Decorator](../structural/decorator.md): designs com muitos desses padrões costumam se beneficiar do Prototype, já que copiar uma estrutura inteira é útil.

## Verificação
- Clonar devolve um objeto independente: alterar o clone não altera o protótipo, incluindo coleções aninhadas.
- Adicionar uma nova variante do produto exige um cadastro, não uma nova classe ou fábrica.
- Todo protótipo concreto sobrescreve `Clone()` de modo que o clone tenha o mesmo tipo em tempo de execução.
- Se os clones nunca são personalizados e os objetos nunca mudam, verifique se compartilhar uma única instância imutável não bastaria.
