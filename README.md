# Premier League Analytics

Projeto de análise de dados da Premier League desenvolvido com **Python, PostgreSQL, JupyterLab e Streamlit**.

O projeto contempla **10 temporadas, de 2016/17 a 2025/26**, totalizando **3.800 partidas**, e explora o desempenho dos clubes por meio de indicadores ofensivos, defensivos, disciplinares e estatísticos.

Além das análises exploratórias realizadas em notebooks, o projeto possui um **dashboard interativo** para visualização, comparação e exploração dos resultados.

---

## Dashboard online

O dashboard está publicado e pode ser acessado em:

**https://premier-league-analytics.streamlit.app**

A aplicação foi desenvolvida com **Streamlit** e utiliza um banco **PostgreSQL hospedado no Neon** para consultar os dados das 3.800 partidas.

---

## Objetivo

O objetivo do projeto é explorar padrões de desempenho dos clubes da Premier League ao longo das temporadas utilizando técnicas de análise exploratória, visualização de dados e estatística.

Entre as principais questões analisadas estão:

- evolução da média de gols por temporada;
- vantagem de jogar em casa;
- desempenho ofensivo dos clubes;
- desempenho defensivo dos clubes;
- eficiência de finalizações;
- clean sheets;
- faltas e cartões;
- correlações entre indicadores;
- consistência de desempenho entre temporadas;
- diferenças entre desempenho como mandante e visitante;
- significância estatística da vantagem de mando.

---

## Dashboard

O dashboard foi desenvolvido com **Streamlit** e **Plotly** e está organizado em cinco áreas principais.

### 🏠 Visão Geral

Apresenta uma visão consolidada da competição.

Principais recursos:

- quantidade de temporadas;
- quantidade de partidas;
- quantidade de clubes;
- total de gols;
- evolução da média de gols por partida;
- evolução de vitórias dos mandantes, empates e vitórias dos visitantes;
- desempenho histórico dos clubes;
- ranking por pontos, gols e aproveitamento.

---

### Análise Ofensiva

Permite explorar o desempenho ofensivo dos clubes.

Indicadores:

- gols;
- gols por jogo;
- finalizações por jogo;
- finalizações no alvo por jogo;
- conversão de finalizações.

Análises disponíveis:

- ranking ofensivo;
- finalizações por jogo × gols por jogo;
- finalizações no alvo × gols por jogo;
- evolução ofensiva dos clubes entre temporadas;
- evolução da conversão de finalizações.

---

### Análise Defensiva

Explora a capacidade defensiva dos clubes.

Indicadores:

- gols sofridos;
- gols sofridos por jogo;
- finalizações concedidas por jogo;
- finalizações no alvo concedidas por jogo;
- clean sheets.

Análises disponíveis:

- ranking defensivo;
- finalizações concedidas × gols sofridos;
- finalizações no alvo concedidas × gols sofridos;
- evolução defensiva dos clubes;
- evolução dos clean sheets.

---

### Análise Disciplinar

Analisa o comportamento disciplinar das equipes.

Indicadores:

- faltas por jogo;
- cartões amarelos por jogo;
- cartões por jogo;
- cartões vermelhos;
- cartões vermelhos a cada 100 jogos.

Análises disponíveis:

- ranking disciplinar;
- faltas × cartões amarelos;
- incidência proporcional de cartões vermelhos;
- evolução disciplinar dos clubes ao longo das temporadas.

---

### Análise Estatística

Apresenta análises estatísticas relacionadas ao comportamento da competição.

Principais análises:

- evolução da vantagem de mando;
- diferença entre gols dos mandantes e visitantes;
- intervalo de confiança de 95%;
- teste t pareado;
- teste não paramétrico de Wilcoxon;
- tamanho de efeito de Cohen (dz);
- correção de Holm para múltiplos testes;
- análise da vantagem de mando por temporada;
- matriz de correlação de Pearson;
- comparação entre Pearson e Spearman;
- análise de desempenho médio × consistência dos clubes.

---

## Filtros interativos

As páginas do dashboard permitem filtrar os dados por:

- temporada;
- clube.

Ao selecionar um clube, ele é destacado visualmente nos rankings e gráficos sem alterar sua posição real.

Quando uma temporada específica é selecionada, ela também é destacada nos gráficos históricos do clube, mantendo as demais temporadas como contexto para comparação.

---

## Métodos estatísticos

O projeto utiliza diferentes técnicas estatísticas para investigar os dados.

### Teste t pareado

Utilizado para comparar a quantidade de gols marcados pelos mandantes e visitantes.

### Teste de Wilcoxon

Utilizado como alternativa não paramétrica ao teste t.

### Cohen's dz

Utilizado para estimar o tamanho do efeito da vantagem de mando.

### Intervalo de confiança

Foi utilizado intervalo de confiança de 95% para estimar a diferença média entre gols de mandantes e visitantes.

### Correção de Holm

Aplicada para controlar o erro decorrente da realização de múltiplos testes estatísticos entre temporadas.

### Correlação de Pearson

Utilizada para analisar relações lineares entre indicadores como:

- gols;
- finalizações;
- finalizações no alvo;
- faltas;
- cartões amarelos;
- cartões vermelhos.

### Correlação de Spearman

Utilizada como comparação com Pearson para avaliar a robustez das relações identificadas.

---

## Tecnologias

O projeto utiliza:

