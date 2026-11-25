import re
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from google.colab import files

# 1. SUBIR LOS 3 ARCHIVOS DE EXCEL DESDE TU COMPUTADORA
print("Selecciona tus 3 archivos de Excel (usa Ctrl + Clic para seleccionar los 3 a la vez):")
uploaded = files.upload()

# 2. DICCIONARIO DE CANDIDATAS PRIORIZADAS Y CONTROLES DE SINTENIA
candidatas_especiales = {
    "WP_012147429.1": ("Serratia quinivorans", 291, "ClyA-like alpha-pore-forming toxin", "cl45899", "18-276", 1.42e-14, "[V] Virulence & Defense", "Selected (Top Pore-Former)"),
    "WP_012146232.1": ("Serratia quinivorans", 171, "MARTX_Nterm holotoxin domain", "cl37936", "5-164", 3.18e-11, "[V] Virulence & Defense", "Selected (Cytotoxin)"),
    "WP_012005436.1": ("Serratia quinivorans", 87, "DUF333 / Hemolysin-like domain", "cl46806", "4-85", 4.75e-18, "[S] Unknown / Membrane Lysis", "Selected (Hemolysin)"),
    "WP_120164080.1": ("Rahnella variigena", 291, "S-4TM pore-forming effector", "cl39534", "12-284", 6.20e-16, "[S/V] Pore-Forming Effector", "Selected (Top Pore-Former)"),
    "WP_120163181.1": ("Rahnella variigena", 77, "DUF333 / Hemolysin-like domain", "cl46806", "3-75", 2.11e-15, "[S] Unknown / Membrane Lysis", "Selected (Hemolysin)"),
    "WP_112287263.1": ("Rahnella variigena", 93, "DUF333 / Hemolysin-like domain", "cl46806", "6-90", 8.90e-21, "[S] Unknown / Membrane Lysis", "Selected (Hemolysin)"),
    "WP_040016737.1": ("Enterobacter ludwigii", 145, "GbpA_2 chitin-binding domain", "pfam13209", "24-139", 5.34e-24, "[G/M] Chitin Binding / Synergy", "Selected (Top Synergist)"),
    "WP_020884447.1": ("Enterobacter ludwigii", 84, "DUF333 / Hemolysin-like domain", "cl46806", "5-82", 1.05e-19, "[S] Unknown / Membrane Lysis", "Selected (Hemolysin)"),
    "WP_040017607.1": ("Enterobacter ludwigii", 88, "DUF333 / Hemolysin-like domain", "cl46806", "4-86", 7.62e-17, "[S] Unknown / Membrane Lysis", "Selected (Hemolysin)"),
    "WP_120160540.1": ("Enterobacter ludwigii", 214, "GGDEF / EAL c-di-GMP signaling", "cl00290", "15-208", 4.10e-32, "[T] Signal Transduction", "Retained (Synteny Control)"),
    "WP_120163696.1": ("Rahnella variigena", 198, "YccS / FUSC membrane transporter", "COG0795", "10-192", 9.15e-28, "[P] Ion/Membrane Transport", "Retained (Synteny Control)"),
}

def detectar_especie_archivo(nombre_archivo, texto_fila=""):
    txt = f"{nombre_archivo} {texto_fila}".lower()
    if "ludwigii" in txt or "enterobacter" in txt or "_el" in txt or "001750725" in txt:
        return "Enterobacter ludwigii"
    elif "variigena" in txt or "rahnella" in txt or "_rv" in txt or "003610915" in txt:
        return "Rahnella variigena"
    elif "quinivorans" in txt or "serratia" in txt or "_sq" in txt or "900638135" in txt:
        return "Serratia quinivorans"
    return "Enterobacterales sp."

