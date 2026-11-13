# Encapsular Registro (Encapsulate Record)

Fowler (2018), cap. 7, p. 162. Nome anterior / outro nome: Replace Record with Data Class.
Inversa: —.

## Quando usar
Smells: Classe de Dados (Data Class).

- Dados mutáveis vivem em um registro simples e muitos lugares leem e escrevem seus campos diretamente.
  Uma classe pode expor um valor derivado pela mesma propriedade que um valor armazenado, e manter
  um alias obsoleto enquanto os chamadores migram para um novo nome.
- O registro é um mapa livre com campos implícitos: para saber se ele contém
  `price`/`currency` ou apenas `amount`, você precisa ler todos os lugares que o constroem ou usam.
  Isso custa mais conforme o escopo cresce. Uma classe torna os campos explícitos.
- Os dados são uma estrutura aninhada de listas e mapas, muitas vezes vinda de JSON ou XML. Ela também pode ser
  encapsulada, o que protege você de mudanças de formato e de atualizações difíceis de
  rastrear.

Desnecessário para um valor imutável usado em um escopo pequeno: ali, adicionar ou copiar um campo
é barato e um registro simples serve.

## Mecânica
1. Aplique Encapsular Variável (Encapsulate Variable) ([encapsulate-variable.md](../first-set/encapsulate-variable.md)) à variável que guarda o
   registro. Dê ao getter um nome temporário e fácil de buscar com grep, como `GetRawProfile`; ele é
   removido no passo 5.
2. Introduza uma classe pequena que guarde o registro e armazene uma instância dela na variável.
   Dê a ela uma propriedade que exponha o registro subjacente (uma propriedade `RawData` no exemplo
   em C#) e aponte as funções de encapsulamento para essa propriedade. Compile e teste.
3. Adicione novas funções que retornem a instância da classe em vez do registro bruto.
4. Mova os chamadores um de cada vez da função do registro bruto para a função que retorna o
   objeto. Em cada uso, chame um acessor no objeto, criando-o se ainda não existir
   (um setter para uma escrita, um getter para uma leitura; para um acesso profundo, aplique antes Extrair
   Função (Extract Function) e Mover Função (Move Function) para que o acesso aconteça dentro da classe). Compile e teste
   após cada chamador.
   - Para um registro aninhado, converta primeiro os escritores: reunir todas as atualizações em um só lugar é
     a parte mais valiosa. Os leitores podem então receber uma cópia ou uma visão somente leitura.
   - Para verificar que nenhum escritor foi esquecido, faça temporariamente o acessor bruto retornar uma cópia profunda
     (ou uma cópia congelada): um teste falha se algum código ainda atualizar o original.
5. Quando nenhum chamador os usar mais, apague o acessor bruto e as funções fáceis de buscar.
   Compile e teste.
6. Opcionalmente, desmembre o registro encapsulado em campos individuais da classe. Isso quebra o
   vínculo com os dados de entrada, de modo que uma referência perdida em outro lugar não possa contornar a classe. Se você
   mantiver o registro dentro, copie-o ao atribuí-lo.
7. Se um campo for ele mesmo uma estrutura, aplique Encapsular Registro ou Encapsular Coleção (Encapsulate Collection)
   ([encapsulate-collection.md](encapsulate-collection.md)) a ele, recursivamente, quando o controle valer o esforço.

Para leitores de uma estrutura aninhada grande há três opções: extrair cada leitura para um
método da classe (uma API explícita, mas possivelmente com muitos casos especiais); entregar uma cópia dos
dados (simples, mas custa tempo e surpreende chamadores que esperam modificar o original, então
meça primeiro); ou recorrer a classes menores (mais controle, mais trabalho). Uma mistura serve.

## Exemplo

Antes: um perfil de cobrança compartilhado, guardado em um dicionário.

```csharp
using System.Collections.Generic;

public static class Billing
{
    public static Dictionary<string, string> Profile =
        new() { ["plan"] = "Team", ["billingEmail"] = "finance@example.com" };
}

public static class InvoiceHeader
{
    public static string Render() => $"Plan: {Billing.Profile["plan"]}";
}

public static class ProfileForm
{
    public static void ChangeEmail(string email) => Billing.Profile["billingEmail"] = email;
}
```

Estado intermediário (passos 1 a 3): classe invólucro (wrapper), acessor bruto e acessor de objeto. O passo 1 também
faz `InvoiceHeader` e `ProfileForm` chamarem o acessor bruto.

```csharp
using System.Collections.Generic;

public class BillingProfile
{
    private readonly Dictionary<string, string> _data;
    public BillingProfile(Dictionary<string, string> data) => _data = data;
    public Dictionary<string, string> RawData => _data;
}

public static class Billing
{
    private static BillingProfile _profile = new(
        new() { ["plan"] = "Team", ["billingEmail"] = "finance@example.com" });

    public static Dictionary<string, string> GetRawProfile() => _profile.RawData;
    public static BillingProfile GetProfile() => _profile;
}

public static class InvoiceHeader
{
    public static string Render() => $"Plan: {Billing.GetRawProfile()["plan"]}";
}

public static class ProfileForm
{
    public static void ChangeEmail(string email) => Billing.GetRawProfile()["billingEmail"] = email;
}
```

Depois (passos 4 a 6): os chamadores usam o objeto, os acessores brutos somem, e o dicionário é
convertido em propriedades.

```csharp
using System.Collections.Generic;

public class BillingProfile
{
    public BillingProfile(Dictionary<string, string> data)
    {
        Plan = data["plan"];
        BillingEmail = data["billingEmail"];
    }

    public string Plan { get; set; }
    public string BillingEmail { get; set; }
}

public static class Billing
{
    private static BillingProfile _profile = new(
        new() { ["plan"] = "Team", ["billingEmail"] = "finance@example.com" });

    public static BillingProfile GetProfile() => _profile;
}

public static class InvoiceHeader
{
    public static string Render() => $"Plan: {Billing.GetProfile().Plan}";
}

public static class ProfileForm
{
    public static void ChangeEmail(string email) => Billing.GetProfile().BillingEmail = email;
}
```

## Notas (C#)
- Dados em dicionário, tupla, tipo anônimo ou `dynamic` viram uma classe ou um `record` com propriedades.
  Tipos anônimos não atravessam fronteiras de método como valor tipado, o que é um bom motivo para convertê-los.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Depois do passo 5, faça uma busca pelos nomes dos acessores brutos e pela indexação direta da variável antiga.
  Espere zero ocorrências.
