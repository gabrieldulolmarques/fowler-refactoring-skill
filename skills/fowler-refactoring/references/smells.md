# Os 24 smells (cheiros de código)

Fowler (2018), cap. 3, pp. 71-84 (a página de cada smell está no título). Os sintomas são parafraseados; as listas de refatorações seguem o texto do capítulo. Cada refatoração tem link para o seu arquivo nesta pasta (`<slug>.md`).

Um smell é uma pista, não um veredito. Decida lendo o código; nenhuma métrica substitui o julgamento.

---

## Nome Misterioso (Mysterious Name, p. 72)
**Sintomas:** você precisa ler o corpo para saber para que serve uma função, variável, campo ou classe; nenhum bom nome vem à mente (muitas vezes um sinal de que o design está confuso).
**Tente:**
- Mudar Declaração de Função ([change-function-declaration.md](first-set/change-function-declaration.md)), para renomear uma função
- Renomear Variável ([rename-variable.md](first-set/rename-variable.md))
- Renomear Campo ([rename-field.md](organizing-data/rename-field.md))

## Código Duplicado (Duplicated Code, p. 72)
**Sintomas:** a mesma estrutura em mais de um lugar, então cada leitor precisa comparar as cópias e cada mudança precisa atingir todas.
**Tente:**
- Extrair Função ([extract-function.md](first-set/extract-function.md)), para código idêntico na mesma classe
- Deslocar Instruções ([slide-statements.md](moving-features/slide-statements.md)), para agrupar fragmentos parecidos, mas não idênticos, antes de extrair
- Subir Método ([pull-up-method.md](inheritance/pull-up-method.md)), para cópias em subclasses irmãs

## Função Longa (Long Function, p. 73)
**Sintomas:** uma função em que você precisa rolar a tela; blocos que precisam de um comentário para dizer o que fazem; muitas variáveis temporárias e parâmetros; laços ou condicionais que fazem vários trabalhos.
**Tente:**
- Extrair Função ([extract-function.md](first-set/extract-function.md)), a resposta habitual, guiada pela intenção por trás de um comentário
- Extrair Função em cada ramo de um `switch` grande, de modo que cada ramo vire uma única chamada
- Extrair um laço junto com o seu corpo, como uma função, antes de considerar se ele deve ser dividido
- Substituir Variável Temporária por Consulta ([replace-temp-with-query.md](encapsulation/replace-temp-with-query.md)), quando variáveis temporárias impedem a extração
- Introduzir Objeto de Parâmetros ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)) e Preservar Objeto Inteiro ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), quando os parâmetros impedem a extração
- Substituir Função por Comando ([replace-function-with-command.md](refactoring-apis/replace-function-with-command.md)), quando variáveis temporárias e parâmetros ainda atrapalham
- Decompor Condicional ([decompose-conditional.md](conditional-logic/decompose-conditional.md)), para condicionais grandes
- Substituir Condicional por Polimorfismo ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md)), para o mesmo switch repetido
- Dividir Laço ([split-loop.md](moving-features/split-loop.md)), quando um laço faz duas coisas e o pedaço extraído não tem um bom nome

## Lista Longa de Parâmetros (Long Parameter List, p. 74)
**Sintomas:** uma assinatura difícil de ler ou de chamar corretamente.
**Tente:**
- Substituir Parâmetro por Consulta ([replace-parameter-with-query.md](refactoring-apis/replace-parameter-with-query.md)), se um argumento puder ser derivado de outro
- Preservar Objeto Inteiro ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), em vez de desempacotar uma estrutura em vários argumentos
- Introduzir Objeto de Parâmetros ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), para argumentos que sempre viajam juntos
- Remover Argumento de Flag ([remove-flag-argument.md](refactoring-apis/remove-flag-argument.md)), quando um parâmetro seleciona o comportamento
- Combinar Funções em Classe ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)), quando várias funções compartilham os mesmos argumentos

## Dados Globais (Global Data, p. 74)
**Sintomas:** dados que qualquer código pode alterar e que ninguém consegue rastrear (variáveis globais, estáticos no nível da classe, singletons).
**Tente:**
- Encapsular Variável ([encapsulate-variable.md](first-set/encapsulate-variable.md)), primeiro, para que o acesso passe por uma função; depois reduza o escopo para uma classe ou módulo

