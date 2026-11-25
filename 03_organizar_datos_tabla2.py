import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from google.colab import files

# 1. SUBIR EL/LOS ARCHIVO(S) DE BLOC DE NOTAS (.txt / .faa / .fasta)
print("Selecciona tu(s) archivo(s) de Bloc de notas desde tu computadora:")
print("(Puedes seleccionar 1 archivo consolidado o los 3 archivos .txt/.faa a la vez)")
uploaded = files.upload()

# 2. DICCIONARIOS DE REFERENCIA DE TU ESTUDIO
candidatas_priorizadas = {
    "WP_040016737.1": ("Enterobacter ludwigii", "GCF_001750725.1", "Yes (GbpA_2)", "Prioritized Candidate (Table 3)"),
    "WP_020884447.1": ("Enterobacter ludwigii", "GCF_001750725.1", "Yes (DUF333)", "Prioritized Candidate (Table 3)"),
    "WP_040017607.1": ("Enterobacter ludwigii", "GCF_001750725.1", "Yes (DUF333)", "Prioritized Candidate (Table 3)"),
    "WP_120160540.1": ("Enterobacter ludwigii", "GCF_001750725.1", "Yes (GGDEF/EAL)", "Synteny Analyzed (Table 4)"),
    "WP_120163696.1": ("Enterobacter ludwigii", "GCF_001750725.1", "Yes (YccS/FUSC)", "Synteny Analyzed (Table 4)"),
    "WP_120164080.1": ("Rahnella variigena", "GCF_003610915.1", "Yes (S-4TM)", "Prioritized Candidate (Table 3)"),
    "WP_120163181.1": ("Rahnella variigena", "GCF_003610915.1", "Yes (DUF333)", "Prioritized Candidate (Table 3)"),
    "WP_112287263.1": ("Rahnella variigena", "GCF_003610915.1", "Yes (DUF333)", "Prioritized Candidate (Table 3)"),
    "WP_012147429.1": ("Serratia quinivorans", "GCA_900638135.1", "Yes (ClyA-like)", "Prioritized Candidate (Table 3)"),
    "WP_012146232.1": ("Serratia quinivorans", "GCA_900638135.1", "Yes (MARTX_Nterm)", "Prioritized Candidate (Table 3)"),
    "WP_012005436.1": ("Serratia quinivorans", "GCA_900638135.1", "Yes (DUF333)", "Prioritized Candidate (Table 3)"),
}

def detectar_organismo(texto_header, nombre_archivo):
    combinado = f"{texto_header} {nombre_archivo}".lower()
    if "ludwigii" in combinado or "enterobacter" in combinado or "_el" in combinado or "001750725" in combinado:
        return "Enterobacter ludwigii", "GCF_001750725.1", "EL"
    elif "variigena" in combinado or "rahnella" in combinado or "_rv" in combinado or "003610915" in combinado:
        return "Rahnella variigena", "GCF_003610915.1", "RV"
    elif "quinivorans" in combinado or "serratia" in combinado or "_sq" in combinado or "900638135" in combinado:
        return "Serratia quinivorans", "GCA_900638135.1", "SQ"
    return "Enterobacterales sp.", "RefSeq_Assembly", "SP"

# 3. LECTURA INTELIGENTE DE BLOC DE NOTAS (SOPORTA FORMATO FASTA O LISTA SIMPLE)
registros = []
contadores = {"EL": 0, "RV": 0, "SQ": 0, "SP": 0}

