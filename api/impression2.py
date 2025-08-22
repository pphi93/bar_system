import sys
import mysql.connector
import os

# Récupération de l'ID de commande passé en argument
if len(sys.argv) < 2:
    print("Erreur : ID de commande manquant")
    sys.exit(1)

commande_id = sys.argv[1]

# Connexion à la base de données
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpass",  # ⚠️ à changer si besoin
    database="bar"
)
cursor = db.cursor()

# Infos de la commande
cursor.execute("SELECT table_num, total FROM commandes WHERE id=%s", (commande_id,))
table_num, total = cursor.fetchone()

# Détails des produits commandés
cursor.execute("""
    SELECT p.nom, cd.quantite, p.prix
    FROM commande_details cd
    JOIN produits p ON p.id = cd.id_produit
    WHERE cd.id_commande=%s
""", (commande_id,))
lignes = cursor.fetchall()
db.close()

# Génération du texte du ticket
ticket = f"*** BAR ***\n"
ticket += f"Table {table_num}\n"
ticket += f"Commande #{commande_id}\n"
ticket += "-------------------\n"

for nom, qte, prix in lignes:
    ticket += f"{nom} x{qte} - {prix*qte:.2f}€\n"

ticket += "-------------------\n"
ticket += f"TOTAL : {total:.2f}€\n\n"
ticket += "Merci et santé ! 🍻\n"

# Sauvegarde temporaire du ticket
ticket_file = "/tmp/ticket.txt"
with open(ticket_file, "w") as f:
    f.write(ticket)

# Impression via CUPS
os.system(f"lp {ticket_file}")
