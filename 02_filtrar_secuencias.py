import re
from google.colab import files

def limpiar_fasta_para_ngphylogeny(input_path, output_path):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        secuencia_actual = []
        cabeza_actual = None

        for linea in infile:
            linea = linea.strip()
            if linea.startswith('>'):
                # Escribir el registro anterior si existe
                if cabeza_actual and secuencia_actual:
                    outfile.write(f"{cabeza_actual}\n{''.join(secuencia_actual)}\n")
                    secuencia_actual = []

                # Buscar el identificador WP_ (ej. >WP_008502331.1)
                match = re.search(r'>(WP_\d+\.\d+|WP_\d+)', linea)
                if match:
                    cabeza_actual = f">{match.group(1)}"
                else:
                    # Si la cabecera no tiene WP_, tomar el primer token limpio
                    primer_token = linea.split()[0]
                    cabeza_actual = re.sub(r'[^a-zA-Z0-9_>.-]', '', primer_token)
            else:
                # Mantener solo letras aminoacídicas/nucleotídicas válidas
                secuencia_limpia = re.sub(r'[^a-zA-Z*]', '', linea)
                if secuencia_limpia:
                    secuencia_actual.append(secuencia_limpia)

        # Escribir el último registro
        if cabeza_actual and secuencia_actual:
            outfile.write(f"{cabeza_actual}\n{''.join(secuencia_actual)}\n")

# 1. Subir archivo FASTA
print("Sube tu archivo .fasta o .faa:")
uploaded = files.upload()

for filename in uploaded.keys():
    output_filename = "secuencias_limpias_ngphylogeny.fasta"
    limpiar_fasta_para_ngphylogeny(filename, output_filename)
    print(f"\nArchivo procesado con éxito: {output_filename}")

    # 2. Descargar automáticamente el archivo limpio
    files.download(output_filename)