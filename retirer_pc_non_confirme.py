# -*- coding: utf-8 -*-
"""
Script ponctuel : retire les 9 matières de L2 PC (semestre 3) qui avaient
été ajoutées à partir d'un emploi du temps, en attendant la vraie fiche
officielle de la formation.

Sécurité : une matière n'est supprimée QUE si elle ne contient aucun
document. Si tu as déjà ajouté un document dedans, elle est laissée en
place (avec un message d'avertissement) pour ne rien perdre.

Utilisation :
    python retirer_pc_non_confirme.py
"""

import sqlite3
from app import DB_PATH

NOMS_A_RETIRER = [
    "Analyse",
    "Algèbre",
    "Chimie minérale",
    "Chimie organique",
    "Cinétique chimique",
    "Mécanique quantique",
    "Thermodynamique physique",
    "Algorithmique et structures de données en C",
    "Anglais scientifique",
]


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    pc_row = cur.execute("SELECT id FROM filieres WHERE slug = 'pc'").fetchone()
    if not pc_row:
        print("Filière PC introuvable, rien à faire.")
        return
    pc_id = pc_row["id"]

    nb_supprimees = 0
    nb_conservees = 0
    for nom in NOMS_A_RETIRER:
        matiere = cur.execute(
            "SELECT id FROM matieres WHERE filiere_id = ? AND nom = ?", (pc_id, nom)
        ).fetchone()
        if not matiere:
            continue
        nb_docs = cur.execute(
            "SELECT COUNT(*) AS n FROM documents WHERE matiere_id = ?", (matiere["id"],)
        ).fetchone()["n"]
        if nb_docs > 0:
            print(f"  ⚠ '{nom}' contient {nb_docs} document(s), non supprimée.")
            nb_conservees += 1
        else:
            cur.execute("DELETE FROM matieres WHERE id = ?", (matiere["id"],))
            nb_supprimees += 1

    db.commit()
    db.close()
    print(f"\n{nb_supprimees} matière(s) retirée(s), {nb_conservees} conservée(s) (car déjà utilisée(s)).")


if __name__ == "__main__":
    main()
