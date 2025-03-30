import os
import random
import string
import threading
import time
from queue import Queue
import platform
import requests
from colorama import Fore, init
import concurrent.futures
from urllib.parse import urlparse
import socket
import json
import re
import psutil
import multiprocessing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import chromedriver_autoinstaller
from selenium.webdriver.common.keys import Keys

init(autoreset=True)

# Diccionarios de idiomas
LANGUAGES = {
    'en': {
        'intro': """
  _/|       |\_
 /  |       |  \ 
|    \     /    |
|  \ /     \ /  |
| \  |     |  / |
| \ _\_/^\_/_ / |
|    --\//--    |
 \_  \     /  _/
   \__  |  __/
      \ _ /
     _/   \_   YouTube Livestream Bot - Phoenix Version
    / _/|\_ \  https://github.com/Omar-Obando/Youtube-Livestream-bot
     /  |  \   V 1.5
      / v \ 
""",
        'stream_id': "Enter stream ID: ",
        'proxy_method': "\nHow do you want to load proxies?",
        'proxy_option1': "[1] Use proxys.txt",
        'proxy_option2': "[2] Use sitios.txt",
        'proxy_choice': "Choose an option (1-2): ",
        'scrape_amount': "How many proxies do you want to scrape? (Recommended: 1000-5000): ",
        'system_resources': "\nSystem Resources:",
        'available_memory': "Available Memory: {:.2f} MB",
        'available_cpu': "Available CPU: {:.1f}%",
        'cpu_cores': "CPU Cores: {}",
        'recommended_threads': "Recommended Threads: {}",
        'thread_config': "\nHow do you want to configure threads?",
        'thread_option1': "[1] Automatic adjustment based on resources",
        'thread_option2': "[2] Manual selection",
        'thread_choice': "Choose an option (1-2): ",
        'thread_count': "How many threads? (Recommended: 500-1000): ",
        'starting_threads': "Starting {} threads...",
        'stopping_bot': "\nStopping bot...",
        'no_proxies': "[-] No proxies available",
        'proxy_verified': "[+] Proxy verified: {}",
        'proxy_not_working': "[-] Non-functional proxy: {}",
        'no_working_proxies': "No functional proxies found",
        'loaded_proxies': "[+] Loaded {} proxies from {}",
        'scraping_url': "[*] Scraping: {}",
        'found_proxies': "[+] Found {} proxies in {}",
        'verifying_proxies': "[*] Verifying {} unique proxies...",
        'saving_proxies': "[+] Saving {} proxies to scrapeado.txt",
        'error_file_not_found': "Error: {} not found",
        'error_loading_proxies': "Error loading proxies: {}",
        'error_scraping': "Error scraping {}: {}"
    },
    'es': {
        'intro': """
  _/|       |\_
 /  |       |  \ 
|    \     /    |
|  \ /     \ /  |
| \  |     |  / |
| \ _\_/^\_/_ / |
|    --\//--    |
 \_  \     /  _/
   \__  |  __/
      \ _ /
     _/   \_   YouTube Livestream Bot - Phoenix Version
    / _/|\_ \  https://github.com/Omar-Obando/Youtube-Livestream-bot
     /  |  \   V 1.5
      / v \ 
""",
        'stream_id': "Ingresa el ID del stream: ",
        'proxy_method': "\n¿Cómo deseas cargar los proxies?",
        'proxy_option1': "[1] Usar proxys.txt",
        'proxy_option2': "[2] Usar sitios.txt",
        'proxy_choice': "Elige una opción (1-2): ",
        'scrape_amount': "¿Cuántos proxies deseas scrapear? (Recomendado: 1000-5000): ",
        'system_resources': "\nRecursos del sistema:",
        'available_memory': "Memoria disponible: {:.2f} MB",
        'available_cpu': "CPU disponible: {:.1f}%",
        'cpu_cores': "Núcleos CPU: {}",
        'recommended_threads': "Hilos recomendados: {}",
        'thread_config': "\n¿Cómo deseas configurar los hilos?",
        'thread_option1': "[1] Ajuste automático basado en recursos",
        'thread_option2': "[2] Selección manual",
        'thread_choice': "Elige una opción (1-2): ",
        'thread_count': "¿Cuántos hilos? (Recomendado: 500-1000): ",
        'starting_threads': "Iniciando {} hilos...",
        'stopping_bot': "\nDeteniendo bot...",
        'no_proxies': "[-] No hay proxies disponibles",
        'proxy_verified': "[+] Proxy verificado: {}",
        'proxy_not_working': "[-] Proxy no funcional: {}",
        'no_working_proxies': "No se encontraron proxies funcionales",
        'loaded_proxies': "[+] Cargados {} proxies desde {}",
        'scraping_url': "[*] Scrapeando: {}",
        'found_proxies': "[+] Encontrados {} proxies en {}",
        'verifying_proxies': "[*] Verificando {} proxies únicos...",
        'saving_proxies': "[+] Guardando {} proxies en scrapeado.txt",
        'error_file_not_found': "Error: {} no encontrado",
        'error_loading_proxies': "Error al cargar proxies: {}",
        'error_scraping': "Error al scrapear {}: {}"
    }
}

