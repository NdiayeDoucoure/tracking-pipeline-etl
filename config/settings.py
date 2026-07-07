import os
from pathlib import Path

# Chemins de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Fichiers locaux de transit
FILE_LOCAL_TMP = DATA_DIR / "downloaded_events.json"
LOG_FILE = LOG_DIR / "pipeline_tracking.log"

# Configurations de l'infrastructure (Docker)
SFTP_HOST = "127.0.0.1"
SFTP_PORT = 2222
SFTP_USER = "user_data_office"
SFTP_PASS = "MotDePasseSecurise2026"
SFTP_REMOTE_PATH = "upload/evenements_app_daily.json"

DB_URL = "postgresql://ing_data:PassDwhCbao@localhost:5432/dwh_decisionnel"