## Dados Mutáveis (Mutable Data, p. 75)
**Sintomas:** valores que mudam de formas surpreendentes, longe de onde são lidos; variáveis que guardam coisas diferentes em momentos diferentes; dados que poderiam ser calculados, mas são armazenados e atualizados.
O escopo determina a gravidade: uma variável alterada dentro de duas linhas é inofensiva; quanto maior o alcance, mais urgente a correção.
**Tente:**
- Encapsular Variável ([encapsulate-variable.md](first-set/encapsulate-variable.md)), para que as atualizações passem por funções estreitas
- Dividir Variável ([split-variable.md](organizing-data/split-variable.md)), quando uma variável armazena coisas diferentes
- Deslocar Instruções ([slide-statements.md](moving-features/slide-statements.md)) e Extrair Função ([extract-function.md](first-set/extract-function.md)), para separar o código sem efeitos colaterais do código que atualiza
- Separar Consulta de Modificador ([separate-query-from-modifier.md](refactoring-apis/separate-query-from-modifier.md)), para que os chamadores não disparem efeitos colaterais ao ler
- Remover Método de Escrita ([remove-setting-method.md](refactoring-apis/remove-setting-method.md)), quando nenhum chamador precisar atribuir o campo
- Substituir Variável Derivada por Consulta ([replace-derived-variable-with-query.md](organizing-data/replace-derived-variable-with-query.md)), para dados armazenados que podem ser calculados
- Combinar Funções em Classe ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)) ou Combinar Funções em Transformação ([combine-functions-into-transform.md](first-set/combine-functions-into-transform.md)), para limitar quanto código pode atualizar os dados
- Mudar Referência para Valor ([change-reference-to-value.md](organizing-data/change-reference-to-value.md)), para substituir uma estrutura em vez de editá-la no lugar

## Alteração Divergente (Divergent Change, p. 76)
**Sintomas:** um módulo muda o tempo todo por motivos não relacionados (um conjunto de edições para um novo banco de dados, outro para um novo formato de relatório).
**Tente:**
- Dividir em Fases ([split-phase.md](first-set/split-phase.md)), se as duas preocupações formarem uma sequência
- Mover Função ([move-function.md](moving-features/move-function.md)), para módulos separados quando as chamadas vão e voltam
- Extrair Função ([extract-function.md](first-set/extract-function.md)), para dividir funções que misturam as duas preocupações antes de movê-las
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)), quando os módulos são classes

## Cirurgia com Espingarda (Shotgun Surgery, p. 76)
**Sintomas:** uma única mudança força pequenas edições em muitas classes; é fácil esquecer uma. O oposto de Alteração Divergente.
**Tente:**
- Mover Função ([move-function.md](moving-features/move-function.md)) e Mover Campo ([move-field.md](moving-features/move-field.md)), para reunir as edições em um módulo
- Combinar Funções em Classe ([combine-functions-into-class.md](first-set/combine-functions-into-class.md)), para funções que trabalham sobre os mesmos dados
- Combinar Funções em Transformação ([combine-functions-into-transform.md](first-set/combine-functions-into-transform.md)), para funções que enriquecem uma estrutura
- Dividir em Fases ([split-phase.md](first-set/split-phase.md)), quando as funções compartilhadas podem alimentar uma fase consumidora
- Internalizar Função ([inline-function.md](first-set/inline-function.md)) e Internalizar Classe ([inline-class.md](encapsulation/inline-class.md)), para reunir primeiro a lógica mal dividida e depois extrair de novo (uma função ou classe grande temporária é aceitável)

## Inveja de Recursos (Feature Envy, p. 77)
**Sintomas:** uma função conversa mais com os dados ou getters de outro módulo do que com os seus próprios.
**Tente:**
- Mover Função ([move-function.md](moving-features/move-function.md)), para colocá-la junto dos dados
- Extrair Função ([extract-function.md](first-set/extract-function.md)), quando só parte da função tem inveja, e então mover essa parte
- Quando a função toca vários módulos, coloque-a junto do que guarda mais dados. Alguns padrões mantêm de propósito o comportamento separado dos dados, para que cada um possa variar por conta própria (Strategy, Visitor e Self Delegation, de Kent Beck); trate-os como exceções legítimas, e como remédios para Alteração Divergente.

## Agrupamentos de Dados (Data Clumps, p. 78)
**Sintomas:** os mesmos poucos valores aparecem juntos como campos em várias classes e como parâmetros em muitas assinaturas. Verificação rápida: se um valor perde o significado quando tomado sozinho, o grupo é um conceito esperando para virar objeto.
**Tente:**
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)), primeiro nos campos
- Introduzir Objeto de Parâmetros ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), depois nas assinaturas
- Preservar Objeto Inteiro ([preserve-whole-object.md](refactoring-apis/preserve-whole-object.md)), depois nas assinaturas
- Prefira uma classe (ou record) que possa ganhar comportamento depois, não um simples recipiente de dados ou tupla
- Ainda vale extrair quando um chamador precisa de apenas parte do novo objeto, desde que o objeto absorva dois ou mais dos campos ou argumentos desse chamador

