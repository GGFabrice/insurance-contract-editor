Insurance Contract Editor
Application de gestion et d’édition des contrats d’assurance santé collective.
Le projet a pour objectif d’automatiser la gestion des contrats, des assurés et des mouvements d’effectif, ainsi que le calcul des primes d’incorporation et des ristournes lors des retraits.
________________________________________
1. Présentation du projet
Insurance Contract Editor est une application backend destinée à faciliter la gestion des contrats d’assurance santé collective.
L’application permet notamment de :
•	rechercher les souscripteurs ;
•	consulter leurs contrats ;
•	consulter les assurés rattachés à un contrat ;
•	enregistrer les mouvements d’effectif ;
•	gérer les incorporations ;
•	gérer les retraits ;
•	calculer automatiquement les primes d’incorporation ;
•	calculer automatiquement les ristournes de retrait ;
•	consulter le détail complet d’un mouvement ;
•	préparer les données nécessaires à la génération future d’un avenant.
Le projet est développé progressivement afin d’intégrer les différentes règles métier de l’assurance santé.
________________________________________
2. Objectif fonctionnel
L’objectif final est de disposer d’un outil permettant à un gestionnaire de contrat d’assurance santé de :
1.	sélectionner un souscripteur ;
2.	consulter ses contrats ;
3.	sélectionner un contrat ;
4.	consulter les assurés du contrat ;
5.	enregistrer une incorporation ou un retrait ;
6.	calculer automatiquement le montant correspondant ;
7.	contrôler les informations du mouvement ;
8.	générer automatiquement un document d’avenant à partir d’un modèle ;
9.	conserver l’historique des mouvements.
________________________________________
3. Stack technique
Backend
•	Python
•	FastAPI
•	SQLAlchemy
•	PostgreSQL
•	Uvicorn
Base de données
•	PostgreSQL
•	SQLAlchemy ORM
Documentation API
FastAPI génère automatiquement une documentation interactive Swagger/OpenAPI.
Une fois l’application démarrée :
http://127.0.0.1:8000/docs
________________________________________
4. Architecture du projet
insurance-contract-editor/
│
├── backend/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── calculs.py
│   └── test_database.py
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
________________________________________
5. Modèle de données
Le modèle actuel comprend principalement quatre entités métier.
Souscripteur
Un souscripteur représente l’entreprise ou l’organisation ayant souscrit le contrat.
Informations principales :
•	identifiant ;
•	code souscripteur ;
•	raison sociale ;
•	adresse ;
•	téléphone ;
•	email.
Contrat
Le contrat contient les informations relatives à la police d’assurance.
Informations principales :
•	souscripteur ;
•	compagnie ;
•	code compagnie ;
•	intermédiaire ;
•	numéro de police ;
•	nature du risque ;
•	période de validité ;
•	prime nette par personne ;
•	accessoire ;
•	taxe ;
•	statut du contrat.
Assuré
Un assuré est rattaché à un contrat.
Informations principales :
•	numéro assuré ;
•	nom ;
•	prénom ;
•	date de naissance ;
•	sexe ;
•	lien de parenté ;
•	date d’entrée ;
•	date de sortie ;
•	statut actif.
Mouvement d’effectif
Un mouvement permet d’enregistrer une modification de l’effectif assuré.
Deux types de mouvements sont actuellement supportés :
INCORPORATION
RETRAIT
Informations principales :
•	contrat ;
•	assuré ;
•	type de mouvement ;
•	date du mouvement ;
•	début de période ;
•	fin de période ;
•	commentaire.
________________________________________
6. API actuellement disponible
Accueil
GET /
Retourne l’état de l’application.
________________________________________
Recherche de souscripteurs
GET /api/souscripteurs/recherche?nom=NSIA
Permet de rechercher un souscripteur à partir de sa raison sociale.
________________________________________
Contrats d’un souscripteur
GET /api/souscripteurs/{souscripteur_id}/contrats
Exemple :
GET /api/souscripteurs/1/contrats
Retourne les contrats associés au souscripteur.
________________________________________
Assurés d’un contrat
GET /api/contrats/{contrat_id}/assures
Exemple :
GET /api/contrats/1/assures
Retourne la liste des assurés rattachés au contrat.
________________________________________
Mouvements d’un contrat
GET /api/contrats/{contrat_id}/mouvements
Exemple :
GET /api/contrats/1/mouvements
Retourne l’historique des mouvements du contrat.
________________________________________
Mouvements d’un assuré
GET /api/assures/{assure_id}/mouvements
Exemple :
GET /api/assures/1/mouvements
Retourne l’historique des mouvements d’un assuré.
________________________________________
Création d’un mouvement
POST /api/mouvements
Les paramètres permettent notamment de renseigner :
•	contrat ;
•	assuré ;
•	type de mouvement ;
•	date du mouvement ;
•	période ;
•	commentaire.
Les types autorisés sont :
INCORPORATION
RETRAIT
________________________________________
Détail d’un mouvement
GET /api/mouvements/{mouvement_id}
Cet endpoint retourne :
•	le mouvement ;
•	l’assuré ;
•	le contrat ;
•	le souscripteur ;
•	le calcul financier.
Exemple :
GET /api/mouvements/8
________________________________________
7. Règles de calcul actuellement implémentées
Le calcul actuel fonctionne sur une base mensuelle.
7.1 Incorporation
Pour une incorporation, le mois de la date d’effet est considéré comme dû.
Exemple :
Date d'effet : 17/08/2026
Fin du contrat : 31/12/2026
Les mois pris en compte sont :
Août
Septembre
Octobre
Novembre
Décembre
Soit :
5 mois
La prime mensuelle est calculée ainsi :
Prime mensuelle = Prime annuelle / 12
Puis :
Prime d'incorporation = Prime mensuelle × Nombre de mois
Exemple avec une prime annuelle de 150 000 FCFA :
150 000 / 12 = 12 500 FCFA
12 500 × 5 = 62 500 FCFA
________________________________________
7.2 Retrait
Pour un retrait, le mois du retrait reste dû.
La ristourne commence donc le mois suivant la date du retrait.
Exemple :
Date de retrait : 05/09/2026
Fin du contrat : 31/12/2026
Le mois de septembre reste dû.
La ristourne concerne :
Octobre
Novembre
Décembre
Soit :
3 mois
Avec une prime annuelle de 150 000 FCFA :
Prime mensuelle = 150 000 / 12
Prime mensuelle = 12 500 FCFA

