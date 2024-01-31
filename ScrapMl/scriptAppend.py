import os
import pandas as pd

# Ruta de la carpeta que contiene los archivos CSV
carpeta = './data/'

# Lista para almacenar todos los DataFrames
dfs = []

# Iterar sobre los archivos en la carpeta
for archivo in os.listdir(carpeta):
    if archivo.endswith('.csv'):
        # Leer el archivo CSV y especificar el tipo de datos de todas las columnas como cadena
        ruta_archivo = os.path.join(carpeta, archivo)
        df = pd.read_csv(ruta_archivo, dtype=str)  # Todos los datos como cadena

        # Verificar duplicados en la columna 'Publicacion'
        duplicados = df[df.duplicated('Publicacion')]

        # Eliminar duplicados
        df = df.drop_duplicates('Publicacion')

        # Imprimir los duplicados encontrados
        if not duplicados.empty:
            print(f'Duplicados en {archivo}:\n{duplicados}')

        # Agregar el DataFrame limpio a la lista
        dfs.append(df)

# Configurar opciones de formato
pd.set_option('display.float_format', '{:.3f}'.format)
pd.set_option('display.precision', 3)  # Controlar la precisión al imprimir

# Consolidar todos los DataFrames en uno
df_consolidado = pd.concat(dfs, ignore_index=True)

# Restaurar configuración predeterminada después de la concatenación
pd.reset_option('display.float_format')
pd.reset_option('display.precision')

# Guardar el DataFrame consolidado en un nuevo archivo CSV
df_consolidado.to_csv('consolidado.csv', index=False)

# Mostrar información del DataFrame consolidado
print('DataFrame Consolidado:\n', df_consolidado)
