from bs4 import BeautifulSoup
import requests

url = 'https://listado.mercadolibre.com.ar/continental#D[A:continental]'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Ahora puedes buscar elementos y extraer información usando soup.find() o soup.select()
