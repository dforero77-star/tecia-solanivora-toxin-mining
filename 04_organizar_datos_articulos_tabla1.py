import re
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from google.colab import files

# 1. SUBIR EL ARCHIVO DIRECTAMENTE DESDE TU COMPUTADORA
print("Selecciona tu archivo CSV de Scopus desde tu computadora:")
uploaded = files.upload()
archivo_csv = list(uploaded.keys())[0]

# 2. EXTRACCIÓN EXACTA DE LOS 49 ARTÍCULOS DE SCOPUS
with open(archivo_csv, "r", encoding="utf-8-sig") as f:
    raw_lines = f.read().splitlines()

records = []
for line in raw_lines[1:]:
    line = re.sub(r';+$', '', line.strip())
    if not line:
        continue
    # Separador real de columnas en tu archivo exportado por Excel/Scopus: ,""
    parts = line.split(',""')
    if len(parts) >= 6:
        authors_raw = parts[0].lstrip('"')
        clean_parts = [re.sub(r'"+$', '', p) for p in parts]

        title = clean_parts[3]
        year = clean_parts[4]
        journal = clean_parts[5]
        rest = " ".join(clean_parts[6:])

        first_author = authors_raw.split(";")[0].strip()
        authors_fmt = f"{first_author} et al. ({year})" if ";" in authors_raw else f"{first_author} ({year})"

        records.append({
            "Authors & Year": authors_fmt,
            "Article Title": title,
            "Journal": journal,
            "Year": year,
            "Full_Text": f"{title} {rest}".lower()
        })

df_scopus = pd.DataFrame(records)
print(f"\n¡Artículos recuperados correctamente!: {len(df_scopus)}")

# 3. CLASIFICACIÓN AUTOMÁTICA DE COLUMNAS DE LA TABLA
def infer_pest(text):
    if "tecia solanivora" in text or "guatemalan potato moth" in text:
        return "Tecia solanivora"
    elif "phthorimaea" in text or "potato tuber moth" in text:
        return "Phthorimaea operculella / Gelechiidae"
    elif "lepidoptera" in text or "spodoptera" in text or "helicoverpa" in text:
        return "Lepidoptera"
    elif "insect" in text or "pest" in text or "arthropod" in text:
        return "Insecta / Agricultural pests"
    return "Multi-taxa / Venomous & pathogenic models"

def infer_agent(text):
    agents = []
    for tax in ["Bacillus thuringiensis", "Enterobacter", "Serratia", "Rahnella", "Pseudomonas", "Photorhabdus", "Xenorhabdus", "Francisella", "Campylobacter"]:
        if tax.lower() in text:
            agents.append(tax)
    if agents:
        return ", ".join(agents)
    if "conotoxin" in text or "venom" in text or "scorpion" in text or "snail" in text:
        return "Venom peptides / Conotoxins"
    if "toxin" in text or "cry" in text or "pore-forming" in text:
        return "Bacterial insecticidal toxins"
    return "Entomopathogenic bacteria / Genomic targets"

def infer_method(text):
    if "machine learning" in text or "ai " in text or "unsupervised" in text or "pipeline" in text or "bioinformatic" in text or "in silico" in text:
        return "In Silico / Computational & ML Mining"
    elif "genome" in text or "genomic" in text or "transcriptom" in text or "sequencing" in text:
        return "Comparative Genomics / Transcriptomics"
    elif "bioassay" in text or "mortality" in text or "larvae" in text:
        return "Bioassays + Molecular Profiling"
    return "Molecular / Functional Characterization"

def infer_relevance(text, title):
    if "tecia solanivora" in text:
        return "Direct reference on T. solanivora biocontrol, gut microbiota, or susceptibility."
    elif "pipeline" in text or "mining" in text or "in silico" in text or "machine learning" in text:
        return "Supports computational genome mining and discovery of novel toxin architectures."
    elif "pore" in text or "toxin" in text or "venom" in text or "virulen" in text:
        return "Provides structural and mechanistic insight into pore-forming or secreted toxins."
    return f"Contextualizes comparative genomics relevant to {title[:52]}..."

# 4. CONSTRUCCIÓN DEL EXCEL CON EL FORMATO DE LA IMAGEN
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Table_S1_Literature_Search"
ws.views.sheetView[0].showGridLines = True

DARK_HEADER = "1F3A52"
ZEBRA_FILL = "F2F5F9"
BORDER_COLOR = "CBD5E1"

font_title = Font(name="Arial", size=12, bold=True, color="1F3A52")
font_subtitle = Font(name="Arial", size=9.5, italic=True, color="475569")
font_header = Font(name="Arial", size=10, bold=True, color="FFFFFF")
font_body = Font(name="Arial", size=9.5, color="0F172A")
font_italic = Font(name="Arial", size=9.5, italic=True, color="0F172A")

thin = Side(style="thin", color=BORDER_COLOR)
med_navy = Side(style="medium", color=DARK_HEADER)
cell_border = Border(left=thin, right=thin, top=thin, bottom=thin)
header_border = Border(left=thin, right=thin, top=med_navy, bottom=med_navy)

# Títulos superiores (Filas 1 y 2)
ws["A1"] = f"Tabla 1. Matriz de revisión sistemática de la literatura (Scopus 2015–2026; N = {len(df_scopus)} artículos examinados)"
ws["A1"].font = font_title
ws["A2"] = "Consulta de búsqueda: TITLE-ABS-KEY(('Tecia solanivora' OR 'polilla guatemalteca de la papa') AND ('biocontrol' OR 'control biológico' OR 'entomopatógeno' OR 'toxina' OR 'genom*'))."
ws["A2"].font = font_subtitle

# Encabezados (Fila 4)
headers = ["Ref_ID", "Authors & Year", "Article Title", "Journal", "Target Pest", "Biocontrol Agent / Taxa", "Methodology Type", "Key Relevance to Current Study"]
ws.row_dimensions[4].height = 28

for col_idx, h_text in enumerate(headers, start=1):
    c = ws.cell(row=4, column=col_idx, value=h_text)
    c.font = font_header
    c.fill = PatternFill("solid", fgColor=DARK_HEADER)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = header_border

# Llenar las 49 filas
for idx, row in df_scopus.iterrows():
    r_num = idx + 5
    ws.row_dimensions[r_num].height = 28
    vals = [
        f"LIT-{idx+1:02d}",
        row["Authors & Year"],
        row["Article Title"],
        row["Journal"],
        infer_pest(row["Full_Text"]),
        infer_agent(row["Full_Text"]),
        infer_method(row["Full_Text"]),
        infer_relevance(row["Full_Text"], row["Article Title"])
    ]
    for col_idx, val in enumerate(vals, start=1):
        cell = ws.cell(row=r_num, column=col_idx, value=val)
        cell.border = cell_border
        cell.font = font_italic if col_idx in [4, 5] else font_body
        if idx % 2 == 1:
            cell.fill = PatternFill("solid", fgColor=ZEBRA_FILL)
        cell.alignment = Alignment(
            horizontal="center" if col_idx in [1, 5, 6, 7] else "left",
            vertical="center",
            wrap_text=True
        )

col_widths = [12, 24, 48, 24, 22, 26, 26, 46]
for i, w in enumerate(col_widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w

ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:H{len(df_scopus) + 4}"

output_excel = "Table_S1_Literature_Search_49_Articulos.xlsx"
wb.save(output_excel)

# 5. DESCARGAR EL EXCEL AUTOMÁTICAMENTE A TU COMPUTADORA
files.download(output_excel)