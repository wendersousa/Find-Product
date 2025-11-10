import pyautogui
import time

# --- (IMPORTANTE!) SUAS COORDENADAS ---

# 1. Posição no Excel (Canto/Célula inicial)
# X=1279, Y=109
pos_1_x, pos_1_y = (1279, 109)

# 6. Posição da Barra de URL do navegador
# X=351, Y=60
pos_2_x, pos_2_y = (351, 60)

# 10. Posição para estabilizar/focar na tela do ML
# X=1312, Y=190
pos_3_x, pos_3_y = (1312, 190) 

# 11. Posição do Botão "Compartilhar"
# X=1204, Y=110
pos_4_x, pos_4_y = (1204, 110) 

# 16. Posição do Código do Produto no ML
# X=1208, Y=461
pos_5_x, pos_5_y = (1208, 461)

# 11b. Posição do "Link" (após clicar em compartilhar)
# X=1212, Y=366
pos_6_x, pos_6_y = (1212, 366)
# ----------------------------------------------------


# --- Configuração do PyAutoGUI ---
pyautogui.PAUSE = 0.5 
pyautogui.FAILSAFE = True 


# --- Início do Script ---
while True:
    try:
        total_loops = int(input("Quantas vezes você quer que o loop se repita? "))
        if total_loops > 0:
            break
        else:
            print("Por favor, insira um número maior que zero.")
    except ValueError:
        print("Entrada inválida. Por favor, digite apenas um número.")

print(f"\nAutomação iniciando... O script rodará {total_loops} vez(es).")
print("Você tem 5 segundos para focar na janela correta (Alt+Tab).")
print("!!! LEMBRE-SE: Mova o mouse para o canto superior esquerdo para PARAR FORÇADAMENTE !!!")

time.sleep(9) # <--- Tempo de 9s mantido
print("Iniciando!")


# --- O Loop Principal ---
try:
    for i in range(total_loops):
        loop_atual = i + 1
        print(f"\n--- Iniciando Loop {loop_atual} de {total_loops} ---")

        # 1. clique no canto superior excel (X=1279, Y=109)
        print(f"Loop {loop_atual}: 1. Clicando em Posição 1 (Excel) ({pos_1_x}, {pos_1_y})")
        pyautogui.click(811, 547)
        print('click retornar bot')
        time.sleep(5) # Pequena pausa antes do próximo loop

        pyautogui.click(116,53)
        print('Atualizar tela')
        time.sleep(10) # Pequena pausa antes do próximo loop

        pyautogui.click(803,625)
        print('Pausar bot')
        time.sleep(60) # Pequena pausa antes do próximo loop
        print('Atualizar Pagina')
        time.sleep(60)
        print('1 minuto')
        time.sleep(60)
        print('2 minuto')
        time.sleep(60)
        print('3 minuto')
        time.sleep(60)
        print('4 minuto')
        time.sleep(60)
        print('5 minuto')
        time.sleep(60)
        print('6 minuto')
        time.sleep(60)
        print('7 minuto')
        time.sleep(60)
        print('8 minutos')
        time.sleep(60)
        print('9 minutos')


        print(f"--- Loop {loop_atual} Concluído ---")
        time.sleep(5) # Pequena pausa antes do próximo loop

    print("\n\KAutomação Concluída! Todos os loops foram executados.")

except KeyboardInterrupt:
    print("\n\nPROGRAMA INTERROMPIDO MANUALMENTE (Ctrl+C).")
except pyautogui.FailSafeException:
    print("\n\nPROGRAMA INTERROMPIDO (FAILSAFE)! O mouse foi movido para o canto.")