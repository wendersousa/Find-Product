# =====================================================================
# IMPORTAÇÕES
# =====================================================================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from typing import Tuple

# =====================================================================
# CONFIGURAÇÃO DO DRIVER SELENIUM
# =====================================================================
def iniciar_driver() -> webdriver.Chrome:
    """Inicia o driver do Chrome com opções configuradas."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # opcional: remover se quiser ver o navegador
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1400, 1000)
    return driver

# =====================================================================
# SELETORES ATUALIZADOS (2025)
# =====================================================================
class Seletores:
    BLOCO_PRODUTO = (By.XPATH, "//div[@data-component-type='s-search-result']")
    LINK = (By.XPATH, ".//a[@class='a-link-normal s-no-outline']")
    IMAGEM = (By.XPATH, ".//img[contains(@class, 's-image')]")
    PRECO_NOVO = (By.XPATH, ".//span[@class='a-price-whole']")
    PRECO_ANTIGO = (By.XPATH, ".//span[contains(@class,'a-text-price')]")

# =====================================================================
# FUNÇÕES AUXILIARES
# =====================================================================
def get_text(element, by_tuple: Tuple, default: str = "Não encontrado") -> str:
    """Obtém o texto de um elemento, com fallback padrão."""
    try:
        return element.find_element(*by_tuple).text.strip()
    except Exception:
        return default

def get_attr(element, by_tuple: Tuple, attr: str, default: str = "Não encontrado") -> str:
    """Obtém um atributo de um elemento, com fallback padrão."""
    try:
        return element.find_element(*by_tuple).get_attribute(attr)
    except Exception:
        return default

# =====================================================================
# FUNÇÃO PRINCIPAL DE COLETA
# =====================================================================
def coletar_dados(url: str, limite: int = 50):
    """Acessa a página de ofertas da Amazon e coleta os primeiros N produtos."""
    driver = iniciar_driver()
    driver.get(url)

    print("🔄 Aguardando carregamento inicial dos produtos...")
    # Ativa o lazy loading inicial
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)

    wait = WebDriverWait(driver, 15)
    produtos = []

    try:
        wait.until(EC.presence_of_all_elements_located(Seletores.BLOCO_PRODUTO))

        while len(produtos) < limite:
            blocos = driver.find_elements(*Seletores.BLOCO_PRODUTO)

            for bloco in blocos:
                if len(produtos) >= limite:
                    break

                nome = get_attr(bloco, Seletores.IMAGEM, "alt")
                imagem = get_attr(bloco, Seletores.IMAGEM, "src")
                preco = get_text(bloco, Seletores.PRECO_NOVO)
                link = get_attr(bloco, Seletores.LINK, "href")

                if nome != "Não encontrado" and link != "Não encontrado":
                    produtos.append({
                        "Nome": nome,
                        "Imagem": imagem,
                        "Preço": preco,
                        "Link": link
                    })

            # Rola a página para carregar mais produtos (lazy load)
            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(2)

            # Atualiza blocos após o scroll
            novos_blocos = driver.find_elements(*Seletores.BLOCO_PRODUTO)
            if len(novos_blocos) == len(blocos):
                # Nenhum novo produto apareceu — encerra o loop
                break

        print(f"✅ Total de produtos coletados: {len(produtos)}")

    except Exception as e:
        print(f"⚠️ Erro durante a coleta: {e}")

    finally:
        driver.quit()

    return produtos[:limite]

# =====================================================================
# EXPORTAÇÃO DOS DADOS
# =====================================================================
def salvar_excel(dados, nome_arquivo: str = "ofertas_amazon.xlsx"):
    """Salva os dados em um arquivo Excel."""
    if not dados:
        print("⚠️ Nenhum dado coletado para exportar.")
        return

    df = pd.DataFrame(dados)
    df.to_excel(nome_arquivo, index=False)
    print(f"💾 Dados salvos com sucesso em: {nome_arquivo}")

# =====================================================================
# EXECUÇÃO PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    URL_AMAZON_DEALS = "https://www.amazon.com.br/gp/goldbox"
    ofertas = coletar_dados(URL_AMAZON_DEALS, limite=50)
    salvar_excel(ofertas)