## Obsessão por Primitivos (Primitive Obsession, p. 78)
**Sintomas:** conceitos do domínio guardados como números ou strings simples (quantidades sem unidades, intervalos como comparações em pares, códigos "stringly typed").
**Tente:**
- Substituir Primitivo por Objeto ([replace-primitive-with-object.md](encapsulation/replace-primitive-with-object.md))
- Substituir Código de Tipo por Subclasses ([replace-type-code-with-subclasses.md](inheritance/replace-type-code-with-subclasses.md)), depois Substituir Condicional por Polimorfismo ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md)), quando o primitivo é um código de tipo que dirige condicionais
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)) e Introduzir Objeto de Parâmetros ([introduce-parameter-object.md](first-set/introduce-parameter-object.md)), para primitivos que viajam em grupos

## Switches Repetidos (Repeated Switches, p. 79)
**Sintomas:** o mesmo switch ou cascata de if/else sobre a mesma condição aparece em vários lugares, então cada novo caso exige uma caçada.
**Tente:**
- Substituir Condicional por Polimorfismo ([replace-conditional-with-polymorphism.md](conditional-logic/replace-conditional-with-polymorphism.md))

## Laços (Loops, p. 79)
**Sintomas:** laços em que um pipeline de filtro/mapeamento mostraria o que é selecionado e o que é feito com isso.
**Tente:**
- Substituir Laço por Pipeline ([replace-loop-with-pipeline.md](moving-features/replace-loop-with-pipeline.md))

## Elemento Ocioso (Lazy Element, p. 80)
**Sintomas:** uma função, classe ou nível de hierarquia que já não justifica a sua estrutura (um nome que repete o corpo, uma classe que é uma única função trivial).
**Tente:**
- Internalizar Função ([inline-function.md](first-set/inline-function.md))
- Internalizar Classe ([inline-class.md](encapsulation/inline-class.md))
- Colapsar Hierarquia ([collapse-hierarchy.md](inheritance/collapse-hierarchy.md))

## Generalidade Especulativa (Speculative Generality, p. 80)
**Sintomas:** ganchos, abstrações e parâmetros adicionados para necessidades que nunca vieram; às vezes só os testes os usam.
**Tente:**
- Colapsar Hierarquia ([collapse-hierarchy.md](inheritance/collapse-hierarchy.md)), para classes abstratas que fazem pouco
- Internalizar Função ([inline-function.md](first-set/inline-function.md)) e Internalizar Classe ([inline-class.md](encapsulation/inline-class.md)), para delegação desnecessária
- Mudar Declaração de Função ([change-function-declaration.md](first-set/change-function-declaration.md)), para eliminar parâmetros não usados
- Remover Código Morto ([remove-dead-code.md](moving-features/remove-dead-code.md)), inclusive código que só os testes chamam (apague esses testes também)

## Campo Temporário (Temporary Field, p. 80)
**Sintomas:** um campo definido só em algumas circunstâncias, então os leitores se perguntam por que ele existe quando está vazio.
**Tente:**
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)), para dar um lar a esses campos
- Mover Função ([move-function.md](moving-features/move-function.md)), para mover o código que os usa para essa classe
- Introduzir Caso Especial ([introduce-special-case.md](conditional-logic/introduce-special-case.md)), para substituir as verificações de "campos não válidos" por uma classe alternativa

## Cadeias de Mensagens (Message Chains, p. 81)
**Sintomas:** um cliente navega objeto após objeto (`a.b().c().d()`), ficando acoplado à estrutura do caminho.
**Tente:**
- Ocultar Delegação ([hide-delegate.md](encapsulation/hide-delegate.md)), em um ou mais pontos da cadeia
- Extrair Função ([extract-function.md](first-set/extract-function.md)) no código que usa o fim da cadeia, depois Mover Função ([move-function.md](moving-features/move-function.md)) pela cadeia abaixo; muitas vezes melhor que ocultar cada elo, o que cria intermediários
- Adicione um método no objeto intermediário que faça toda a navegação, quando vários clientes quiserem percorrer o resto da cadeia

