import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from config.settings import DATA_DIR

def generer_flux_evenements(nb_lignes=30):
    actions = ['CLICK_BOUTON', 'AJOUT_PANIER', 'VALIDATION_COMMANDE', 'ABONNEMENT_PREMIUM']
    types_compte = ['COURANT', 'EPARGNE', 'BUSINESS', None]
    noms = ["  ndiaye ", "fall", "DIOP ", "cissé", "sy"]
    
    events = []
    base_id = 550000
    
    for i in range(nb_lignes):
        # Création artificielle d'un doublon strict à l'index 3 pour tester la gouvernance de l'ETL
        if i == 3:
            transac_id = base_id + 2
        else:
            transac_id = base_id + i
            
        event = {
            "meta_data": {
                "transaction_id": transac_id,
                "date_insertion": "2026-07-07"
            },
            "user_info": {
                "nom": random.choice(noms),
                "type_compte": random.choice(types_compte)
            },
            "payload": {
                "action": random.choice(actions),
                # Simule un montant négatif aberrant à l'index 5 pour tester la qualité
                "montant": -7500 if i == 5 else random.choice([15000, 50000, 120000, 350000]),
                "date_evenement": (datetime.now() - timedelta(hours=random.randint(1, 12))).strftime("%Y/%m/%d %H:%M:%S")
            }
        }
        events.append(event)
        
    # Destination directe dans le dossier partagé avec le conteneur SFTP Docker
    output_path = DATA_DIR / "temp_sftp" / "evenements_app_daily.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=4)
        
    print(f"📦 [MOCK] 30 événements applicatifs simulés injectés dans la zone SFTP.")

if __name__ == "__main__":
    generer_flux_evenements()