Ristourne = 12 500 × 3
Ristourne = 37 500 FCFA
Dans l’application, la ristourne est présentée comme une valeur négative :
-37 500 FCFA
Cette convention permet de distinguer clairement une prime supplémentaire d’une ristourne.
________________________________________
8. Tests réalisés
Les principales fonctionnalités ont été testées avec succès.
Test des modèles
python -c "from backend.models import Souscripteur, Contrat, Assure, MouvementEffectif; print('MODELES OK')"
Résultat :
MODELES OK
Vérification syntaxique
python -m py_compile backend/main.py
La compilation s’est terminée sans erreur.
Test d’une incorporation
Une incorporation de l’assuré a permis d’obtenir automatiquement :
nombre_mois = 5
prime_mensuelle = 12 500 FCFA
montant = 62 500 FCFA
Test d’un retrait
Un retrait effectué le 05/09/2026 a permis d’obtenir :
nombre_mois_ristourne = 3
prime_mensuelle = 12 500 FCFA
montant_ristourne = -37 500 FCFA
________________________________________
9. Installation
Cloner le projet
git clone https://github.com/GGFabrice/insurance-contract-editor.git
cd insurance-contract-editor
Créer l’environnement virtuel
Sous Windows :
python -m venv .venv
Activer l’environnement
.\.venv\Scripts\Activate.ps1
Installer les dépendances
pip install -r requirements.txt
________________________________________
10. Configuration de la base de données
Le projet utilise PostgreSQL.
Les variables de connexion doivent être configurées dans le fichier .env.
Un exemple de configuration est disponible dans :
.env.example
Le fichier .env ne doit pas être versionné dans Git.
________________________________________
11. Lancement de l’application
Depuis la racine du projet :
uvicorn backend.main:app --reload
L’application est alors accessible à :
http://127.0.0.1:8000
Documentation Swagger :
http://127.0.0.1:8000/docs
________________________________________
12. État actuel du projet
Fonctionnalités terminées
☒	Configuration du projet FastAPI
☒	Connexion PostgreSQL
☒	Modèles SQLAlchemy
☒	Gestion des souscripteurs
☒	Gestion des contrats
☒	Gestion des assurés
☒	Gestion des mouvements d’effectif
☒	Incorporation
☒	Retrait
☒	Calcul mensuel des incorporations
☒	Calcul mensuel des ristournes
☒	Ristourne négative
☒	Consultation du détail d’un mouvement
☒	Documentation Swagger
☒	Versionnement Git
☒	Sauvegarde sur GitHub
________________________________________
13. Prochaines étapes
Les prochaines évolutions prévues sont :
Règles métier
☐	Calcul de l’âge de l’assuré
☐	Gestion des catégories d’assurés
☐	Gestion des principaux, conjoints et enfants
☐	Gestion des collèges
☐	Gestion des garanties
☐	Gestion des conditions d’assurabilité
☐	Gestion de la surprime d’âge
☐	Gestion du prorata selon les règles métier
☐	Calcul des accessoires
☐	Calcul des taxes
☐	Calcul du montant total
Gestion documentaire
☐	Intégration du modèle Word d’avenant
☐	Identification des champs dynamiques
☐	Remplissage automatique du modèle
☐	Génération automatique de l’avenant
☐	Export du document
☐	Historisation des avenants
Interface utilisateur
☐	Création de l’interface web
☐	Recherche des souscripteurs
☐	Sélection d’un contrat
☐	Consultation des assurés
☐	Saisie d’un mouvement
☐	Affichage du calcul
☐	Validation du mouvement
☐	Génération de l’avenant
________________________________________
14. Structure cible du processus
Le processus cible de l’application est :
Souscripteur
     │
     ▼
Contrat
     │
     ▼
Assuré
     │
     ▼
Mouvement d'effectif
     │
     ├── INCORPORATION
     │       │
     │       ▼
     │   Calcul de prime
     │
     └── RETRAIT
             │
             ▼
        Calcul de ristourne
             │
             ▼
       Calcul financier
             │
             ▼
       Génération avenant
________________________________________
15. Version du projet
Version actuelle :
1.0.0
Projet en cours de développement.
________________________________________
16. Auteur
GGFabrice
GitHub :
https://github.com/GGFabrice
Dépôt du projet :
https://github.com/GGFabrice/insurance-contract-editor