- Python
- Pandas
- NumPy
- Matplotlib
- SciPy
- SQLAlchemy
- PostgreSQL
- Neon PostgreSQL
- Psycopg
- JupyterLab
- Streamlit
- Streamlit Community Cloud
- Plotly

---

## Estrutura do projeto

```text
premier-league-analytics/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_eda_overview.ipynb
│   ├── 02_analise_ofensiva.ipynb
│   ├── 03_analise_defensiva.ipynb
│   └── 04_analise_estatistica.ipynb
│
├── dashboard/
│   ├── app.py
│   │
│   ├── pages/
│   │   ├── visao_geral.py
│   │   ├── ataque.py
│   │   ├── defesa.py
│   │   ├── disciplina.py
│   │   └── estatistica.py
│   │
│   └── utils/
│       └── database.py
│
├── sql/
├── src/
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Arquitetura

A aplicação segue uma estrutura em que os dados são armazenados em PostgreSQL e consultados pelo dashboard conforme a interação do usuário.

```text
Dados das partidas
        ↓
Preparação e tratamento
        ↓
PostgreSQL / Neon
        ↓
SQLAlchemy + Psycopg
        ↓
Pandas
        ↓
Streamlit + Plotly
        ↓
Dashboard interativo
```

O banco de dados utilizado em produção está hospedado no **Neon PostgreSQL**.

A interface do dashboard é executada no **Streamlit Community Cloud**.

As credenciais de acesso ao banco de dados não são armazenadas no repositório. Elas são configuradas por meio do sistema de **Secrets do Streamlit**.

A arquitetura de produção pode ser resumida da seguinte forma:

```text
GitHub
   ↓
Streamlit Community Cloud
   ↓
Aplicação Streamlit
   ↓
SQLAlchemy + Psycopg
   ↓
Neon PostgreSQL
   ↓
Dados da Premier League
```

---

## Executando o projeto localmente

Clone o repositório:

```bash
git clone https://github.com/FernandoPCJ/premier-league-analytics.git
```

Entre na pasta do projeto:

```bash
cd premier-league-analytics
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

No Windows, ative o ambiente:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure a conexão com o PostgreSQL conforme descrito na seção de configuração do banco.

Depois execute o dashboard:

```bash
streamlit run dashboard/app.py
```

A aplicação ficará disponível localmente, normalmente em:

```text
http://localhost:8501
```

---

## Configuração do banco de dados

A conexão com PostgreSQL é realizada utilizando **SQLAlchemy** e **Psycopg**.

As configurações de acesso são obtidas por meio do `st.secrets` do Streamlit.

Para desenvolvimento local, deve ser criado o arquivo:

```text
.streamlit/secrets.toml
```

com estrutura semelhante a:

```toml
[postgres]
host = "HOST"
port = 5432
database = "DATABASE"
user = "USER"
password = "PASSWORD"
```

O arquivo `secrets.toml` contém informações sensíveis e **não deve ser enviado ao GitHub**.

No ambiente de produção, essas mesmas informações são configuradas diretamente na área de **Secrets do Streamlit Community Cloud**.

---

## Banco de dados

O projeto utiliza **PostgreSQL** para armazenar os dados utilizados nas análises.

As principais tabelas são:

- `seasons`: informações sobre as temporadas;
- `teams`: clubes presentes no conjunto de dados;
- `matches`: informações e estatísticas das partidas.

A base utilizada em produção contém:

- **10 temporadas**;
- **34 clubes distintos**;
- **3.800 partidas**.

O PostgreSQL utilizado pela aplicação publicada está hospedado no **Neon**, na região de São Paulo.

---

##  Dependências principais

As dependências utilizadas no projeto estão registradas no arquivo `requirements.txt`.

```text
pandas
numpy
matplotlib
scipy
SQLAlchemy
psycopg[binary]
jupyterlab
streamlit
plotly
```

---

## Notebooks

Os notebooks foram utilizados nas etapas de exploração, preparação e validação das análises antes da construção do dashboard.

Eles estão disponíveis no diretório:

```text
notebooks/
```

Os principais notebooks são:

- `01_eda_overview.ipynb`: visão exploratória inicial;
- `02_analise_ofensiva.ipynb`: análise ofensiva;
- `03_analise_defensiva.ipynb`: análise defensiva;
- `04_analise_estatistica.ipynb`: análises estatísticas.

Para executar os notebooks:

```bash
jupyter lab
```

---

## Período analisado

O conjunto de dados compreende as seguintes temporadas:

```text
2016/17
2017/18
2018/19
2019/20
2020/21
2021/22
2022/23
2023/24
2024/25
2025/26
```

Total:

**10 temporadas e 3.800 partidas.**

---

## V Status do projeto

- Coleta e preparação dos dados: V
- Banco PostgreSQL: V
- Análise exploratória: V
- Análise ofensiva: V
- Análise defensiva: V
- Análise disciplinar: V
- Análise estatística: V
- Dashboard interativo: V
- Revisão funcional do dashboard: V
- Migração do PostgreSQL para o Neon: V
- Configuração do banco de produção: V
- Deploy público no Streamlit Community Cloud: V

---

## Aplicação publicada

A versão pública do projeto está disponível em:

**https://premier-league-analytics.streamlit.app**

O dashboard permite explorar os dados das dez temporadas por meio dos filtros de temporada e clube e navegar pelas análises de visão geral, ataque, defesa, disciplina e estatística.