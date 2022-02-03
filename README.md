# Star Jeans

<b>AVISO:</b> Todos os problemas e premissas contextualizados no projeto são fictícios. Seu único objetivo é dar sentido para o desenvolvimento da solução.<br><br>
<img src='imgs/maxresdefault.jpg'>
<br><br>
## 1. Sobre a Star Jeans
Eduardo e Marcelo são dois brasileiros, amigos e parceiros de negócios. Depois de vários negócios de sucesso, eles planejam entrar no mercado de moda nos EUA como modelo de negócios de e-commerce. A ideia inicial é entrar no mercado com apenas um produto e para um público específico, neste caso o produto seria Jeans para o público masculino. 
<br><br>

### 1.1. Problema de negócio
<p>O objetivo é manter o custo operacional baixo e escalar à medida que conquistam clientes. Porém, mesmo com o produto de entrada e público definidos, os dois sócios não possuem experiência nesse mercado de moda e por isso não sabem definir coisas básicas como preço, tipo de calça e material para confecção de cada peça . Os principais concorrentes da empresa Star Jeans são as empresas americanas H&M e Macys.</p>
<p>Os dois sócios contrataram uma consultoria de Data Science para responder as seguintes perguntas:</p>

- Qual é o melhor preço de venda para calças?
- Quantos tipos de calças e suas cores para o produto inicial?
- Quais são as matérias-primas necessárias para fazer as calças?
<br><br>


## 2. Estratégia de solução
1. Coletar dados dos principais concorrentes
    - H&M
    - Macys
    <br><br>
1. Defina o formato de entrega (Visualização, Tabela, Frase)
    - Gráfico de barras com a mediana dos preços dos produtos, por tipo e cor nos últimos 30 dias.
    - Tabela com as seguintes colunas: id | product_name | product_type | product_color | product_price
    - Definição de esquema: colunas e seu tipo
    - Definição de infraestrutura de armazenamento (SQLITE3)
    - Design ETL (Extrair, Transformar e Carregar Scripts)
    <br><br>
1. Entrega do produto final
    - Aplicativo com Streamlit
    <br><br>
1. Ferramentas
    - Python 3.8.
    - Recuperando Bibliotecas (BS4, Selenium)
    - PyCharmName
    - Jupyter Notebook (Análise e prototipagem)
    - Agendador de tarefas
    - Iluminado
<br><br>

## 3. Lições aprendidas
- Noções iniciais de webscraping
- Tratamento de dados utilizando expressões regulares (Regex)
<br><br>

## 4. Próximos passos
- Utilizar os dados coletados para responder as perguntas dos sócios
- Análise exploratória de dados para gerar insights
- Estudar a viabilidade de aplicação de um modelo de machine learning