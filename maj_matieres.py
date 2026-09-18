# -*- coding: utf-8 -*-
"""
Script de mise à jour des matières officielles
=================================================
À utiliser quand une nouvelle fiche officielle de formation a été ajoutée
dans la liste MATIERES_OFFICIELLES (dans app.py), et qu'on veut faire
apparaître ces nouvelles matières dans une base de données DÉJÀ existante,
sans rien perdre de ce qu'elle contient (documents, autres matières, etc.).

COMMENT S'EN SERVIR
--------------------
1. D'abord, fais ajouter la nouvelle filière/matières dans la liste
   MATIERES_OFFICIELLES au début de app.py (ou demande-le).
2. Lance simplement, depuis le dossier du projet :

     python maj_matieres.py

3. Le script ajoute uniquement ce qui manque. Il ne touche jamais aux
   matières ou documents déjà présents.
"""

import sqlite3
from app import DB_PATH, ajouter_matieres_officielles


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    nb_ajoutees = ajouter_matieres_officielles(db)
    db.close()

    if nb_ajoutees == 0:
        print("Rien à ajouter, ta base est déjà à jour.")
    else:
        print(f"{nb_ajoutees} nouvelle(s) matière(s) ajoutée(s) avec succès.")


if __name__ == "__main__":
    main()
