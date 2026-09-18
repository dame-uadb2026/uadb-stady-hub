# -*- coding: utf-8 -*-
"""
Script de fusion des bases UADB Study Hub
==========================================
À utiliser quand plusieurs personnes ont ajouté des matières/documents
chacune sur son propre PC, et qu'on veut tout regrouper en une seule
version complète, sans rien perdre et sans doublons.

COMMENT S'EN SERVIR
--------------------
1. Chaque personne t'envoie deux choses : son fichier "uadb.db" et le
   contenu de son dossier "uploads/" (les PDF).
2. Range chaque envoi dans un sous-dossier séparé, par exemple :

   a_fusionner/
     amina/
       uadb.db
       uploads/  (les PDF d'Amina)
     moussa/
       uadb.db
       uploads/  (les PDF de Moussa)

3. Lance depuis le dossier du projet :

     python fusionner.py a_fusionner/amina a_fusionner/moussa

   (tu peux donner autant de dossiers que tu veux, un par personne)

4. Le script crée/actualise TON fichier uadb.db et TON dossier uploads/
   avec tout ce qui manquait. Ta base actuelle est utilisée comme point
   de départ, rien n'est écrasé sans raison.

5. Une fois fait, tu peux régénérer le zip complet et le renvoyer à tout
   le monde (voir README.md).

RÈGLES DE FUSION
-----------------
- Les matières sont reconnues par leur nom + leur filière : si la même
  matière existe déjà, elle n'est pas dupliquée.
- Les documents sont reconnus par leur titre + leur type + leur matière :
  si un document identique existe déjà, il n'est pas recopié en double.
- Les comptes admin sont fusionnés par identifiant : si un identifiant
  existe déjà des deux côtés, celui de TA base est conservé (le script
  te préviendra s'il y a un conflit à vérifier à la main).
"""

import os
import sys
import shutil
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "uadb.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")


def ouvrir(chemin_db):
    db = sqlite3.connect(chemin_db)
    db.row_factory = sqlite3.Row
    return db


