# 📊 Pipeline ETL & Architecture Data Warehouse

Ce projet implémente une architecture Data complète et industrialisée. Il automatise la récupération de logs comportementaux bruts (format JSON) depuis un serveur sécurisé, applique des règles de gouvernance et de qualité de données, et alimente un entrepôt de données structuré en modèle en étoile pour de la Business Intelligence.

## 🛠️ Architecture Technique & Pipeline ETL

Le flux de données est orchestré de manière logicielle à travers 4 modules Python :

1. **La Source (`scripts/mock_generator.py`) :** Simule la génération quotidienne de logs de tracking (clics, achats, connexions) avec des anomalies intégrées (doublons, montants négatifs) et les dépose sur un serveur SFTP.
2. **L'Extraction (`scripts/extractor.py`) :** Initialise une connexion SSH/SFTP sécurisée via **Paramiko** pour rapatrier le flux JSON brut localement.
3. **La Transformation (`scripts/transformer.py`) :** Nettoie et fragmente la donnée au scalpel avec **Pandas** (suppression des doublons via `.drop_duplicates()`, redressement des anomalies financières à 0 FCFA, et agrégations des indicateurs).
4. **Le Chargement (`scripts/loader.py`) :** Pilote l'injection incrémentale et sécurisée dans l'entrepôt de données via **SQLAlchemy** en gérant les transactions.

---

## 📐 Conception de la Base de Données : Modélisation en Étoile (Kimball)

Pour garantir des performances analytiques optimales et éviter la redondance de texte, l'entrepôt de données **PostgreSQL** a été modélisé selon la méthodologie de Ralph Kimball (*Star Schema*) :

### 1. La Table de Dimension : `dim_actions`
* **Rôle :** Centralise le contexte textuel (les actions métiers de l'application).
* **Clé Substituée :** `action_key` (`SERIAL PRIMARY KEY`), indépendante des identifiants de l'application.
* **Mécanisme ETL :** Injection via l'instruction SQL `ON CONFLICT (nom_action) DO NOTHING` pour garantir l'unicité des dimensions et éviter les doublons.

### 2. La Table des Faits : `fact_marketing_tracking`
* **Rôle :** Stocke les métriques quantitatives et financières au centre de l'étoile.
* **Clé Étrangère :** `action_key INT REFERENCES dim_actions(action_key)`.
* **Mécanisme ETL :** Un mapping dynamique par jointure (`.merge()` sous Pandas) remplace le texte brut de l'application par la clé numérique correspondante de la dimension avant l'écriture en base, rendant la table des faits ultra-légère.

### 3. Restitution Business Intelligence (Power BI)
L'entrepôt PostgreSQL est connecté à **Power BI** où une relation de cardinalité **Plusieurs-à-un (*:1)** est activée de manière stricte entre la table des faits et la dimension. Les jointures se font instantanément en mémoire, permettant d'analyser les volumes financiers (`volume_total_fcfa`) selon les libellés explicites de la dimension.

---

## 🚀 Fonctionnalités Clés de Production
* **Conteneurisation (Docker) :** Isolation complète de l'infrastructure (serveur SFTP Atmoz et base PostgreSQL 15) via un fichier `docker-compose.yml`.
* **Traçabilité (Logging professionnel) :** Gestion centralisée des logs avec niveaux de criticité (`INFO`, `WARNING`, `ERROR`, `CRITICAL`) enregistrés dans un fichier permanent pour le monitoring de production.
* **Intégrité des données :** Gestion des connexions via des blocs `try/except` et utilisation de transactions SQL (`engine.begin()`) pour assurer un rollback complet en cas d'anomalie durant le chargement.