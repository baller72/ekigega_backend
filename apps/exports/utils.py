import csv
import pandas as pd
from io import BytesIO
from django.core.files.base import ContentFile
from apps.exports.models import ExportHistory

# Pour PDF, on peut utliser reportlab ou weasyprint si besoin

def export_to_csv(queryset, fields, filename="export.csv"):
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(fields)
    for obj in queryset:
        writer.writerow([getattr(obj, f, '') for f in fields])
    content = ContentFile(output.getvalue().encode('utf-8'))
    return filename, content

def export_to_excel(queryset, fields, filename="export.xlsx"):
    data = [{f: getattr(obj, f) for f in fields} for obj in queryset]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Export")
    content = ContentFile(output.getvalue())
    return filename, content