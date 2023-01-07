from flask import Flask, render_template, request, make_response
import pandas as pd
import datetime
from datetime import date, datetime
import logging
import uuid
import hashlib
import random
import geoip2.database
import requests

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

def get_location(ip_address):
    # Costruisci l'URL dell'API
    api_url = f"https://api.ip2location.io/?key={LGKZK4WSTZ}&ip={ip_address}"

    # Invia la richiesta all'API e recupera la risposta
    response = requests.get(api_url)

    # Verifica se la richiesta ha avuto successo
    if response.status_code == 200:
        # Recupera la località dalla risposta
        location = response.json()
        city = location["city"]

        # Restituisci la località
        return f"{city}"
    else:
        # Se la richiesta non è riuscita, restituisci un messaggio di errore
        return "Errore durante il recupero della località"

def has_liked(user_id, link):
    # Carica il dataframe delle interazioni
    df_interactions = pd.read_csv("data/interactions.csv")

    # Controlla se l'utente ha già espresso un like per questo articolo
    liked = (df_interactions['user_id'] == user_id) & (df_interactions['link'] == link)

    # Restituisci True se l'utente ha già espresso un like, False altrimenti
    return liked.any()


@app.route("/")
def index():

    # Recupera l'utente corrente (per esempio, dal browser o dal dispositivo)
    current_user = get_current_user()
    
    # Carica il dataframe delle interazioni
    df_interactions = pd.read_csv("data/interactions.csv")

    # Carica il dataframe delle notizie
    df = pd.read_csv("data/daily_news.csv")
    df_oggi = df.loc[df['date'] == datetime.today().strftime("%Y-%m-%d")]

    # Riordino casualmente gli articoli di oggi
    df_oggi = df_oggi.sample(frac=1, random_state=random.seed(42))

    # Crea una lista di dizionari con i dati degli articoli
    articles = []
    for index, row in df.iterrows():
        link = row['link']

    # Controlla se l'utente ha già espresso un like per questo articolo
    liked = has_liked(current_user, link)

    # Crea una lista di dizionari con i dati degli articoli
    articles = []
    for index, row in df_oggi.iterrows():
        articles.append({
            "title": row["title"],
            "link": row["link"],
            "image": row["image"],
            "likes": row["likes"],  # Aggiungi il numero di like all'articolo
            "liked": liked,  # Aggiungi lo stato del like all'articolo
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

    # Recupera l'indirizzo IP dell'utente
    ip_address = request.remote_addr

    # Recupera il timestamp corrente
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Recupera il link dell'articolo dai dati inviati con la richiesta POST
    link = request.form["link"]

    # Controlla se l'utente è già presente nel dataframe delle interazioni
    user_exists = df_interactions['user_id'] == current_user
    

    # Controlla se l'utente ha già espresso un like per questo articolo
    already_liked = (df_interactions['user_id'] == current_user) & (df_interactions['link'] == link)

    # Se l'utente non ha ancora espresso un like per questo articolo, aggiungi una nuova riga al dataframe
    if not already_liked.any():
        df_interactions = df_interactions.append({'user_id': current_user, 'link': link, 'ip_address': ip_address, 'timestamp': timestamp}, ignore_index=True)
        # Aggiorna il numero di like per l'articolo nel dataframe delle notizie
        df.loc[df['link'] == link, 'likes'] += 1

    # Salva il dataframe aggiornato
    df_interactions.to_csv("data/interactions.csv", index=False)

     # Salva ildataframe aggiornato
    df.to_csv("data/daily_news.csv", index=False)

    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)