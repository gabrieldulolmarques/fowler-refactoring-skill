# Remover Código Morto (Remove Dead Code)

Fowler (2018), cap. 8, p. 237. Antes / também: —. Inversa: —.

## Quando usar
Smells: Generalidade Especulativa (Speculative Generality).
- Uma função, classe, campo, parâmetro ou ramo que nada mais alcança. Não custa
  nada em tempo de execução, mas todo leitor ainda precisa descobrir o que ele faz e por que pode ser
  ignorado.
- Código deixado em comentários, ou atrás de uma condição que nunca pode ser verdadeira. O controle de
  versão já guarda o texto antigo, então o comentário não acrescenta nada.
- Não apague código que seja alcançável de formas que uma busca textual não enxerga até que você tenha
  descartado essas possibilidades (veja Notas (C#)). Se tiver dúvida, descubra antes, ou pergunte ao responsável.
- Se quiser lembrar o que foi removido, uma nota curta com o nome da revisão basta.
  Não deixe o próprio código para trás.

## Mecânica
1. Se o código puder ser referenciado de fora de seu próprio corpo (uma função inteira, classe, campo
   ou parâmetro), busque os usos: chamadores, overrides, implementações e qualquer lugar que
   o nomeie como string. Para uma API pública, considere também chamadores fora do repositório.
2. Se algo ainda o usa, ele não é morto. Pare; esta não é a refatoração a aplicar.
3. Apague o código morto. Faça o build.
4. Execute os testes.
5. Faça o commit da remoção isoladamente, para que possa ser revertida de forma limpa se um uso aparecer depois.

## Exemplo
Antes:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class TrackingEvent
{
    public TrackingEvent(DateTime at, string status)
    {
        At = at;
        Status = status;
    }

    public DateTime At { get; }
    public string Status { get; }
}

public class Shipment
{
    public Shipment(string carrier, List<TrackingEvent> events)
    {
        Carrier = carrier;
        Events = events;
    }

    public string Carrier { get; }
    public List<TrackingEvent> Events { get; }
}

public class TrackingService
{
    private const bool UseLegacyCodes = false;

    public string LatestStatus(Shipment shipment)
    {
        string status = shipment.Events.OrderByDescending(e => e.At).First().Status;

        if (UseLegacyCodes)
        {
            status = status.Substring(0, 3).ToUpperInvariant();
        }

        // status = status + " (" + shipment.Carrier + ")";
        return status.Trim();
    }

    private string ToLegacyCode(string status) => status.Substring(0, 3).ToUpperInvariant();
}
```

Depois (uma busca não encontrou chamadores de `ToLegacyCode`, e `UseLegacyCodes` é uma constante que nunca é verdadeira):

```csharp
using System.Linq;

public class TrackingService
{
    public string LatestStatus(Shipment shipment)
    {
        string status = shipment.Events.OrderByDescending(e => e.At).First().Status;
        return status.Trim();
    }
}
```

O comportamento é o mesmo: o ramo removido nunca executava, o comentário nunca era executado, e o método privado não tinha chamadores.

## Notas (C#)
- Código sem chamadores estáticos ainda pode ser alcançado por reflexão, injeção de dependência ou serialização. Antes de apagar um tipo ou membro que parece não usado, verifique: tipos registrados ou resolvidos por um contêiner (inclusive por varredura de assemblies), membros descobertos por reflexão ou por convenção de nome, propriedades lidas ou gravadas por um serializador ou ORM, manipuladores de eventos ligados pelo nome, e membros usados apenas em arquivos de configuração ou views.
- Um membro `public` ou `protected` de uma biblioteca pode ser usado por projetos que você não enxerga. Trate-o como morto só se conhecer todos os consumidores.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