class ProxyManager:
    """
    Clase para gestionar proxies, incluyendo carga, verificación y scraping.
    """
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.lock = threading.Lock()
        self.proxy_timeout = 10
        self.required_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-419,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        }
        
    def verify_proxy(self, proxy):
        try:
            # Verificar si es un proxy IPv4 válido
            if not re.match(r'^(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}$', proxy):
                return False

            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            # Primera verificación con ip-api.com
            try:
                response = requests.get(
                    'http://ip-api.com/json',
                    proxies=proxy_dict,
                    timeout=5,
                    verify=False,
                    headers=self.required_headers
                )
                
                if response.status_code != 200:
                    return False
                    
                data = response.json()
                if data.get('status') != 'success':
                    return False
                    
                # Segunda verificación con YouTube
                response = requests.get(
                    'https://www.youtube.com',
                    proxies=proxy_dict,
                    timeout=5,
                    verify=False,
                    headers=self.required_headers,
                    allow_redirects=True
                )
                
                if response.status_code != 200:
                    return False
                    
                if 'youtube.com' not in response.url:
                    return False
                    
                return True
                
            except requests.exceptions.RequestException:
                return False
            except Exception:
                return False
                
        except Exception:
            return False

    def scrape_proxies_from_url(self, url, max_proxies=None, current_total=0):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            }
            response = requests.get(url, timeout=10, verify=False, headers=headers)
            if response.status_code == 200:
                # Patrones para diferentes formatos de proxy
                patterns = [
                    r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b',  # IPv4:Puerto
                    r'\b(?:\d{1,3}\.){3}\d{1,3}\s+:\s+\d{2,5}\b',  # IPv4 : Puerto
                    r'\b(?:\d{1,3}\.){3}\d{1,3}\t+\d{2,5}\b',  # IPv4\tPuerto
                    r'\b(?:\d{1,3}\.){3}\d{1,3}\s+\d{2,5}\b',  # IPv4 Puerto
                ]
                
                proxies = set()
                content = response.text
                
                # Limpiar el contenido
                content = content.replace('\r', '')
                content = content.replace('\t', ' ')
                
                # Buscar proxies con diferentes patrones
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Limpiar y validar el proxy
                        proxy = re.sub(r'\s+', '', match)
                        if re.match(r'^(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}$', proxy):
                            proxies.add(proxy)
                
                # Si hay un límite máximo, ajustar el número de proxies
                if max_proxies:
                    remaining_slots = max_proxies - current_total
                    if remaining_slots <= 0:
                        return []
                    proxies = list(proxies)[:remaining_slots]
                else:
                    proxies = list(proxies)
                    
                return proxies
        except Exception as e:
            print(f"{Fore.RED}{LANGUAGES[lang]['error_scraping'].format(url, str(e))}")
        return []
            
    def load_proxies_from_file(self, filename, lang='es', max_proxies=None):
        try:
            if filename == "sitios.txt":
                print(f"{Fore.YELLOW}{LANGUAGES[lang]['scraping_url']}")
                with open(filename, "r") as f:
                    urls = [line.strip() for line in f if line.strip()]
                
                if not urls:
                    print(f"{Fore.RED}{LANGUAGES[lang]['error_file_not_found'].format(filename)}")
                    return False
                
                working_proxies = 0
                current_url_index = 0
                batch_size = 100  # Aumentar el tamaño del lote
                
                while working_proxies < max_proxies and current_url_index < len(urls):
                    url = urls[current_url_index]
                    print(f"{Fore.YELLOW}{LANGUAGES[lang]['scraping_url'].format(url)}")
                    
                    # Scrapear un lote de proxies
                    proxies = self.scrape_proxies_from_url(url, batch_size)
                    print(f"{Fore.GREEN}{LANGUAGES[lang]['found_proxies'].format(len(proxies), url)}")
                    
                    if not proxies:
                        current_url_index += 1
                        continue
                    
                    # Verificar los proxies en paralelo
                    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:  # Aumentar workers
                        future_to_proxy = {executor.submit(self.verify_proxy, proxy): proxy for proxy in proxies}
                        
                        for future in concurrent.futures.as_completed(future_to_proxy):
                            proxy = future_to_proxy[future]
                            try:
                                if future.result():
                                    self.proxies.append(proxy)
                                    working_proxies += 1
                                    print(f"{Fore.GREEN}{LANGUAGES[lang]['proxy_verified'].format(proxy)}")
                                    
                                    if working_proxies >= max_proxies:
                                        break
                            except Exception as e:
                                print(f"{Fore.RED}{LANGUAGES[lang]['proxy_not_working'].format(proxy)}")
                    
                    # Si no encontramos suficientes proxies funcionales, continuamos con el siguiente sitio
                    if working_proxies < max_proxies:
                        current_url_index += 1
                
                if not self.proxies:
                    print(f"{Fore.RED}{LANGUAGES[lang]['no_working_proxies']}")
                    return False
                    
                print(f"{Fore.GREEN}{LANGUAGES[lang]['loaded_proxies'].format(len(self.proxies), filename)}")
            else:
                with open(filename, "r") as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                print(f"{Fore.GREEN}{LANGUAGES[lang]['loaded_proxies'].format(len(self.proxies), filename)}")
            
            return True
            
        except FileNotFoundError:
            print(f"{Fore.RED}{LANGUAGES[lang]['error_file_not_found'].format(filename)}")
            return False
        except Exception as e:
            print(f"{Fore.RED}{LANGUAGES[lang]['error_loading_proxies'].format(str(e))}")
            return False

    def get_random_proxy(self):
        """
        Obtiene un proxy aleatorio de la lista.
        
        Returns:
            str: Proxy aleatorio o None si no hay disponibles
        """
        with self.lock:
            if not self.proxies:
                return None
            proxy = random.choice(self.proxies)
            if not self.verify_proxy(proxy):
                self.proxies.remove(proxy)
                if not self.proxies:
                    return None
                proxy = random.choice(self.proxies)
            return proxy

