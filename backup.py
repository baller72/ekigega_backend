import datetime
import json
import uuid

from apps.commerce.models import Categorie

# Récupérer les données
data = list(Categorie.objects.all().values())

# Fonction de conversion pour JSON
def convert_types(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} non serializable")

# Sauvegarder dans JSON
with open("unite_mesure_backup.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4, default=convert_types)

print(f"{len(data)} unités sauvegardées dans unite_mesure_backup.json")

###################################################################################################

# Lire le fichier JSON
with open("unite_mesure_backup.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Recréer les objets
objs = [Categorie(**item) for item in data]

# Insérer dans la base
Categorie.objects.bulk_create(objs)
print(f"{len(objs)} unités restaurées !")


