# Premier League Analytics

Projeto de análise de dados da Premier League utilizando Python, PostgreSQL,
Jupyter Notebook e técnicas de análise estatística.

O conjunto de dados utilizado contempla as temporadas de **2016/17 a 2025/26**,
totalizando **3.800 partidas**.

## Objetivos

O projeto busca explorar padrões de desempenho dos clubes da Premier League
a partir de indicadores ofensivos, defensivos, disciplinares e estatísticos.

Entre as questões analisadas estão:

- evolução da média de gols por temporada;
- vantagem de jogar em casa;
- desempenho ofensivo dos clubes;
- desempenho defensivo dos clubes;
- eficiência de finalizações;
- clean sheets;
- faltas e cartões;
- correlações entre indicadores;
- consistência de desempenho entre temporadas;
- comparação estatística entre clubes.

## Tecnologias

- Python
- Pandas
- NumPy
- Matplotlib
- SciPy
- SQLAlchemy
- PostgreSQL
- Psycopg
- JupyterLab

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
├── sql/
├── src/
├── .gitignore
├── requirements.txt
└── README.md