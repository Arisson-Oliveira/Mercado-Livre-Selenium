import logging
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from time import sleep
import random

# Configurar logging
logging.basicConfig(filename='app.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Definir o caminho para o chromedriver
    if getattr(sys, 'frozen', False):
        chromedriver_path = os.path.join(sys._MEIPASS, 'chromedriver.exe')
    else:
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')

    # Configuração do serviço do ChromeDriver
    service = Service(chromedriver_path)
    logging.info('Serviço do ChromeDriver configurado.')

    # Inicializa o WebDriver com o serviço
    driver = webdriver.Chrome(service=service)
    logging.info('WebDriver inicializado.')

    try:
        # Navegar até o site
        driver.get('https://www.mercadolivre.com.br')
        logging.info('Navegou até Mercado Livre.')

        # Esperar até que o campo de pesquisa esteja presente
        campo_pesquisa = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@class='nav-search-input']"))
        )
        logging.info('Campo de pesquisa encontrado.')

        # Simular o clique e enviar o nome do produto
        nome_produto = input('Digite o nome do produto que deseja buscar! ')
        campo_pesquisa.click()
        campo_pesquisa.send_keys(nome_produto)
        campo_pesquisa.send_keys(Keys.ENTER)
        logging.info('Produto buscado: %s', nome_produto)

        # Loop para extrair títulos e preços
        while True:
            try:
                # Esperar até que os títulos e preços estejam presentes
                titulos = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='ui-search-item__title']"))
                )
                precos = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[@class='ui-search-price__second-line']//span[@class='andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript']//span[@class='andes-money-amount__fraction']"))
                )
                logging.info('Títulos e preços encontrados.')

                # Escrever os dados no arquivo
                for titulo, preco in zip(titulos, precos):
                    try:
                        with open('produtos.txt', 'a', newline='', encoding='utf-8') as arquivo:
                            arquivo.write(titulo.text + ',' + preco.text + os.linesep)
                    except StaleElementReferenceException:
                        continue

                # Tentar encontrar e clicar no botão 'Próximo'
                try:
                    botao_proximo = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//li[@class='andes-pagination__button andes-pagination__button--next']"))
                    )
                    driver.execute_script('arguments[0].scrollIntoView(true);', botao_proximo)
                    botao_proximo.click()
                    sleep(random.randint(3, 5))
                except NoSuchElementException:
                    logging.info("Fim da paginação ou botão 'Próximo' não encontrado.")
                    break

            except TimeoutException:
                logging.error("Erro ao carregar elementos da página.")
                break

    finally:
        # Fechar o driver corretamente
        driver.quit()
        logging.info('Driver fechado.')

except Exception as e:
    logging.exception("Ocorreu um erro durante a execução do script.")
