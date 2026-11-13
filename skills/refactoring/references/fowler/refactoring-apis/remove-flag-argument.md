# Remover Argumento de Flag (Remove Flag Argument)

Fowler (2018), cap. 11, p. 314. Antes / também: antes Replace Parameter with Explicit Methods. Inversa: —.

## Quando usar
Smells: Lista Longa de Parâmetros (Long Parameter List).

Um argumento de flag é um parâmetro que o chamador define como um literal (`true`, um membro de enum, uma string) apenas para dizer ao método qual ramo executar. O ponto de chamada então não diz nada sobre o que o valor significa, e a lista de métodos não mostra quais variações existem.

É um argumento de flag somente quando as duas condições valem:
- o chamador passa uma constante que apenas escolhe um ramo, não um valor que se origina em outro lugar do programa;
- o método usa o parâmetro apenas para escolher um caminho, não para repassar ou armazenar.

Não mude chamadores que passam valores calculados. Se alguns chamadores passam literais e outros passam dados, adicione os métodos explícitos, migre apenas os chamadores de literais e mantenha o método original para os chamadores de dados.

Com várias flags independentes, um método por combinação é impraticável, então manter as flags pode ser razoável. Trate-as como um sinal para dividir o método em métodos menores e combináveis.

## Mecânica
1. Crie um método explícito para cada valor do parâmetro, nomeado pelo que aquele valor significa.
   - Se o método original já despacha pelo parâmetro no seu nível mais externo, aplique [decompose-conditional.md](../conditional-logic/decompose-conditional.md): cada ramo vira o corpo de um método explícito, e o original apenas os chama.
   - Se o parâmetro estiver entrelaçado pelo corpo, faça de cada método explícito um invólucro fino que chama o original com um valor fixo.
2. Compile e teste.
3. Substitua cada chamador que passa um literal por uma chamada ao método explícito correspondente. Compile e teste após cada chamador (ou grupo pequeno).
4. Quando nenhum chamador usar mais o parâmetro, apague o método original. Se ele permanecer como alvo dos invólucros, reduza a sua visibilidade ou renomeie-o para sinalizar "interno" (por exemplo, com o sufixo `Core` ou `Impl`).
5. Compile e teste.

## Exemplo
Antes:

```csharp
using System.IO;
using System.IO.Compression;
using System.Text;

public record Report(string Title, string Body);

public static class Exporter
{
    public static byte[] Export(Report report, bool compressed)
    {
        var raw = Encoding.UTF8.GetBytes(report.Title + "\n" + report.Body);
        if (!compressed) return raw;

        using var output = new MemoryStream();
        using (var gzip = new GZipStream(output, CompressionLevel.Optimal))
        {
            gzip.Write(raw);
        }
        return output.ToArray();
    }
}
```

Chamadores (um fragmento separado, por exemplo instruções de nível superior em outro arquivo):

```csharp
var report = new Report("Q3", "Totais...");
var plain = Exporter.Export(report, false);
var packed = Exporter.Export(report, true);
```

Depois:

```csharp
public static class Exporter
{
    public static byte[] ExportPlain(Report report)
    {
        return Encoding.UTF8.GetBytes(report.Title + "\n" + report.Body);
    }

    public static byte[] ExportCompressed(Report report)
    {
        var raw = ExportPlain(report);
        using var output = new MemoryStream();
        using (var gzip = new GZipStream(output, CompressionLevel.Optimal))
        {
            gzip.Write(raw);
        }
        return output.ToArray();
    }
}
```

Chamadores:

```csharp
var report = new Report("Q3", "Totais...");
var plain = Exporter.ExportPlain(report);
var packed = Exporter.ExportCompressed(report);
```

Quando a flag é usada em vários lugares do corpo, mantenha o original e adicione invólucros no lugar. No estado final abaixo, o `Export` original foi renomeado para `ExportCore` e tornado privado, o que é possível quando nenhum chamador de literal o usa mais:

```csharp
public static byte[] ExportPlain(Report report) => ExportCore(report, compressed: false);
public static byte[] ExportCompressed(Report report) => ExportCore(report, compressed: true);

private static byte[] ExportCore(Report report, bool compressed)
{
    var title = compressed ? report.Title.ToUpperInvariant() : report.Title;
    var raw = Encoding.UTF8.GetBytes(title + "\n" + report.Body);
    if (!compressed) return raw;

    using var output = new MemoryStream();
    using (var gzip = new GZipStream(output, CompressionLevel.Optimal))
    {
        gzip.Write(raw);
    }
    return output.ToArray();
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Todo chamador de literal agora se lê como o método explícito, e o comportamento para cada valor não mudou.
