from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route("/")
def index():
    # Carica il dataframe
    df = pd.read_csv("data/daily_news.csv")

    # Crea una lista di dizionari con i dati degli articoli
    articles = []
    for index, row in df.iterrows():
        articles.append({
            "title": row["title"],
            "link": row["link"],
            "image": row["image"],
        })

    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    app.run()