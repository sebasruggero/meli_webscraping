from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import etree
from datetime import datetime
import tkinter as tk
from tkinter import Label, Entry, Button, Text, Scrollbar

class MercadoLibreScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("MercadoLibre Scraper made by Sebastian Ruggero")

        self.create_widgets()

    def create_widgets(self):
        self.label_busqueda = Label(self.master, text="Ingrese lo que desea buscar en MercadoLibre:")
        self.label_busqueda.pack()

        self.entry_busqueda = Entry(self.master)
        self.entry_busqueda.pack()

        self.label_max_pages = Label(self.master, text="Número máximo de páginas a scrapear:")
        self.label_max_pages.pack()

        self.entry_max_pages = Entry(self.master)
        self.entry_max_pages.pack()

        self.scrape_button = Button(self.master, text="Scrapear", command=self.scrape)
        self.scrape_button.pack()

        self.output_text = Text(self.master, wrap=tk.WORD, height=20, width=50)
        self.output_text.pack()

        self.scrollbar = Scrollbar(self.master, command=self.output_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    def scrape(self):
        texto_busqueda = self.entry_busqueda.get()
        max_pages = int(self.entry_max_pages.get())

        all_dfs = []

        for page_number in range(1, max_pages + 1):
            current_url = self.get_search_url(texto_busqueda, page_number)
            response = requests.get(current_url)

            if response.status_code == 200:
                self.output_text.insert(tk.END, f"Scraping data from page {page_number}\n")
                self.master.update()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Resto del código para scraping...
                # Resto del código para scraping...

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
                self.output_text.insert(tk.END, f"Failed to retrieve data from page {page_number}. Status code: {response.status_code}\n")
                self.master.update()

        texto_archivo_formateado = texto_busqueda.replace(' ', '_')

        fecha_actual = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        nombre_archivo = f'{texto_archivo_formateado}_{fecha_actual}.csv'

        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(nombre_archivo, index=False)

        self.output_text.insert(tk.END, f"Scraping completado. El archivo fue exportado con éxito. Fecha y hora: {fecha_actual}\n")
        self.master.update()

    def get_search_url(self, texto_busqueda, page_number):
        texto_busqueda_formateado = texto_busqueda.replace(' ', '-')
        base_url = f'https://listado.mercadolibre.com.ar/{texto_busqueda_formateado}'
        if page_number > 1:
            return f'{base_url}_Desde_{(page_number - 1) * 50 + 1}_NoIndex_True'
        else:
            return base_url

if __name__ == "__main__":
    root = tk.Tk()
    app = MercadoLibreScraperApp(root)
    root.mainloop()
