# Mover Função (Move Function)

Fowler (2018), cap. 8, p. 198. Antes / também: Move Method. Inversa: —.

## Quando usar
Smells: Inveja de Recursos (Feature Envy), Alteração Divergente (Divergent Change), Cirurgia com Espingarda (Shotgun Surgery), Campo Temporário (Temporary Field), Cadeias de Mensagens (Message Chains), Troca de Informações Privilegiadas (Insider Trading), Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces), Classe de Dados (Data Class).

- A função lê ou escreve membros de outro tipo mais do que membros do tipo em que vive.
- Seus chamadores, ou o lugar de onde você precisa chamá-la em seguida, estão em outro contexto.
- Um auxiliar aninhado dentro de outra função (ou enterrado em uma seção privada) tem valor por si só.
- Um comportamento está prestes a variar conforme o outro tipo (por exemplo, por tipo de cliente), então pertence a ele.

Quando a escolha do novo lar não é clara, ela costuma importar pouco. Coloque a função no melhor candidato e mova-a de novo quando souber mais. Se nenhum contexto existente servir para um grupo de funções, crie um primeiro (Combinar Funções em Classe (Combine Functions into Class), Extrair Classe (Extract Class)).

## Mecânica
1. Liste tudo o que a função usa em seu contexto atual: outras funções, campos, constantes. Decida se algum deles deve ser movido também. Se uma função chamada deve ser movida, mova-a primeiro; comece o grupo pela função que menos depende das outras. Quando alguns auxiliares são chamados só por essa função e por nenhum outro lugar, pode ser mais simples internalizá-los, mover a função única e extrair os auxiliares de novo quando ela estiver em seu novo lugar.
2. Verifique se a função é polimórfica (virtual, override, implementação de interface ou membro de uma hierarquia). Se for, leve em conta as outras declarações antes de mover.
3. Copie a função para o contexto de destino, com um nome temporário se ajudar a distinguir as duas. Ajuste-a para se encaixar: substitua os usos de membros da origem pelos membros do próprio destino e passe como parâmetros o que ainda for necessário da origem (um valor ou o próprio objeto de origem).
4. Compile. Corrija símbolos indefinidos ou inacessíveis na cópia (visibilidade, parâmetros faltando, auxiliares faltando). O original está intocado, então o comportamento não muda.
5. Decida como o contexto de origem alcança o destino: um campo, uma propriedade, um parâmetro ou uma busca.
6. Transforme o original em um encaminhador fino: seu corpo vira uma única chamada que entrega o trabalho à cópia movida.
7. Compile e execute os testes. Esse é o passo que prova que a função movida funciona em seu novo lar.
8. Decida se mantém a função delegadora. Se os chamadores puderem alcançar o destino diretamente, internalize a função de origem ([inline-function.md](../first-set/inline-function.md)) e atualize os chamadores; caso contrário, ela pode ficar.
9. Dê à função de destino seu nome final, agora que ela vive em seu novo contexto ([change-function-declaration.md](../first-set/change-function-declaration.md)), e mova quaisquer funções auxiliares que só ela usava.

## Exemplo
Antes: `Delivery` calcula uma sobretaxa a partir de dados que em sua maioria pertencem a `Zone`.

```csharp
public class Zone
{
    public Zone(string name, bool isRemote)
    {
        Name = name;
        IsRemote = isRemote;
    }

    public string Name { get; }
    public bool IsRemote { get; }
}

public class Delivery
{
    public Delivery(Zone zone, decimal baseRate)
    {
        Zone = zone;
        BaseRate = baseRate;
    }

    public Zone Zone { get; }
    public decimal BaseRate { get; }

    public decimal Total => BaseRate + Surcharge();

    public decimal Surcharge()
    {
        if (Zone.IsRemote) return 12m;
        return Zone.Name == "urban" ? 0m : 4m;
    }
}
```

Passos 3 a 7: copie a função para `Zone` (a entrega não é necessária, então não há parâmetro) e depois delegue a partir de `Delivery`.

```csharp
public class Zone
{
    public Zone(string name, bool isRemote)
    {
        Name = name;
        IsRemote = isRemote;
    }

    public string Name { get; }
    public bool IsRemote { get; }

    public decimal Surcharge()
    {
        if (IsRemote) return 12m;
        return Name == "urban" ? 0m : 4m;
    }
}

public class Delivery
{
    public Delivery(Zone zone, decimal baseRate)
    {
        Zone = zone;
        BaseRate = baseRate;
    }

    public Zone Zone { get; }
    public decimal BaseRate { get; }

    public decimal Total => BaseRate + Surcharge();

    public decimal Surcharge() => Zone.Surcharge();
}
```

Passo 8: só `Total` a chama, então internalize a função delegadora.

```csharp
public class Zone
{
    public Zone(string name, bool isRemote)
    {
        Name = name;
        IsRemote = isRemote;
    }

    public string Name { get; }
    public bool IsRemote { get; }

    public decimal Surcharge()
    {
        if (IsRemote) return 12m;
        return Name == "urban" ? 0m : 4m;
    }
}

public class Delivery
{
    public Delivery(Zone zone, decimal baseRate)
    {
        Zone = zone;
        BaseRate = baseRate;
    }

    public Zone Zone { get; }
    public decimal BaseRate { get; }

    public decimal Total => BaseRate + Zone.Surcharge();
}
```

Se a função movida depois precisar de mais dados da entrega (por exemplo, a taxa base para uma sobretaxa percentual), passe a entrega em vez de valores isolados: `Zone.Surcharge(this)`.

## Notas (C#)
- O destino pode ser outra classe, uma classe estática ou um método de extensão. Um método de extensão serve para um tipo que você não pode editar, mas só pode usar membros públicos.
- Mover um método `virtual`, `override` ou que implementa interface muda o contrato para as outras implementações; verifique-as primeiro.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