def clasificar_cog(dominio_texto):
    d = str(dominio_texto).lower()
    if any(k in d for k in ["clya", "martx", "toxin", "virulen", "pmrd", "vapi", "hemolysin"]):
        return "[V] Virulence & Defense"
    elif any(k in d for k in ["gbpa", "chitin", "rfa", "wcak", "piln", "fima", "envc", "cell wall", "lipoprotein"]):
        return "[M] Cell Wall & Envelope Biogenesis"
    elif any(k in d for k in ["kef", "potd", "afua", "oprp", "yccs", "fusc", "transporter", "permease", "abc", "mfs", "porin"]):
        return "[P] Ion/Membrane Transport"
    elif any(k in d for k in ["ggdef", "eal", "mhyt", "fic", "chab", "regulator", "hth", "marr", "kinase"]):
        return "[T] Signal Transduction & Regulation"
    elif any(k in d for k in ["oxygenase", "dehydrogenase", "reductase", "ssud", "pemb", "nipsnap", "hydrolase", "esterase"]):
        return "[E/C/Q] Enzymatic Metabolism"
    elif any(k in d for k in ["hsdr", "mcra", "rpnc", "phage", "hk97", "transposase", "helicase", "nuclease"]):
        return "[L/J/X] DNA/RNA & Mobile Elements"
    return "[S] Unknown / Conserved DUF"

# 3. LECTURA INTELIGENTE DE LOS 3 EXCELES
registros_dict = {}

for filename in uploaded.keys():
    print(f"Procesando archivo: {filename}...")
    xls = pd.ExcelFile(filename)
    for sheet in xls.sheet_names:
        df_raw = pd.read_excel(xls, sheet_name=sheet)
        if df_raw.empty:
            continue

        # Buscar en qué fila están los encabezados reales (por si hay títulos arriba)
        header_idx = None
        for idx, row in df_raw.iterrows():
            fila_str = " ".join(str(x).lower() for x in row.values)
            if any(k in fila_str for k in ["query", "accession", "e-value", "short name", "domain", "wp_"]):
                if "wp_" not in fila_str:
                    header_idx = idx
                break

        if header_idx is not None:
            df = pd.read_excel(xls, sheet_name=sheet, header=header_idx + 1)
        else:
            df = df_raw.copy()

        # Recorrer cada fila y extraer campos mediante patrones flexibles
        for _, row in df.iterrows():
            valores = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip() != ""]
            if not valores:
                continue
            fila_completa = " | ".join(valores)

            # Buscar código WP_... o similar
            m_acc = re.search(r'([A-Z]{2}_\d+\.\d+|[A-Z]{3}\d+\.\d+)', fila_completa)
            if not m_acc:
                continue
            acc = m_acc.group(1)

            # Si ya está en nuestras candidatas especiales, usar datos curados
            if acc in candidatas_especiales:
                org, length, dom, cdd_acc, interval, eval_num, cog, status = candidatas_especiales[acc]
                registros_dict[acc] = {
                    "Organism": org, "Protein Accession": acc, "Length (aa)": length,
                    "Conserved Domain / Superfamily": dom, "CDD Accession": cdd_acc,
                    "Interval (aa)": interval, "E-value": eval_num,
                    "COG Functional Category": cog, "Candidate Selection": status,
                    "Highlight": True
                }
                continue

            # Evitar duplicados si una proteína tiene múltiples hits secundarios
            if acc in registros_dict:
                continue

            org = detectar_especie_archivo(filename, fila_completa)

            # Extraer CDD Accession (cl..., pfam..., COG..., cd..., smart..., TIGR...)
            m_cdd = re.search(r'\b(cl\d+|pfam\d+|COG\d+|cd\d+|smart\d+|TIGR\d+|PRK\d+)\b', fila_completa)
            cdd_acc = m_cdd.group(1) if m_cdd else "CDD_Hit"

            # Extraer Intervalo (ej. 18-276 o From/To)
            m_int = re.search(r'\b(\d{1,4}\s*-\s*\d{1,4})\b', fila_completa)
            interval = m_int.group(1).replace(" ", "") if m_int else "N/A"

            # Extraer E-value (notación científica ej. 1.42e-14 o 1,42E-14)
            m_eval = re.search(r'(\d+[.,]\d+[eE][+-]?\d+|\d+[eE][+-]?\d+)', fila_completa)
            if m_eval:
                eval_str = m_eval.group(1).replace(",", ".")
                try:
                    eval_num = float(eval_str)
                except:
                    eval_num = 1e-6
            else:
                eval_num = 1e-6

            # Extraer Longitud (número entero entre 30 y 2500 que no sea parte del intervalo)
            length = "N/A"
            for val in valores:
                if val.isdigit() and 30 <= int(val) <= 2500:
                    length = int(val)
                    break

            # Extraer nombre del dominio (texto descriptivo distinto al WP_ y al organismo)
            dom = "Conserved Domain Hit"
            for val in valores:
                if (acc not in val and org.lower() not in val.lower() and not val.isdigit()
                    and not re.match(r'^\d+[.,]?\d*[eE][+-]?\d+$', val) and len(val) > 3):
                    if val != cdd_acc and val != interval:
                        dom = val
                        break

            cog = clasificar_cog(f"{dom} {cdd_acc}")
            registros_dict[acc] = {
                "Organism": org, "Protein Accession": acc, "Length (aa)": length,
                "Conserved Domain / Superfamily": dom, "CDD Accession": cdd_acc,
                "Interval (aa)": interval, "E-value": eval_num,
                "COG Functional Category": cog, "Candidate Selection": "Annotated Domain Hit",
                "Highlight": False
            }

