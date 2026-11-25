import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from google.colab import files

# 1. SUBIR EL BLOC DE NOTAS '(18) toxinas seleccionadas 12-10-26.txt'
print("Selecciona tu archivo '(18) toxinas seleccionadas 12-10-26.txt':")
uploaded = files.upload()
archivo_txt = list(uploaded.keys())[0]

with open(archivo_txt, "r", encoding="utf-8", errors="ignore") as f:
    texto = f.read()

# 2. DICCIONARIO COMPLETO PARA LAS 17 TOXINAS ÚNICAS DE TU ARCHIVO
info_toxinas = {
    "P06575": ("Binary larvicide subunit BinA", "Bin Toxin", "Lysinibacillus sphaericus", "Mosquitocidal binary pore component A", "Binary Toxin Outgroup"),
    "P02931": ("Outer membrane porin F (OmpF)", "OM Porin Control", "Escherichia coli", "Non-specific outer membrane beta-barrel channel", "Enterobacterial Porin Outgroup"),
    "P05519": ("Pesticidal crystal protein Cry4Ba", "3-Domain Cry", "Bacillus thuringiensis", "Three-domain delta-endotoxin pore formation", "Classical Bt Outgroup"),
    "Q06117": ("Pesticidal crystal protein Cry3Bb", "3-Domain Cry", "Bacillus thuringiensis", "Coleopteran midgut epithelial pore formation", "Classical Bt Outgroup"),
    "P81694": ("Venom neurotoxin CSTX-1", "Knottin / ICK Toxin", "Cupiennius salei", "Insecticidal voltage-gated Ca2+ channel blocker", "Arthropod Venom Outgroup"),
    "Q9KS12": ("Multifunctional autoprocessing RTX toxin (MARTX)", "RTX / MARTX", "Vibrio cholerae", "Pore formation & effector translocation", "Gram-Negative Virulence Ref"),
    "A1YKW7": ("RTX hemolysin toxin RtxA", "RTX Toxin", "Kingella kingae", "Calcium-dependent pore-forming cytolysin", "Gram-Negative Virulence Ref"),
    "A0A1S4GGP7": ("Cadherin-AgCad1 receptor", "Midgut Receptor", "Anopheles gambiae", "Membrane receptor control for Cry toxin binding", "Host Receptor Outgroup"),
    "P69437": ("Protonectin antimicrobial/insecticidal peptide", "Venom Peptide", "Agelaia pallipes pallipes", "Direct membrane permeabilization & mast-cell degranulation", "Hymenoptera Venom Outgroup"),
    "P01446": ("Cytotoxin 3 (Cardiotoxin)", "Three-Finger Toxin", "Naja kaouthia", "Direct membrane lipid-bilayer cytolysis", "Cytolytic Toxin Outgroup"),
    "D3V916": ("Insecticidal binary toxin PirA", "PirAB Toxin", "Xenorhabdus nematophila", "JHE-like binary toxin partner A", "Entomopathogen Ref"),
    "A0A068R5C3": ("Insecticidal binary toxin PirA", "PirAB Toxin", "Xenorhabdus poinarii", "JHE-like binary toxin partner A", "Entomopathogen Ref"),
    "A0A2S8Q8L8": ("Insecticidal binary toxin PirB", "PirAB Toxin", "Photorhabdus hindustanensis", "Pore-forming binary toxin partner B", "Entomopathogen Ref"),
    "P05516": ("Binary larvicide subunit BinA2", "Bin Toxin", "Lysinibacillus sphaericus", "Mosquitocidal binary pore component variant", "Binary Toxin Outgroup"),
    "P0C5F2": ("Insecticidal toxin LaIT1", "Arthropod Toxin", "Liocheles australasiae", "Insect-selective pore/ion-channel toxin", "Arthropod Venom Outgroup"),
    "P0DRM3": ("Insecticidal scorpine-like peptide LaIT3", "Scorpine-like", "Liocheles australasiae", "Antimicrobial & insecticidal membrane-active peptide", "Arthropod Venom Outgroup"),
    "P58604": ("Venom neurotoxin CSTX-9", "Knottin / ICK Toxin", "Cupiennius salei", "Insecticidal ion-channel neurotoxin", "Arthropod Venom Outgroup"),
}

# 3. PARSEAR FASTA, CALCULAR LONGITUD EXACTA Y ELIMINAR DUPLICADO (P06575)
registros = []
vistos = set()
header_actual = None
seq_actual = []

