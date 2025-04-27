from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from zapv2 import ZAPv2
import time

# Target de prueba
target_url = 'http://localhost:3000/'
apiKey = 'e2q0nlun84j194hscevlrem7d0'  # Asegúrate de usar tu API Key si es necesario

# Iniciar ZAP API
zap = ZAPv2(apikey=apiKey)

# Verificar que las cookies se han añadido correctamente
tokens = zap.httpsessions.session_tokens(target_url)
for token in tokens:
    print(f"Token: {token}")

# Ahora que el navegador está configurado y Selenium está interactuando, podemos lanzar el Ajax Spider.
print(f'Iniciando el Ajax Spider para: {target_url}')
scan_id = zap.ajaxSpider.scan(target_url)
time.sleep(5)  # Esperar un poco para que el escaneo comience
zap.ajaxSpider.stop()
# Espera a que el escaneo termine
timeout = time.time() + 60*3  # Tiempo de espera de 2 minutos
while time.time() < timeout:
    # Verificar si el Ajax Spider ha terminado
    status = zap.ajaxSpider.status  # Llamado como función
    print(f'Estatus del Ajax Spider: {status}')
    if status == 'stopped':
        print('El Ajax Spider ha terminado')
        break
    time.sleep(2)


# Generar reporte XML después de que el escaneo termine
report_xml = zap.core.xmlreport()
with open('zap_report.xml', 'w') as f:
    f.write(report_xml)

# Imprimir los resultados
urls = zap.core.urls(baseurl=target_url)
print(f'URLs descubiertas por el Ajax Spider: {urls}')
