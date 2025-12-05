import pygame
import sys
import random
import math

# --- 1. Inicialización ---
pygame.init()
pygame.font.init()

# --- 2. Configuración ---
TILE_SIZE = 32
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GRAY = (30, 30, 30)
GOLD = (255, 215, 0)
GREEN_WIN = (50, 205, 50) # Color verde para la victoria
BUTTON_COLOR = (50, 50, 150)
BUTTON_HOVER_COLOR = (80, 80, 200)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Dungeon Quest: Mata a 20 Enemigos")

# FUENTES
font_ui = pygame.font.SysFont(None, 30)
font_gameover = pygame.font.SysFont(None, 40)
font_pause = pygame.font.SysFont(None, 60)
font_victory = pygame.font.SysFont(None, 50) # Fuente para ganar

# --- CARGA DE IMÁGENES ---
try:
    sprite_sheet = pygame.image.load("img/Dungeon_Character_2.png").convert_alpha()
    player_clip = pygame.Rect(0, 0, 16, 16)
    player_img = pygame.transform.scale(sprite_sheet.subsurface(player_clip), (TILE_SIZE, TILE_SIZE))
    enemy_clip = pygame.Rect(16, 16, 16, 16)
    enemy_img = pygame.transform.scale(sprite_sheet.subsurface(enemy_clip), (TILE_SIZE, TILE_SIZE))
    bullet_clip = pygame.Rect(0, 16, 16, 16)
    bullet_img = pygame.transform.scale(sprite_sheet.subsurface(bullet_clip), (20, 20))
    
    menu_bg_original = pygame.image.load("img/menu_bg.png").convert()
    menu_bg = pygame.transform.scale(menu_bg_original, (SCREEN_WIDTH, SCREEN_HEIGHT))

except FileNotFoundError:
    print("¡ERROR! Faltan imágenes. Usando fallbacks.")
    player_img = pygame.Surface((TILE_SIZE, TILE_SIZE)); player_img.fill(WHITE)
    enemy_img = pygame.Surface((TILE_SIZE, TILE_SIZE)); enemy_img.fill((255,0,0))
    bullet_img = pygame.Surface((20, 20)); bullet_img.fill(GOLD)
    menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); menu_bg.fill(BLACK)

# --- 3. Generar Mapa ---
MAP_WIDTH_TILES = 50; MAP_HEIGHT_TILES = 50
WORLD_WIDTH = MAP_WIDTH_TILES * TILE_SIZE; WORLD_HEIGHT = MAP_HEIGHT_TILES * TILE_SIZE
GAME_MAP = []
for row in range(MAP_HEIGHT_TILES):
    new_row = []
    for col in range(MAP_WIDTH_TILES):
        if row == 0 or row == MAP_HEIGHT_TILES - 1 or col == 0 or col == MAP_WIDTH_TILES - 1: new_row.append(1)
        else:
            if random.random() < 0.1: new_row.append(1)
            else: new_row.append(0)
    GAME_MAP.append(new_row)

# --- 4. Variables Globales ---
player_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE); player_speed = 5
player_gold = 0
kill_count = 0 # <--- NUEVO: Contador de enemigos muertos
TARGET_KILLS = 20 # <--- META: 20 enemigos

enemy_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE); enemy_speed = 3
camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
bullets = []; BULLET_SPEED = 8
game_state = "menu"

# Botones
start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 70, 105, 110, 35)
exit_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 30, 120, 80, 40)
resume_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 200, 200, 50)
menu_return_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 280, 200, 50)

# --- 5. Funciones ---

def reset_game():
    global game_state, bullets, player_gold, kill_count
    player_rect.x = WORLD_WIDTH // 2
    player_rect.y = WORLD_HEIGHT // 2
    spawn_new_enemy()
    bullets = []
    player_gold = 0
    kill_count = 0 # Reiniciamos el contador a 0
    game_state = "playing"

def spawn_new_enemy():
    global enemy_rect
    while True:
        rx = random.randint(1, MAP_WIDTH_TILES - 2) * TILE_SIZE
        ry = random.randint(1, MAP_HEIGHT_TILES - 2) * TILE_SIZE
        dist_x = abs(rx - player_rect.x); dist_y = abs(ry - player_rect.y)
        if dist_x > 300 and dist_y > 300:
            enemy_rect.x = rx; enemy_rect.y = ry; break

