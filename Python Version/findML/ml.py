# -*- coding: utf-8 -*-
"""
Bot de Scraping Avançado - MERCADO LIVRE DEALS
Versão: 4.6-ML (Corrige "Lazy Loading" de imagens)
Descrição: Coleta dados de produtos da página de ofertas do Mercado Livre Brasil.
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pyperclip
import time
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Tuple, Optional


# --- Configuração de Perfil (Opcional - DESATIVADO) ---
#user_data_path = r"C:\Users\SEU_USUARIO\AppData\Local\Google\Chrome\User Data"
#profile_name = "Profile 3"
# -----------------------------

# 2. Configura as Opções do Chrome para carregar o perfil
chrome_options = Options()
#chrome_options.add_argument(f"user-data-dir={user_data_path}")
#chrome_options.add_argument(f"profile-directory={profile_name}")

# ============================================================================
# CONFIGURAÇÃO GLOBAL
# ============================================================================

CATEGORY_URLS = [
    "https://lista.mercadolivre.com.br/ofertas"
    # Você pode adicionar mais links de busca/categoria do ML aqui
    # Ex: "https://lista.mercadolivre.com.br/celulares-smartphones"
]
# Tempos de espera (em segundos)
WAIT_TIME = 30
SHORT_WAIT_TIME = 15
SCROLL_REPETICOES = 30
SCROLL_PAUSA = 1.5

# Limites
DESCRIPTION_LIMIT = 500

# ============================================================================
# SELETORES CSS/XPATH (MERCADO LIVRE - ATUALIZADO Nov/2025)
# ============================================================================

class Selectors:
    """Centraliza todos os seletores do site (Mercado Livre - Layout "Poly-Card")"""
    
    # Bloco principal do produto (o 'div' que contém tudo)
    PRODUCT_BLOCK = (By.CSS_SELECTOR, "div.andes-card.poly-card")
    
    # Link (o 'a' que tem o href)
    LINK = (By.CSS_SELECTOR, "a.poly-component__title")
    
    # Título (está dentro do link)
    TITLE = (By.CSS_SELECTOR, "a.poly-component__title")
    
    # Imagem
    IMAGE_CARD = (By.CSS_SELECTOR, "img.poly-component__picture")
    
    # --- Seletores de Preço (Página de Listagem) ---
    
    # Preço Antigo (riscado)
    OLD_PRICE = (By.CSS_SELECTOR, "s.andes-money-amount--previous .andes-money-amount__fraction")
    
    # Preço Novo (o principal)
    NEW_PRICE_WHOLE = (By.CSS_SELECTOR, "div.poly-price__current .andes-money-amount__fraction")
    NEW_PRICE_CENTS = (By.CSS_SELECTOR, "div.poly-price__current .andes-money-amount__cents")
    
    # Parcelamento
    INSTALLMENTS = (By.CSS_SELECTOR, "span.poly-price__installments")
    

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_text_or_default(element, by_tuple: Tuple, default: str = "Not Found") -> str:
    """Extrai texto de um elemento ou retorna um valor padrão"""
    try:
        return element.find_element(*by_tuple).text.strip().replace("\n", " ")
    except Exception:
        return default


def get_attr_or_default(element, by_tuple: Tuple, attr: str = "href", default: str = "Not Found") -> str:
    """Extrai um atributo de um elemento ou retorna um valor padrão"""
    try:
        return element.find_element(*by_tuple).get_attribute(attr)
    except Exception:
        return default


def save_error_screenshot(driver, base_name: str) -> str:
    """Salva um screenshot com timestamp para debug"""
    timestamp = int(time.time())
    file_name = f"{base_name}_{timestamp}.png"
    try:
        driver.save_screenshot(file_name)
        return file_name
    except Exception:
        return "Não foi possível salvar o screenshot"

# ============================================================================
# CONFIGURAÇÃO DO DRIVER
# ============================================================================

def initialize_driver() -> webdriver.Chrome:
    """
    Inicializa o ChromeDriver com configurações otimizadas e anti-detecção.
    
    ⚠️ IMPORTANTE: Feche TODAS as janelas do Chrome antes de rodar!
    
    Retorna:
          webdriver.Chrome: Instância do driver configurada
          
    Levanta:
          Exception: Se houver erro na inicialização
    """
    print("\n" + "="*80)
    print("🔧 INICIALIZANDO CHROMEDRIVER")
    print("="*80)
    
    global chrome_options # Usa as opções globais definidas com a config de perfil
    options = chrome_options # Começa com as opções já configuradas para o perfil

    # Configurações anti-detecção
    print("   → Aplicando configurações anti-detecção...")
    # options.add_argument("--headless=new") # MANTENHA COMENTADO PARA TESTAR
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Remove detecção de automação
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User agent realista
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    # Porta de debug (tenta várias portas)
    print("   → Configurando porta de debug...")
    port_found = False
    for port in [9223, 9224, 9225, 9226, 9227]:
        try:
            options.add_argument(f"--remote-debugging-port={port}")
            print(f"   ✅ Porta {port} configurada")
            port_found = True
            break
        except Exception:
            continue
    
    if not port_found:
        print("   ⚠️ Nenhuma porta de debug disponível")

    # Inicialização
    try:
        print("   → Instalando/Atualizando ChromeDriver...")
        service = ChromeService(ChromeDriverManager().install())
        
        print("   → Iniciando navegador...")
        driver = webdriver.Chrome(service=service, options=options)
        
        # Remove propriedades de automação via JavaScript
        print("   → Aplicando máscaras anti-detecção via JavaScript...")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("\n" + "✅"*40)
        print("✅ DRIVER INICIADO COM SUCESSO!")
        print("✅"*40 + "\n")
        
        return driver
        
    except Exception as e:
        print("\n" + "❌"*40)
        print(f"❌ ERRO AO INICIAR DRIVER")
        print("❌"*40)
        print(f"\n🔴 Erro: {str(e)}\n")
        print("💡 POSSÍVEIS SOLUÇÕES:")
        print("   1. Feche TODAS as janelas/processos do Chrome")
        print("   2. Rode o script como Administrador")
        print("   3. Desative temporariamente o antivírus")
        print("   4. Atualize o Google Chrome para a última versão")
        print("   5. Se estiver usando um perfil do Chrome, comente as linhas user-data-dir")
        print("   6. Reinicie o computador")
        print("   7. Verifique se há atualizações pendentes do Windows")
        print("\n" + "="*80 + "\n")
        raise


# ============================================================================
# FUNÇÕES DE NAVEGAÇÃO
# ============================================================================

def scroll_page(driver, repetitions: int = SCROLL_REPETICOES) -> None:
    """
    Realiza um scroll suave na página para carregar produtos dinamicamente.
    
    Args:
          driver: Instância do WebDriver
          repetitions: Número máximo de scrolls
    """
    print(f"\n   📜 Iniciando scroll da página (max: {repetitions} repetições)...")
    last_height = 0
    scrolls_without_change = 0
    
    for i in range(repetitions):
        # Scroll até o fim
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSA)
        
        # Checa nova altura
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if i % 5 == 0:  # Log a cada 5 scrolls
            print(f"     → Scroll {i+1}/{repetitions} | Altura: {new_height}px")
        
        # Checa se chegou ao fim
        if new_height == last_height:
            scrolls_without_change += 1
            if scrolls_without_change >= 3:
                print(f"   ✅ Fim da página alcançado (scroll {i+1})")
                break
        else:
            scrolls_without_change = 0
            
        last_height = new_height
    
    # Scroll de volta ao topo
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    
    # Tenta fechar pop-up de CEP (comum no ML)
    try:
        driver.find_element(By.CSS_SELECTOR, "button.andes-modal__close-button").click()
        print("   ℹ️ Pop-up de CEP fechado.")
    except Exception:
        pass # Ignora se não encontrar

# ============================================================================
# FUNÇÕES DE COLETA DE DADOS (MERCADO LIVRE)
# ============================================================================

def collect_mercadolivre_data(driver, wait: WebDriverWait, wait_short: WebDriverWait, url: str) -> List[Dict]:
    """
    Coleta TODOS os dados dos produtos da página de listagem do Mercado Livre.
    
    Args:
          driver: Instância do WebDriver
          wait: WebDriverWait longo
          wait_short: WebDriverWait curto
          url: URL da Categoria
          
    Retorna:
          Lista de dicionários com os dados completos dos produtos
    """
    products = []

    print("\n" + "━"*80)
    print(f"🔗 URL: {url}")
    print("━"*80)
    
    # Acessa a página
    print("\n   → Carregando página...")
    driver.get(url)

    try:
        # Espera os produtos carregarem
        print("     → Esperando produtos carregarem...")
        # Tenta fechar o pop-up de Cookies ANTES de esperar os produtos
        try:
            cookie_button = wait_short.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='action:understood-button']")))
            cookie_button.click()
            print("   ℹ️ Pop-up de Cookies fechado.")
        except Exception:
            print("   ℹ️ Pop-up de Cookies não encontrado/ignorado.")
            
        # Agora espera o bloco principal de produtos
        wait.until(EC.presence_of_element_located(Selectors.PRODUCT_BLOCK))
        time.sleep(2)
        
        # Rola a página para carregar mais produtos
        scroll_page(driver)

        # Encontra todos os blocos de produto
        blocks = driver.find_elements(*Selectors.PRODUCT_BLOCK)
        total_products = len(blocks)
        print(f"\n   ✅ {total_products} produtos encontrados!")
        print(f"\n   → Extraindo dados...")

        for idx, block in enumerate(blocks, 1):
            if idx % 20 == 0:
                print(f"           → Processando produto {idx}/{total_products}...")
                
            # --- Coleta de Dados Básicos ---
            title = get_text_or_default(block, Selectors.TITLE)
            link = get_attr_or_default(block, Selectors.LINK, "href")
            
            # --- LÓGICA DE IMAGEM ATUALIZADA (Lazy Load) ---
            image_url = get_attr_or_default(block, Selectors.IMAGE_CARD, "data-src")
            if image_url == "Not Found" or not image_url:
                # Fallback: Tenta pegar o 'src' se 'data-src' falhar
                image_url = get_attr_or_default(block, Selectors.IMAGE_CARD, "src")
            # --- FIM DA LÓGICA DE IMAGEM ---

            installments = get_text_or_default(block, Selectors.INSTALLMENTS, default="Não informado")
            
            # --- Lógica de Preço (Mercado Livre) ---
            old_price = get_text_or_default(block, Selectors.OLD_PRICE, default="Não informado")
            
            new_price_whole = get_text_or_default(block, Selectors.NEW_PRICE_WHOLE)
            new_price_cents = get_text_or_default(block, Selectors.NEW_PRICE_CENTS, default=None)
            
            new_price = "Not Found"
            if new_price_whole != "Not Found":
                if new_price_cents:
                    new_price = f"{new_price_whole},{new_price_cents}"
                else:
                    new_price = new_price_whole
            
            # --- Monta o dicionário (Nomes internos) ---
            product = {
                "ID": idx,
                "Title": title,
                "Original_Value": old_price,
                "Discount_Value": new_price,
                "Installments": installments,
                "Link": link,
                "Image_Card": image_url,
            }
            products.append(product)
        
        print(f"     ✅ Dados coletados: {len(products)} produtos")
            
    except Exception as e:
        print(f"\n   ❌ ERRO ao processar categoria")
        print(f"     🔴 Detalhes: {str(e)}")
        screenshot = save_error_screenshot(driver, f"error_category_generic")
        print(f"     📸 Screenshot: {screenshot}")

    return products


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Função principal do scraper.
    Orquestra todo o processo de coleta de dados.
    """
    print("\n" + "="*80)
    print("🚀 BOT DE SCRAPING - MERCADO LIVRE v4.6-ML")
    print("="*80)
    print("\n📋 CONFIGURAÇÃO:")
    print(f"   • Categorias para processar: {len(CATEGORY_URLS)}")
    print(f"   • Tempo máx. espera: {WAIT_TIME}s")
    print(f"   • Tempo curto espera: {SHORT_WAIT_TIME}s")
    print(f"   • Repetições de scroll: {SCROLL_REPETICOES}")
    print("\n" + "="*80 + "\n")
    
    # input("⚠️ IMPORTANTE: Feche TODAS as janelas do Chrome e pressione ENTER para continuar...")
    
    driver = None
    all_products = []
    
    try:
        # Inicializa driver
        driver = initialize_driver()
        wait = WebDriverWait(driver, WAIT_TIME)
        wait_short = WebDriverWait(driver, SHORT_WAIT_TIME)

        # Processa cada categoria
        for idx, url in enumerate(CATEGORY_URLS, 1):
            print(f"\n{'█'*80}")
            print(f"█ PROCESSANDO CATEGORIA {idx}/{len(CATEGORY_URLS)}")
            print(f"{'█'*80}")
            
            # Coleta dados (lógica de 1 passagem)
            complete_products = collect_mercadolivre_data(driver, wait, wait_short, url)
            
            if complete_products:
                all_products.extend(complete_products)
                
                print(f"\n{'✅'*40}")
                print(f"✅ Categoria {idx} CONCLUÍDA! {len(complete_products)} produtos processados.")
                print(f"{'✅'*40}\n")
            else:
                print(f"\n⚠️ Nenhum produto encontrado na categoria {idx}\n")

    except KeyboardInterrupt:
        print("\n\n⚠️ PROCESSO INTERROMPIDO PELO USUÁRIO (Ctrl+C)")
        
    except Exception as e:
        print(f"\n\n❌ ERRO FATAL: {e}")
        if driver:
            screenshot_name = f"fatal_error_{int(time.time())}.png"
            driver.save_screenshot(screenshot_name)
            print(f"📸 Screenshot do erro: {screenshot_name}")
            
    finally:
        if driver:
            print("\n🛑 Fechando navegador...")
            driver.quit()
            print("✅ Navegador fechado.\n")

    # Salva resultados
    print("\n" + "="*80)
    print("💾 SALVANDO RESULTADOS")
    print("="*80)
    
    if all_products:
        try:
            df = pd.DataFrame(all_products)
            
            # Reorganiza colunas (nomes internos)
            column_order = [
                "ID", "Title", 
                "Original_Value", "Discount_Value", "Installments",
                "Link", "Image_Card"
            ]
            
            # Filtra colunas para garantir que só as existentes sejam usadas
            final_columns = [col for col in column_order if col in df.columns]
            df = df[final_columns]
            
            # Renomeia as colunas para o Excel
            rename_map = {
                "Title": "Nome",
                "Original_Value": "Valor Produto",
                "Discount_Value": "Valor Promoção",
                "Installments": "Descrição",
                "Link": "Link Afiliado",
                "Image_Card": "Imagem"
            }
            df.rename(columns=rename_map, inplace=True)
            
            # Nome do arquivo com timestamp
            file_name = f"mercadolivre_products_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            print(f"\n   → Criando arquivo Excel...")
            df.to_excel(file_name, index=False, engine='openpyxl')
            
            print(f"\n{'🎉'*40}")
            print(f"✅ PROCESSO CONCLUÍDO COM SUCESSO!")
            print(f"{'🎉'*40}")
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"   • Total de produtos: {len(all_products)}")
            print(f"   • Arquivo gerado: {file_name}")
            print(f"\n{'='*80}\n")
            
        except Exception as e:
            print(f"\n❌ ERRO AO SALVAR ARQUIVO EXCEL: {e}")
            print(f"💡 Os dados foram coletados, mas não puderam ser salvos.\n")
            
    else:
        print("\n" + "⚠️"*40)
        print("⚠️ NENHUM PRODUTO FOI COLETADO!")
        print("⚠️"*40)
        print("\n💡 LISTA DE VERIFICAÇÃO:")
        print("   ✓ A conexão com a internet está ativa?")
        print("   ✓ As URLs de categoria estão corretas e acessíveis?")
        print("   ✓ O site do Mercado Livre está online?")
        print("   ✓ Os seletores CSS/XPATH ainda são válidos? (Este script é v4.6, o mais novo)")
        print("   ✓ Verifique os screenshots de erro salvos para análise visual (pode ser CAPTCHA)")
        print(f"\n{'='*80}\n")


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "⚠️"*40)
        print("⚠️ PROCESSO INTERROMPIDO PELO USUÁRIO (Ctrl+C)")
        print("⚠️"*40 + "\n")
    except Exception as e:
        print("\n\n" + "❌"*40)
        print(f"❌ ERRO FATAL NÃO TRATADO")
        print("❌"*40)
        print(f"\n🔴 Erro: {str(e)}")
        print("\n💡 Contate o suporte técnico com esta mensagem de erro.\n")