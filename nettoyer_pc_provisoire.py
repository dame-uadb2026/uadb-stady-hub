# -*- coding: utf-8 -*-
"""
Script ponctuel : retire les anciennes matières provisoires de L2 PC
(semestres 3 et 4), remplacées par la liste officielle confirmée.

Sécurité : une matière n'est supprimée QUE si elle ne contient aucun
document. Si un document a déjà été ajouté dedans, elle est laissée en
place (avec un message d'avertissement) pour ne rien perdre.

Utilisation :
    python nettoyer_pc_provisoire.py
"""

import sqlite3
from app import DB_PATH

# Anciens noms (provisoires, tirés d'emplois du temps) qui ne font plus
# partie de la liste officielle.
NOMS_A_RETIRER_S3 = [
    "Analyse",
    "Algèbre",
    "Algorithmique et structures de données en C",
    "Anglais scientifique",
]
NOMS_A_RETIRER_S4 = [
    "Électromagnétisme dans le vide",
    "Mécanique du solide",
    "Probabilités et statistiques",
    "Calcul différentiel et intégral",
    "Algorithmique et structures de données en C",
    "Biochimie structurale",
    "Anglais scientifique",
]


def retirer(cur, pc_id, semestre, noms):
    nb_supprimees = 0
    nb_conservees = 0
    for nom in noms:
        matiere = cur.execute(
            "SELECT id FROM matieres WHERE filiere_id = ? AND semestre = ? AND nom = ?",
            (pc_id, semestre, nom),
        ).fetchone()
        if not matiere:
            continue
        nb_docs = cur.execute(
            "SELECT COUNT(*) AS n FROM documents WHERE matiere_id = ?", (matiere["id"],)
        ).fetchone()["n"]
        if nb_docs > 0:
            print(f"  ⚠ Semestre {semestre} — '{nom}' contient {nb_docs} document(s), non supprimée.")
            nb_conservees += 1
        else:
            cur.execute("DELETE FROM matieres WHERE id = ?", (matiere["id"],))
            nb_supprimees += 1
    return nb_supprimees, nb_conservees


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    pc_row = cur.execute("SELECT id FROM filieres WHERE slug = 'pc'").fetchone()
    if not pc_row:
        print("Filière PC introuvable, rien à faire.")
        return
    pc_id = pc_row["id"]

    s3_sup, s3_cons = retirer(cur, pc_id, 3, NOMS_A_RETIRER_S3)
    s4_sup, s4_cons = retirer(cur, pc_id, 4, NOMS_A_RETIRER_S4)

    db.commit()
    db.close()
    total_sup = s3_sup + s4_sup
    total_cons = s3_cons + s4_cons
    print(f"\n{total_sup} matière(s) retirée(s), {total_cons} conservée(s) (car déjà utilisée(s)).")
    print("Lance maintenant 'python maj_matieres.py' pour ajouter la liste officielle.")


if __name__ == "__main__":
    main()
