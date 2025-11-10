import pyautogui
import time

print("Você tem 5 segundos para posicionar o mouse...")
print("-" * 30)

# Contagem regressiva
for i in range(5, 0, -1):
    print(f"Capturando em {i}...")
    time.sleep(1)

# Captura a posição
try:
    x, y = pyautogui.position()
    print("\nCaptura concluída!")
    print(f"Anotar -> X={x}, Y={y}")

except Exception as e:
    print(f"\nOcorreu um erro: {e}")