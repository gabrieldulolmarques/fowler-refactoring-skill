# Renomear Campo (Rename Field)

Fowler (2018), cap. 9, p. 244. Antes / também: —. Inversa: —.

## Quando usar
Smell: Nome Misterioso (Mysterious Name). Estruturas de dados carregam a maior parte do significado de um programa, então os nomes dos seus campos
merecem o mesmo cuidado que os nomes de funções. À medida que você aprende o domínio, coloque o melhor
entendimento no nome. A ideia vale para registros simples e para classes: a propriedade
(ou o par getter e setter) que os chamadores veem é o campo, então renomeie-a com o mesmo cuidado.

O custo depende do alcance. Um campo usado em um escopo pequeno pode ser renomeado de uma só vez. Um campo
lido e escrito por toda a base de código precisa do caminho gradual abaixo.

## Mecânica
1. Se o registro só é usado em um escopo pequeno (uma função, uma classe), renomeie todo acesso
   ao campo de uma só vez, rode os testes e pare aqui.
2. Caso contrário, garanta que os dados estejam atrás de acessores. Se for um registro simples que os chamadores tocam
   diretamente, aplique antes Encapsular Registro (Encapsulate Record) ([encapsulate-record.md](../encapsulation/encapsulate-record.md)).
3. Renomeie o campo de apoio privado dentro da classe e corrija os membros internos que o usam.
   Compile e teste. Se o construtor copiava a entrada direto para o campo de apoio, separe
   os dois primeiro para que o nome interno possa mudar sozinho.
4. Se um construtor, fábrica ou inicializador recebe um registro ou objeto de opções indexado pelo nome
   antigo do campo, faça-o aceitar também o novo nome e preferir o novo quando ambos aparecerem. Mova os
   chamadores um a um, testando ao longo do caminho, e então descarte o nome antigo. Use Mudar Declaração de
   Função (Change Function Declaration) ([change-function-declaration.md](../first-set/change-function-declaration.md)) para este passo.
   Com parâmetros posicionais simples não há nada a aceitar duas vezes: renomear o parâmetro
   basta, e apenas os chamadores com argumentos nomeados percebem.
5. Renomeie os acessores (getter e setter) para o novo nome, de novo com Mudar Declaração de
   Função, para que os chamadores migrem em passos pequenos.
6. Compile e teste. Procure usos baseados em string (reflexão, configuração, payloads serializados,
   query strings) que o compilador não enxerga.

Se os dados são imutáveis, você pode pular o encapsulamento: adicione o novo nome com o mesmo valor,
migre os usuários gradualmente e então apague o nome antigo. Nunca mantenha duas cópias de dados mutáveis.

Se os testes quebrarem durante uma renomeação de uma só vez, desfaça e use o caminho gradual.

## Exemplo
Antes: `Device` expõe um campo público chamado `Rev` que na verdade guarda a versão do firmware, e muitos chamadores o usam.

```csharp
using System;

public class Device
{
    public string Rev; // na verdade a versão do firmware
    public int SamplingSeconds;
}

public class Caller
{
    public void Run()
    {
        var device = new Device { Rev = "2.4.1", SamplingSeconds = 30 };
        Console.WriteLine(device.Rev);
    }
}
```

Passo 1, encapsule e dê ao campo de suporte um nome próprio. O inicializador de objeto no chamador continua compilando, porque passa pelos setters da propriedade:

```csharp
public class Device
{
    private string _firmwareVersion;
    private int _samplingSeconds;

    public string Rev
    {
        get => _firmwareVersion;
        set => _firmwareVersion = value;
    }

    public int SamplingSeconds
    {
        get => _samplingSeconds;
        set => _samplingSeconds = value;
    }
}
```

Passo 2, renomeie a propriedade e atualize os chamadores. Esta classe não tem construtor, então o passo 4 da mecânica não tem nada a fazer aqui:

```csharp
public class Device
{
    private string _firmwareVersion;
    private int _samplingSeconds;

    public string FirmwareVersion
    {
        get => _firmwareVersion;
        set => _firmwareVersion = value;
    }

    public int SamplingSeconds
    {
        get => _samplingSeconds;
        set => _samplingSeconds = value;
    }
}

public class Caller
{
    public void Run()
    {
        var device = new Device { FirmwareVersion = "2.4.1", SamplingSeconds = 30 };
        Console.WriteLine(device.FirmwareVersion);
    }
}
```

O comportamento não muda; só o nome mudou.

## Notas (C#)
- Um campo serializado ou persistido mantém seu nome no formato só com um atributo de mapeamento (por exemplo `[JsonPropertyName("oldName")]`) ou uma migração. Renomear a propriedade sem um deles muda o JSON, a coluna ou os dados armazenados.
- Transformar um campo público em propriedade muda o próprio membro: consumidores por reflexão e binários quebram, e os serializadores podem tratar os dois de forma diferente.
- O compilador encontra usos diretos, não reflexão, vinculação de dados por string nem chaves de configuração.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
