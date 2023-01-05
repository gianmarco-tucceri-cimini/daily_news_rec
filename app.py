from flask import Flask, render_template
import pandas as pd
import datetime
from datetime import date

app = Flask(__name__)

@app.route("/")
def index():
    # Carica il dataframe
    df = pd.read_csv("data/daily_news.csv")
    df_oggi = df.loc[df['date'] == datetime.datetime.today().strftime("%Y-%m-%d")]

    # Crea una lista di dizionari con i dati degli articoli
    articles = []
    for index, row in df_oggi.iterrows():
        articles.append({
            "title": row["title"],
            "link": row["link"],
            "image": row["image"],
        })
        
    # Se non ci sono articoli per il giorno corrente
    if len(articles) == 0:
        return render_template("index.html", message="il giornale lo scaricano alle 9")

    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)