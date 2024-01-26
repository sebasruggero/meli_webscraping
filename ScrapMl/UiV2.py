import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import etree
from datetime import datetime

class MercadoLibreScraperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MercadoLibre Scraper")

        self.label_busqueda = ttk.Label(root, text="Ingrese lo que desea buscar en MercadoLibre:")
        self.label_busqueda.pack(pady=10)

        self.entry_busqueda = ttk.Entry(root, width=40)
        self.entry_busqueda.pack(pady=10)

        self.label_paginas = ttk.Label(root, text="Ingrese la cantidad de páginas a scrapear:")
        self.label_paginas.pack(pady=10)

        self.entry_paginas = ttk.Entry(root, width=10)
        self.entry_paginas.pack(pady=10)

        self.button_scrapear = ttk.Button(root, text="Scrapear", command=self.scrapear)
        self.button_scrapear.pack(pady=10)

        self.button_cerrar = ttk.Button(root, text="Cerrar", command=root.destroy)
        self.button_cerrar.pack(pady=10)

    def scrapear(self):
        texto_busqueda = self.entry_busqueda.get()
        cantidad_paginas = int(self.entry_paginas.get())

        def get_search_url(page_number):
            texto_busqueda_formateado = texto_busqueda.replace(' ', '-')
            base_url = f'https://listado.mercadolibre.com.ar/{texto_busqueda_formateado}'
            if page_number > 1:
                return f'{base_url}_Desde_{(page_number - 1) * 50 + 1}_NoIndex_True'
            else:
                return base_url

        texto_busqueda_formateado = texto_busqueda.replace(' ', '-')
        all_dfs = []

        for page_number in range(1, cantidad_paginas + 1):
            current_url = get_search_url(page_number)
            response = requests.get(current_url)

            if response.status_code == 200:
                print(f"Scraping data from page {page_number}")

                soup = BeautifulSoup(response.content, 'html.parser')
                titulos = soup.find_all('h2', attrs={"class": "ui-search-item__title"})
                titulos = [i.text for i in titulos]

                urls = soup.find_all('a', attrs={"class": "ui-search-item__group__element ui-search-link__title-card ui-search-link"})
                urls = [i.get('href') for i in urls]

                dom = etree.HTML(str(soup))
                precios = dom.xpath('//li[contains(@class, "ui-search-layout__item")]//span[@class="andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript"]/span[@class="andes-money-amount__fraction"]/text()')

                df = pd.DataFrame({
                    'Titulo': titulos,
                    'Enlace': urls,
                    'Precios': precios
                })

                df['Vendedor'] = ""
                df['Detalles'] = ""
                df['Cantidad'] = ""
                df['Estado'] = ""
                df['Oferta'] = ""
                df['Publicacion'] = ""
                df['Fecha_Ejecucion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for index, row in df.iterrows():
                    product_url = row['Enlace']
                    product_response = requests.get(product_url)
                    product_soup = BeautifulSoup(product_response.content, 'html.parser')

                    vendedor = product_soup.find('span', attrs={"class": "ui-pdp-color--BLUE ui-pdp-family--REGULAR"})
                    detalles = product_soup.find('span', attrs={"class": "ui-pdp-subtitle"})
                    cantidad = product_soup.find('span', attrs={"class": "ui-pdp-buybox__quantity__available"})
                    estado = product_soup.find('span', attrs={"class": "ui-pdp-subtitle"})
                    oferta = product_soup.find('div', attrs={"class": "ui-pdp-promotions-pill-label ui-pdp-background-color--BLUE ui-pdp-color--WHITE ui-pdp-size--XXSMALL ui-pdp-family--SEMIBOLD"})
                    publicacion = product_soup.find('span', attrs={"class": "ui-pdp-color--BLACK ui-pdp-family--SEMIBOLD"})
                    familia_elements = product_soup.find_all('li', class_='andes-breadcrumb__item')

                    df.at[index, 'Vendedor'] = vendedor.text if vendedor else "No disponible"
                    df.at[index, 'Detalles'] = detalles.text if detalles else "No disponible"
                    df.at[index, 'Cantidad'] = cantidad.text if cantidad else "No disponible"
                    df.at[index, 'Estado'] = estado.text if estado else "No disponible"
                    df.at[index, 'Oferta'] = oferta.text if oferta else "No disponible"
                    df.at[index, 'Publicacion'] = publicacion.text if publicacion else "No disponible"

                    for i, familia_element in enumerate(familia_elements):
                        familia_column_name = f'Familia{i+1}'
                        df.at[index, familia_column_name] = familia_element.find('a', class_='andes-breadcrumb__link').text if familia_element else "No disponible"

                all_dfs.append(df)
            else:
                print(f"Failed to retrieve data from page {page_number}. Status code: {response.status_code}")

        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'{texto_busqueda_formateado}_{fecha_actual}_pages.csv'

        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(nombre_archivo, index=False)

        messagebox.showinfo("Scraping completado", f"El archivo fue exportado con éxito. Fecha y hora: {fecha_actual}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MercadoLibreScraperUI(root)
    root.mainloop()
