import csv
from io import StringIO
from .models import Catalog

def import_catalog_from_csv(csv_file):
    """
    Importuje katalogové položky z CSV a vrací výsledek s podrobnými chybami.
    """
    result = {'added': 0, 'updated': 0, 'errors': []}
    try:
        file_data = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(file_data))

        for row_index, row in enumerate(csv_reader, start=1):
            catalog_number = row.get('katalogove_cislo')
            if not catalog_number:
                result['errors'].append(f"Řádek {row_index}: Chybí katalogové číslo.")
                continue

            try:
                defaults = {
                    'name': row.get('nazev', '').strip(),
                    'points': int(row.get('body', 0)),
                    'price': float(row.get('cena', 0.0)),
                    'duration_minutes': int(row.get('cas', 0)),
                    'notes': row.get('poznamky', '').strip(),
                    'is_active': row.get('is_active', 'True').lower() == 'true',
                }

                obj, created = Catalog.objects.update_or_create(
                    catalog_number=catalog_number, defaults=defaults
                )

                if created:
                    result['added'] += 1
                else:
                    result['updated'] += 1
            except Exception as e:
                result['errors'].append(f"Řádek {row_index}: {str(e)}")

    except Exception as e:
        result['errors'].append(f"Obecná chyba: {str(e)}")

    return result


def export_catalog_to_csv(active_only=False):
    """
    Exportuje katalogové položky do CSV. Pokud `active_only=True`, exportuje pouze aktivní položky.
    """
    output = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(['katalogove_cislo', 'nazev', 'body', 'cena', 'cas', 'poznamky', 'is_active'])

    query = Catalog.objects.all()
    if active_only:
        query = query.filter(is_active=True)

    for catalog in query:
        csv_writer.writerow([
            catalog.catalog_number,
            catalog.name,
            catalog.points,
            catalog.price,
            catalog.duration_minutes,
            catalog.notes,
            catalog.is_active,
        ])

    output.seek(0)
    return output.getvalue()

