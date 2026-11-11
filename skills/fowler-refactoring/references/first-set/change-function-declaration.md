# Mudar Declaração de Função (Change Function Declaration)

Fowler (2018), cap. 6, p. 124. Antes / também: Rename Function, Change Signature; antes Rename Method, Add Parameter, Remove Parameter. Inversa: —.

## Quando usar
Smells: Nome Misterioso (Mysterious Name), Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces), Generalidade Especulativa (Speculative Generality) (parâmetros não usados), Comentários (Comments) (um comentário que explica a função costuma ser um nome melhor).

- O nome não diz ao leitor o que a função faz. Renomeie assim que souber um nome melhor; um bom truque é escrever um comentário descrevendo a finalidade e transformá-lo no nome.
- Um parâmetro prende a função a um tipo de que ela não precisa de fato (passe o valor, não o objeto inteiro), para que possa ser reutilizada em outro lugar e o acoplamento diminua.
- O caso oposto: uma função precisa de mais de um valor de um objeto, e passar o objeto mantém os chamadores estáveis quando a lógica crescer.
- Um parâmetro não é usado, ou é preciso um novo.

Não existe uma escolha de parâmetros permanentemente certa; a declaração deve acompanhar o seu entendimento atual, então espere mudá-la de novo.

## Mecânica
Escolha uma de duas rotas. Use a simples quando puder alterar a declaração e todos os chamadores de uma vez. Use a de migração quando houver muitos chamadores, alguns forem difíceis de alcançar, a função for polimórfica, a mudança for complexa, ou for uma API publicada.

Mude uma coisa de cada vez: se precisar renomear e adicionar um parâmetro, faça a renomeação, teste, depois o parâmetro, teste.

**Rota simples**
1. Se for remover um parâmetro, confirme que o corpo não o usa mais.
2. Mude a declaração para o novo nome ou lista de parâmetros.
3. Encontre toda referência à declaração antiga e atualize-a.
4. Compile e teste. Se der errado, reverta e use a rota de migração.

**Rota de migração**
1. Se necessário, remodele o corpo para que o próximo passo fique fácil (por exemplo, Extrair Variável (Extract Variable) no valor que virará o novo parâmetro, [extract-variable.md](extract-variable.md)).
2. Aplique Extrair Função (Extract Function) ([extract-function.md](extract-function.md)) ao corpo inteiro para criar a nova função. Enquanto as duas funções existirem, a nova precisa de um nome provisório único e fácil de buscar; você o trocará pelo nome final (possivelmente o antigo) no fim.
3. Se a nova função precisar de parâmetros extras, adicione-os com a rota simples.
4. Teste.
5. Aplique Internalizar Função (Inline Function) ([inline-function.md](inline-function.md)) à função antiga, o que move os chamadores para a nova, um de cada vez se quiser, testando a cada passo.
6. Se usou um nome provisório, renomeie-o para o nome final com a rota simples.
7. Teste.

Polimorfismo: cada vínculo que os chamadores podem alcançar precisa da função de encaminhamento. Dentro de uma hierarquia, um encaminhador no tipo base basta; para implementações não relacionadas, adicione um em cada.

API publicada: pare depois de criar a nova função, marque a antiga como obsoleta e mantenha-a encaminhando para a nova até que os clientes tenham migrado; apague-a só quando tiver confiança (ou nunca, se não conseguir alcançá-los).

## Exemplo
Objetivo: `Overdue(Invoice)` deve receber apenas a data de vencimento, para também funcionar com qualquer coisa que tenha uma data de vencimento. Rota de migração, com um nome provisório.

Antes:

```csharp
using System;

public class Invoice
{
    public DateTime DueDate { get; init; }
}

public static class Billing
{
    public static bool Overdue(Invoice invoice) =>
        invoice.DueDate < DateTime.Today;
}

// chamador
// var late = invoices.Where(i => Billing.Overdue(i));
```

Passo 1, extraia o corpo para uma nova função com um nome provisório e o parâmetro desejado:

```csharp
public static bool Overdue(Invoice invoice) =>
    Overdue_new(invoice.DueDate);

public static bool Overdue_new(DateTime dueDate) =>
    dueDate < DateTime.Today;
```

Passo 2, internalize `Overdue` em cada chamador (teste após cada um) e depois apague-a:

```csharp
// var late = invoices.Where(i => Billing.Overdue_new(i.DueDate));
```

Passo 3, renomeie `Overdue_new` de volta para `Overdue`:

```csharp
public static bool Overdue(DateTime dueDate) =>
    dueDate < DateTime.Today;

// var late = invoices.Where(i => Billing.Overdue(i.DueDate));
```

Mesmo comportamento o tempo todo; o build continua verde após cada passo.

## Notas de C#
- O compilador encontra os chamadores diretos, mas não reflexão, buscas baseadas em string (exceto `nameof`) nem nomes serializados; procure por eles separadamente.
- Em uma API pública, mantenha a assinatura antiga como um encaminhador `[Obsolete]` para a nova durante a migração.
- Alterar um `override`, um membro `virtual` ou um membro de interface afeta todas as implementações; atualize-as juntas ou encaminhe a partir de cada uma.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
