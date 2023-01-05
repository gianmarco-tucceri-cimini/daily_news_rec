from flask import Flask, render_template, request, make_response
import pandas as pd
import datetime
from datetime import date
import logging
import uuid
import hashlib
import random

app = Flask(__name__)

def generate_unique_id():
    # Recupera informazioni univoche dal dispositivo dell'utente
    user_agent = request.headers.get('User-Agent')
    user_ip = request.remote_addr

    # Crea una stringa con queste informazioni
    user_info = user_agent + user_ip

    # Calcola l'hash della stringa
    user_hash = hashlib.sha256(user_info.encode()).hexdigest()

    # Restituisci l'hash come identificatore univoco dell'utente
    return user_hash

def get_current_user():
    # Controlla se esiste già un cookie per l'utente
    user_id = request.cookies.get("user_id")

    # Se non esiste, genera un nuovo ID e lo salva come cookie
    if user_id is None:
        user_id = generate_unique_id()
        response = make_response(render_template("index.html"))
        response.set_cookie("user_id", user_id)
        return user_id
    # Se esiste già un cookie, restituisci l'ID senza modificare il browser dell'utente
    else:
        return user_id, None

@app.route("/")
def index():

    # Recupera l'utente corrente (per esempio, dal browser o dal dispositivo)
    current_user = get_current_user()
    
    # Carica il dataframe delle interazioni
    df_interactions = pd.read_csv("data/interactions.csv")

    # Carica il dataframe delle notizie
    df = pd.read_csv("data/daily_news.csv")
    df_oggi = df.loc[df['date'] == datetime.datetime.today().strftime("%Y-%m-%d")]

    # Riordino casualmente gli articoli di oggi
    df_oggi = df_oggi.sample(frac=1, random_state=random.seed(42))

    # Crea una lista di dizionari con i dati degli articoli
    articles = []
    for index, row in df_oggi.iterrows():
        articles.append({
            "title": row["title"],
            "link": row["link"],
            "image": row["image"],
            "likes": row["likes"],  # Aggiungi il numero di like all'articolo
        })
        
    # Se non ci sono articoli per il giorno corrente
    if len(articles) == 0:
        return render_template("index.html", message="il giornale lo scaricano alle 9")

    return render_template("index.html", articles=articles, current_user=current_user)

@app.route("/like", methods=["POST"])
def like():
    # Carica il dataframe delle interazioni
    df_interactions = pd.read_csv("data/interactions.csv")

    # Carica il dataframe delle notizie
    df = pd.read_csv("data/daily_news.csv")

    # Recupera l'utente corrente (per esempio, dal browser o dal dispositivo)
    current_user = get_current_user()

    # Recupera il link dell'articolo dai dati inviati con la richiesta POST
    link = request.form["link"]

    # Controlla se l'utente ha già espresso un like per questo articolo
    already_liked = (df_interactions['user_id'] == current_user) & (df_interactions['link'] == link)

    # Se l'utente non ha ancora espresso un like per questo articolo, aggiungi una nuova riga al dataframe
    if not already_liked.any():
        df_interactions = df_interactions.append({'user_id': current_user, 'link': link}, ignore_index=True)
    
    # Aggiorna il numero di like per l'articolo nel dataframe delle notizie
    df.loc[df['link'] == link, 'likes'] += 1

    # Salva il dataframe aggiornato
    df_interactions.to_csv("data/interactions.csv", index=False)

     # Salva ildataframe aggiornato
    df.to_csv("data/daily_news.csv", index=False)

    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)