from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from zapv2 import ZAPv2
import time

# Configuración del Proxy ZAP
ZAP_PROXY_ADDRESS = '127.0.0.1'
ZAP_PROXY_PORT = 8080
# Target de prueba
target_url = 'https://www.hackthissite.org/'
apiKey = 'e2q0nlun84j194hscevlrem7d0'  # Asegúrate de usar tu API Key si es necesario

# Configuración del Proxy en Selenium
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = f'{ZAP_PROXY_ADDRESS}:{ZAP_PROXY_PORT}'
proxy.ssl_proxy = f'{ZAP_PROXY_ADDRESS}:{ZAP_PROXY_PORT}'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')  # Para manejar errores de SSL
chrome_options.add_argument('--incognito')  # Modo incógnito si lo prefieres
chrome_options.proxy = proxy

# Iniciar WebDriver de Selenium
driver = webdriver.Chrome(options=chrome_options)

# Iniciar ZAP API
zap = ZAPv2(apikey=apiKey)


# Realiza las interacciones necesarias en la página usando Selenium
driver.get(target_url)

# Aquí puedes agregar el código para iniciar sesión u otras interacciones:
# driver.find_element_by_id('login').send_keys('myusername')
# driver.find_element_by_id('password').send_keys('mypassword')
# driver.find_element_by_id('submit').click()

# Ahora que el navegador está configurado y Selenium está interactuando, podemos lanzar el Ajax Spider.
print(f'Iniciando el Ajax Spider para: {target_url}')
scan_id = zap.ajaxSpider.scan(target_url)

# Espera a que el escaneo termine
timeout = time.time() + 60*5  # Tiempo de espera de 5 minutos
while time.time() < timeout:
    # Verificar si el Ajax Spider ha terminado
    status = zap.ajaxSpider.status
    print(f'Estatus del Ajax Spider: {status}')
    if status == 'stopped':
        print('El Ajax Spider ha terminado')
        break
    time.sleep(2)

# Opcional: Imprimir los resultados
ajax_results = zap.ajaxSpider.results(start=0, count=10)
print('Resultados del Ajax Spider:')
for result in ajax_results:
    print(f'Resultado: {result}')

# Cerrar el navegador al finalizar
driver.quit()