## Intermediário (Middle Man, p. 81)
**Sintomas:** cerca de metade dos métodos de uma classe apenas repassa para outra classe.
**Tente:**
- Remover Intermediário ([remove-middle-man.md](encapsulation/remove-middle-man.md))
- Internalizar Função ([inline-function.md](first-set/inline-function.md)), se apenas alguns métodos só delegam
- Substituir Superclasse por Delegação ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)) ou Substituir Subclasse por Delegação ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)), quando o intermediário também tem comportamento próprio, para transformá-lo no colaborador de verdade

## Troca de Informações Privilegiadas (Insider Trading, p. 82)
**Sintomas:** módulos que trocam dados livremente demais; subclasses que sabem demais sobre os pais.
**Tente:**
- Mover Função ([move-function.md](moving-features/move-function.md)) e Mover Campo ([move-field.md](moving-features/move-field.md)), para reduzir a conversa
- Ocultar Delegação ([hide-delegate.md](encapsulation/hide-delegate.md)), para usar um intermediário
- Crie um terceiro módulo para os interesses compartilhados
- Substituir Subclasse por Delegação ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)) ou Substituir Superclasse por Delegação ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)), para conluio por herança

## Classe Grande (Large Class, p. 82)
**Sintomas:** campos demais (muitas vezes com prefixos ou sufixos comuns) ou código demais; a duplicação cresce lá dentro. Clientes que usam só um subconjunto dos recursos sugerem a divisão.
**Tente:**
- Extrair Classe ([extract-class.md](encapsulation/extract-class.md)), para agrupar campos relacionados ou um subconjunto usado por clientes; uma classe que não usa todos os seus campos o tempo todo pode ser dividida mais de uma vez
- Extrair Superclasse ([extract-superclass.md](inheritance/extract-superclass.md)), quando o componente faz sentido como herança
- Substituir Código de Tipo por Subclasses ([replace-type-code-with-subclasses.md](inheritance/replace-type-code-with-subclasses.md)), que na prática é extrair uma subclasse

## Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces, p. 83)
**Sintomas:** duas classes fazem o mesmo trabalho, mas não podem ser trocadas porque os nomes e assinaturas dos métodos diferem.
**Tente:**
- Mudar Declaração de Função ([change-function-declaration.md](first-set/change-function-declaration.md)), para fazer as assinaturas coincidirem
- Mover Função ([move-function.md](moving-features/move-function.md)), até que os protocolos coincidam
- Extrair Superclasse ([extract-superclass.md](inheritance/extract-superclass.md)), se o alinhamento deixar duplicação

## Classe de Dados (Data Class, p. 83)
**Sintomas:** uma classe com campos e acessores e nada mais, manipulada em detalhe por outras (muitas vezes com campos públicos). Exceção: um record de resultado imutável, como o que fica entre duas fases após um Dividir em Fases.
**Tente:**
- Encapsular Registro ([encapsulate-record.md](encapsulation/encapsulate-record.md)), de imediato, para campos públicos
- Remover Método de Escrita ([remove-setting-method.md](refactoring-apis/remove-setting-method.md)), para campos que não devem mudar
- Mover Função ([move-function.md](moving-features/move-function.md)), para trazer o comportamento dos clientes para dentro da classe
- Extrair Função ([extract-function.md](first-set/extract-function.md)), para isolar primeiro um trecho movível

## Herança Recusada (Refused Bequest, p. 83)
**Sintomas:** uma subclasse usa pouco do que herda. Costuma ser um smell fraco; forte quando a subclasse recusa a interface do pai e não só a implementação.
**Tente:**
- Descer Método ([push-down-method.md](inheritance/push-down-method.md)) e Descer Campo ([push-down-field.md](inheritance/push-down-field.md)), movendo os membros não usados para uma nova irmã (o conselho tradicional; só vale a pena quando causa confusão real)
- Substituir Subclasse por Delegação ([replace-subclass-with-delegate.md](inheritance/replace-subclass-with-delegate.md)) ou Substituir Superclasse por Delegação ([replace-superclass-with-delegate.md](inheritance/replace-superclass-with-delegate.md)), quando a interface é recusada

## Comentários (Comments, p. 84)
**Sintomas:** comentários que existem porque o código não é claro. Comentários que explicam o porquê, ou admitem dúvida, são bons.
**Tente:**
- Extrair Função ([extract-function.md](first-set/extract-function.md)), quando um comentário explica um bloco
- Mudar Declaração de Função ([change-function-declaration.md](first-set/change-function-declaration.md)), para renomear uma função que ainda precisa de um comentário
- Introduzir Asserção ([introduce-assertion.md](conditional-logic/introduce-assertion.md)), para declarar uma regra sobre o estado necessário
