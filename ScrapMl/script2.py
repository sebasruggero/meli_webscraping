from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import etree

url = 'https://listado.mercadolibre.com.ar/apple-watch#D[A:apple watch]'
response = requests.get(url)

print(response.status_code)

response.text

soup = BeautifulSoup(response.content, 'html.parser')

titulos = soup.find_all('h2', attrs={"class":"ui-search-item__title"})
titulos = [i.text for i in titulos]

urls = soup.find_all('a', attrs={"class":"ui-search-item__group__element ui-search-link__title-card ui-search-link"})
urls = [i.get('href') for i in urls]

dom = etree.HTML(str(soup))
precios = dom.xpath('//li[contains(@class, "ui-search-layout__item")]//span[@class="andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript"]/span[@class="andes-money-amount__fraction"]/text()')

# Crear un DataFrame
df = pd.DataFrame({
    'Cubierta': titulos,
    'Enlace': urls,
    'Precios': precios
}) 

print("Se creo el dataframe")

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

print("Aguarde un momento")

# Guardar en un archivo CSV
df.to_csv('informacion_apple_watch.csv', index=False)

print("El archivo fue exportado con exito")