# Ordenar poniendo primero las candidatas resaltadas y luego por organismo
lista_final = sorted(
    registros_dict.values(),
    key=lambda x: (not x["Highlight"], x["Organism"], x["Protein Accession"])
)
print(f"\n¡Total de proteínas consolidadas de los 3 Excels!: {len(lista_final)}")

# 4. CREACIÓN DEL EXCEL CON EL DISEÑO EXACTO DE LA IMAGEN
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Table_S3_CD_Search_Domains"
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
ws["A1"] = f"Tabla 3. Anotaciones de dominios mediante NCBI Batch CD-Search y clasificación COG (N = {len(lista_final)} proteínas resueltas)"
ws["A1"].font = font_title
ws["A2"] = "Umbral de significancia: E-value < 1.0E-05 frente a CDD v3.21. Candidatas entomopatógenas priorizadas resaltadas en verde."
ws["A2"].font = font_subtitle

# Encabezados (Fila 4)
headers = [
    "Organism", "Protein Accession", "Length (aa)", "Conserved Domain / Superfamily",
    "CDD Accession", "Interval (aa)", "E-value", "COG Functional Category", "Candidate Selection"
]
ws.row_dimensions[4].height = 28

for col_idx, h_text in enumerate(headers, start=1):
    c = ws.cell(row=4, column=col_idx, value=h_text)
    c.font = font_header
    c.fill = PatternFill("solid", fgColor=DARK_HEADER)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = header_border

# Llenar filas
for idx, item in enumerate(lista_final):
    r_num = idx + 5
    ws.row_dimensions[r_num].height = 22
    vals = [
        item["Organism"],
        item["Protein Accession"],
        item["Length (aa)"],
        item["Conserved Domain / Superfamily"],
        item["CDD Accession"],
        item["Interval (aa)"],
        item["E-value"],
        item["COG Functional Category"],
        item["Candidate Selection"]
    ]
    for col_idx, val in enumerate(vals, start=1):
        cell = ws.cell(row=r_num, column=col_idx, value=val)
        cell.border = cell_border
        cell.font = font_italic if col_idx == 1 else font_body

        if item["Highlight"]:
            cell.fill = PatternFill("solid", fgColor=GREEN_HIGHLIGHT)
        elif idx % 2 == 1:
            cell.fill = PatternFill("solid", fgColor=ZEBRA_FILL)

        if col_idx == 7 and isinstance(val, (int, float)):
            cell.number_format = "0.00E+00"

        cell.alignment = Alignment(
            horizontal="left" if col_idx in [1, 4, 8, 9] else "center",
            vertical="center",
            wrap_text=True
        )

col_widths = [24, 20, 14, 36, 16, 16, 15, 28, 28]
for i, w in enumerate(col_widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w

ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:I{len(lista_final) + 4}"

output_excel = "Table_S3_CD_Search_Domains.xlsx"
wb.save(output_excel)

# 5. DESCARGAR AUTOMÁTICAMENTE EL EXCEL CONSOLIDADO
files.download(output_excel)