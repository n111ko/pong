import pygame, sys, random
from datetime import datetime

# класс ракетки
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, 10, 100)
        self.rect.center = (x, y)
        self.speed = 2
    
    # перемещение ракетки по нажатию клавиш
    def move(self, up_key, down_key):
        keys = pygame.key.get_pressed()
        if keys[up_key] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[down_key] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
    
    # отрисовка ракетки
    def draw(self, screen):
        pygame.draw.rect(screen, "white", self.rect)

# класс мяча
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.set_random_direction()

    def set_random_direction(self):
        # возможные направления: к игроку (вправо) или к врагу (влево)
        # и вверх или вниз по вертикали
        to_player = 1 # вправо
        to_opponent = -1 # влево
        horizontal = random.choice([to_player, to_opponent])
        vertical = random.choice([-1, 1])
        self.x_speed = horizontal
        self.y_speed = vertical

    # обновление позиции мяча
    def update(self):
        self.rect.x += self.x_speed * 2
        self.rect.y += self.y_speed * 2
        # отскок от стен
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.y_speed *= -1

    # отрисовка мяча
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.rect.center, 10)

# класс кнопки
class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = "white"
        self.hover_color = "gray"
        self.is_hovered = False
    
    # обработка событий для кнопки
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
    
    # отрисовка кнопки
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

# инициализация PyGame
pygame.init()
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")
FONT = pygame.font.SysFont("Consolas", int(WIDTH/20))
MENU_FONT = pygame.font.SysFont("Consolas", 60)
CLOCK = pygame.time.Clock()

# состояния игры
MENU = 0
MODE_SELECT = 1
PLAYING = 2
SCORES_SCREEN = 3 # добавлено состояние для экрана результатов

game_state = MENU

# режимы игры
PVP = 0 # player vs player
PVC = 1 # player vs computer
game_mode = PVP

