import paramiko
import logging
from config.settings import (
    SFTP_HOST, SFTP_PORT, SFTP_USER, SFTP_PASS, 
    SFTP_REMOTE_PATH, FILE_LOCAL_TMP
)
logger = logging.getLogger("PipelineTracking")

def extraire_depuis_sftp():
    logger.info("DÉMARRAGE DE L'EXTRACTION - Connexion au serveur SFTP ...")
    
    transport = None
    sftp = None
    
    try:
        # 1. Initialisation du protocole de transport SSH
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        
        # 2. Ouverture du client SFTP sur le canal SSH
        sftp = paramiko.SFTPClient.from_transport(transport)
        logger.info("Connexion SFTP établie avec succès.")
        
        # 3. Rapatriement du fichier distant vers notre dossier local temporaire
        logger.info(f"Téléchargement du fichier distant : {SFTP_REMOTE_PATH}")
        sftp.get(SFTP_REMOTE_PATH, str(FILE_LOCAL_TMP))
        
        logger.info(f"Extraction réussie. Fichier sauvegardé localement sous : {FILE_LOCAL_TMP}")
        return True
        
    except Exception as e:
        # Si la connexion échoue (ex: mauvaise IP ou serveur Docker éteint), on loggue l'erreur au niveau CRITICAL
        logger.critical(f"ERREUR FATALE LORS DE L'EXTRACTION SFTP : {str(e)}")
        raise e
        
    finally:
        # On ferme les connexions réseau, même en cas de plantage
        if sftp:
            sftp.close()
            logger.info("Canal SFTP fermé.")
        if transport:
            transport.close()
            logger.info("Connexion de transport SSH fermée.")