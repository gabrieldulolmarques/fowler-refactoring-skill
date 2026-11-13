# Princípios de design e como usar um padrão

Gamma et al. (1995), cap. 1 e cap. 6, §6.1. Paráfrase. O catálogo de padrões está em
[catalog.md](catalog.md).

## O que é um padrão (§1.1, §1.3)

Um padrão de design nomeia um problema de design recorrente e o núcleo de uma solução que pode ser
reutilizado sem nunca ser implementado da mesma forma duas vezes. Cada padrão tem quatro partes
essenciais:

- um **nome**, que passa a fazer parte do vocabulário da equipe;
- o **problema**, que diz quando aplicá-lo;
- a **solução**, que descreve os elementos, suas responsabilidades e colaborações, como um modelo e não como um design concreto;
- as **consequências**, os benefícios e custos de aplicá-lo, que decidem se vale a pena.

Os arquivos de padrão nesta pasta seguem essa ordem: intenção, quando compensa, participantes, exemplo,
variações, riscos.

## Princípios de design orientado a objetos reutilizável (§1.6)

- **Programe para uma interface, não para uma implementação** (pp. 16-18). Declare variáveis, parâmetros e
  campos com interfaces ou tipos abstratos. Assim, os clientes não dependem de classes concretas, apenas das
  operações que usam, e qualquer objeto que implemente a interface pode participar. Os padrões criacionais
  existem em grande parte para que classes concretas sejam nomeadas no menor número possível de lugares.
- **Prefira composição de objetos a herança de classes** (pp. 18-20). Herança é reúso decidido em tempo de
  compilação, e expõe os detalhes internos da superclasse à subclasse, então uma mudança na superclasse pode quebrar as
  subclasses. A composição é decidida em tempo de execução, por meio de interfaces, mantém cada classe
  encapsulada e focada, e permite mudar o comportamento plugando outro objeto. Use herança onde ela for o
  encaixe mais simples, mas não a escolha primeiro.
- **Delegação** (pp. 20-21). Um objeto repassa parte de uma requisição a outro objeto que ele contém, em vez de
  herdar o comportamento. Isso torna a composição tão poderosa quanto a herança (State, Strategy e Visitor
  dependem dela), ao custo de designs mais dinâmicos e mais difíceis de acompanhar.
- **Herança versus tipos parametrizados** (pp. 21-22). Os genéricos são uma terceira forma de variar o comportamento,
  pelos tipos com que uma operação trabalha, fixados em tempo de compilação.
- **A estrutura em tempo de execução não é a estrutura do código** (pp. 22-23). As classes mostram o que os
  objetos podem conter ou conhecer (agregação, conhecimento mútuo ou acquaintance); a rede real de objetos em tempo de execução só é
  visível quando o programa roda. Muitos padrões, como Observer, Composite e Chain of Responsibility, são mais
  fáceis de entender pela estrutura em tempo de execução.
- **Projetar para a mudança** (p. 24). A maior parte dos reprojetos tem algumas causas conhecidas: nomear classes
  concretas, codificar requisições de forma fixa, dependência de plataforma, expor representações, dependência de
  algoritmo, acoplamento forte, estender apenas por subclasses e classes que não podem ser alteradas. Cada padrão
  permite que um aspecto varie de forma independente; [catalog.md](catalog.md) relaciona cada causa aos padrões
  que a evitam.
- **Aplicações, toolkits e frameworks** (pp. 25-27). O código de aplicação valoriza o reúso interno e a facilidade de
  alteração; bibliotecas e toolkits devem evitar suposições sobre seus usuários; frameworks fixam a arquitetura
  e chamam o seu código, então seus padrões devem ser escolhidos com mais cuidado.

## Como escolher um padrão (§1.7, p. 28)

O livro apresenta seis abordagens alternativas para encontrar o padrão de um problema. Elas não são
passos; use a que servir à situação, ou combine-as.

- **Como os padrões resolvem problemas de design.** O §1.6 do livro trata de encontrar objetos, da
  granularidade dos objetos, da especificação de interfaces e dos demais pontos dessa seção. A lista
  acima resume só os princípios que mais importam para o código daqui; para o resto, consulte o livro.
- **Percorrer as intenções.** Leia as intenções em [catalog.md](catalog.md) e restrinja a lista por
  propósito e escopo (Tabela 1.1, p. 10).
- **Estudar como os padrões se relacionam.** A Figura 1.1 (p. 12) do livro desenha as relações entre os
  padrões; ela não está reproduzida aqui.
- **Estudar padrões de propósito parecido.** A comparação que fecha cada categoria em
  [catalog.md](catalog.md) mostra o que separa padrões semelhantes.
- **Examinar uma causa de reprojeto.** Verifique se o problema corresponde a uma das causas e veja os
  padrões que a evitam ([catalog.md](catalog.md), p. 24).
- **Considerar o que deve ser variável.** O inverso da abordagem anterior: decida o que você quer poder
  mudar sem reprojetar e escolha o padrão que permite variar esse aspecto. Isolar o que varia é a ideia
  por trás de muitos dos padrões.

## Como usar um padrão (§1.8, p. 29)

1. Leia o padrão inteiro uma vez, prestando mais atenção a quando ele compensa e às suas consequências.
2. Estude os participantes e como eles colaboram.
3. Observe o exemplo para ver o padrão em código.
4. Nomeie os participantes de acordo com a aplicação, mantendo uma pista do papel quando ajudar
   (`ShippingStrategy`, `OrderBuilder`).
5. Declare os tipos: interfaces, herança, campos e referências. Identifique as classes existentes que o padrão
   toca e altere-as.
6. Nomeie as operações de acordo com suas responsabilidades, de forma consistente (por exemplo, sempre `Create...`
   para factory methods).
7. Implemente as operações, usando as variações como guia.

**Quando não usar um padrão** (§1.8). Padrões compram flexibilidade com indireção extra, o que pode tornar um
design mais complicado e mais lento. Aplique um padrão somente quando a flexibilidade que ele oferece for de fato
necessária; suas consequências dizem o que ele custa.

## O que esperar dos padrões (§6.1, pp. 351-354)

- **Um vocabulário comum** (p. 352): "use um Observer aqui" diz em três palavras o que levaria um parágrafo, e
  torna os designs mais fáceis de discutir e revisar.
- **Documentação e aprendizado:** nomear os padrões que um sistema usa torna muito mais fácil entendê-lo.
- **Um complemento aos métodos de design:** os padrões mostram como usar bem objetos, herança e polimorfismo, e
  ajudam a passar de um modelo do problema para código funcionando.
- **Um alvo para refatoração** (p. 353): o software cresce em fases, de prototipagem a expansão e consolidação.
  Na fase de consolidação ele é reorganizado, e muitos padrões são as estruturas a que essa reorganização chega.
  Conhecê-los ajuda a ver para onde levar um design, mesmo quando o padrão só fica visível depois que o sistema
  está construído.

## Checklist de verificação (igual para todo padrão)

- O problema que o padrão resolve está presente no código, não é previsto para algum dia.
- Os participantes têm nomes do domínio, e os clientes dependem de interfaces, não das classes concretas que o
  padrão introduziu.
- O design fica mais simples de mudar do jeito que o padrão promete, e a indireção extra vale a pena.
- Compila e os testes passam; o comportamento não muda quando o padrão foi introduzido por refatoração.
