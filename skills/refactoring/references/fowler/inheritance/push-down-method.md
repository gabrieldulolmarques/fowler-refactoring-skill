# Descer Método (Push Down Method)

Fowler (2018), cap. 12, p. 359. Nome anterior / outro nome: —. Inversa: Subir Método (Pull Up Method)
([pull-up-method.md](pull-up-method.md)).

## Quando usar
Smell: Herança Recusada (Refused Bequest). Um método definido em uma classe base é relevante para apenas uma subclasse,
ou para uma pequena parte delas. Deixá-lo na classe base sugere que toda subclasse o suporta
e torna a hierarquia mais difícil de ler. Descê-lo coloca o comportamento onde ele pertence.

Pré-condição: o código que chama o método já deve ter uma referência tipada como essa
subclasse específica. Se os chamadores usam o tipo base e contam com o método disponível em todas as
subclasses, descê-lo os quebra. Nesse caso, mantenha-o na classe base e use
Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism) ([replace-conditional-with-polymorphism.md](../conditional-logic/replace-conditional-with-polymorphism.md)), com uma
implementação padrão neutra na classe base.

## Mecânica
1. Encontre todo chamador do método e confirme que cada um funciona com o tipo da subclasse específica
   (ou pode ser mudado para isso).
2. Copie o método para cada subclasse que o precisa.
3. Remova o método da superclasse.
4. Compile e rode os testes. Corrija qualquer chamador que o compilador apontar dando a ele o tipo da subclasse.
5. Se uma subclasse que não precisa do método ainda acabar com uma cópia (ou uma sobrescrita),
   remova-a ali.
6. Compile e rode os testes de novo.

## Exemplo
Antes: `Subscriber` oferece uma cota de downloads, mas apenas assinantes premium podem baixar.

```csharp
public abstract class Subscriber
{
    public string Name { get; set; } = "";

    public int RemainingDownloads(int used)
    {
        return used >= 50 ? 0 : 50 - used;
    }
}

public class PremiumSubscriber : Subscriber { }

public class FreeSubscriber : Subscriber { }

public class OfflineLibrary
{
    public bool CanDownload(PremiumSubscriber subscriber, int used)
    {
        return subscriber.RemainingDownloads(used) > 0;
    }
}
```

Depois: o método vive apenas em `PremiumSubscriber`. `OfflineLibrary` já usava esse tipo, então não
precisa de mudança.

```csharp
public abstract class Subscriber
{
    public string Name { get; set; } = "";
}

public class PremiumSubscriber : Subscriber
{
    public int RemainingDownloads(int used)
    {
        return used >= 50 ? 0 : 50 - used;
    }
}

public class FreeSubscriber : Subscriber { }

public class OfflineLibrary
{
    public bool CanDownload(PremiumSubscriber subscriber, int used)
    {
        return subscriber.RemainingDownloads(used) > 0;
    }
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
