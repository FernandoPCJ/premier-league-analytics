# ⚽ Premier League Analytics

Projeto de análise de dados da Premier League desenvolvido com Python, PostgreSQL, Jupyter Notebook e Streamlit.

O projeto contempla **10 temporadas, de 2016/17 a 2025/26**, totalizando **3.800 partidas**, e explora o desempenho dos clubes por meio de indicadores ofensivos, defensivos, disciplinares e estatísticos.

Além das análises exploratórias realizadas em notebooks, o projeto possui um **dashboard interativo** para visualização e comparação dos resultados.

---

## 🎯 Objetivo

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

## 📊 Dashboard

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

### ⚽ Análise Ofensiva

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

### 🛡️ Análise Defensiva

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

### 🟨 Análise Disciplinar

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

### 📊 Análise Estatística

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

## 🔎 Filtros interativos

As páginas do dashboard permitem filtrar os dados por:

- temporada;
- clube.

Ao selecionar um clube, ele é destacado visualmente nos rankings e gráficos.

Quando uma temporada específica é selecionada, ela também é destacada nos gráficos históricos do clube.

---

## 🧪 Métodos estatísticos

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

## 🧰 Tecnologias

O projeto utiliza:

- Python
- Pandas
- NumPy
- Matplotlib
- SciPy
- SQLAlchemy
- PostgreSQL
- Psycopg
- JupyterLab
- Streamlit
- Plotly

---

## 📁 Estrutura do projeto

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