for linea in texto.splitlines() + [">END"]:
    linea = linea.strip()
    if not linea:
        continue
    if linea.startswith(">"):
        if header_actual:
            m_acc = re.search(r'\|([A-Z0-9]{6,10})\|', header_actual)
            acc = m_acc.group(1) if m_acc else header_actual.split()[0]
            if acc not in vistos:
                vistos.add(acc)
                longitud = len("".join(seq_actual))
                prot_name, fam, org, mech, role = info_toxinas.get(
                    acc, (acc, "Reference Toxin", "Reference Organism", "Insecticidal activity", "Phylogenetic Outgroup")
                )
                registros.append({
                    "Accession": acc,
                    "Protein Name": prot_name,
                    "Toxin Family": fam,
                    "Source Organism": org,
                    "Length (aa)": longitud,
                    "Primary Mechanism of Action": mech,
                    "Phylogenetic Role": role
                })
        if linea != ">END":
            header_actual = linea
            seq_actual = []
    else:
        seq_actual.append(re.sub(r'[^A-Za-z]', '', linea))

print(f"\nSecuencias totales en FASTA: 18 | Únicas procesadas (sin P06575 duplicada): {len(registros)}")

# 4. GENERAR EL EXCEL CON EL MISMO ESTILO DE LA IMAGEN
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Table_S4_Reference_Toxins"
ws.views.sheetView[0].showGridLines = True

DARK_HEADER = "1F3A52"
ZEBRA_FILL = "F7F9FC"
BORDER_COLOR = "CBD5E1"

font_title = Font(name="Arial", size=12, bold=True, color="1F3A52")
font_subtitle = Font(name="Arial", size=9.5, italic=True, color="475569")
font_header = Font(name="Arial", size=10, bold=True, color="FFFFFF")
font_body = Font(name="Arial", size=9.5, color="0F172A")
font_italic = Font(name="Arial", size=9.5, italic=True, color="0F172A")
font_note = Font(name="Arial", size=8.5, italic=True, color="334155")

thin = Side(style="thin", color=BORDER_COLOR)
med_navy = Side(style="medium", color=DARK_HEADER)
cell_border = Border(left=thin, right=thin, top=thin, bottom=thin)
header_border = Border(left=thin, right=thin, top=med_navy, bottom=med_navy)

ws["A1"] = f"Tabla 4. Toxinas de referencia seleccionadas y curadas con actividad insecticida y formadora de poros, utilizadas para la reconstrucción filogenética (N = {len(registros)} únicas; 18 entradas FASTA)"
ws["A1"].font = font_title
ws["A2"] = "Obtenido de UniProtKB/Swiss-Prot como controles evolutivos para NGPhylogeny (MAFFT + ClipKIT + FastTree)."
ws["A2"].font = font_subtitle

headers = [
    "Ref_ID", "UniProt / NCBI Accession", "Protein Name", "Toxin Family",
    "Source Organism", "Length (aa)", "Primary Mechanism of Action", "Phylogenetic Role"
]
ws.row_dimensions[4].height = 28

for col_idx, h_text in enumerate(headers, start=1):
    c = ws.cell(row=4, column=col_idx, value=h_text)
    c.font = font_header
    c.fill = PatternFill("solid", fgColor=DARK_HEADER)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = header_border

for idx, item in enumerate(registros):
    r_num = idx + 5
    ws.row_dimensions[r_num].height = 24
    vals = [
        f"REF-{idx+1:02d}",
        item["Accession"],
        item["Protein Name"],
        item["Toxin Family"],
        item["Source Organism"],
        item["Length (aa)"],
        item["Primary Mechanism of Action"],
        item["Phylogenetic Role"]
    ]
    for col_idx, val in enumerate(vals, start=1):
        cell = ws.cell(row=r_num, column=col_idx, value=val)
        cell.border = cell_border
        cell.font = font_italic if col_idx == 5 else font_body
        if idx % 2 == 1:
            cell.fill = PatternFill("solid", fgColor=ZEBRA_FILL)
        cell.alignment = Alignment(
            horizontal="left" if col_idx in [3, 5, 7, 8] else "center",
            vertical="center",
            wrap_text=True
        )

ws["A23"] = "Nota: El archivo FASTA original contenía 18 entradas, de las cuales P06575 (BINA1_LYSSH) aparecía duplicada (#1 y #14), resultando en 17 secuencias de referencia únicas."
ws["A23"].font = font_note

col_widths = [12, 22, 42, 20, 26, 14, 44, 28]
for i, w in enumerate(col_widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w

ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:H{len(registros) + 4}"

output_excel = "Table_S4_Reference_Toxins_17_Unicas.xlsx"
wb.save(output_excel)
files.download(output_excel)