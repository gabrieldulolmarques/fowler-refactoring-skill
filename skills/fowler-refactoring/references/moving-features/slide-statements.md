# Deslocar Instruções (Slide Statements)

Fowler (2018), cap. 8, p. 223. Antes / também: formerly Consolidate Duplicate Conditional Fragments. Inversa: —.

## Quando usar
Smells: Código Duplicado (Duplicated Code), Dados Mutáveis (Mutable Data) (e como passo dentro de Função Longa (Long Function)).
- Linhas que tocam os mesmos dados estão separadas por linhas que tocam outra coisa.
- Uma variável é declarada bem acima do seu primeiro uso (declare-a logo antes de ser necessária).
- Você quer extrair um grupo de linhas, mas elas estão intercaladas com outro código. Deslocá-las para junto antes torna a extração possível.
- As mesmas instruções aparecem no início ou no fim de todos os ramos de uma condicional.

Não vale a pena se o deslocamento não puder ser feito com segurança em passos pequenos: faça outra preparação antes (por exemplo, Dividir Variável (Split Variable) em uma variável reutilizada) e volte.

## Mecânica
1. Escolha a posição de destino para o fragmento (a instrução ou o bloco que você vai mover).
2. Verifique se há interferência em cada instrução entre o fragmento e o destino. Desista deste deslocamento se qualquer uma destas condições valer:
   - Subindo: o fragmento passaria pela declaração ou atribuição de algo que ele lê.
   - Descendo: o fragmento passaria por uma instrução que lê algo que o fragmento define ou altera.
   - O fragmento passaria por uma instrução que modifica algo que o fragmento lê ou escreve.
   - O fragmento modifica algo que uma instrução intermediária lê.
   Instruções sem efeitos colaterais podem ser reordenadas livremente. Cuidado com chamadas: só trate uma chamada como livre de efeitos colaterais se você souber que é.
3. Recorte o fragmento e cole-o no destino.
4. Compile e execute os testes.
5. Se um teste falhar, desfaça e tente de novo com um passo menor: desloque por cima de menos instruções ou mova um fragmento menor. Se ainda falhar, o deslocamento talvez ainda não valha a pena.

Deslocando para fora de uma condicional: quando as mesmas instruções terminam (ou começam) todos os ramos e não dependem de qual ramo rodou de um jeito que mude o comportamento, remova-as de cada ramo e ponha uma cópia depois (ou antes) da condicional. Deslocar para dentro de uma condicional é o inverso e repete o fragmento em cada ramo.

## Exemplo
Antes: as linhas do desconto estão misturadas com as do frete, e `shippingCost` é declarada cedo.

```csharp
public decimal Total(Invoice invoice)
{
    decimal shippingCost;
    var customer = invoice.Customer;
    decimal discount = 0m;
    var subtotal = invoice.Lines.Sum(l => l.Quantity * l.UnitPrice);
    shippingCost = invoice.Weight * 0.5m;
    if (customer.IsPremium) discount = subtotal * 0.1m;
    if (subtotal > 500m) shippingCost = 0m;
    return subtotal - discount + shippingCost;
}
```

Depois: cada declaração fica ao lado do seu uso, e as linhas do desconto estão adjacentes, prontas para Extrair Função (Extract Function).

```csharp
public decimal Total(Invoice invoice)
{
    var subtotal = invoice.Lines.Sum(l => l.Quantity * l.UnitPrice);

    var customer = invoice.Customer;
    decimal discount = 0m;
    if (customer.IsPremium) discount = subtotal * 0.1m;

    decimal shippingCost = invoice.Weight * 0.5m;
    if (subtotal > 500m) shippingCost = 0m;

    return subtotal - discount + shippingCost;
}
```

Por que foi seguro: `subtotal` é declarado antes de tudo que o lê, e as linhas do frete leem e escrevem apenas `shippingCost`, `invoice` e `subtotal`, nenhum dos quais as linhas do desconto alteram.

Caso da condicional, antes e depois (mesmo comportamento):

```csharp
// antes
if (account.Balance >= amount)
{
    account.Debit(amount);
    auditLog.Add(account.Id);
}
else
{
    account.Overdraft(amount);
    auditLog.Add(account.Id);
}

// depois
if (account.Balance >= amount)
    account.Debit(amount);
else
    account.Overdraft(amount);
auditLog.Add(account.Id);
```

Isso só é válido porque os ramos não mudam o que `auditLog.Add(account.Id)` observa.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Se a cobertura do código movido for fraca, adicione testes antes: um deslocamento que passa por estado mutável compartilhado é o tipo de mudança que os testes capturam melhor.
