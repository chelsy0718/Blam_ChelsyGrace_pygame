import pygame
import math
import sys

pygame.init()
pygame.mixer.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
FPS = 60
MARBLE_RADIUS = 18
TARGET_RADIUS = 22
LEVELS = 100
FONT = pygame.font.SysFont("arial", 32)
SMALL_FONT = pygame.font.SysFont("arial", 20)
BG_COLOR = (30, 40, 60)
MARBLE_COLORS = [(255, 0, 100), (0, 200, 255), (255, 255, 0), (0, 255, 100), (255, 120, 0), (180, 0, 255)]
TARGET_COLORS = [(255, 255, 255), (255, 200, 0), (0, 255, 200), (255, 0, 200)]
HELP_ICON_COLOR = (255, 255, 255)
PAUSE_OVERLAY = (0, 0, 0, 180)

# --- Sounds ---
def load_sound(name):
    try:
        return pygame.mixer.Sound(name)
    except:
        return None

shoot_sound = load_sound("shoot.wav")
hit_sound = load_sound("hit.wav")
win_sound = load_sound("win.wav")
lose_sound = load_sound("lose.wav")

# --- Classes ---
class Marble:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = MARBLE_RADIUS
        self.color = color
        self.vx = 0
        self.vy = 0
        self.active = False

    def shoot(self, angle, power):
        self.vx = math.cos(angle) * power
        self.vy = math.sin(angle) * power
        self.active = True
        if shoot_sound: shoot_sound.play()

    def update(self):
        if self.active:
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.2  # gravity
            # Bounce off walls
            if self.x < self.radius or self.x > SCREEN_WIDTH - self.radius:
                self.vx *= -0.7
                self.x = max(self.radius, min(self.x, SCREEN_WIDTH - self.radius))
            if self.y > SCREEN_HEIGHT - self.radius:
                self.vy *= -0.7
                self.y = SCREEN_HEIGHT - self.radius
                if abs(self.vy) < 1: self.active = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), self.radius//2, 2)