def shoot_fireball():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    target_x = mouse_x + camera.x; target_y = mouse_y + camera.y
    start_x = player_rect.centerx; start_y = player_rect.centery
    angle = math.atan2(target_y - start_y, target_x - start_x)
    vel_x = math.cos(angle) * BULLET_SPEED; vel_y = math.sin(angle) * BULLET_SPEED
    bullets.append({"rect": pygame.Rect(start_x, start_y, 20, 20), "vel_x": vel_x, "vel_y": vel_y})

def update_bullets():
    global player_gold, kill_count, game_state
    for bullet in bullets[:]:
        bullet["rect"].x += int(bullet["vel_x"]); bullet["rect"].y += int(bullet["vel_y"])
        
        # Paredes
        if check_wall_collision(bullet["rect"]): bullets.remove(bullet); continue
        
        # Enemigos
        if bullet["rect"].colliderect(enemy_rect):
            bullets.remove(bullet)
            ganancia = random.randint(2, 5)
            player_gold += ganancia
            
            # --- NUEVA LÓGICA DE PROGRESO ---
            kill_count += 1 # Sumamos una muerte
            print(f"Enemigos eliminados: {kill_count}/{TARGET_KILLS}")
            
            # Verificar si ganamos
            if kill_count >= TARGET_KILLS:
                game_state = "victory" # ¡GANASTE!
            else:
                spawn_new_enemy() # Solo aparece otro si no has ganado todavía
            continue
            
        # Distancia
        if bullet["rect"].x < 0 or bullet["rect"].x > WORLD_WIDTH or bullet["rect"].y < 0 or bullet["rect"].y > WORLD_HEIGHT:
             if bullet in bullets: bullets.remove(bullet)