class YouTubeBot:
    def __init__(self, lang='es'):
        self.proxy_manager = ProxyManager()
        self.botted = 0
        self.lock = threading.Lock()
        self.printing = []
        self.token = None
        self.running = True
        self.max_windows = 10  # Máximo número de ventanas simultáneas
        self.active_windows = 0
        self.window_lock = threading.Lock()
        self.session_duration = 0  # 0 = indefinido
        self.lang = lang
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        ]

    def set_token(self, token):
        self.token = token

    def set_session_duration(self, duration):
        self.session_duration = duration

    def increment_botted(self):
        with self.lock:
            self.botted += 1

    def print_status(self):
        while self.running:
            try:
                os.system('cls' if platform.system() == 'Windows' else 'clear')
                print(Fore.LIGHTCYAN_EX + LANGUAGES[self.lang]['intro'])
                print(f"{Fore.LIGHTMAGENTA_EX}Botted: {self.botted}")
                print(f"{Fore.LIGHTMAGENTA_EX}Ventanas activas: {self.active_windows}")
                for i in range(max(0, len(self.printing) - 10), len(self.printing)):
                    print(self.printing[i])
                time.sleep(0.5)
            except Exception as e:
                print(f"{Fore.RED}Error en print_status: {str(e)}")
                time.sleep(1)

    def wait_for_window_slot(self):
        while True:
            with self.window_lock:
                if self.active_windows < self.max_windows:
                    self.active_windows += 1
                    return True
            time.sleep(1)

    def release_window_slot(self):
        with self.window_lock:
            self.active_windows -= 1

    def setup_driver(self, proxy):
        try:
            if not self.wait_for_window_slot():
                return None

            chromedriver_autoinstaller.install()
            
            options = Options()
            options.add_argument('--start-maximized')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-web-security')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-site-isolation-trials')
            options.add_argument(f'--proxy-server={proxy}')
            
            # Agregar más argumentos para evadir la detección
            options.add_argument('--disable-blink-features')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Usar un user agent más realista
            user_agent = random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            ])
            options.add_argument(f'user-agent={user_agent}')
            
            prefs = {
                'profile.default_content_setting_values.notifications': 2,
                'profile.managed_default_content_settings.images': 1,
                'profile.default_content_setting_values.cookies': 1,
                'profile.default_content_setting_values.plugins': 1,
                'profile.default_content_setting_values.popups': 2,
                'profile.default_content_setting_values.geolocation': 2,
                'profile.default_content_setting_values.media_stream': 2,
                'profile.default_content_setting_values.automatic_downloads': 1,
                'profile.default_content_setting_values.media_stream_mic': 2,
                'profile.default_content_setting_values.media_stream_camera': 2,
                'profile.default_content_setting_values.protocol_handlers': 1,
                'profile.default_content_setting_values.ppapi_broker': 1,
                'profile.default_content_setting_values.automatic_downloads': 1,
                'profile.default_content_setting_values.midi_sysex': 1,
                'profile.default_content_setting_values.push_messaging': 1,
                'profile.default_content_setting_values.ssl_cert_decisions': 1,
                'profile.default_content_setting_values.metro_switch_to_desktop': 1,
                'profile.default_content_setting_values.protected_media_identifier': 1,
                'profile.default_content_setting_values.app_banner': 1,
                'profile.default_content_setting_values.site_engagement': 1,
                'profile.default_content_setting_values.durable_storage': 1,
                'profile.default_content_setting_values.autoplay': 1,
            }
            options.add_experimental_option('prefs', prefs)
            
            driver = webdriver.Chrome(options=options)
            
            # Modificar el navigator.webdriver
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                '''
            })
            
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            with self.lock:
                self.printing.append(f"{Fore.RED}[-] Error al configurar el driver: {str(e)}")
            self.release_window_slot()
            return None

    def bot(self):
        start_time = time.time()
        while self.running:
            try:
                if self.session_duration > 0 and time.time() - start_time > self.session_duration:
                    break

                proxy = self.proxy_manager.get_random_proxy()
                if not proxy:
                    with self.lock:
                        self.printing.append(f"{Fore.RED}[-] {LANGUAGES[self.lang]['no_proxies']}")
                    time.sleep(5)
                    continue

                driver = self.setup_driver(proxy)
                if not driver:
                    continue

                try:
                    # Agregar un pequeño retraso aleatorio antes de cargar la página
                    time.sleep(random.uniform(1, 3))
                    
                    driver.get(f"https://www.youtube.com/watch?v={self.token}")
                    
                    # Simular comportamiento humano
                    self.simulate_human_behavior(driver)
                    
                    # Esperar a que el video cargue
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "video"))
                    )
                    
                    # Intentar autoplay con comportamiento más humano
                    self.handle_video_playback(driver)
                    
                    # Mantener la sesión activa
                    while self.running:
                        if self.session_duration > 0 and time.time() - start_time > self.session_duration:
                            break
                            
                        try:
                            # Simular interacción humana periódica
                            self.simulate_human_interaction(driver)
                            
                            # Verificar y mantener la reproducción
                            self.maintain_video_playback(driver)
                            
                            # Manejar anuncios
                            self.handle_ads(driver)
                            
                            self.increment_botted()
                            with self.lock:
                                self.printing.append(f"{Fore.GREEN}[+] {LANGUAGES[self.lang]['proxy_verified'].format(proxy)}")
                            
                            # Tiempo de espera aleatorio
                            time.sleep(random.uniform(0.5, 2))
                            
                        except Exception as e:
                            with self.lock:
                                self.printing.append(f"{Fore.RED}[-] Error en la sesión: {str(e)}")
                            break
                            
                except TimeoutException:
                    with self.lock:
                        self.printing.append(f"{Fore.RED}[-] Timeout al cargar el video")
                except Exception as e:
                    with self.lock:
                        self.printing.append(f"{Fore.RED}[-] Error: {str(e)}")
                finally:
                    try:
                        driver.quit()
                    except:
                        pass
                    self.release_window_slot()

            except Exception as e:
                with self.lock:
                    self.printing.append(f"{Fore.RED}[-] Error general: {str(e)}")
                time.sleep(2)
                continue

    def simulate_human_behavior(self, driver):
        try:
            # Simular movimiento del mouse
            action = webdriver.ActionChains(driver)
            for _ in range(random.randint(2, 4)):
                x = random.randint(0, 800)
                y = random.randint(0, 600)
                action.move_by_offset(x, y).perform()
                time.sleep(random.uniform(0.1, 0.3))
            
            # Simular scroll
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
            time.sleep(random.uniform(0.5, 1))
            
            # Simular interacción con elementos de la página
            elements = driver.find_elements(By.TAG_NAME, "button")
            if elements:
                random.choice(elements).click()
                time.sleep(random.uniform(0.5, 1))
        except:
            pass

    def simulate_human_interaction(self, driver):
        try:
            # Simular movimiento del mouse aleatorio
            action = webdriver.ActionChains(driver)
            x = random.randint(-100, 100)
            y = random.randint(-100, 100)
            action.move_by_offset(x, y).perform()
            
            # Simular scroll aleatorio
            scroll_amount = random.randint(-100, 100)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # Simular interacción con controles del video
            try:
                controls = driver.find_element(By.CLASS_NAME, "ytp-chrome-controls")
                if controls:
                    action.move_to_element(controls).perform()
            except:
                pass
                
        except:
            pass

    def handle_video_playback(self, driver):
        try:
            # Intentar múltiples métodos de reproducción
            methods = [
                self.click_play_button,
                self.use_javascript_play,
                self.simulate_space_key
            ]
            
            for method in methods:
                try:
                    if method(driver):
                        break
                except:
                    continue
                    
        except:
            pass

    def click_play_button(self, driver):
        try:
            play_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-play-button"))
            )
            play_button.click()
            return True
        except:
            return False

    def use_javascript_play(self, driver):
        try:
            driver.execute_script("""
                const video = document.querySelector('video');
                if(video) {
                    video.play();
                    video.muted = true;
                    video.volume = 0;
                }
            """)
            return True
        except:
            return False

    def simulate_space_key(self, driver):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.SPACE)
            return True
        except:
            return False

    def maintain_video_playback(self, driver):
        try:
            driver.execute_script("""
                const video = document.querySelector('video');
                if(video) {
                    if(video.paused) {
                        video.play();
                    }
                    video.muted = true;
                    video.volume = 0;
                }
            """)
        except:
            pass

    def handle_ads(self, driver):
        try:
            # Manejar botón de skip
            try:
                skip_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-skip-ad-button"))
                )
                skip_button.click()
                with self.lock:
                    self.printing.append(f"{Fore.GREEN}[+] Anuncio omitido")
            except:
                pass

            # Manejar anuncios superpuestos
            try:
                close_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-ad-overlay-close-button"))
                )
                close_button.click()
                with self.lock:
                    self.printing.append(f"{Fore.GREEN}[+] Anuncio superpuesto cerrado")
            except:
                pass
        except:
            pass

def main():
    # Selección de idioma
    print("\nSelect language / Selecciona el idioma:")
    print("1. English")
    print("2. Español")
    lang_choice = input("Choose an option / Elige una opción (1-2): ")
    lang = 'en' if lang_choice == '1' else 'es'
    
    print(LANGUAGES[lang]['intro'])
    
    bot = YouTubeBot(lang)
    token = input(f"{Fore.CYAN}{LANGUAGES[lang]['stream_id']}")
    bot.set_token(token)

    # Configuración de tiempo de sesión
    print(f"\n{Fore.CYAN}Session Duration / Duración de la sesión:")
    print("1. Indefinite / Indefinida")
    print("2. Custom time / Tiempo personalizado")
    duration_choice = input("Choose an option / Elige una opción (1-2): ")
    
    if duration_choice == "2":
        try:
            duration = int(input("Enter duration in seconds / Ingresa la duración en segundos: "))
            bot.set_session_duration(duration)
        except ValueError:
            print(f"{Fore.RED}Invalid input. Using indefinite duration.")
            bot.set_session_duration(0)
    else:
        bot.set_session_duration(0)

    # Configuración de ventanas
    print(f"\n{Fore.CYAN}Window Configuration / Configuración de ventanas:")
    print("1. Default (10 windows) / Por defecto (10 ventanas)")
    print("2. Custom / Personalizado")
    window_choice = input("Choose an option / Elige una opción (1-2): ")
    
    if window_choice == "2":
        try:
            max_windows = int(input("Enter maximum number of windows / Ingresa el número máximo de ventanas: "))
            bot.max_windows = max(1, min(max_windows, 50))  # Limitar entre 1 y 50 ventanas
        except ValueError:
            print(f"{Fore.RED}Invalid input. Using default value of 10 windows.")
            bot.max_windows = 10
    else:
        bot.max_windows = 10

    print(f"\n{Fore.CYAN}{LANGUAGES[lang]['proxy_method']}")
    print(f"{Fore.WHITE}{LANGUAGES[lang]['proxy_option1']}")
    print(f"{Fore.WHITE}{LANGUAGES[lang]['proxy_option2']}")
    
    proxy_choice = input(f"{Fore.CYAN}{LANGUAGES[lang]['proxy_choice']}")

    max_proxies = None
    if proxy_choice == "2":
        try:
            max_proxies = int(input(f"{Fore.CYAN}{LANGUAGES[lang]['scrape_amount']}"))
        except ValueError:
            print(f"{Fore.RED}Invalid input. Using default value.")
            max_proxies = 2000

    if proxy_choice == "1":
        if not bot.proxy_manager.load_proxies_from_file("proxys.txt", lang):
            return
    elif proxy_choice == "2":
        if not bot.proxy_manager.load_proxies_from_file("sitios.txt", lang, max_proxies):
            return
    else:
        print(f"{Fore.RED}Invalid option. Exiting...")
        return

    # Iniciar el thread de impresión
    threading.Thread(target=bot.print_status, daemon=True).start()
    
    # Iniciar los threads del bot basados en el número de ventanas
    print(f"{Fore.GREEN}{LANGUAGES[lang]['starting_threads'].format(bot.max_windows)}")
    for _ in range(bot.max_windows):
        threading.Thread(target=bot.bot, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bot.running = False
        print(f"\n{Fore.YELLOW}{LANGUAGES[lang]['stopping_bot']}")

if __name__ == "__main__":
    main() 