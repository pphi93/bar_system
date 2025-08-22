from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
import subprocess

app = FastAPI()

# Connexion à la base de données
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpass",  # ⚠️ à changer si tu veux plus de sécurité
        database="bar"
    )

# Modèle pour une commande reçue
class CommandeItem(BaseModel):
    produit_id: int
    quantite: int

class Commande(BaseModel):
    table_num: int
    items: list[CommandeItem]

# Endpoint pour lister les produits disponibles
@app.get("/produits")
def liste_produits():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produits WHERE disponible=1")
    produits = cursor.fetchall()
    db.close()
    return produits

# Endpoint pour créer une nouvelle commande
@app.post("/commande")
def nouvelle_commande(cmd: Commande):
    db = get_db()
    cursor = db.cursor()
    total = 0

    # Calcul du total
    for item in cmd.items:
        cursor.execute("SELECT prix FROM produits WHERE id=%s", (item.produit_id,))
        prix = cursor.fetchone()[0]
        total += prix * item.quantite

    # Insertion de la commande
    cursor.execute(
        "INSERT INTO commandes (table_num, total) VALUES (%s, %s)",
        (cmd.table_num, total)
    )
    commande_id = cursor.lastrowid

    # Insertion des détails de commande
    for item in cmd.items:
        cursor.execute(
            "INSERT INTO commande_details (id_commande, id_produit, quantite) VALUES (%s, %s, %s)",
            (commande_id, item.produit_id, item.quantite)
        )

    db.commit()
    db.close()

    # Impression directe du ticket
    subprocess.Popen(["python3", "/opt/bar_app/impression.py", str(commande_id)])

    return {"status": "ok", "commande_id": commande_id}
