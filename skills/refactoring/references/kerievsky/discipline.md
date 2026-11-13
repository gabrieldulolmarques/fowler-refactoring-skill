# Disciplina de refatoração para padrões

Kerievsky (2004), cap. 1-3. Parafraseado.

## O objetivo é um design melhor, não um padrão

Refatorar para um padrão tem as mesmas motivações de qualquer refatoração: remover duplicação, simplificar o que é complicado e fazer o código dizer o que significa (cap. 1). Um padrão é um destino que pode servir a esses objetivos, nunca um objetivo em si. Depois de refatorar até um padrão ou rumo a um padrão, verifique se o design realmente melhorou; se não melhorou, desfaça a mudança ou siga por outro caminho (cap. 3, pp. 29-31).

## Excesso de engenharia e falta de engenharia

- **Excesso de engenharia** (cap. 1, pp. 1-2): código mais flexível ou sofisticado do que as necessidades de hoje, feito para um futuro que pode não chegar. Raramente é removido, deixa a base de código maior do que precisa e custa tempo de todos para entendê-lo.
- **Falta de engenharia** (cap. 1, pp. 3-4): código mal projetado, escrito às pressas, sem tempo para refatorar. Cada versão fica mais lenta que a anterior, até que uma reescrita pareça a única saída.
- Evite os dois evoluindo o design: adicione um padrão quando o código pedir, por meio de refatoração, e não antecipadamente "por precaução" (cap. 1, p. 8).

## *Patterns happy* (encantado por padrões)

Ser *patterns happy* (encantado por padrões) é usar padrões porque se gosta deles, e não porque o código precisa (cap. 3, p. 24). O resultado é código carregado de padrões, mais difícil de ler do que um condicional simples ou uma classe comum. Antes de aplicar uma refatoração para um padrão, pergunte se uma mudança mais simples remove o smell. Quando um padrão deixa de compensar, refatore para longe dele.

## Desenvolvimento guiado por testes e refatoração contínua

Escreva um teste que falha, faça-o passar do jeito mais simples e depois refatore (red, green, refactor; cap. 1, pp. 4-6). Refatore continuamente, aos poucos, em vez de guardar a refatoração para depois (cap. 1, p. 5). Os padrões então aparecem quando a duplicação ou a complexidade os exigem.

## Passos pequenos

Combinar várias refatorações em um passo grande parece mais rápido, mas é mais lento: os testes ficam vermelhos por muito tempo e as correções se acumulam (cap. 2, pp. 14-15). Se os testes estiverem falhando há mais de alguns minutos, o passo é grande demais: volte ao último estado verde e dê um passo menor.

## Refatorações compostas e guiadas por testes

- Quase toda refatoração para um padrão é **composta**: uma sequência de refatorações de baixo nível (em sua maioria de Fowler), com os testes executados entre cada uma (cap. 2, pp. 17-20). A mecânica do livro dá uma ordem que funciona; você pode aplicar os passos em outra ordem, se achar melhor.
- Uma **refatoração guiada por testes** escreve a substituição com desenvolvimento guiado por testes e depois a troca pelo código antigo, mantendo e reexecutando os testes do código antigo (cap. 2, pp. 17-19). Use-a quando o novo design estiver longe demais do atual para chegar apenas movendo código, como ao substituir um algoritmo ou ao introduzir um Builder.

## Até, rumo a e longe

- Algumas refatorações só ajudam se você for **até** o padrão: meio Template Method não remove duplicação alguma.
- Outras já melhoram o design no meio do caminho: ir **rumo a** um Decorator ou a um Command pode bastar, e você pode parar assim que o smell sumir.
- Refatorar para **longe** de um padrão é tão legítimo quanto: remova um Singleton ou um Iterator quando o design ficar melhor sem ele.

Cada arquivo de referência indica sua direção (cap. 3, pp. 29-31).

## Muitas formas de implementar um padrão

O diagrama de classes usual de um padrão é um exemplo, não uma especificação (cap. 3, p. 26). Implemente só o que o código precisa, com nomes próprios; um padrão mínimo é o resultado normal de evoluir um design.

## Padrões tornam o código mais complexo?

Código com um padrão parece mais complexo para quem não conhece o padrão (cap. 3). Prefira ensinar o padrão à equipe a evitá-lo, mas, se uma implementação for realmente mais complexa que o problema, simplifique-a ou refatore para longe dela.

## Projetar antecipadamente com padrões só raramente

Projetar com padrões antes de escrever código às vezes se justifica, por exemplo quando um design detalhado precisa ser apresentado antes do início do trabalho e os requisitos são pequenos e fixos (cap. 3, pp. 33-35). Fora isso, evolua o sistema e refatore até, rumo a ou para longe de padrões, conforme necessário.

## Dívida de design

A dívida de design se acumula sempre que a duplicação não é removida, o código não é simplificado ou a intenção não fica clara (cap. 2, pp. 15-16). Como a dívida financeira, ela cresce se não for quitada; pagá-la aos poucos, por meio da refatoração contínua, mantém o código fácil de mudar.

## Checklist de verificação (igual para toda refatoração para um padrão)

- Compila e os testes passam após cada passo; um commit por refatoração.
- O smell que motivou a refatoração desapareceu.
- O design está mais simples do que antes para quem conhece o padrão; se não estiver, desfaça a mudança ou siga por outro caminho.
