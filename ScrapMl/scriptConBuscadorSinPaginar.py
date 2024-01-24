from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import etree
import urllib.parse

# Función para generar enlace dinámico de MercadoLibre
def generar_enlace_mercadolibre(consulta):
    consulta_codificada = urllib.parse.quote(consulta.lower())
    enlace = f"https://listado.mercadolibre.com.ar/{consulta_codificada}#D[A:{consulta_codificada}]"
    return enlace

# Solicitar al usuario que ingrese la búsqueda
texto_busqueda = input("Ingrese lo que desea buscar en MercadoLibre: ")

# Generar el enlace dinámico
enlace_mercadolibre = generar_enlace_mercadolibre(texto_busqueda)

# Hacer la solicitud HTTP
response = requests.get(enlace_mercadolibre)

# Verificar el código de estado de la respuesta
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraer información de la página
    titulos = [i.text for i in soup.find_all('h2', attrs={"class":"ui-search-item__title"})]
    urls = [i.get('href') for i in soup.find_all('a', attrs={"class":"ui-search-item__group__element ui-search-link__title-card ui-search-link"})]

    dom = etree.HTML(str(soup))
    precios = dom.xpath('//li[contains(@class, "ui-search-layout__item")]//span[@class="andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript"]/span[@class="andes-money-amount__fraction"]/text()')

    # Crear un DataFrame
    df = pd.DataFrame({
        'Cubierta': titulos,
        'Enlace': urls,
        'Precios': precios
    })

    print("Se creó el DataFrame")

    # Agregar columnas para los nuevos datos
    df['Vendedor'] = ""
    df['Detalles'] = ""
    df['Cantidad'] = ""

    print("Se agregaron las columnas para iterar")

    # Iterar sobre los enlaces y obtener información adicional
    for index, row in df.iterrows():
        product_url = row['Enlace']
        product_response = requests.get(product_url)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        # Obtener el color y precio
        vendedor = product_soup.find('span', attrs={"class": "ui-pdp-color--BLUE ui-pdp-family--REGULAR"})
        detalles = product_soup.find('span', attrs={"class": "ui-pdp-subtitle"})
        cantidad = product_soup.find('span', attrs={"class":"ui-pdp-buybox__quantity__available"})
        
        # Asignar los valores a las columnas correspondientes
        df.at[index, 'Vendedor'] = vendedor.text if vendedor else "No disponible"
        df.at[index, 'Detalles'] = detalles.text if detalles else "No disponible"
        df.at[index, 'Cantidad'] = cantidad.text if cantidad else "No disponible"

    print("Espere un momento")

    # Guardar en un archivo CSV
    df.to_csv('resultado_mercadolibre.csv', index=False)

    print("El archivo fue exportado con éxito")
else:
    print(f"Error al acceder a la página. Código de estado: {response.status_code}")
