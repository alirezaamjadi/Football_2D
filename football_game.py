import pygame
import sys
import json
import os
import time
import math

pygame.init()

# تنظیمات کلی
FPS = 60
WHITE = (240, 240, 240)
GREEN = (0, 190, 0)
BLACK = (18, 18, 18)
RED = (230, 50, 50)
BLUE = (50, 120, 230)
YELLOW = (255, 215, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (70, 70, 70)
score1_scale = 1.0
score2_scale = 1.0
score1_target_scale = 1.0
score2_target_scale = 1.0
score_scale_speed = 0.1

score1_changed = False
score2_changed = False

ball_radius = 15
player_width, player_height = 14, 75
player_speed = 7
ball_speed_init = 7
BALL_MAX_SPEED = 12

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Football Game 2D")

try:
    font_small = pygame.font.SysFont("Segoe UI", 24)
    font_medium = pygame.font.SysFont("Segoe UI", 36)
    font_large = pygame.font.SysFont("Segoe UI", 60)
    font_bold_large = pygame.font.SysFont("Segoe UI", 72, bold=True)
except:
    font_small = pygame.font.SysFont(None, 24)
    font_medium = pygame.font.SysFont(None, 36)
    font_large = pygame.font.SysFont(None, 60)
    font_bold_large = pygame.font.SysFont(None, 72, bold=True)

clock = pygame.time.Clock()
RECORD_FILE = "football_records.json"

MODE_MENU = 0
MODE_INPUT_NAMES = 1
MODE_PLAY = 2
MODE_ABOUT = 3
MODE_RECORDS = 4

mode = MODE_MENU

player1_name = ""
player2_name = ""
input_active = None  # فقط 1 یا 2

ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_speed = [ball_speed_init, ball_speed_init]

player1_pos = [50, HEIGHT // 2 - player_height // 2]
player2_pos = [WIDTH - 50 - player_width, HEIGHT // 2 - player_height // 2]

score1 = 0
score2 = 0

menu_options = ["Start Game", "Records", "About Game", "Exit"]
menu_selected = 0

game_start_time = 0
game_duration = 150  # ثانیه

def load_records():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    else:
        return {}

def save_records(records):
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

def draw_text(text, font, color, surface, x, y, center=False):
    text_obj = font.render(text, True, color)
    if center:
        rect = text_obj.get_rect(center=(x, y))
        surface.blit(text_obj, rect)
    else:
        surface.blit(text_obj, (x, y))

def draw_rounded_rect(surface, rect, color, radius=12):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def reset_ball():
    global ball_pos, ball_speed
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    ball_speed = [ball_speed_init * (-1 if score1 <= score2 else 1), ball_speed_init]

def update_player_stats(records, player_name, goals, won):
    if player_name not in records:
        records[player_name] = {"goals": 0, "wins": 0, "games": 0}
    records[player_name]["goals"] += goals
    if won:
        records[player_name]["wins"] += 1
    records[player_name]["games"] += 1

def draw_menu():
    screen.fill(BLACK)
    draw_text("Football Game 2D", font_bold_large, YELLOW, screen, WIDTH//2, HEIGHT//6, True)
    draw_text("Builder Game : alirezaamjadi", font_small, GRAY, screen, WIDTH//2, HEIGHT//6 + 70, True)
    for i, option in enumerate(menu_options):
        color = GREEN if i == menu_selected else LIGHT_GRAY
        rect_w, rect_h = 300, 65
        rect_x = WIDTH // 2 - rect_w // 2
        rect_y = HEIGHT // 3 + i * 90
        if i == menu_selected:
            draw_rounded_rect(screen, (rect_x-5, rect_y-5, rect_w+10, rect_h+10), GREEN, 15)
            draw_rounded_rect(screen, (rect_x, rect_y, rect_w, rect_h), DARK_GRAY, 15)
        else:
            draw_rounded_rect(screen, (rect_x, rect_y, rect_w, rect_h), DARK_GRAY, 15)
        draw_text(option, font_medium, color, screen, WIDTH//2, rect_y + rect_h//2, True)

def draw_input_names():
    screen.fill(BLACK)
    draw_text("Enter Player Names", font_bold_large, YELLOW, screen, WIDTH//2, HEIGHT//8, True)
    box_w, box_h = 420, 70

    rect1 = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//4 + 20, box_w, box_h)
    pygame.draw.rect(screen, DARK_GRAY if input_active == 1 else LIGHT_GRAY, rect1, border_radius=16)
    draw_text("Player 1:", font_medium, GREEN, screen, rect1.x + 25, rect1.y + 16)
    draw_text(player1_name + ("|" if input_active == 1 else ""), font_medium, WHITE, screen, rect1.x + 170, rect1.y + 16)

    rect2 = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//4 + 130, box_w, box_h)
    pygame.draw.rect(screen, DARK_GRAY if input_active == 2 else LIGHT_GRAY, rect2, border_radius=16)
    draw_text("Player 2:", font_medium, BLUE, screen, rect2.x + 25, rect2.y + 16)
    draw_text(player2_name + ("|" if input_active == 2 else ""), font_medium, WHITE, screen, rect2.x + 170, rect2.y + 16)

    # حذف دکمه back to menu

def draw_records(records):
    screen.fill(BLACK)
    draw_text("Top 10 Players by Goals", font_bold_large, YELLOW, screen, WIDTH//2, HEIGHT//12, True)

    box_w, box_h = 850, 530
    rect = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//6, box_w, box_h)
    pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=22)

    players_sorted_goals = sorted(records.items(), key=lambda x: x[1].get("goals",0), reverse=True)[:10]
    players_sorted_wins = sorted(records.items(), key=lambda x: x[1].get("wins",0), reverse=True)[:10]

    left_box = pygame.Rect(rect.x + 40, rect.y + 40, box_w//2 - 60, box_h - 80)
    right_box = pygame.Rect(rect.x + box_w//2 + 20, rect.y + 40, box_w//2 - 60, box_h - 80)

    pygame.draw.rect(screen, LIGHT_GRAY, left_box, border_radius=18)
    pygame.draw.rect(screen, LIGHT_GRAY, right_box, border_radius=18)

    draw_text("Top 10 by Goals", font_medium, GREEN, screen, left_box.centerx, left_box.y + 25, True)
    draw_text("Top 10 by Wins", font_medium, BLUE, screen, right_box.centerx, right_box.y + 25, True)

    for i, (name, stats) in enumerate(players_sorted_goals):
        y_pos = left_box.y + 65 + i*42
        draw_text(f"{i+1}. {name}", font_small, BLACK, screen, left_box.x + 25, y_pos)
        draw_text(str(stats.get("goals", 0)), font_small, BLACK, screen, left_box.right - 40, y_pos)

    for i, (name, stats) in enumerate(players_sorted_wins):
        y_pos = right_box.y + 65 + i*42
        draw_text(f"{i+1}. {name}", font_small, BLACK, screen, right_box.x + 25, y_pos)
        draw_text(str(stats.get("wins", 0)), font_small, BLACK, screen, right_box.right - 40, y_pos)

    # حذف دکمه back to menu

def draw_about():
    
    screen.fill(BLACK)
    lines = [
    "Builder Game : alirezaamjadi",
    "Year : 2025/1404",
    "Version : 1.0",
    "Language : Pygame - Python",
    "",
    "How to Play:",
    "Use arrow keys or mouse to control your player.",
    "Score goals to win the game.",
    "First to reach the target score wins.",
    "Have fun and good luck!"
]

    for i, line in enumerate(lines):
        draw_text(line, font_medium, LIGHT_GRAY, screen, WIDTH//2, HEIGHT//6 + i*50, True)

    # حذف دکمه back to menu

def goal_animation(scored_by_name):
    screen.fill(BLACK)
    draw_text(f"GOAL!!! {scored_by_name} scored!", font_bold_large, YELLOW, screen, WIDTH//2, HEIGHT//2, True)
    pygame.display.flip()
    pygame.time.delay(2000)

def handle_goal(scored_by):
    global score1, score2



def handle_goal(scored_by):
    global score1, score2, goal_time, goal_scored_by, ball_speed, score1_target_scale, score2_target_scale

    if scored_by == 1:
        score1 += 1
        score1_target_scale = 1.3  # انیمیشن بزرگ شدن امتیاز
    elif scored_by == 2:
        score2 += 1
        score2_target_scale = 1.3

    goal_time = time.time()
    goal_scored_by = scored_by

    reset_ball()
    if scored_by == 1:
        goal_animation(player1_name)
    else:
        goal_animation(player2_name)


def handle_game_end():
    global mode, score1, score2, player1_name, player2_name

    records = load_records()

    if score1 > score2:
        update_player_stats(records, player1_name, score1, True)
        update_player_stats(records, player2_name, score2, False)
        winner = player1_name
    elif score2 > score1:
        update_player_stats(records, player2_name, score2, True)
        update_player_stats(records, player1_name, score1, False)
        winner = player2_name
    else:
        update_player_stats(records, player1_name, score1, True)
        update_player_stats(records, player2_name, score2, True)
        winner = None

    save_records(records)

    screen.fill(BLACK)
    if winner:
        draw_text(f"Game Over! Winner: {winner}", font_bold_large, YELLOW, screen, WIDTH//2, HEIGHT//3, True)
    else:
        draw_text("Game Over! It's a Draw!", font_bold_large, YELLOW, screen, WIDTH//2, HEIGHT//3, True)
    draw_text(f"Score: {player1_name} {score1} - {score2} {player2_name}", font_medium, WHITE, screen, WIDTH//2, HEIGHT//3 + 100, True)
    draw_text("Press any key to return to menu", font_small, GRAY, screen, WIDTH//2, HEIGHT - 120, True)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

    reset_game()

def reset_game():
    global mode, player1_name, player2_name, score1, score2, ball_speed, ball_pos, player1_pos, player2_pos, input_active, menu_selected
    mode = MODE_MENU
    player1_name = ""
    player2_name = ""
    score1 = 0
    score2 = 0
    ball_speed[:] = [ball_speed_init, ball_speed_init]
    ball_pos[:] = [WIDTH // 2, HEIGHT // 2]
    player1_pos[:] = [50, HEIGHT // 2 - player_height // 2]
    player2_pos[:] = [WIDTH - 50 - player_width, HEIGHT // 2 - player_height // 2]
    input_active = None
    menu_selected = 0

def handle_ball_movement():
    global ball_pos, ball_speed

    ball_pos[0] += ball_speed[0]
    ball_pos[1] += ball_speed[1]

    if ball_pos[1] - ball_radius <= 0 or ball_pos[1] + ball_radius >= HEIGHT:
        ball_speed[1] = -ball_speed[1]

    p1_rect = pygame.Rect(player1_pos[0], player1_pos[1], player_width, player_height)
    ball_rect = pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius*2, ball_radius*2)
    if ball_rect.colliderect(p1_rect):
        ball_speed[0] = abs(ball_speed[0]) + 0.5
        ball_speed[0] = min(ball_speed[0], BALL_MAX_SPEED)
        ball_speed[1] = (ball_pos[1] - (player1_pos[1] + player_height/2)) / (player_height/2) * ball_speed_init

    p2_rect = pygame.Rect(player2_pos[0], player2_pos[1], player_width, player_height)
    if ball_rect.colliderect(p2_rect):
        ball_speed[0] = -abs(ball_speed[0]) - 0.5
        ball_speed[0] = max(ball_speed[0], -BALL_MAX_SPEED)
        ball_speed[1] = (ball_pos[1] - (player2_pos[1] + player_height/2)) / (player_height/2) * ball_speed_init

    if ball_pos[0] - ball_radius <= 0:
        handle_goal(2)
    elif ball_pos[0] + ball_radius >= WIDTH:
        handle_goal(1)

# اضافه کن این متغیرها رو بالای کد (یا جایی که تعریفشون منطقیه)
score1_scale = 1.0
score2_scale = 1.0
score1_target_scale = 1.0
score2_target_scale = 1.0
scale_speed = 0.1  # سرعت انیمیشن بزرگ شدن و برگشت

def draw_scoreboard():
    global score1_scale, score2_scale, score1_target_scale, score2_target_scale
    
    # بک‌گراند شفاف کمرنگ بالای صفحه
    overlay = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    # تایمر بزرگ و ساده وسط بالا
    elapsed = time.time() - game_start_time
    remaining = max(0, int(game_duration - elapsed))
    timer_font = pygame.font.SysFont("Segoe UI", 60, bold=True)
    timer_text = timer_font.render(f"Time Left: {remaining}s", True, (255, 255, 255))
    timer_rect = timer_text.get_rect(center=(WIDTH // 2, 60))
    screen.blit(timer_text, timer_rect)

    # انیمیشن تغییر سایز برای اسکور بازیکن اول
    if score1_target_scale != 1.0:
        if abs(score1_scale - score1_target_scale) < 0.01:
            score1_target_scale = 1.0
        else:
            score1_scale += (score1_target_scale - score1_scale) * scale_speed

    # انیمیشن تغییر سایز برای اسکور بازیکن دوم
    if score2_target_scale != 1.0:
        if abs(score2_scale - score2_target_scale) < 0.01:
            score2_target_scale = 1.0
        else:
            score2_scale += (score2_target_scale - score2_scale) * scale_speed

    # فونت بزرگ‌تر پایه برای اسکور
    base_font_size = 90
    font_bold_large_scaled_1 = pygame.font.SysFont("Segoe UI", int(base_font_size * score1_scale), bold=True)
    font_bold_large_scaled_2 = pygame.font.SysFont("Segoe UI", int(base_font_size * score2_scale), bold=True)

    # نام بازیکنان بزرگ‌تر و بالاتر از اعداد
    name1_text = font_small.render(player1_name, True, BLUE)
    name2_text = font_small.render(player2_name, True, RED)
    name1_rect = name1_text.get_rect(center=(WIDTH // 4, 10))  # بالاتر
    name2_rect = name2_text.get_rect(center=(WIDTH - WIDTH // 4, 10))

    screen.blit(name1_text, name1_rect)
    screen.blit(name2_text, name2_rect)

    # امتیازها
    score1_text = font_bold_large_scaled_1.render(str(score1), True, BLUE)
    score2_text = font_bold_large_scaled_2.render(str(score2), True, RED)

    score1_rect = score1_text.get_rect(center=(WIDTH // 4, 65))
    score2_rect = score2_text.get_rect(center=(WIDTH - WIDTH // 4, 65))

    screen.blit(score1_text, score1_rect)
    screen.blit(score2_text, score2_rect)

# هر جایی که score1 یا score2 تغییر کرد، برای مثال:
# وقتی score1 اضافه میشه:
score1_target_scale = 1.3  # به عدد ۱.۳ بزرگ میشه و بعد کم میشه به ۱.۰
# وقتی score2 اضافه میشه:
score2_target_scale = 1.3





def draw_game():
    screen.fill(BLACK)
    pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 4)
    pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2), 100, 2)

    pygame.draw.rect(screen, GREEN, (player1_pos[0], player1_pos[1], player_width, player_height))
    pygame.draw.rect(screen, BLUE, (player2_pos[0], player2_pos[1], player_width, player_height))

    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    draw_scoreboard()

def main():
    global mode, menu_selected, player1_name, player2_name, input_active
    global score1, score2, ball_speed, ball_pos, player1_pos, player2_pos
    global game_start_time

    records = load_records()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if mode == MODE_MENU:
                    if event.key == pygame.K_UP:
                        menu_selected = (menu_selected - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        menu_selected = (menu_selected + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if menu_selected == 0:
                            mode = MODE_INPUT_NAMES
                            input_active = 1
                        elif menu_selected == 1:
                            mode = MODE_RECORDS
                        elif menu_selected == 2:
                            mode = MODE_ABOUT
                        elif menu_selected == 3:
                            running = False

                elif mode == MODE_INPUT_NAMES:
                    if input_active:
                        if event.key == pygame.K_BACKSPACE:
                            if input_active == 1:
                                player1_name = player1_name[:-1]
                            elif input_active == 2:
                                player2_name = player2_name[:-1]
                        elif event.key == pygame.K_RETURN:
                            if input_active == 1:
                                if player1_name.strip():
                                    input_active = 2  # بعد از Enter بره بازیکن دوم
                            elif input_active == 2:
                                if player1_name.strip() and player2_name.strip():
                                    mode = MODE_PLAY
                                    score1 = 0
                                    score2 = 0
                                    ball_pos[:] = [WIDTH // 2, HEIGHT // 2]
                                    ball_speed[:] = [ball_speed_init, ball_speed_init]
                                    player1_pos[:] = [50, HEIGHT // 2 - player_height // 2]
                                    player2_pos[:] = [WIDTH - 50 - player_width, HEIGHT // 2 - player_height // 2]
                                    game_start_time = time.time()
                                    input_active = None
                        else:
                            # فقط حروف و اعداد
                            if event.unicode.isalnum() or event.unicode in " -_":
                                if input_active == 1:
                                    if len(player1_name) < 12:
                                        player1_name += event.unicode
                                elif input_active == 2:
                                    if len(player2_name) < 12:
                                        player2_name += event.unicode
                    # Tab رو غیرفعال میکنیم تا نتونه تغییر بده
                    if event.key == pygame.K_TAB:
                        pass

                elif mode == MODE_PLAY:
                    if event.key == pygame.K_ESCAPE:
                        handle_game_end()

                elif mode in (MODE_RECORDS, MODE_ABOUT):
                    if event.key == pygame.K_ESCAPE:
                        mode = MODE_MENU

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if mode == MODE_INPUT_NAMES:
                    box_w, box_h = 420, 70
                    rect1 = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//4 + 20, box_w, box_h)
                    rect2 = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//4 + 130, box_w, box_h)
                    if rect1.collidepoint(mx, my):
                        input_active = 1
                    elif rect2.collidepoint(mx, my):
                        input_active = 2
                elif mode == MODE_MENU:
                    # کلیک موس روی گزینه‌ها برای انتخاب و رفتن
                    for i in range(len(menu_options)):
                        rect_x = WIDTH // 2 - 150
                        rect_y = HEIGHT // 3 + i * 90
                        rect = pygame.Rect(rect_x, rect_y, 300, 65)
                        if rect.collidepoint(mx, my):
                            menu_selected = i
                            if i == 0:
                                mode = MODE_INPUT_NAMES
                                input_active = 1
                            elif i == 1:
                                mode = MODE_RECORDS
                            elif i == 2:
                                mode = MODE_ABOUT
                            elif i == 3:
                                running = False

        keys = pygame.key.get_pressed()

        if mode == MODE_PLAY:
            # حرکت پلیر 1 با W و S
            if keys[pygame.K_w] and player1_pos[1] > 0:
                player1_pos[1] -= player_speed
            if keys[pygame.K_s] and player1_pos[1] < HEIGHT - player_height:
                player1_pos[1] += player_speed

            # حرکت پلیر 2 با UP و DOWN
            if keys[pygame.K_UP] and player2_pos[1] > 0:
                player2_pos[1] -= player_speed
            if keys[pygame.K_DOWN] and player2_pos[1] < HEIGHT - player_height:
                player2_pos[1] += player_speed

            handle_ball_movement()

            # اتمام بازی با پایان تایمر
            if time.time() - game_start_time > game_duration:
                handle_game_end()

        if mode == MODE_MENU:
            draw_menu()
        elif mode == MODE_INPUT_NAMES:
            draw_input_names()
        elif mode == MODE_PLAY:
            draw_game()
        elif mode == MODE_RECORDS:
            draw_records(records)
        elif mode == MODE_ABOUT:
            draw_about()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
