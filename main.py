import pygame
import random
import time
import json
from os import path
import math

pygame.init()

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BACKGROUND_COLOR = (13, 17, 23)
DIFFICULTY_LEVELS = {
    "简单": {"spawn_interval": 1.2, "ball_speed": 1.5, "score_multiplier": 1, "ball_count": 3},
    "普通": {"spawn_interval": 1.0, "ball_speed": 1.0, "score_multiplier": 2, "ball_count": 3},
    "困难": {"spawn_interval": 0.8, "ball_speed": 0.7, "score_multiplier": 3, "ball_count": 3}
}
FONT_PATH = "msyh.ttf"

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Hold your gun steady")
clock = pygame.time.Clock()

class Ball:
    def __init__(self, difficulty="普通", existing_balls=None):
        if existing_balls is None:
            existing_balls = []
            
        while True:
            self.radius = random.randint(20, 50)
            self.original_radius = self.radius
            self.x = random.randint(self.radius, WINDOW_WIDTH - self.radius)
            self.y = random.randint(self.radius, WINDOW_HEIGHT - self.radius)
            
            overlap = False
            for ball in existing_balls:
                distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
                if distance < (self.radius + ball.radius):
                    overlap = True
                    break
            
            if not overlap:
                break
        
        self.creation_time = time.time()
        self.lifetime = DIFFICULTY_LEVELS[difficulty]["ball_speed"]
        self.exploding = False
        self.explosion_particles = []
        self.points = random.randint(1, 3) * DIFFICULTY_LEVELS[difficulty]["score_multiplier"]
        if self.points <= 3:
            self.color = GREEN
        elif self.points <= 6:
            self.color = YELLOW
        else:
            self.color = RED

    def update(self):
        if not self.exploding:
            current_time = time.time()
            elapsed_time = current_time - self.creation_time
            if elapsed_time < self.lifetime:
                self.radius = self.original_radius * (1 - elapsed_time / self.lifetime)
            else:
                self.radius = 0
                return True
        else:
            for particle in self.explosion_particles:
                particle[0] += particle[2]
                particle[1] += particle[3]
                particle[4] -= 0.1
            self.explosion_particles = [p for p in self.explosion_particles if p[4] > 0]
            if not self.explosion_particles:
                return True
        return False

    def draw(self, screen):
        if not self.exploding:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))
            font = pygame.font.Font(FONT_PATH, 20)
            score_text = font.render(str(self.points), True, WHITE)
            screen.blit(score_text, (self.x - score_text.get_width()//2, 
                                   self.y - score_text.get_height()//2))
        else:
            for particle in self.explosion_particles:
                color = (*self.color, int(particle[4] * 255))
                pygame.draw.circle(screen, color, (int(particle[0]), int(particle[1])), 2)

    def explode(self):
        self.exploding = True
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.explosion_particles.append([
                self.x,
                self.y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                1.0
            ])

    def check_click(self, pos):
        if not self.exploding:
            distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
            return distance <= self.radius
        return False

class Game:
    def __init__(self):
        self.reset()
        self.load_highscore()
        self.font_big = pygame.font.Font(FONT_PATH, 32)
        self.font_normal = pygame.font.Font(FONT_PATH, 20)
        self.font_small = pygame.font.Font(FONT_PATH, 16)
        self.menu_state = "menu"
        self.countdown = 3
        self.countdown_timer = 0
        self.difficulty = "普通"
        self.paused = False
        self.combo = 0
        self.max_combo = 0
        self.total_shots = 0
        self.hits = 0
        self.sound_enabled = True
        self.load_sounds()
        
    def reset(self):
        self.score = 10
        self.balls = []
        self.start_time = 0
        self.game_duration = 180
        self.spawn_timer = 0
        self.spawn_interval = 1.0
        self.combo = 0
        self.max_combo = 0
        self.total_shots = 0
        self.hits = 0
        
    def load_highscore(self):
        self.highscore = 0
        if path.exists("highscore.json"):
            try:
                with open("highscore.json", "r", encoding='utf-8') as f:
                    self.highscore = json.load(f)["highscore"]
            except:
                pass

    def save_score(self):
        if self.score > self.highscore:
            self.highscore = self.score
            with open("highscore.json", "w", encoding='utf-8') as f:
                json.dump({"highscore": self.highscore}, f)
        
        with open("game_records.txt", "a", encoding='utf-8') as f:
            f.write(f"游戏时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"难度: {self.difficulty}\n")
            f.write(f"最终得分: {self.score}\n")
            f.write(f"最大连击: {self.max_combo}\n")
            f.write(f"命中率: {(self.hits/self.total_shots*100):.1f}%\n")
            f.write("-"*50 + "\n")

    def load_sounds(self):
        self.hit_sound = pygame.mixer.Sound("hit.wav")
        self.miss_sound = pygame.mixer.Sound("miss.wav")
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.menu_state == "game":
                        self.paused = not self.paused
                    elif event.key == pygame.K_q and self.paused:
                        self.reset()
                        self.menu_state = "menu"
                        self.paused = False

            screen.fill(BACKGROUND_COLOR)
            
            if self.menu_state == "menu":
                self.draw_menu()
            elif self.menu_state == "countdown":
                self.run_countdown()
            elif self.menu_state == "game":
                self.run_game()
            elif self.menu_state == "gameover":
                self.draw_gameover()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()

    def handle_click(self, pos):
        if self.menu_state == "gameover":
            self.reset()
            self.menu_state = "menu"
            return
            
        if self.menu_state == "menu":
            if (WINDOW_WIDTH//2 - 100 <= pos[0] <= WINDOW_WIDTH//2 + 100 and 
                250 <= pos[1] <= 295):
                self.menu_state = "countdown"
                self.countdown = 3
                self.countdown_timer = time.time()
            elif (WINDOW_WIDTH//2 - 100 <= pos[0] <= WINDOW_WIDTH//2 + 100 and 
                  320 <= pos[1] <= 365):
                pygame.quit()
                exit()
            elif 400 <= pos[1] <= 435:
                diff_width = 80
                total_width = diff_width * 3 + 20 * 2
                start_x = WINDOW_WIDTH//2 - total_width//2
                for i, diff in enumerate(DIFFICULTY_LEVELS.keys()):
                    button_x = start_x + i * (diff_width + 20)
                    if button_x <= pos[0] <= button_x + diff_width:
                        self.difficulty = diff
                        break
            elif 455 <= pos[1] <= 485 and WINDOW_WIDTH//2 - 50 <= pos[0] <= WINDOW_WIDTH//2 + 50:
                self.sound_enabled = not self.sound_enabled
        elif self.menu_state == "game" and not self.paused:
            self.total_shots += 1
            hit = False
            for ball in self.balls:
                if ball.check_click(pos):
                    ball.explode()
                    self.score += ball.points
                    self.hits += 1
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    if self.sound_enabled:
                        self.hit_sound.play()
                    hit = True
                    break
            if not hit:
                self.score = max(0, self.score - 1)
                self.combo = 0
                if self.sound_enabled:
                    self.miss_sound.play()
                if self.score <= 0:
                    self.menu_state = "gameover"
                    self.save_score()

    def draw_menu(self):
        title = self.font_big.render("Hold your gun steady", True, WHITE)
        subtitle = self.font_small.render("FPS反应力训练游戏", True, (180, 180, 180))
        author = self.font_small.render("@https://github.com/CNMengHan", True, (128, 128, 128))
        button_color = (50, 150, 50)
        hover_color = (70, 170, 70)
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 120))
        screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 170))
        start_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, 250, 200, 45)
        start_color = hover_color if start_rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, start_color, start_rect, border_radius=8)
        quit_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, 320, 200, 45)
        quit_color = (170, 50, 50) if quit_rect.collidepoint(mouse_pos) else (150, 50, 50)
        pygame.draw.rect(screen, quit_color, quit_rect, border_radius=8)
        start_text = self.font_normal.render("开始游戏", True, WHITE)
        quit_text = self.font_normal.render("退出游戏", True, WHITE)
        
        screen.blit(start_text, (start_rect.centerx - start_text.get_width()//2, 
                                start_rect.centery - start_text.get_height()//2))
        screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width()//2, 
                               quit_rect.centery - quit_text.get_height()//2))

        y_pos = 400
        diff_width = 80
        total_width = diff_width * 3 + 20 * 2
        start_x = WINDOW_WIDTH//2 - total_width//2
        
        for i, diff in enumerate(DIFFICULTY_LEVELS.keys()):
            button_x = start_x + i * (diff_width + 20)
            button_rect = pygame.Rect(button_x, y_pos, diff_width, 35)
            is_hover = button_rect.collidepoint(mouse_pos)
            is_selected = self.difficulty == diff
            if is_selected:
                color = GREEN if not is_hover else (0, 200, 0)
            else:
                color = (100, 100, 100) if not is_hover else (120, 120, 120)
                
            pygame.draw.rect(screen, color, button_rect, border_radius=6)
            text = self.font_small.render(diff, True, WHITE)
            screen.blit(text, (button_rect.centerx - text.get_width()//2,
                              button_rect.centery - text.get_height()//2))

        sound_text = self.font_normal.render(f"声音: {'开' if self.sound_enabled else '关'}", True, 
                                           GREEN if self.sound_enabled else RED)
        sound_rect = sound_text.get_rect(center=(WINDOW_WIDTH//2, 470))
        screen.blit(sound_text, sound_rect)
        highscore_text = self.font_normal.render(f"最高分: {self.highscore}", True, WHITE)
        screen.blit(highscore_text, (WINDOW_WIDTH//2 - highscore_text.get_width()//2, 520))
        screen.blit(author, (WINDOW_WIDTH//2 - author.get_width()//2, WINDOW_HEIGHT - 30))

    def run_countdown(self):
        current_time = time.time()
        if current_time - self.countdown_timer >= 1:
            self.countdown -= 1
            self.countdown_timer = current_time
            
        if self.countdown <= 0:
            self.menu_state = "game"
            self.start_time = time.time()
            return
            
        countdown_text = self.font_normal.render(str(self.countdown), True, WHITE)
        screen.blit(countdown_text, (WINDOW_WIDTH//2 - countdown_text.get_width()//2, 
                                   WINDOW_HEIGHT//2 - countdown_text.get_height()//2))

    def run_game(self):
        if self.paused:
            self.draw_pause_menu()
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= self.game_duration:
            self.menu_state = "gameover"
            self.save_score()
            return
            
        if current_time - self.spawn_timer >= self.spawn_interval:
            required_balls = DIFFICULTY_LEVELS[self.difficulty]["ball_count"]
            current_balls = len([b for b in self.balls if not b.exploding])
            
            for _ in range(required_balls - current_balls):
                new_ball = Ball(self.difficulty, self.balls)
                self.balls.append(new_ball)
            
            self.spawn_timer = current_time
        
        for ball in self.balls[:]:
            if ball.update():
                if not ball.exploding:
                    self.score -= 1
                    if self.score <= 0:
                        self.menu_state = "gameover"
                        self.save_score()
                        return
                self.balls.remove(ball)
            ball.draw(screen)
        
        score_text = self.font_normal.render(f"得分: {self.score}", True, WHITE)
        time_left = max(0, self.game_duration - elapsed_time)
        time_text = self.font_normal.render(f"剩余时间: {int(time_left)}秒", True, WHITE)
        highscore_text = self.font_normal.render(f"最高分: {self.highscore}", True, WHITE)
        screen.blit(score_text, (20, 20))
        screen.blit(time_text, (20, 60))
        screen.blit(highscore_text, (20, 100))
        accuracy = (self.hits / self.total_shots * 100) if self.total_shots > 0 else 0
        combo_text = self.font_normal.render(f"连击: {self.combo}", True, WHITE)
        accuracy_text = self.font_normal.render(f"命中率: {accuracy:.1f}%", True, WHITE)
        difficulty_text = self.font_normal.render(f"难度: {self.difficulty}", True, WHITE)
        screen.blit(combo_text, (20, 140))
        screen.blit(accuracy_text, (20, 180))
        screen.blit(difficulty_text, (20, 220))

    def draw_gameover(self):
        gameover_text = self.font_big.render("游戏结束!", True, WHITE)
        score_text = self.font_normal.render(f"最终得分: {self.score}", True, WHITE)
        highscore_text = self.font_normal.render(f"最高分: {self.highscore}", True, WHITE)
        restart_text = self.font_normal.render("点击任意处返回主菜单", True, WHITE)
        
        screen.blit(gameover_text, (WINDOW_WIDTH//2 - gameover_text.get_width()//2, 200))
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 250))
        screen.blit(highscore_text, (WINDOW_WIDTH//2 - highscore_text.get_width()//2, 300))
        screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, 400))
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.reset()
                self.menu_state = "menu"

    def draw_pause_menu(self):
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        s.set_alpha(128)
        s.fill(BACKGROUND_COLOR)
        screen.blit(s, (0,0))
        
        pause_text = self.font_big.render("游戏暂停", True, WHITE)
        continue_text = self.font_normal.render("按 ESC 继续", True, WHITE)
        quit_text = self.font_normal.render("按 Q 退出到主菜单", True, WHITE)
        
        screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2 - 60))
        screen.blit(continue_text, (WINDOW_WIDTH//2 - continue_text.get_width()//2, WINDOW_HEIGHT//2))
        screen.blit(quit_text, (WINDOW_WIDTH//2 - quit_text.get_width()//2, WINDOW_HEIGHT//2 + 60))

if __name__ == "__main__":
    game = Game()
    game.run()
