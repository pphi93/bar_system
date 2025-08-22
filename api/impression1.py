import sys
import mysql.connector
import os

# Récupération de l'ID de la commande passée en argument
commande_id = sys.argv[1]

# Connexion à la base de données
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpass",  # ⚠️ même mot de passe que dans main.py
    database="bar"
)
cursor = db.cursor()

# Récupération des infos de la commande
cursor.execute("SELECT table_num, total FROM commandes WHERE id=%s", (commande_id,))
table_num, total = cursor.fetchone()

# Récupération des détails de commande
cursor.execute("""
    SELECT p.nom, cd.quantite, p.prix
    FROM commande_details cd
    JOIN produits p ON p.id = cd.id_produit
    WHERE cd.id_commande=%s
""", (commande_id,))
lignes = cursor.fetchall()
db.close()

# Génération du ticket en texte
ticket = f"\n--- COMMANDE #{commande_id} ---\n"
ticket += f"Table : {table_num}\n"
ticket += "----------------------------\n"
for nom, qte, prix in lignes:
    ticket += f"{nom} x{qte}  -> {prix*qte:.2f}€\n"
ticket += "----------------------------\n"
ticket += f"TOTAL : {total:.2f}€\n"
ticket += "----------------------------\n\n"

# Sauvegarde temporaire du ticket
with open("/tmp/ticket.txt", "w") as f:
    f.write(ticket)

# Envoi à l’imprimante par CUPS
os.system("lp /tmp/ticket.txt")