class Target:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = TARGET_RADIUS
        self.color = color
        self.hit = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (0,0,0), (int(self.x), int(self.y)), self.radius//2, 2)
        if self.hit:
            pygame.draw.circle(screen, (255,0,0), (int(self.x), int(self.y)), self.radius//3)

class MarbleMasterGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Marble Master")
        self.clock = pygame.time.Clock()
        self.level = 1
        self.shots = 0
        self.marbles = []
        self.targets = []
        self.aiming = False
        self.aim_start = (0,0)
        self.aim_end = (0,0)
        self.paused = False
        self.show_help = False
        self.running = True
        self.score = 0
        self.load_level(self.level)

    def load_level(self, level):
        self.marbles = []
        self.targets = []
        self.shots = 0
        self.max_shots = 6 + level // 7  # More shots per level
        # Place marbles at bottom center, spaced evenly
        for i in range(self.max_shots):
            mx = SCREEN_WIDTH//2 + (i - self.max_shots//2)*50
            color = MARBLE_COLORS[i % len(MARBLE_COLORS)]
            self.marbles.append(Marble(mx, SCREEN_HEIGHT-40, color))
        # Place targets in a pattern (no random)
        num_targets = 2 + level // 5
        for i in range(num_targets):
            # Targets arranged in a wave pattern
            tx = 100 + i * ((SCREEN_WIDTH-200)//max(1,num_targets-1))
            ty = 120 + int(60 * math.sin(level + i))
            color = TARGET_COLORS[i % len(TARGET_COLORS)]
            self.targets.append(Target(tx, ty, color))

    def draw_background(self):
        self.screen.fill(BG_COLOR)
        # Aurora effect
        for i in range(0, SCREEN_WIDTH, 60):
            color = (30, 40 + (i//10)%80, 60 + (i//5)%100)
            pygame.draw.ellipse(self.screen, color, (i, 0, 200, 120), 0)
        # Floor
        pygame.draw.rect(self.screen, (60, 80, 120), (0, SCREEN_HEIGHT-60, SCREEN_WIDTH, 60))
        # Decorative marbles
        for i in range(8):
            pygame.draw.circle(self.screen, MARBLE_COLORS[i % len(MARBLE_COLORS)], (100+i*100, SCREEN_HEIGHT-30), 15)

    def draw_ui(self):
        level_text = FONT.render(f"Level: {self.level}/100", True, (255,255,255))
        shots_text = FONT.render(f"Shots: {self.max_shots - self.shots}", True, (255,255,0))
        score_text = FONT.render(f"Score: {self.score}", True, (0,255,255))
        self.screen.blit(level_text, (20, 20))
        self.screen.blit(shots_text, (20, 60))
        self.screen.blit(score_text, (20, 100))
        # Help icon
        pygame.draw.circle(self.screen, HELP_ICON_COLOR, (SCREEN_WIDTH-40, 40), 20)
        pygame.draw.line(self.screen, (0,0,0), (SCREEN_WIDTH-40, 30), (SCREEN_WIDTH-40, 50), 3)
        pygame.draw.circle(self.screen, (0,0,0), (SCREEN_WIDTH-40, 55), 3)
        # Pause icon
        pygame.draw.rect(self.screen, (255,255,255), (SCREEN_WIDTH-80, 30, 8, 20))
        pygame.draw.rect(self.screen, (255,255,255), (SCREEN_WIDTH-65, 30, 8, 20))

    def draw_help(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY)
        self.screen.blit(overlay, (0,0))
        help_text = FONT.render("How to Play Marble Master", True, (255,255,255))
        self.screen.blit(help_text, (SCREEN_WIDTH//2-220, 100))
        lines = [
            "Aim with mouse: Drag from marble to set direction and power.",
            "Release mouse to shoot the marble.",
            "Hit all targets to win the level.",
            "Each level has more targets and shots.",
            "Press [P] to pause/resume.",
            "Press [?] icon for help.",
            "Press [ESC] to quit."
        ]
        for i, line in enumerate(lines):
            txt = SMALL_FONT.render(line, True, (255,255,255))
            self.screen.blit(txt, (SCREEN_WIDTH//2-220, 160 + i*32))
        # Example marbles
        for i in range(3):
            pygame.draw.circle(self.screen, MARBLE_COLORS[i], (500 + i*40, 350), MARBLE_RADIUS)
        pygame.draw.circle(self.screen, HELP_ICON_COLOR, (SCREEN_WIDTH-40, 40), 20)
        pygame.draw.line(self.screen, (0,0,0), (SCREEN_WIDTH-40, 30), (SCREEN_WIDTH-40, 50), 3)
        pygame.draw.circle(self.screen, (0,0,0), (SCREEN_WIDTH-40, 55), 3)

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY)
        self.screen.blit(overlay, (0,0))
        pause_text = FONT.render("Paused", True, (255,255,255))
        self.screen.blit(pause_text, (SCREEN_WIDTH//2-70, SCREEN_HEIGHT//2-40))
        resume_text = SMALL_FONT.render("Press [P] to resume", True, (255,255,255))
        self.screen.blit(resume_text, (SCREEN_WIDTH//2-90, SCREEN_HEIGHT//2+10))

    def check_collision(self, marble, target):
        dist = math.hypot(marble.x - target.x, marble.y - target.y)
        return dist < marble.radius + target.radius

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r and self.paused:
                        self.paused = False
                        self.load_level(self.level)
                    elif event.key == pygame.K_F1 or event.key == pygame.K_SLASH:
                        self.show_help = not self.show_help
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.paused and not self.show_help:
                    mx, my = pygame.mouse.get_pos()
                    for marble in self.marbles:
                        if not marble.active and math.hypot(mx-marble.x, my-marble.y) < marble.radius:
                            self.aiming = True
                            self.aim_start = (marble.x, marble.y)
                            self.aim_end = (mx, my)
                            self.active_marble = marble
                            break
                    # Help icon click
                    if math.hypot(mx-(SCREEN_WIDTH-40), my-40) < 20:
                        self.show_help = True
                    # Pause icon click
                    if SCREEN_WIDTH-80 < mx < SCREEN_WIDTH-57 and 30 < my < 50:
                        self.paused = not self.paused
                elif event.type == pygame.MOUSEMOTION and self.aiming:
                    self.aim_end = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP and self.aiming:
                    self.aiming = False
                    angle = math.atan2(self.aim_start[1]-self.aim_end[1], self.aim_start[0]-self.aim_end[0])
                    power = min(20, math.hypot(self.aim_start[0]-self.aim_end[0], self.aim_start[1]-self.aim_end[1]) / 5)
                    self.active_marble.shoot(angle, power)
                    self.shots += 1

            self.draw_background()
            self.draw_ui()

            if self.show_help:
                self.draw_help()
            elif self.paused:
                self.draw_pause()
            else:
                # Draw marbles and targets
                for marble in self.marbles:
                    marble.update()
                    marble.draw(self.screen)
                for target in self.targets:
                    target.draw(self.screen)
                # Draw aiming line
                if self.aiming:
                    pygame.draw.line(self.screen, (255,255,255), self.aim_start, self.aim_end, 3)
                # Check collisions
                for marble in self.marbles:
                    if marble.active:
                        for target in self.targets:
                            if not target.hit and self.check_collision(marble, target):
                                target.hit = True
                                self.score += 100
                                if hit_sound: hit_sound.play()
                # Win/lose logic
                if all(t.hit for t in self.targets):
                    win_text = FONT.render("Level Complete!", True, (0,255,0))
                    self.screen.blit(win_text, (SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2-60))
                    pygame.display.flip()
                    pygame.time.wait(1200)
                    if win_sound: win_sound.play()
                    self.level += 1
                    if self.level > LEVELS:
                        self.level = 1
                        self.score = 0
                    self.load_level(self.level)
                elif self.shots >= self.max_shots and not all(t.hit for t in self.targets):
                    lose_text = FONT.render("Out of Shots!", True, (255,0,0))
                    self.screen.blit(lose_text, (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2-60))
                    pygame.display.flip()
                    pygame.time.wait(1200)
                    if lose_sound: lose_sound.play()
                    self.load_level(self.level)

            pygame.display.flip()

# --- Run Game ---
if __name__ == "__main__":
    MarbleMasterGame().run()