import logging
from config.settings import LOG_FILE
from scripts.extractor import extraire_depuis_sftp
from scripts.transformer import transformer_donnees_brutes
from scripts.loader import charger_dans_le_dwh

# =====================================================================
# SETUP DU SYSTÈME DE LOGS PROFESSIONNEL
# =====================================================================
logger = logging.getLogger("PipelineTracking")
logger.setLevel(logging.INFO)

# Empêcher la duplication des logs si le script est importé
if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

    # Handler pour écrire les traces dans un fichier permanent (.log)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler pour afficher également les logs en direct dans le terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# =====================================================================
# ORCHESTRATION DU PIPELINE BI (RUN)
# =====================================================================
def run_pipeline():
    logger.info("==================================================================")
    logger.info("🚀 LANCEMENT DU PIPELINE D'INGESTION ET DE TRACKING MARKETING")
    logger.info("==================================================================")
    
    try:
        # Étape 1 : Extraction du fichier depuis le SFTP Docker
        extraire_depuis_sftp()
        print("\n" + "-"*50 + "\n")
        
        # Étape 2 : Nettoyage et transformation chirurgicale avec Pandas
        df_indicateurs = transformer_donnees_brutes()
        print("\n" + "-"*50 + "\n")
        
        # Étape 3 : Chargement final dans l'entrepôt de données PostgreSQL
        charger_dans_le_dwh(df_indicateurs)
        
        logger.info("==================================================================")
        logger.info("✅ PIPELINE EXÉCUTÉ AVEC SUCCÈS À 100% - TOUS LES VOYANTS SONT VERTS")
        logger.info("==================================================================")
        
    except Exception as pipeline_error:
        logger.error("❌ LE PIPELINE AÉROPORTÉ A SOUFFERT D'UN CRASH CRITIQUE.")
        logger.error(f"Détails de l'incident : {str(pipeline_error)}")

if __name__ == "__main__":
    run_pipeline()