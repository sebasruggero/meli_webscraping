import os
import csv
import codecs
from datetime import datetime

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

# Obtener la fecha y hora actual
fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Agregar la fecha y hora al nombre del archivo combinado
nombre_archivo_combinado = f'combinado_{fecha_hora_actual}.csv'
ruta_salida = os.path.join(carpeta, nombre_archivo_combinado)

# Paso 4: Guardar los datos combinados en un nuevo archivo CSV
with codecs.open(ruta_salida, 'w', encoding='utf-8') as file:
    escritor_csv = csv.writer(file)
    
    # Escribir una fila con la fecha y hora actual como metadatos
    escritor_csv.writerow(['Fecha y Hora de Creación', fecha_hora_actual])

    # Escribir el encabezado si existe
    if encabezado:
        escritor_csv.writerow(encabezado)
    
    # Escribir los datos combinados
    escritor_csv.writerows(datos_combinados)

print(f"¡Operación completada con éxito! Archivo combinado creado: {nombre_archivo_combinado}")
