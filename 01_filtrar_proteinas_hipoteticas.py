import re
from google.colab import files
import pandas as pd

# 1. Subir el archivo FASTA de forma interactiva
print("Por favor, sube tu archivo FASTA:")
uploaded = files.upload()

# Obtener el nombre del archivo subido
nombre_archivo = list(uploaded.keys())[0]

# 2. Palabras clave para identificar proteínas desconocidas/hipotéticas
palabras_clave = [
    "hypothetical",
    "unknown",
    "uncharacterized",
    "putative",
    "predicted",
]
patron = re.compile(
    "|".join(palabras_clave), re.IGNORECASE
)

# 3. Procesar el archivo FASTA
resultados = []
total_proteinas = 0
header_actual = ""
secuencia_actual = []

with open(nombre_archivo, "r", encoding="utf-8", errors="ignore") as f:
    for linea in f:
        linea = linea.strip()
        if linea.startswith(">"):
            # Si ya teníamos una proteína previa, evaluarla
            if header_actual:
                total_proteinas += 1
                texto_header = header_actual[1:]  # Quitar el símbolo '>'
                if patron.search(texto_header):
                    resultados.append(
                        {
                            "ID/Header": texto_header,
                            "Secuencia": "".join(secuencia_actual),
                        }
                    )
            # Reiniciar para la nueva proteína
            header_actual = linea
            secuencia_actual = []
        else:
            secuencia_actual.append(linea)

    # Procesar la última proteína del archivo
    if header_actual:
        total_proteinas += 1
        texto_header = header_actual[1:]
        if patron.search(texto_header):
            resultados.append(
                {"ID/Header": texto_header, "Secuencia": "".join(secuencia_actual)}
            )

# 4. Mostrar estadísticas y exportar resultados
print(f"\n--- ANÁLISIS COMPLETADO ---")
print(f"Total de proteínas analizadas: {total_proteinas}")
print(f"Proteínas hipotéticas/desconocidas encontradas: {len(resultados)}")

# Guardar resultados en un archivo de texto en formato FASTA
archivo_salida = "proteinas_hipoteticas_filtradas.fasta"
with open(archivo_salida, "w", encoding="utf-8") as f_out:
    for prot in resultados:
        f_out.write(f">{prot['ID/Header']}\n")
        f_out.write(f"{prot['Secuencia']}\n")

print(f"Se ha guardado el reporte en '{archivo_salida}'.")

# Descargar el archivo automáticamente a tu computadora
files.download(archivo_salida)