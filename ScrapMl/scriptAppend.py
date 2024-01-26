import os
import csv
import codecs

# Paso 1: Obtener la lista de archivos CSV en la carpeta
carpeta = './data/'
archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.csv')]

# Paso 2: Crear una lista vacía para almacenar los datos combinados
datos_combinados = []

# Paso 3: Iterar sobre los archivos CSV y agregar los datos a la lista
for archivo_csv in archivos_csv:
    ruta_completa = os.path.join(carpeta, archivo_csv)
    with codecs.open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as file:
        lector_csv = csv.reader(file)
        # Ignorar la primera línea si es un encabezado
        encabezado = next(lector_csv, None)
        for fila in lector_csv:
            datos_combinados.append(fila)

# Paso 4: Guardar los datos combinados en un nuevo archivo CSV
ruta_salida = './data/combinado.csv'
with codecs.open(ruta_salida, 'w', encoding='utf-8') as file:
    escritor_csv = csv.writer(file)
    # Escribir el encabezado si existe
    if encabezado:
        escritor_csv.writerow(encabezado)
    # Escribir los datos combinados
    escritor_csv.writerows(datos_combinados)

print("¡Operación completada con éxito!")