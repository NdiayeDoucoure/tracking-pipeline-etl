import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DB_URL

logger = logging.getLogger("PipelineTracking")

def charger_dans_le_dwh(df_propre):
    logger.info("DÉMARRAGE DU CHARGEMENT - Connexion au Data Warehouse PostgreSQL...")
    
    if df_propre is None or df_propre.empty:
        logger.warning("Qualité Data : Le DataFrame fourni est vide. Annulation du chargement.")
        return False
        
    try:
        # 1. Création du moteur de connexion SQLAlchemy
        engine = create_engine(DB_URL)
        
        # On ouvre une transaction SQL sécurisée
        with engine.begin() as connexion:
            
            # --- ÉTAPE A : MISE À JOUR DE LA DIMENSION (dim_actions) ---
            logger.info("Mise à jour de la table de dimension 'dim_actions'...")
            
            # Extraction des actions uniques du flux Pandas
            actions_uniques = df_propre[['payload_action']].drop_duplicates()
            actions_uniques = actions_uniques.rename(columns={'payload_action': 'nom_action'})
            
            # Insertion des nouvelles actions dans la dimension avec gestion des conflits (ON CONFLICT DO NOTHING)  
            for action in actions_uniques['nom_action']:
                connexion.execute(
                    text("""
                        INSERT INTO dim_actions (nom_action) 
                        VALUES (:action) 
                        ON CONFLICT (nom_action) DO NOTHING
                    """),
                    {"action": action}
                )
            
            # --- ÉTAPE B : RÉCUPÉRATION DES CLÉS SUBSTITUÉES ---
            logger.info("Récupération des clés générées de la dimension...")
            dim_actions_db = pd.read_sql("SELECT action_key, nom_action FROM dim_actions", connexion)
            
            # --- ÉTAPE C : MAPPING ET PRÉPARATION DE LA TABLE DES FAITS ---
            # Jointure Pandas pour remplacer le texte 'payload_action' par sa clé numérique 'action_key'
            df_mappe = df_propre.merge(dim_actions_db, left_on='payload_action', right_on='nom_action')
            
            # Sélection stricte des colonnes pour la table des faits conforme au modèle
            df_faits = df_mappe[[
                'user_info_type_compte', 
                'action_key', 
                'volume_total_fcfa', 
                'nombre_evenements', 
                'date_traitement'
            ]]
            
            # --- ÉTAPE D : INJECTION DANS LA TABLE DES FAITS (fact_marketing_tracking) ---
            logger.info("Écriture incrémentale des indicateurs dans la table des faits...")
            df_faits.to_sql(
                name='fact_marketing_tracking',
                con=connexion,
                if_exists='append',
                index=False
            )
        
        logger.info("Chargement réussi ! Le modèle en étoile (Dimension + Faits) a été mis à jour.")
        return True
        
    except Exception as e:
        logger.critical(f"ERREUR FATALE LORS DU CHARGEMENT MODELE ETOILE : {str(e)}")
        raise e