# Flyweight

Gamma et al. (1995), cap. 4, p. 195. Categoria: estrutural de objeto.

## Intenção
Compartilhar objetos para que um número muito grande de objetos pequenos, de granularidade fina, se torne viável. A parte compartilhada fica dentro do objeto, e a parte que varia é passada pelo chamador.

## Quando compensa
- Todas estas condições valem: o programa tem uma quantidade enorme de objetos parecidos, eles custam memória demais, a maior parte do estado pode ser movida para fora, e depois disso poucos objetos compartilhados podem representar muitos dos antigos.
- O código não depende da identidade dos objetos (dois objetos lógicos podem ser a mesma instância).
- Benefício: a memória cai conforme o compartilhamento aumenta, sobretudo quando os dados externos podem ser calculados ou guardados em uma estrutura compacta.
- Custo: quem chama precisa fornecer o estado externo a cada chamada, e há um custo de busca ou de cálculo para isso. O código fica mais difícil de acompanhar.
- Não vale a pena quando a quantidade é pequena, quando a memória não é um problema medido, ou quando o estado não pode ser separado. Meça antes.

## Participantes em C#
- **Flyweight** (`VehicleKind`): o objeto compartilhado, com apenas estado intrínseco (o mesmo para todos que o usam). Suas operações recebem o estado extrínseco como parâmetros. Em C# é uma classe imutável, já que objetos compartilhados não podem mudar.
- **ConcreteFlyweight** (o próprio `VehicleKind`): aqui o flyweight é uma única classe. Várias classes concretas atrás de uma interface também funcionam.
- **UnsharedConcreteFlyweight** (não necessário no exemplo): uma variante da interface que não é compartilhada, por exemplo, um veículo com estado único.
- **FlyweightFactory** (`VehicleKinds`): cria flyweights, guarda-os por chave e devolve o existente quando pedido de novo.
- **Client** (`Vehicle`, `Main`): guarda ou calcula o estado extrínseco (posição, motorista, status) e o passa adiante.

## Exemplo (C#)
Um mapa de corridas compartilhadas acompanha centenas de milhares de veículos. O tipo de veículo (ícone, lugares, tarifas) é o mesmo para milhares deles, então é compartilhado. Cada veículo guarda apenas seu identificador e sua posição.

```csharp
using System;
using System.Collections.Generic;

public sealed class VehicleKind
{
    public string Name { get; }
    public string IconUrl { get; }
    public int Seats { get; }
    public decimal PricePerKm { get; }

    public VehicleKind(string name, string iconUrl, int seats, decimal pricePerKm)
    {
        Name = name;
        IconUrl = iconUrl;
        Seats = seats;
        PricePerKm = pricePerKm;
    }

    // O estado extrínseco (a distância) vem do chamador.
    public decimal Estimate(double distanceKm) => PricePerKm * (decimal)distanceKm;

    public string Describe(string id, double lat, double lon) =>
        $"{id} ({Name}, {Seats} seats) at {lat:F4},{lon:F4} icon={IconUrl}";
}

public class VehicleKinds
{
    private readonly Dictionary<string, VehicleKind> _kinds = new();

    public VehicleKind Get(string name, string iconUrl, int seats, decimal pricePerKm)
    {
        if (!_kinds.TryGetValue(name, out VehicleKind? kind))
        {
            kind = new VehicleKind(name, iconUrl, seats, pricePerKm);
            _kinds[name] = kind;
        }
        return kind;
    }

    public int Count => _kinds.Count;
}

public class Vehicle
{
    public string Id { get; }
    public VehicleKind Kind { get; }
    public double Latitude { get; set; }
    public double Longitude { get; set; }

    public Vehicle(string id, VehicleKind kind, double lat, double lon)
    {
        Id = id;
        Kind = kind;
        Latitude = lat;
        Longitude = lon;
    }

    public string Describe() => Kind.Describe(Id, Latitude, Longitude);
}

public static class Program
{
    public static void Main()
    {
        var kinds = new VehicleKinds();
        var fleet = new List<Vehicle>();
        for (int i = 0; i < 100000; i++)
        {
            VehicleKind kind = i % 3 == 0
                ? kinds.Get("Van", "icons/van.png", 6, 1.9m)
                : kinds.Get("Sedan", "icons/sedan.png", 4, 1.2m);
            fleet.Add(new Vehicle("v" + i, kind, 38.7 + i * 1e-6, -9.1));
        }
        Console.WriteLine($"{fleet.Count} vehicles, {kinds.Count} shared kinds");
        Console.WriteLine(fleet[3].Describe());
        Console.WriteLine(fleet[3].Kind.Estimate(12.5));
    }
}
```

## Variações
- **Onde o estado extrínseco vive**: no objeto cliente (como o `Vehicle` faz), em uma estrutura separada e compacta (por exemplo, intervalos de itens que compartilham um estilo), ou calculado a partir do contexto quando preciso. Quanto mais ele é calculado em vez de guardado, maior a economia.
- **Compartilhar apenas algumas classes**: compartilhe as muitas folhas pequenas e deixe sem compartilhamento os compostos ou os objetos raros. A interface do flyweight permite compartilhar sem obrigar a isso.
- **Tempo de vida do pool**: se o conjunto de flyweights é pequeno e fixo, mantenha-os para sempre. Se pode crescer sem limite, a fábrica precisa de uma política de remoção ou de referências fracas para descartar os que não são usados.
- **Combinado com uma árvore**: folhas compartilhadas em uma hierarquia não podem guardar o seu pai. Passe o pai como estado extrínseco.

## Riscos e alternativas em C#
- Os flyweights precisam ser imutáveis. Um objeto compartilhado mutável muda para todos os usuários ao mesmo tempo. Use propriedades somente leitura, uma classe `sealed` e nenhuma coleção pública.
- Segurança para threads: um `Dictionary` não é seguro para escritas concorrentes. Use `ConcurrentDictionary<TKey, TValue>` com `GetOrAdd`, ou monte o pool na inicialização.
- O C# já compartilha algumas coisas para você: internação de strings (`string.Intern`), valores de enum e instâncias `static readonly` em cache. Um conjunto fechado de tipos pode ser um campo `static readonly` por tipo, sem fábrica.
- Um `struct` para a parte pequena que varia (aqui, um par de coordenadas) reduz ainda mais as alocações, o que pode importar mais do que o compartilhamento. Considere arrays de structs ou pooling (`ArrayPool<T>`) antes de construir uma fábrica de flyweights.
- Não compare objetos compartilhados por igualdade de referência para significar "o mesmo veículo". Use identificadores.

## Padrões relacionados
- [composite.md](composite.md): costuma ser combinado com o flyweight, formando uma árvore com folhas compartilhadas.
- [state.md](../behavioral/state.md): objetos de estado costumam ser mais bem compartilhados como flyweights quando não guardam dados próprios.
- [strategy.md](../behavioral/strategy.md): objetos de estratégia também são bons flyweights, já que guardam comportamento e recebem seus dados como argumentos.

## Verificação
- O número de instâncias da classe compartilhada permanece pequeno conforme os dados crescem (o exemplo imprime dois tipos para 100000 veículos).
- Números de memória ou de alocação de um profiler mostram uma queda real. Sem essa medição, o padrão é um palpite.
- Nada altera um flyweight depois de criado; todo campo é somente leitura.
- Os clientes obtêm flyweights apenas da fábrica, nunca com `new`.
