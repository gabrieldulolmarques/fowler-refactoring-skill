# Mudar Valor para Referência (Change Value to Reference)

Fowler (2018), cap. 9, p. 256. Antes / também: —. Inversa: Mudar Referência para Valor (Change Reference to Value)
([change-reference-to-value.md](change-reference-to-value.md)).

## Quando usar
- Vários objetos hospedeiros (faturas, pedidos) guardam cada um a sua própria cópia da mesma entidade lógica
  (uma conta, um cliente), construída com `new` a partir do mesmo identificador.
- A entidade é atualizada ou enriquecida ao longo do tempo, então toda cópia precisa ser encontrada e alterada. Uma cópia
  esquecida deixa os dados inconsistentes.
- A entidade tem identidade real: dois objetos com o mesmo id são a mesma coisa, não apenas
  valores iguais.

Não vale a pena quando a entidade nunca é atualizada: as cópias são então inofensivas, e um valor é mais simples
(sem repositório, sem ciclo de vida para gerenciar). Memória duplicada, por si só, raramente é motivo.

## Mecânica
1. Crie um repositório (ou registro) que guarde uma instância por identificador, se o código ainda não
   tiver um. Reutilize um existente, se houver.
2. Garanta que o código que constrói o objeto hospedeiro tenha o que precisa para localizar a instância
   correta, normalmente o identificador que já está presente na sua entrada.
3. Mude o construtor do hospedeiro (ou o código que o cria) para pedir a instância ao repositório
   em vez de chamar `new`. Compile e teste após cada construtor que você mudar.
4. Decida como o repositório é preenchido: criado no primeiro pedido, ou pré-carregado de modo que um
   id desconhecido seja um erro. Faça o comportamento do hospedeiro corresponder a essa escolha.
5. Se o repositório for global, considere passá-lo como parâmetro do construtor para que o hospedeiro
   não fique acoplado a estado compartilhado.

## Exemplo
Antes: cada leitura cria o seu próprio `Sensor`, então duas leituras do mesmo sensor guardam dois objetos separados.

```csharp
public class Sensor
{
    public Sensor(string id) { Id = id; }
    public string Id { get; }
    public double AlarmThreshold { get; set; }
}

public class Reading
{
    public Reading(double value, string sensorId)
    {
        Value = value;
        Sensor = new Sensor(sensorId);
    }

    public double Value { get; }
    public Sensor Sensor { get; }
}
```

Alterar o limite de alarme por meio de uma leitura não afeta a outra.

Depois: um registro entrega um único `Sensor` por id, e `Reading` o usa.

```csharp
using System.Collections.Generic;

public class SensorRegistry
{
    private readonly Dictionary<string, Sensor> _sensors = new();

    public Sensor GetOrRegister(string id)
    {
        if (!_sensors.TryGetValue(id, out var sensor))
        {
            sensor = new Sensor(id);
            _sensors[id] = sensor;
        }
        return sensor;
    }

    public Sensor? Find(string id) =>
        _sensors.TryGetValue(id, out var sensor) ? sensor : null;
}

public class Reading
{
    public Reading(double value, string sensorId, SensorRegistry sensors)
    {
        Value = value;
        Sensor = sensors.GetOrRegister(sensorId);
    }

    public double Value { get; }
    public Sensor Sensor { get; }
}
```

Agora `a.Sensor` e `b.Sensor` são o mesmo objeto para o mesmo id, então uma mudança feita por uma leitura é vista por todas. Aqui o registro é passado como parâmetro, em vez de ser lido de uma variável global.

## Notas (C#)
- Um repositório ou registro que entrega a instância compartilhada é o formato usual: um dicionário indexado por id, dentro de uma pequena classe.
- Se o repositório for compartilhado entre threads, use uma estrutura thread-safe (por exemplo, `ConcurrentDictionary.GetOrAdd`) para que dois chamadores não criem duas instâncias para um mesmo id.
- A igualdade por referência é o padrão de uma classe, e é o que se quer aqui: não adicione igualdade por valor à entidade compartilhada.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Adicione um teste de que duas instâncias criadas com o mesmo id retornam a mesma instância (`Assert.Same`), e de que uma mudança feita por uma é visível pela outra.
