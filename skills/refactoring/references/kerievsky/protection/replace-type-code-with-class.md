# Substituir Código de Tipo por Classe (Replace Type Code with Class)

Kerievsky (2004), cap. 9, p. 286. Padrão: —. Direção: —.

## Quando usar
Smells: Obsessão por Primitivos (Primitive Obsession).

- Um campo guarda uma string ou um int que é atribuído e comparado com uma família fixa de constantes (status de pedido, estado de permissão). Nada impede que uma string com erro de digitação ou um número qualquer seja atribuído, e o objeto pode acabar em um estado do qual nunca consegue sair.
- Dar ao campo uma classe como tipo faz com que toda atribuição e toda comparação passem por um conjunto fechado de constantes, que não pode ser imitado por outros valores.
- Um enum da linguagem não torna isso obsoleto. A classe pode ganhar comportamento depois, e é isso que os próximos passos costumam exigir. O exemplo do próprio livro é o primeiro passo de [replace-state-altering-conditionals-with-state.md](../simplification/replace-state-altering-conditionals-with-state.md), que se apoia nesta classe e não conseguiria se apoiar em um enum simples.
- Custo: mais código do que um primitivo.
- Relação com Fowler: isto é [replace-primitive-with-object.md](../../fowler/encapsulation/replace-primitive-with-object.md) aplicado a um código de tipo. A versão de Fowler envolve qualquer primitivo; a de Kerievsky trata especificamente de uma família fechada de constantes.

## Mecânica
Siga [replace-primitive-with-object.md](../../fowler/encapsulation/replace-primitive-with-object.md). O que Kerievsky acrescenta ou ordena de outro modo:

1. Encapsule primeiro o campo sem segurança de tipo com Encapsular Variável (Encapsulate Variable) ([encapsulate-variable.md](../../fowler/first-set/encapsulate-variable.md)). Compile e teste.
2. Crie a nova classe, com nome derivado do tipo de valor que guarda, ainda sem construtor público.
3. Para cada constante com a qual o campo é atribuído ou comparado, adicione uma instância estática da nova classe. Compile. Se a família precisar continuar fechada, torne o construtor privado e a classe sealed.
4. Adicione um campo com segurança de tipo da nova classe ao lado do campo antigo, e espelhe cada atribuição ao campo antigo com uma atribuição ao novo. Compile.
5. Faça a nova classe capaz de produzir o valor antigo (um nome ou código), e faça o getter antigo ler do novo campo. Compile e teste.
6. Apague o campo antigo, seu setter e suas atribuições. Compile e teste.
7. Substitua cada uso das constantes antigas pelas novas, altere o tipo de retorno do getter para a nova classe, e corrija os chamadores. Compare com `==` nas instâncias compartilhadas, ou dê à classe igualdade se ela puder ser criada de fora. Compile e teste.
8. Apague as constantes antigas.

O exemplo está no arquivo de Fowler; o formato do resultado é a classe sealed com instâncias estáticas mostrada lá, por exemplo uma `OrderStatus` sealed com `Pending`, `Paid` e `Shipped`.

## Notas (C#)
- Um `enum` do C# é apenas um inteiro por baixo: `(OrderStatus)42` compila e executa. Se o conjunto precisar ser fechado e o tipo precisar carregar comportamento, use uma classe sealed com construtor privado. Se nenhuma dessas coisas importar, um enum está bom e esta refatoração não é necessária.
- Com construtor privado as instâncias são únicas, então `==` sobre referências basta. Sem ele, sobrescreva `Equals` e `GetHashCode` (ou use um record).
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhuma constante `string` ou `int` da família permanece, e não há forma pública de criar um valor fora da família se ela for feita para ser fechada.
