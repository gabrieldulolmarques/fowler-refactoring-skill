# Flyweight

Gamma et al. (1995), ch. 4, p. 195. Category: object structural.

## Intent
Share objects so that a very large number of small, fine-grained objects becomes affordable. The shared part stays inside the object, and the part that varies is handed in by the caller.

## When it pays off
- All of these hold: the program has a huge number of similar objects, they cost too much memory, most of their state can be moved outside, and after that a few shared objects can stand for many of the old ones.
- The code does not depend on the identity of the objects (two logical objects can be the same instance).
- Benefit: memory falls as sharing rises, most of all when the external data can be computed or stored in a compact structure.
- Liability: callers must supply external state on each call, and there is a lookup or computation cost for it. The code gets harder to follow.
- Skip it when the count is small, when memory is not a measured problem, or when the state cannot be separated. Measure first.

## Participants in C#
- **Flyweight** (`VehicleKind`): the shared object, with only intrinsic state (the same for every user of it). Its operations take extrinsic state as parameters. In C# this is an immutable class, since shared objects must not change.
- **ConcreteFlyweight** (`VehicleKind` itself): the flyweight is a single class here. Several concrete classes behind an interface also work.
- **UnsharedConcreteFlyweight** (not needed in the example): a variant of the interface that is not shared, for example a vehicle with unique state.
- **FlyweightFactory** (`VehicleKinds`): creates flyweights, stores them by key, and returns the existing one when asked again.
- **Client** (`Vehicle`, `Main`): stores or computes the extrinsic state (position, driver, status) and passes it in.

## Example (C#)
A ride-sharing map tracks hundreds of thousands of vehicles. The kind of vehicle (icon, seats, fare rates) is the same for thousands of them, so it is shared. Each vehicle keeps only its id and position.

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

    // Extrinsic state (the distance) comes from the caller.
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

## Variations
- **Where extrinsic state lives**: in the client object (as `Vehicle` does), in a separate compact structure (for example ranges of items that share a style), or computed from context when needed. The more it is computed rather than stored, the bigger the saving.
- **Sharing only some classes**: share the many small leaves, and leave composite or rare objects unshared. The flyweight interface allows sharing without forcing it.
- **Lifetime of the pool**: if the set of flyweights is small and fixed, keep them forever. If it can grow without bound, the factory needs an eviction policy or weak references to let unused ones go.
- **Combined with a tree**: shared leaves in a hierarchy cannot store their parent. Pass the parent in as extrinsic state.

## Risks and C# alternatives
- Flyweights must be immutable. A mutable shared object changes for every user at once. Use get-only properties, a sealed class and no public collections.
- Thread safety: a `Dictionary` is not safe for concurrent writes. Use `ConcurrentDictionary<TKey, TValue>` with `GetOrAdd`, or build the pool at startup.
- C# already shares some things for you: string interning (`string.Intern`), enum values, and cached `static readonly` instances. A closed set of kinds can be a `static readonly` field per kind, with no factory.
- A `struct` for the small varying part (here a coordinate pair) cuts allocations further, which can matter more than sharing. Consider arrays of structs or pooling (`ArrayPool<T>`) before building a flyweight factory.
- Do not compare shared objects with reference equality to mean "the same vehicle". Use ids.

## Related patterns
- [composite.md](composite.md): often combined with flyweight, giving a tree with shared leaves.
- [state.md](../behavioral/state.md): state objects are usually best shared as flyweights when they hold no data of their own.
- [strategy.md](../behavioral/strategy.md): strategy objects are also good flyweights, since they hold behavior and take their data as arguments.

## Verification
- The number of instances of the shared class stays small as the data grows (the example prints two kinds for 100000 vehicles).
- Memory or allocation numbers from a profiler show a real drop. Without that measurement, the pattern is a guess.
- Nothing mutates a flyweight after it is created; every field is get-only.
- Clients get flyweights only from the factory, never with `new`.
