import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from config.settings import FILE_LOCAL_TMP

logger = logging.getLogger("PipelineTracking")

def transformer_donnees_brutes():
    logger.info("DÉMARRAGE DES TRANSFORMATIONS - Traitement au scalpel avec Pandas...")
    
    if not FILE_LOCAL_TMP.exists():
        logger.error(f"Erreur de flux : Le fichier temporaire {FILE_LOCAL_TMP} est introuvable.")
        raise FileNotFoundError("Impossible de transformer un fichier inexistant.")
        
    # 1. Chargement du fichier JSON rapatrié
    df_raw = pd.read_json(FILE_LOCAL_TMP)
    logger.info(f"Fichier brut chargé en mémoire : {len(df_raw)} lignes détectées.")
    
    # 2. Aplatissement (Flattening) des structures JSON imbriquées
    # Permet de passer de sous-dictionnaires à de vraies colonnes distinctes
    df_flat = pd.json_normalize(df_raw.to_dict(orient='records'))
    
    # Normalisation propre des noms de colonnes pour éviter les points '.' complexes en SQL
    df_flat.columns = [col.replace('.', '_') for col in df_flat.columns]
    
    # 3. GOUVERNANCE DATA : Élimination des doublons techniques sur l'ID Unique de transaction
    nb_lignes_avant_doublons = len(df_flat)
    df_flat = df_flat.drop_duplicates(subset=['meta_data_transaction_id'], keep='first')
    nb_doublons = nb_lignes_avant_doublons - len(df_flat)
    if nb_doublons > 0:
        logger.warning(f"Gouvernance Data : {nb_doublons} doublon(s) technique(s) identifié(s) et supprimé(s).")
        
    # 4. QUALITÉ DATA : Nettoyage textuel et gestion des valeurs manquantes
    # Nettoyage des espaces blancs inutiles et passage en majuscules pour uniformiser les saisies
    df_flat['user_info_nom'] = df_flat['user_info_nom'].str.strip().str.upper()
    
    # Remplacement des valeurs manquantes (None/NaN) par une chaîne explicite pour le reporting BI
    df_flat['user_info_type_compte'] = df_flat['user_info_type_compte'].fillna('NON_SPECIFIE')
    
    # 5. CONFORMITÉ FINANCIÈRE : Redressement des montants aberrants (Masques Booléens Numpy)
    # En banque, un montant de transaction applicative ne peut pas être négatif
    anomalies_montant = df_flat[df_flat['payload_montant'] < 0]
    if not anomalies_montant.empty:
        logger.error(f"Qualité Financière : {len(anomalies_montant)} transaction(s) avec montant négatif détectée(s). Application de la règle de redressement à 0 FCFA.")
        # Redressement chirurgical direct sans boucle lente
        df_flat.loc[df_flat['payload_montant'] < 0, 'payload_montant'] = 0

    # 6. STANDARDISATION DES DATES
    df_flat['payload_date_evenement'] = pd.to_datetime(df_flat['payload_date_evenement'], errors='coerce')
    # On élimine les lignes si la date de l'événement n'est pas une date valide après conversion
    df_flat = df_flat.dropna(subset=['payload_date_evenement'])

    # 7. AGRÉGATION BI : Préparation du modèle de données pour l'entrepôt (Data Warehouse)
    # On groupe par type de compte et par type d'action pour alléger le stockage et accélérer Power BI
    df_metrics = df_flat.groupby(['user_info_type_compte', 'payload_action']).agg(
        volume_total_fcfa=('payload_montant', 'sum'),
        nombre_evenements=('meta_data_transaction_id', 'count')
    ).reset_index()
    
    # Ajout d'une colonne de traçabilité temporelle pour savoir quand la donnée a été injectée
    df_metrics['date_traitement'] = datetime.now().date()
    
    logger.info(f"Transformations terminées. Données condensées en {len(df_metrics)} indicateurs clés.")
    return df_metrics

if __name__ == "__main__":
    # Test à blanc pour vérifier que la transformation fonctionne correctement
    try:
        df_test = transformer_donnees_brutes()
        print("\n--- Aperçu des données prêtes pour le Data Warehouse ---")
        print(df_test.to_string())
    except Exception as e:
        print(f"Erreur lors du test de transformation : {e}")