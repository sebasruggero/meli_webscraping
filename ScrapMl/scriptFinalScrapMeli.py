from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import etree
from datetime import datetime

# Lista de productos
productos = ["aceite de oliva","aceite de girasol", "arroz", "leche descremada", "yerba", "azúcar", "harina", "fideos", "café", "té", "pañales", "papel higienico", "yogur", "queso", "galletas", "cereal", "agua mineral"]


for producto in productos:
    # Obtener la URL de la página de resultados según el número de página
    texto_busqueda = producto
    texto_busqueda_formateado = texto_busqueda.replace(' ', '-')
    
    # Función para obtener la URL de la página de resultados según el número de página
    def get_search_url(page_number):
        base_url = f'https://listado.mercadolibre.com.ar/{texto_busqueda_formateado}'
        if page_number > 1:
            # Ajustando la URL para páginas más allá de la primera
            return f'{base_url}_Desde_{(page_number - 1) * 50 + 1}_NoIndex_True'
        else:
            return base_url

    # Lista para almacenar los DataFrames de cada página
    all_dfs = []

    # Número máximo de páginas a scrapear (ajústalo según sea necesario)
    max_pages = 2

    # Bucle para iterar sobre las páginas
    for page_number in range(1, max_pages + 1):
        # Obtener la URL de la página actual
        current_url = get_search_url(page_number)

        # Realizar la solicitud para la página actual
        response = requests.get(current_url)

        # Verificar el código de estado
        if response.status_code == 200:
            print(f"Scraping data from page {page_number}")

            # Parsear la página actual
            soup = BeautifulSoup(response.content, 'html.parser')

            # Tu código para extraer información de la página va aquí
            titulos = soup.find_all('h2', attrs={"class":"ui-search-item__title"})
            titulos = [i.text for i in titulos]

            urls = soup.find_all('a', attrs={"class":"ui-search-item__group__element ui-search-link__title-card ui-search-link"})
            urls = [i.get('href') for i in urls]

            dom = etree.HTML(str(soup))
            precios = dom.xpath('//li[contains(@class, "ui-search-layout__item")]//span[@class="andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript"]/span[@class="andes-money-amount__fraction"]/text()')

            # Crear un DataFrame para la página actual
            df = pd.DataFrame({
                'Titulo': titulos,
                'Enlace': urls,
                'Precios': precios
                })

            # Agregar columnas adicionales
            df['Vendedor'] = ""
            df['Detalles'] = ""
            df['Cantidad'] = ""
            df['Estado'] = ""
            df['Oferta'] = ""
            df['Publicacion'] = ""
            df['Fecha_Ejecucion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Iterar sobre los enlaces y obtener información adicional
            for index, row in df.iterrows():
                product_url = row['Enlace']
                product_response = requests.get(product_url)
                product_soup = BeautifulSoup(product_response.content, 'html.parser')

                # Obtener el color y precio
                vendedor = product_soup.find('span', attrs={"class": "ui-pdp-color--BLUE ui-pdp-family--REGULAR"})
                detalles = product_soup.find('span', attrs={"class": "ui-pdp-subtitle"})
                cantidad = product_soup.find('span', attrs={"class":"ui-pdp-buybox__quantity__available"})
                estado = product_soup.find('span', attrs={"class":"ui-pdp-subtitle"})
                oferta = product_soup.find('div', attrs={"class":"ui-pdp-promotions-pill-label ui-pdp-background-color--BLUE ui-pdp-color--WHITE ui-pdp-size--XXSMALL ui-pdp-family--SEMIBOLD"})
                publicacion = product_soup.find('span', attrs={"class":"ui-pdp-color--BLACK ui-pdp-family--SEMIBOLD"})
                familia_elements = product_soup.find_all('li', class_='andes-breadcrumb__item')

                # Asignar los valores a las columnas correspondientes
                df.at[index, 'Vendedor'] = vendedor.text if vendedor else "No disponible"
                df.at[index, 'Detalles'] = detalles.text if detalles else "No disponible"
                df.at[index, 'Cantidad'] = cantidad.text if cantidad else "No disponible"
                df.at[index, 'Estado'] = estado.text if estado else "No disponible"
                df.at[index, 'Oferta'] = oferta.text if oferta else "No disponible"
                df.at[index, 'Publicacion'] = publicacion.text if publicacion else "No disponible"
                
                # Extraer información de las familias
                for i, familia_element in enumerate(familia_elements):
                    familia_column_name = f'Familia{i+1}'
                    df.at[index, familia_column_name] = familia_element.find('a', class_='andes-breadcrumb__link').text if familia_element else "No disponible"

            # Agregar el DataFrame al listado
            all_dfs.append(df)

        else:
            print(f"Failed to retrieve data from page {page_number}. Status code: {response.status_code}")
            
    texto_archivo_formateado = texto_busqueda.replace(' ', '_')

    fecha_actual = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    nombre_archivo = f'{texto_archivo_formateado}_{fecha_actual}.csv'

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.to_csv(nombre_archivo, index=False)

    # Imprimir el mensaje con la fecha y hora
    print(f"Scraping completado para {producto}. El archivo fue exportado con éxito. Fecha y hora: {fecha_actual}")