for filename, content in uploaded.items():
    texto = content.decode("utf-8", errors="ignore")
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]

    # Caso A: El archivo tiene formato FASTA (encabezados con '>')
    if any(l.startswith(">") for l in lineas):
        acc_actual = None
        header_actual = ""
        seq_actual = []

        for linea in lineas + [">END"]:
            if linea.startswith(">"):
                if acc_actual:
                    longitud = len("".join(seq_actual)) if seq_actual else "N/A"
                    if acc_actual in candidatas_priorizadas:
                        org, gcf, dom_hit, status = candidatas_priorizadas[acc_actual]
                        pref = "EL" if "Enterobacter" in org else ("RV" if "Rahnella" in org else "SQ")
                    else:
                        org, gcf, pref = detectar_organismo(header_actual, filename)
                        dom_hit = "Screened (CD-Search)"
                        status = "Screened in Hypothetical Pool"

                    contadores[pref] += 1
                    pool_id = f"HYP-{pref}-{contadores[pref]:03d}"
                    registros.append({
                        "Pool_ID": pool_id,
                        "Organism": org,
                        "NCBI Assembly": gcf,
                        "Protein Accession": acc_actual,
                        "Original RefSeq Annotation": "hypothetical protein",
                        "Length (aa)": longitud,
                        "CD-Search Domain Hit?": dom_hit,
                        "Status in Pipeline": status,
                        "Highlight": "Table 3" in status
                    })
                if linea != ">END":
                    header_actual = linea[1:]
                    m_acc = re.search(r'([A-Z]{2}_\d+\.\d+|[A-Z]{3}\d+\.\d+)', header_actual)
                    acc_actual = m_acc.group(1) if m_acc else header_actual.split()[0]
                    seq_actual = []
            else:
                seq_actual.append(re.sub(r'[^A-Za-z]', '', linea))

    # Caso B: El archivo es una lista simple de códigos o columnas separadas por tab/espacio
    else:
        for linea in lineas:
            if linea.lower().startswith(("accession", "id", "protein")):
                continue
            m_acc = re.search(r'([A-Z]{2}_\d+\.\d+|[A-Z]{3}\d+\.\d+)', linea)
            acc = m_acc.group(1) if m_acc else linea.split()[0]

            # Buscar si la línea trae un número de longitud (ej: WP_012345.1  145)
            m_len = re.search(r'\b(\d{2,4})\b', linea.replace(acc, ""))
            longitud = int(m_len.group(1)) if m_len else "N/A"

            if acc in candidatas_priorizadas:
                org, gcf, dom_hit, status = candidatas_priorizadas[acc]
                pref = "EL" if "Enterobacter" in org else ("RV" if "Rahnella" in org else "SQ")
            else:
                org, gcf, pref = detectar_organismo(linea, filename)
                dom_hit = "Screened (CD-Search)"
                status = "Screened in Hypothetical Pool"

            contadores[pref] += 1
            pool_id = f"HYP-{pref}-{contadores[pref]:03d}"
            registros.append({
                "Pool_ID": pool_id,
                "Organism": org,
                "NCBI Assembly": gcf,
                "Protein Accession": acc,
                "Original RefSeq Annotation": "hypothetical protein",
                "Length (aa)": longitud,
                "CD-Search Domain Hit?": dom_hit,
                "Status in Pipeline": status,
                "Highlight": "Table 3" in status
            })

print(f"\n¡Total de proteínas hipotéticas procesadas!: {len(registros)}")

# 4. CONSTRUCCIÓN DEL EXCEL CON EL MISMO ESTILO DE LA IMAGEN
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Table_S2_Hypothetical_Pool"
ws.views.sheetView[0].showGridLines = True

DARK_HEADER = "1F3A52"
ZEBRA_FILL = "F7F9FC"
GREEN_HIGHLIGHT = "E6F4EA"
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

# Título y subtítulo
ws["A1"] = f"Tabla 2. Inventario de proteínas hipotéticas extraídas (Total analizado = {len(registros)})"
ws["A1"].font = font_title
ws["A2"] = "Filtrado desde proteomas RefSeq (.faa): E. ludwigii, R. variigena y S. quinivorans. Candidatas priorizadas resaltadas en verde."
ws["A2"].font = font_subtitle

# Encabezados (Fila 4)
headers = ["Pool_ID", "Organism", "NCBI Assembly", "Protein Accession", "Original RefSeq Annotation", "Length (aa)", "CD-Search Domain Hit?", "Status in Pipeline"]
ws.row_dimensions[4].height = 28

for col_idx, h_text in enumerate(headers, start=1):
    c = ws.cell(row=4, column=col_idx, value=h_text)
    c.font = font_header
    c.fill = PatternFill("solid", fgColor=DARK_HEADER)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = header_border

# Llenar filas
for idx, item in enumerate(registros):
    r_num = idx + 5
    ws.row_dimensions[r_num].height = 22
    vals = [
        item["Pool_ID"],
        item["Organism"],
        item["NCBI Assembly"],
        item["Protein Accession"],
        item["Original RefSeq Annotation"],
        item["Length (aa)"],
        item["CD-Search Domain Hit?"],
        item["Status in Pipeline"]
    ]
    for col_idx, val in enumerate(vals, start=1):
        cell = ws.cell(row=r_num, column=col_idx, value=val)
        cell.border = cell_border
        cell.font = font_italic if col_idx == 2 else font_body

        if item["Highlight"]:
            cell.fill = PatternFill("solid", fgColor=GREEN_HIGHLIGHT)
        elif idx % 2 == 1:
            cell.fill = PatternFill("solid", fgColor=ZEBRA_FILL)

        cell.alignment = Alignment(
            horizontal="left" if col_idx in [2, 5, 7, 8] else "center",
            vertical="center",
            wrap_text=True
        )

col_widths = [15, 24, 20, 20, 26, 14, 24, 30]
for i, w in enumerate(col_widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w

ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:H{len(registros) + 4}"

output_excel = "Table_S2_Hypothetical_Pool.xlsx"
wb.save(output_excel)

# 5. DESCARGAR AUTOMÁTICAMENTE EL EXCEL A TU COMPUTADORA
files.download(output_excel)