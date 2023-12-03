import os
import zipfile
from auth_config import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
import log_config
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle
from selenium.common.exceptions import NoSuchElementException
import random
from selenium.webdriver.common.action_chains import ActionChains

class Instagram_Liker:
    def __init__(self, url:str): #функция ицициализации основной страницы +хэштэг
        self.url = url
        log_config.logging.info('Инициализация прошла')

    def __get_chromedriver(self, use_proxy=False, user_agent=None): #функция создания драйвера
        manifest_json = """
        {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_IP, PROXY_PORT, PROXY_LOGIN, PROXY_PASSWORD)
        chrome_options = webdriver.ChromeOptions()
        if use_proxy:
            plugin_file = 'proxy_auth_plugin.zip'
            with zipfile.ZipFile(plugin_file, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            chrome_options.add_extension(plugin_file)
        if user_agent:
            chrome_options.add_argument(f'--user-agent={user_agent}')
        #chrome_options.add_argument("--headless=new")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--log-level=3")
        mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''
        })
        log_config.logging.info('Драйвер получен')
        
    def __authorization(self): #функция ыполняет авторизацию
        self.driver.get(self.url)
        for cookie in pickle.load(open('session', "rb")):
            self.driver.add_cookie(cookie)
        log_config.logging.info('Куки загружены')
        #time.sleep(100)
        #pickle.dump(self.driver.get_cookies(), open('session', 'wb'))
        log_config.logging.info(f'URL {self.url} загружен')
        self.driver.refresh()
        time.sleep(10)
        
 
    def __get_urls(self):
        #список исключений при сборке ссылок на профили
        except_list = [
            'https://about.instagram.com/',
            'https://about.instagram.com/blog/',
            'https://developers.facebook.com/docs/instagram',
            'https://help.instagram.com/',
            'https://www.instagram.com/',
            'https://www.instagram.com/about/jobs/',
            'https://www.instagram.com/accounts/meta_verified/?entrypoint=web_footer',
            'https://www.instagram.com/direct/inbox/',
            'https://www.instagram.com/explore/',
            'https://www.instagram.com/explore/locations/',
            'https://www.instagram.com/reels/',
            'https://www.threads.net/',
            'https://www.instagram.com/legal/terms/',
            'https://www.instagram.com/legal/privacy/',
        ] 
        
        try:
            WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[class*='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _alvs _a6hd']"))).click()
            WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, '_aano')))
            log_config.logging.info('Кнопка ПОДПИСЧИКИ нажата')
            time.sleep(5)
        except Exception as ex:
            log_config.logging.info('Кнопка ПОДПИСЧИКИ НЕ нажата')
            self.driver.close()
            Instagram_Liker(url='https://www.instagram.com/xudozhka39/').parse()
        users = set()
        existing_urls = self.__read_file()
        while len(users) < NUMBER_OF_USERS: #пока количество собранных меньше указанноу число
            log_config.logging.info(f'Собрано {len(users)} ссылок')
            try:
                followers = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/')]")
                for i in followers:
                    if i.get_attribute("href") and (i.get_attribute("href") not in except_list) and (i.get_attribute("href") not in existing_urls):
                        users.add(i.get_attribute("href"))
                    else:
                        continue
                ActionChains(self.driver).send_keys(Keys.END).perform()
                time.sleep(1)
 
            except Exception as ex:
                log_config.logging.info(f'Ошибка при парсинге.. {ex}')
                self.__write_file(list(users)) #запись в файл в случае ошибки
                break
        self.__write_file(list(users)) #заспись в файл после окончания парсинга
                
        

    def __read_file(self, filename = 'urls.txt') -> list: #функция чтения из файла где хранятся все ссылки которые уже скачаны
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    url_list = []
                    for line in file:
                        url_list.append(line.rstrip())
                        
                log_config.logging.info('Чтение списка существующих ссылко успешно')
                return url_list
            except Exception as ex:
                log_config.logging.info(f'Ошибка чтения списка суествующих файлов - {ex}')
        

    def __write_file(self, new_urls:list, filename = 'urls.txt'): #функция записи в файл, где хранятся все пролайканные посты - получает список, добавляет элементы построчно
        try:
            with open(filename, 'a', encoding='utf-8') as file:
                for line in new_urls:
                    file.write(line + '\n')
            log_config.logging.info('Успешная запись в файл urls.txt')
        except Exception as ex:
            log_config.logging.info('Ошибка записи в файл urls.txt')

    def parse(self):
        self.__get_chromedriver(use_proxy=True, user_agent=None)
        self.__authorization()
        self.__get_urls()

if __name__ == "__main__":
    Instagram_Liker(url='https://www.instagram.com/xudozhka39/').parse()