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

# Guardar en un archivo CSV
df.to_csv('informacion_apple_watch.csv', index=False)
