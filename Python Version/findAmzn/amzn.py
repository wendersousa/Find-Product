# -*- coding: utf-8 -*-
"""
Bot de Scraping Avançado - AMAZON DEALS
Versão: 5.1 (Seletores `data-testid` + Correção de Caracteres)
Descrição: Coleta dados de produtos da página "Ofertas do Dia" da Amazon Brasil.
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.common.exceptions import TimeoutException  # Importar exceção correta
from typing import List, Dict, Tuple
from urllib.parse import urlparse

# =====================================================================
# CONFIGURAÇÕES GLOBAIS
# =====================================================================

URL_AMAZON_DEALS = "https://www.amazon.com.br/gp/goldbox"
TEMPO_ESPERA = 30
SCROLL_REPETICOES = 25
SCROLL_PAUSA = 1.5

# =====================================================================
# SELETORES CSS/XPATH (ATUALIZADOS)
# =====================================================================

class Seletores:
    # O bloco de produto agora é o "product-card"
    BLOCO_PRODUTO = (By.XPATH, "//div[@data-testid='product-card']")
    
    # O link também tem um testid
    LINK = (By.XPATH, ".//a[@data-testid='product-card-link']")
    
    # A imagem tem uma classe nova
    IMAGEM = (By.XPATH, ".//img[contains(@class,'ProductCardImage-module__image')]")
    
    # Este seletor ainda funciona
    PRECO_NOVO = (By.XPATH, ".//span[contains(@class,'a-price-whole')]")
    
    # O preço antigo mudou de 'a-text-strike' para 'a-text-price'
    PRECO_ANTIGO = (By.XPATH, ".//span[contains(@class,'a-text-price')]")

# =====================================================================
# FUNÇÕES AUXILIARES
# =====================================================================

def get_text(element, by_tuple: Tuple, default: str = "Não encontrado") -> str:
    try:
        return element.find_element(*by_tuple).text.strip()
    except Exception:
        return default

def get_attr(element, by_tuple: Tuple, attr: str, default: str = "Não encontrado") -> str:
    try:
        return element.find_element(*by_tuple).get_attribute(attr)
    except Exception:
        return default

# =====================================================================
# CONFIGURAÇÃO DO DRIVER
# =====================================================================

def iniciar_driver() -> webdriver.Chrome:
    print("\n🚀 Iniciando ChromeDriver (modo visível para teste)...")

    options = Options()
    # options.add_argument("--headless=new")  # MANTENHA COMENTADO PARA TESTAR
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Evita detecção
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    print("✅ Driver pronto!\n")
    return driver

# =====================================================================
# SCROLL
# =====================================================================

def scroll_pagina(driver, repeticoes=SCROLL_REPETICOES):
    print("📜 Fazendo scroll na página...")
    last_height = 0
    for i in range(repeticoes):
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSA)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print(f"✅ Fim da página após {i+1} scrolls.")
            break
        last_height = new_height

# =====================================================================
# COLETA DE DADOS (LÓGICA ATUALIZADA)
# =====================================================================

def coletar_dados(driver, wait, url: str) -> List[Dict]:
    print(f"\n🌐 Acessando: {url}")
    driver.get(url)
    time.sleep(3)

    # --- LINHAS DE DIAGNÓSTICO ---
    print(f"DEBUG: Título da página: {driver.title}")
    driver.save_screenshot("debug_pagina.png")
    print("DEBUG: Screenshot 'debug_pagina.png' salvo.")
    # --- FIM DO DIAGNÓSTICO ---

    wait.until(EC.presence_of_all_elements_located(Seletores.BLOCO_PRODUTO))
    scroll_pagina(driver)

    produtos = driver.find_elements(*Seletores.BLOCO_PRODUTO)
    print(f"✅ {len(produtos)} produtos encontrados.\n")

    lista = []
    for i, bloco in enumerate(produtos, 1):
        
        # --- LÓGICA DE COLETA ATUALIZADA ---
        
        # 1. Pega o elemento da imagem primeiro
        try:
            img_element = bloco.find_element(*Seletores.IMAGEM)
            # 2. Pega o NOME (do 'alt') e IMAGEM (do 'src') deste elemento
            nome = img_element.get_attribute('alt').strip()
            imagem = img_element.get_attribute('src').strip()
        except Exception:
            nome = "Nome não encontrado"
            imagem = "Imagem não encontrada"
        
        # 3. Pega o resto dos dados
        preco_novo = get_text(bloco, Seletores.PRECO_NOVO)
        preco_antigo = get_text(bloco, Seletores.PRECO_ANTIGO, default="Não informado")
        link = get_attr(bloco, Seletores.LINK, "href")
        
        # --- FIM DA ATUALIZAÇÃO ---

        # Limpa o link para remover parâmetros desnecessários
        if link != "Não encontrado":
            link = link.split("?")[0]
            if link.startswith("/"):
                link = "https://www.amazon.com.br" + link

        lista.append({
            "Nome_Produto": nome,
            "Valor_Promocional": preco_novo,
            "Valor_Original": preco_antigo,
            "Link_Produto": link,
            "Link_Imagem": imagem
        })

        if i % 20 == 0:
            print(f"  → {i} produtos processados...")

    return lista

# =====================================================================
# MAIN (TRY/EXCEPT ATUALIZADO)
# =====================================================================

def main():
    print("="*80)
    print("🛒 BOT AMAZON DEALS - v5.1 (data-testid)")
    print("="*80)

    driver = iniciar_driver()
    wait = WebDriverWait(driver, TEMPO_ESPERA)

    try:
        produtos = coletar_dados(driver, wait, URL_AMAZON_DEALS)

        if not produtos:
            print("⚠️ Nenhum produto encontrado.")
            return

        df = pd.DataFrame(produtos)
        nome_arquivo = f"amazon_ofertas_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(nome_arquivo, index=False)
        print(f"\n🎉 Coleta concluída com sucesso! {len(df)} produtos salvos em '{nome_arquivo}'.")

    except TimeoutException:  # Exceção específica
        print(f"\n❌ ERRO DE TIMEOUT: O seletor 'BLOCO_PRODUTO' não foi encontrado em 30 segundos.")
        print(f"   A Amazon pode ter mudado o HTML. Verifique o 'debug_pagina.png'.")
    
    except Exception as e:
        print(f"\n❌ Erro inesperado durante execução: {type(e).__name__}")
        print(f"   Mensagem: {e}")

    finally:
        driver.quit()
        print("🛑 Navegador fechado.")

# =====================================================================
# EXECUÇÃO
# =====================================================================

if __name__ == "__main__":
    main()
    