def check_wall_collision(rect):
    hitbox = rect.inflate(-10, -10)
    start_col = max(0, hitbox.left // TILE_SIZE); end_col = min(MAP_WIDTH_TILES - 1, hitbox.right // TILE_SIZE)
    start_row = max(0, hitbox.top // TILE_SIZE); end_row = min(MAP_HEIGHT_TILES - 1, hitbox.bottom // TILE_SIZE)
    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            if GAME_MAP[row][col] == 1: return True
    return False

def update_camera():
    target_x = player_rect.centerx - SCREEN_WIDTH // 2; target_y = player_rect.centery - SCREEN_HEIGHT // 2
    camera.x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
    camera.y = max(0, min(target_y, WORLD_HEIGHT - SCREEN_HEIGHT))

def handle_player_movement(keys):
    dx, dy = 0, 0
    if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -player_speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = player_speed
    if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -player_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = player_speed
    new_rect = player_rect.copy(); new_rect.x += dx
    if not check_wall_collision(new_rect): player_rect.x = new_rect.x
    new_rect = player_rect.copy(); new_rect.y += dy
    if not check_wall_collision(new_rect): player_rect.y = new_rect.y

def move_enemy():
    if player_rect.x > enemy_rect.x: enemy_rect.x += enemy_speed
    if player_rect.x < enemy_rect.x: enemy_rect.x -= enemy_speed
    if player_rect.y > enemy_rect.y: enemy_rect.y += enemy_speed
    if player_rect.y < enemy_rect.y: enemy_rect.y -= enemy_speed

# --- DIBUJADO ---
def draw_game():
    start_col = camera.x // TILE_SIZE; end_col = (camera.x + SCREEN_WIDTH) // TILE_SIZE + 1
    start_row = camera.y // TILE_SIZE; end_row = (camera.y + SCREEN_HEIGHT) // TILE_SIZE + 1
    for row in range(max(0, start_row), min(MAP_HEIGHT_TILES, end_row)):
        for col in range(max(0, start_col), min(MAP_WIDTH_TILES, end_col)):
            screen_x = (col * TILE_SIZE) - camera.x; screen_y = (row * TILE_SIZE) - camera.y
            if GAME_MAP[row][col] == 1: pygame.draw.rect(screen, BROWN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
            elif GAME_MAP[row][col] == 0: pygame.draw.rect(screen, GRAY, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
    for bullet in bullets: screen.blit(bullet_img, (bullet["rect"].x - camera.x, bullet["rect"].y - camera.y))
    screen.blit(player_img, (player_rect.x - camera.x, player_rect.y - camera.y))
    # Solo dibujamos enemigo si no hemos ganado (o si no es el último frame)
    if game_state == "playing": 
        screen.blit(enemy_img, (enemy_rect.x - camera.x, enemy_rect.y - camera.y))

def draw_ui():
    # Mostramos Oro y Enemigos restantes
    text_gold = font_ui.render(f"Oro: {player_gold}", True, GOLD)
    screen.blit(text_gold, (SCREEN_WIDTH - 120, 10))
    
    text_kills = font_ui.render(f"Enemigos: {kill_count}/{TARGET_KILLS}", True, WHITE)
    screen.blit(text_kills, (10, 10))

def draw_menu():
    screen.blit(menu_bg, (0, 0))
    pygame.draw.rect(screen, (255,0,0), start_button_rect, 2)
    pygame.draw.rect(screen, (255,0,0), exit_button_rect, 2)

def draw_pause_menu():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150); overlay.fill(BLACK)
    screen.blit(overlay, (0,0))
    pause_text = font_pause.render("JUEGO PAUSADO", True, WHITE)
    screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH//2, 100)))
    mouse_pos = pygame.mouse.get_pos()
    
    color = BUTTON_HOVER_COLOR if resume_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, resume_button_rect, border_radius=10)
    res_text = font_ui.render("Continuar", True, WHITE)
    screen.blit(res_text, res_text.get_rect(center=resume_button_rect.center))
    
    color = BUTTON_HOVER_COLOR if menu_return_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, menu_return_rect, border_radius=10)
    menu_text = font_ui.render("Menú Principal", True, WHITE)
    screen.blit(menu_text, menu_text.get_rect(center=menu_return_rect.center))

# --- Bucle Principal ---
running = True
clock = pygame.time.Clock()

while running:
    # --- EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # 1. MENU
        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button_rect.collidepoint(pygame.mouse.get_pos()): reset_game()
                elif exit_button_rect.collidepoint(pygame.mouse.get_pos()): running = False

        # 2. JUGANDO
        elif game_state == "playing":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_state = "paused"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                 shoot_fireball()
        
        # 3. PAUSA
        elif game_state == "paused":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p: game_state = "playing"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if resume_button_rect.collidepoint(mouse_pos): game_state = "playing"
                elif menu_return_rect.collidepoint(mouse_pos): game_state = "menu"

        # 4. GAME OVER o VICTORIA
        elif game_state == "game_over" or game_state == "victory":
             if event.type == pygame.KEYDOWN and event.key == pygame.K_r: game_state = "menu"

    # --- DIBUJO ---
    if game_state == "menu":
        draw_menu()
        
    elif game_state == "playing":
        keys = pygame.key.get_pressed()
        handle_player_movement(keys)
        move_enemy()
        update_bullets()
        update_camera()
        if player_rect.inflate(-15,-15).colliderect(enemy_rect.inflate(-15,-15)): game_state = "game_over"
        screen.fill(BLACK); draw_game(); draw_ui()
    
    elif game_state == "paused":
        screen.fill(BLACK); draw_game(); draw_ui()
        draw_pause_menu()

    elif game_state == "game_over":
        screen.fill(BLACK); draw_game(); draw_ui()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180); overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        text_go = font_gameover.render("¡TE ATRAPARON!", True, (255, 50, 50)) # Rojo
        screen.blit(text_go, text_go.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        text_restart = font_ui.render("Presiona 'R' para volver al Menú", True, GOLD)
        screen.blit(text_restart, text_restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))

    elif game_state == "victory": # <--- PANTALLA DE VICTORIA
        screen.fill(BLACK); draw_game(); draw_ui()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180); overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        # Mensaje de Victoria
        text_vic = font_victory.render("¡MISIÓN COMPLETADA!", True, GREEN_WIN)
        screen.blit(text_vic, text_vic.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        
        text_info = font_ui.render(f"Mataste 20 Fantasmas y ganaste {player_gold} de Oro", True, WHITE)
        screen.blit(text_info, text_info.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
        
        text_back = font_ui.render("Presiona 'R' para ir al Lobby", True, GOLD)
        screen.blit(text_back, text_back.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60)))


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()