# создание кнопок меню
button_width, button_height = 200, 80
play_button = Button(WIDTH//2 - button_width//2, HEIGHT//2 - 100, button_width, button_height, "PLAY", MENU_FONT)
scores_button = Button(WIDTH//2 - button_width//2, HEIGHT//2, button_width, button_height, "SCORES", MENU_FONT)
quit_button = Button(WIDTH//2 - button_width//2, HEIGHT//2 + 100, button_width, button_height, "QUIT", MENU_FONT)

# создание кнопок выбора режима
mode_button_width, mode_button_height = 300, 80
pvp_button = Button(WIDTH//2 - mode_button_width//2, HEIGHT//2 - 50, mode_button_width, mode_button_height, "2 PLAYERS", MENU_FONT)

pvc_button_width = 600
pvc_button = Button(WIDTH//2 - pvc_button_width//2, HEIGHT//2 + 50, pvc_button_width, mode_button_height, "PLAYER vs COMPUTER", MENU_FONT)

back_button = Button(WIDTH//2 - 100, HEIGHT//2 + 150, 200, 60, "BACK", pygame.font.SysFont("Consolas", 40))

# создание объектов игры
def reset_game():
    global player, opponent, ball, player_score, opponent_score
    player = Paddle(WIDTH-100, HEIGHT/2)
    opponent = Paddle(100, HEIGHT/2)
    ball = Ball()
    player_score, opponent_score = 0, 0

# сохранение результата в файл
def save_score(player_score, opponent_score):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode = "PvP" if game_mode == PVP else "PvC"
    with open("scores.txt", "a") as file:
        file.write(f"[{now}] Mode: {mode}, Player_1: {player_score}, Player_2: {opponent_score}\n")

reset_game()

# функция для отображения результатов из файла
def draw_scores_screen():
    SCREEN.fill("black")
    title_text = MENU_FONT.render("SCORES", True, "white")
    title_rect = title_text.get_rect(center=(WIDTH//2, 100))
    SCREEN.blit(title_text, title_rect)

    # кнопка назад
    back_button.draw(SCREEN)

    # чтение и отображение результатов
    try:
        with open("scores.txt", "r") as file:
            lines = file.readlines()
            
    except FileNotFoundError:
        lines = ["No scores recorded yet."]

    score_font = pygame.font.SysFont("Consolas", 28)
    y_offset = 160
    max_lines = 10 # показывается максимум 10 строк результатов
    for i, line in enumerate(lines[-max_lines:]):
        score_text = score_font.render(line.strip(), True, "gray")
        SCREEN.blit(score_text, (50, y_offset + i * 30))

# основной игровой цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_score(player_score, opponent_score)
            pygame.quit()
            sys.exit()
        
        if game_state == MENU:
            if play_button.handle_event(event):
                game_state = MODE_SELECT
            elif scores_button.handle_event(event):
                game_state = SCORES_SCREEN
            elif quit_button.handle_event(event):
                pygame.quit()
                sys.exit()
        
        elif game_state == MODE_SELECT:
            if pvp_button.handle_event(event):
                game_mode = PVP
                game_state = PLAYING
                reset_game()
            elif pvc_button.handle_event(event):
                game_mode = PVC
                game_state = PLAYING
                reset_game()
            elif back_button.handle_event(event):
                game_state = MENU
        
        elif game_state == SCORES_SCREEN:
            if back_button.handle_event(event):
                game_state = MENU
        
        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_score(player_score, opponent_score)
                    game_state = MENU
    
    # отрисовка в зависимости от состояния
    if game_state == MENU:
        SCREEN.fill("black")
        
        # заголовок
        title_text = MENU_FONT.render("PONG", True, "white")
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 180))
        SCREEN.blit(title_text, title_rect)
        
        # кнопки
        play_button.draw(SCREEN)
        scores_button.draw(SCREEN)
        quit_button.draw(SCREEN)
        
        # инструкция
        instruction_font = pygame.font.SysFont("Consolas", 24)
        instruction_text = instruction_font.render("Click PLAY to choose game mode", True, "gray")
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        SCREEN.blit(instruction_text, instruction_rect)
    
    elif game_state == MODE_SELECT:
        SCREEN.fill("black")
        
        # заголовок
        title_text = MENU_FONT.render("SELECT MODE", True, "white")
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 150))
        SCREEN.blit(title_text, title_rect)
        
        # кнопки режима
        pvp_button.draw(SCREEN)
        pvc_button.draw(SCREEN)
        back_button.draw(SCREEN)
        
        # инструкции
        instruction_font = pygame.font.SysFont("Consolas", 20)
        pvp_inst = instruction_font.render("2 Players: Player 1 (W/S), Player 2 (UP/DOWN)", True, "gray")
        pvc_inst = instruction_font.render("vs Computer: Use UP/DOWN arrows", True, "gray")
        pvp_rect = pvp_inst.get_rect(center=(WIDTH//2, HEIGHT - 120))
        pvc_rect = pvc_inst.get_rect(center=(WIDTH//2, HEIGHT - 90))
        SCREEN.blit(pvp_inst, pvp_rect)
        SCREEN.blit(pvc_inst, pvc_rect)

    elif game_state == SCORES_SCREEN:
        draw_scores_screen()

    elif game_state == PLAYING:
        # движение игроков
        if game_mode == PVP:
            # режим 2 игрока
            opponent.move(pygame.K_w, pygame.K_s) # игрок 1: W/S
            player.move(pygame.K_UP, pygame.K_DOWN) # игрок 2: UP/DOWN
        else:
            # режим против компьютера
            player.move(pygame.K_UP, pygame.K_DOWN)
            
            if opponent.rect.centery < ball.rect.centery:
                opponent.rect.y += 1
            if opponent.rect.centery > ball.rect.centery:
                opponent.rect.y -= 1
            
            # ограничение движения ии в пределах экрана
            if opponent.rect.top < 0:
                opponent.rect.top = 0
            if opponent.rect.bottom > HEIGHT:
                opponent.rect.bottom = HEIGHT
        
        # обновление мяча
        ball.update()
        
        # проверка столкновений и счёта
        if ball.rect.left <= 0:
            player_score += 1
            ball = Ball()  # создаётся новый мяч
        if ball.rect.right >= WIDTH:
            opponent_score += 1
            ball = Ball()
        
        # отскок от ракеток
        if player.rect.colliderect(ball.rect) or opponent.rect.colliderect(ball.rect):
            ball.x_speed *= -1
        
        # отрисовка
        SCREEN.fill("black")
        player.draw(SCREEN)
        opponent.draw(SCREEN)
        ball.draw(SCREEN)
        
        # отрисовка счёта
        player_text = FONT.render(str(player_score), True, "white")
        opponent_text = FONT.render(str(opponent_score), True, "white")
        SCREEN.blit(player_text, (WIDTH/2 + 50, 50))
        SCREEN.blit(opponent_text, (WIDTH/2 - 50, 50))
        
        # подсказка для выхода в меню и управления
        esc_font = pygame.font.SysFont("Consolas", 20)
        esc_text = esc_font.render("Press ESC to return to menu", True, "gray")
        SCREEN.blit(esc_text, (10, HEIGHT - 30))
        
        if game_mode == PVP:
            control_text = esc_font.render("Player 1: UP/DOWN | Player 2: W/S", True, "gray")
            SCREEN.blit(control_text, (10, 10))
        else:
            control_text = esc_font.render("Player: UP/DOWN arrows", True, "gray")
            SCREEN.blit(control_text, (10, 10))
    
    pygame.display.update()
    CLOCK.tick(300)
