# UADB Study Hub — Phase 1

Plateforme de ressources pédagogiques pour les étudiants de l'Université
Alioune Diop de Bambey (UADB). Cette Phase 1 couvre :

- la page d'accueil avec accès rapides et recherche
- le niveau **L1**, filière **MPCI**, avec les 8 matières confirmées
- l'affichage des ressources (Cours, TD, Exercices, Corrigés, Annales, Résumés, Examens, Autres)
- la recherche par mot-clé
- l'espace administrateur (connexion, ajout/modification/suppression de matières et de documents PDF)

Les niveaux **L2** (MPI, PC, SID) et **L3** sont déjà créés dans la structure
mais restent vides tant que leurs programmes ne sont pas confirmés — aucune
matière n'a été inventée, conformément au cahier des charges.

## 1. Installation

Il faut Python 3.9 ou plus récent.

```bash
cd uadb_study_hub
python3 -m venv venv
source venv/bin/activate        # sous Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Lancer le site en local

```bash
python app.py
```

Le site est alors disponible sur **http://localhost:5000** (accessible aussi
depuis un téléphone sur le même réseau Wi-Fi via l'adresse IP de l'ordinateur,
par exemple `http://192.168.1.23:5000`).

Au premier lancement, la base de données `uadb.db` est créée automatiquement
et remplie avec L1 MPCI et ses 8 matières.

## 3. Se connecter à l'espace administrateur

Rendez-vous sur `/admin/connexion` (lien « Administration » en haut à droite).

- **Identifiant :** `admin`
- **Mot de passe :** `uadb2026`

**Important : changez ce mot de passe avant toute mise en ligne réelle.**
Le plus simple est d'ouvrir une console Python et de générer un nouveau
mot de passe :

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash("votre-nouveau-mot-de-passe"))
```

Puis remplacez le `password_hash` de la ligne `admin` dans la table
`admins` de `uadb.db` (avec un outil comme DB Browser for SQLite, ou une
petite commande SQL).

## 4. Structure du projet

```
uadb_study_hub/
├── app.py                  # routes Flask + logique de la base de données
├── requirements.txt
├── uadb.db                 # créé automatiquement au premier lancement
├── uploads/                 # fichiers PDF envoyés par l'administrateur
├── templates/
│   ├── base.html            # en-tête, pied de page, styles communs
│   ├── index.html           # accueil
│   ├── niveau.html          # liste des filières d'un niveau
│   ├── filiere.html         # liste des matières d'une filière
│   ├── matiere.html         # documents d'une matière, groupés par type
│   ├── recherche.html
│   ├── login.html
│   └── admin/
│       ├── dashboard.html
│       ├── matiere_form.html
│       └── document_form.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## 5. Ajouter du contenu

1. Connectez-vous à l'espace admin.
2. « + Ajouter une matière » si la matière n'existe pas encore (choisissez sa filière).
3. « + Ajouter un document » : titre, type (Cours, TD, Corrigés…), matière, puis le fichier PDF (25 Mo max).

## 6. Étapes suivantes (Phase 2 et 3)

- **Phase 2** : renseigner les matières réelles de L2 MPI, L2 PC et L2 SID
  dès que les programmes seront confirmés (il suffit d'utiliser
  « + Ajouter une matière » dans l'espace admin — aucune modification de
  code n'est nécessaire, la structure est déjà prête).
- **Phase 3** : L3, comptes étudiants, favoris, notifications, statistiques.

## 7. Mise en ligne (déploiement)

Pour que les étudiants y accèdent depuis Internet (et pas seulement en local),
il faudra héberger l'application sur un service comme PythonAnywhere, Render
ou un VPS, avec un serveur de production (par exemple `gunicorn`) à la place
du serveur de développement Flask. Cette étape n'est pas nécessaire pour
tester la Phase 1 avec quelques étudiants sur le même réseau.
