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
        pyautogui.click(pos_1_x, pos_1_y)

        # 2. Espere 2 segundos
        print(f"Loop {loop_atual}: 2. Esperando 2 segundos...")
        time.sleep(2)

        # 4. Copie CTRL + C
        print(f"Loop {loop_atual}: 4. Pressionando CTRL + C")
        pyautogui.hotkey('ctrl', 'c')
        
        # 5. aperte alt + Tab (Indo para o Navegador)
        print(f"Loop {loop_atual}: 5. Pressionando Alt + Tab")
        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.5) 

        # 6. clique na URL (X=351, Y=60)
        print(f"Loop {loop_atual}: 6. Clicando em Posição 2 (URL) ({pos_2_x}, {pos_2_y})")
        pyautogui.click(pos_2_x, pos_2_y)

        # 7. Aperte CTRL + A (Selecionar tudo)
        print(f"Loop {loop_atual}: 7. Pressionando CTRL + A")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace') 

        # 8. Aperte CTRL + V (Colar) e Enter
        print(f"Loop {loop_atual}: 8. Pressionando CTRL + V e Enter")
        pyautogui.hotkey('ctrl', 'v')
        
        # O clique extra aqui foi removido
        pyautogui.press('enter') 

        # 9. Espere 5 segundos (para a página carregar)
        print(f"Loop {loop_atual}: 9. Esperando 5 segundos...")
        time.sleep(10)

        # 10. Clique para estabilizar na tela do ML (X=1312, Y=190)
        print(f"Loop {loop_atual}: 10. Clicando em Posição 3 (Foco ML) ({pos_3_x}, {pos_3_y})")
        pyautogui.click(pos_3_x, pos_3_y)

        # 11. Clique no Botão compartilhar (X=1204, Y=110)
        print(f"Loop {loop_atual}: 11. Clicando em Posição 4 (Compartilhar) ({pos_4_x}, {pos_4_y})")
        pyautogui.click(pos_4_x, pos_4_y)

        time.sleep(3)

        # 11b. Clique no Link de compartilhar (X=1212, Y=366)
        print(f"Loop {loop_atual}: 11b. Clicando em Posição 6 (Link) ({pos_6_x}, {pos_6_y})")
        pyautogui.click(pos_6_x, pos_6_y) 

        # 12. aperte alt + TAB (Voltando para o Excel)
        print(f"Loop {loop_atual}: 12. Pressionando Alt + Tab")
        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.5) 

        # Resetar Posição no Excel (X=1279, Y=109)
        print(f"Loop {loop_atual}: Resetando Posição 1 (Excel) ({pos_1_x}, {pos_1_y})")
        pyautogui.click(pos_1_x, pos_1_y)

        # 13. aperte o botão right (ir para a célula do lado)
        print(f"Loop {loop_atual}: 13. Pressionando Seta para Direita")
        pyautogui.press('right') # <--- CORRIGIDO de click() para press()

        # 14. Pressione CTRL + V (Colar link no Excel)
        print(f"Loop {loop_atual}: 14. Pressionando CTRL + V")
        pyautogui.hotkey('ctrl', 'v')

        # 15. aperte alt + TAB (Voltando para o Navegador)
        #print(f"Loop {loop_atual}: 15. Pressionando Alt + Tab")
        #pyautogui.hotkey('alt', 'tab')
        #time.sleep(0.5) 

        # 16. Copiar codigo do produto (X=1208, Y=461)
        #print(f"Loop {loop_atual}: 16. Clicando em Posição 5 (Cód. Produto) ({pos_5_x}, {pos_5_y})")
        #pyautogui.click(pos_5_x, pos_5_y)
        #pyautogui.hotkey('ctrl', 'c') # (Assumindo que você quer copiar após clicar)

        ## 17. aperte alt + TAB (Voltando para o Excel)
        #print(f"Loop {loop_atual}: 17. Pressionando Alt + Tab")
        #pyautogui.hotkey('alt', 'tab')
        #time.sleep(0.5) 

        # Resetar Posição no Excel (X=1279, Y=109)
        #print(f"Loop {loop_atual}: Resetando Posição 1 (Excel) ({pos_1_x}, {pos_1_y})")
        #pyautogui.click(pos_1_x, pos_1_y)

        # 18. aperte o botão right
        #print(f"Loop {loop_atual}: 18. Pressionando Seta para Direita 2x")
        #pyautogui.press('right') # <--- CORRIGIDO de click() para press()

        # 19. Pressione CTRL + V (Colar código do produto)
        #print(f"Loop {loop_atual}: 19. Pressionando CTRL + V")
        #pyautogui.hotkey('ctrl', 'v')
        
        # 20. Voltar para a célula inicial da próxima linha
        print(f"Loop {loop_atual}: 20. Indo para próxima linha (Baixo, Esquerda 2x)")
        pyautogui.press('down') # <--- CORRIGIDO de click() para press()
        pyautogui.press('left') # <--- CORRIGIDO de click() para press()

        print(f"--- Loop {loop_atual} Concluído ---")
        time.sleep(5) # Pequena pausa antes do próximo loop

    print("\n\KAutomação Concluída! Todos os loops foram executados.")

except KeyboardInterrupt:
    print("\n\nPROGRAMA INTERROMPIDO MANUALMENTE (Ctrl+C).")
except pyautogui.FailSafeException:
    print("\n\nPROGRAMA INTERROMPIDO (FAILSAFE)! O mouse foi movido para o canto.")