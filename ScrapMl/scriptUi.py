from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import etree
from datetime import datetime
import tkinter as tk
from tkinter import Entry, Button, Label

# Función para obtener la URL de la página de resultados según el número de página
def get_search_url(search_text, page_number):
    search_text_formated = search_text.replace(' ', '-')
    base_url = f'https://listado.mercadolibre.com.ar/{search_text_formated}'
    
    if page_number > 1:
        return f'{base_url}_Desde_{(page_number - 1) * 50 + 1}_NoIndex_True'
    else:
        return base_url

# Función para realizar el web scraping
def scrape_mercadolibre(search_text, max_pages):
    all_dfs = []

    for page_number in range(1, max_pages + 1):
        current_url = get_search_url(search_text, page_number)
        response = requests.get(current_url)

        if response.status_code == 200:
            print(f"Scraping data from page {page_number}")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            titulos = soup.find_all('h2', attrs={"class":"ui-search-item__title"})
            titulos = [i.text for i in titulos]

            urls = soup.find_all('a', attrs={"class":"ui-search-item__group__element ui-search-link__title-card ui-search-link"})
            urls = [i.get('href') for i in urls]

            dom = etree.HTML(str(soup))
            precios = dom.xpath('//li[contains(@class, "ui-search-layout__item")]//span[@class="andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript"]/span[@class="andes-money-amount__fraction"]/text()')

            df = pd.DataFrame({
                'Titulo': titulos,
                'Enlace': urls,
                'Precios': precios
            })

            all_dfs.append(df)
        else:
            print(f"Failed to retrieve data from page {page_number}. Status code: {response.status_code}")

    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f'{search_text}_{fecha_actual}_pages.csv'
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.to_csv(nombre_archivo, index=False)
    print(f"Scraping completed. The file was successfully exported. Date and time: {fecha_actual}")

# Función que se ejecutará al hacer clic en el botón de búsqueda
def search_button_clicked():
    texto_busqueda = entry_texto_busqueda.get()
    max_pages = int(entry_max_pages.get())
    scrape_mercadolibre(texto_busqueda, max_pages)

# Crear la ventana principal
window = tk.Tk()
window.title("MercadoLibre Web Scraper")

# Crear y posicionar los elementos en la ventana
label_texto_busqueda = Label(window, text="Ingrese lo que desea buscar en MercadoLibre:")
label_texto_busqueda.pack()

entry_texto_busqueda = Entry(window)
entry_texto_busqueda.pack()

label_max_pages = Label(window, text="Número máximo de páginas a scrapear:")
label_max_pages.pack()

entry_max_pages = Entry(window)
entry_max_pages.pack()

button_scrape = Button(window, text="Scrapear MercadoLibre", command=search_button_clicked)
button_scrape.pack()

# Iniciar el bucle principal de la interfaz gráfica
window.mainloop()