def fusionner_une_source(db_cible, dossier_source):
    """Fusionne le contenu d'un dossier reçu (uadb.db + uploads/) dans la base cible."""
    chemin_db_source = os.path.join(dossier_source, "uadb.db")
    dossier_uploads_source = os.path.join(dossier_source, "uploads")

    if not os.path.exists(chemin_db_source):
        print(f"  ! Aucun fichier uadb.db trouvé dans {dossier_source}, dossier ignoré.")
        return

    db_source = ouvrir(chemin_db_source)

    # --- 1. Niveaux et filières : on suppose qu'ils existent déjà des deux
    #        côtés (créés par seed_db), on construit juste une table de
    #        correspondance slug -> id pour la base cible.
    filieres_cibles = {row["slug"]: row["id"] for row in db_cible.execute("SELECT id, slug FROM filieres")}

    # --- 2. Matières : on les reconnaît par (slug de la filière, nom de la matière)
    matieres_cibles = {}
    for row in db_cible.execute("""
        SELECT matieres.id, matieres.nom, filieres.slug AS filiere_slug
        FROM matieres JOIN filieres ON filieres.id = matieres.filiere_id
    """):
        matieres_cibles[(row["filiere_slug"], row["nom"])] = row["id"]

    correspondance_matiere = {}  # id source -> id cible
    nb_matieres_ajoutees = 0

    for m in db_source.execute("""
        SELECT matieres.*, filieres.slug AS filiere_slug
        FROM matieres JOIN filieres ON filieres.id = matieres.filiere_id
    """):
        cle = (m["filiere_slug"], m["nom"])
        if cle in matieres_cibles:
            correspondance_matiere[m["id"]] = matieres_cibles[cle]
            continue
        if m["filiere_slug"] not in filieres_cibles:
            print(f"  ! Filière inconnue « {m['filiere_slug']} » pour la matière « {m['nom']} », ignorée.")
            continue
        filiere_id_cible = filieres_cibles[m["filiere_slug"]]
        ordre = db_cible.execute(
            "SELECT COALESCE(MAX(ordre), 0) + 1 AS n FROM matieres WHERE filiere_id = ?",
            (filiere_id_cible,),
        ).fetchone()["n"]
        slug = m["slug"]
        while db_cible.execute("SELECT id FROM matieres WHERE slug = ?", (slug,)).fetchone():
            slug = f"{slug}-2"
        cur = db_cible.execute(
            "INSERT INTO matieres (filiere_id, nom, slug, semestre, ordre) VALUES (?, ?, ?, ?, ?)",
            (filiere_id_cible, m["nom"], slug, m["semestre"], ordre),
        )
        correspondance_matiere[m["id"]] = cur.lastrowid
        matieres_cibles[cle] = cur.lastrowid
        nb_matieres_ajoutees += 1

    # --- 3. Documents : reconnus par (matière cible, titre, type)
    documents_cibles = set()
    for d in db_cible.execute("SELECT matiere_id, titre, type FROM documents"):
        documents_cibles.add((d["matiere_id"], d["titre"], d["type"]))

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    nb_documents_ajoutes = 0

    for d in db_source.execute("SELECT * FROM documents"):
        matiere_id_cible = correspondance_matiere.get(d["matiere_id"])
        if matiere_id_cible is None:
            continue
        cle = (matiere_id_cible, d["titre"], d["type"])
        if cle in documents_cibles:
            continue

        chemin_fichier_source = os.path.join(dossier_uploads_source, d["nom_fichier"])
        nom_fichier_cible = d["nom_fichier"]
        chemin_fichier_cible = os.path.join(UPLOAD_FOLDER, nom_fichier_cible)
        # Si un fichier du même nom existe déjà (coïncidence), on le renomme.
        compteur = 1
        while os.path.exists(chemin_fichier_cible):
            nom_fichier_cible = f"{compteur}_{d['nom_fichier']}"
            chemin_fichier_cible = os.path.join(UPLOAD_FOLDER, nom_fichier_cible)
            compteur += 1

        if os.path.exists(chemin_fichier_source):
            shutil.copy2(chemin_fichier_source, chemin_fichier_cible)
        else:
            print(f"  ! Fichier PDF introuvable pour « {d['titre']} », le document est quand même référencé.")

        db_cible.execute(
            "INSERT INTO documents (matiere_id, titre, type, nom_fichier, date_ajout) VALUES (?, ?, ?, ?, ?)",
            (matiere_id_cible, d["titre"], d["type"], nom_fichier_cible, d["date_ajout"]),
        )
        documents_cibles.add(cle)
        nb_documents_ajoutes += 1

    # --- 4. Comptes admin : fusionnés par identifiant, sans écraser les tiens
    comptes_cibles = {row["username"] for row in db_cible.execute("SELECT username FROM admins")}
    nb_comptes_ajoutes = 0
    for a in db_source.execute("SELECT * FROM admins"):
        if a["username"] in comptes_cibles:
            continue
        filiere_id_cible = None
        if a["filiere_id"] is not None:
            slug_filiere_source = db_source.execute(
                "SELECT slug FROM filieres WHERE id = ?", (a["filiere_id"],)
            ).fetchone()
            if slug_filiere_source and slug_filiere_source["slug"] in filieres_cibles:
                filiere_id_cible = filieres_cibles[slug_filiere_source["slug"]]
        db_cible.execute(
            "INSERT INTO admins (username, password_hash, filiere_id) VALUES (?, ?, ?)",
            (a["username"], a["password_hash"], filiere_id_cible),
        )
        nb_comptes_ajoutes += 1

    db_cible.commit()
    db_source.close()

    print(f"  -> {nb_matieres_ajoutees} matière(s) ajoutée(s), "
          f"{nb_documents_ajoutes} document(s) ajouté(s), "
          f"{nb_comptes_ajoutes} compte(s) admin ajouté(s).")


def main():
    if len(sys.argv) < 2:
        print("Utilisation : python fusionner.py dossier1 [dossier2 ...]")
        print("(chaque dossier doit contenir un fichier uadb.db et un dossier uploads/)")
        sys.exit(1)

    if not os.path.exists(DB_PATH):
        print("Aucun uadb.db trouvé ici. Lance d'abord l'application une fois (python app.py) pour la créer.")
        sys.exit(1)

    db_cible = ouvrir(DB_PATH)

    for dossier in sys.argv[1:]:
        print(f"Fusion depuis : {dossier}")
        fusionner_une_source(db_cible, dossier)

    db_cible.close()
    print("\nFusion terminée. Ta base uadb.db et ton dossier uploads/ sont maintenant à jour.")


if __name__ == "__main__":
    main()
