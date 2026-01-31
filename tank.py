import pygame
import time
import random
import json
import os
import socket
import threading

pygame.init()

display_width = 900
display_height = 640

gameDisplay = pygame.display.set_mode((display_width, display_height))

pygame.display.set_caption('Tanks')

icon = pygame.image.load("ic.jpg")
pygame.display.set_icon(icon)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

net_state = {
    "enabled": False,
    "role": 1,
    "sock": None,
    "rx_thread": None,
    "alive": False,
    "lock": threading.Lock(),
    "messages": [],
    "seed": None,
}

def _net_disconnect():
    with net_state["lock"]:
        sock = net_state.get("sock")
        net_state["alive"] = False
        net_state["enabled"] = False
        net_state["sock"] = None
        net_state["messages"] = []
        net_state["seed"] = None
    if sock is not None:
        try:
            sock.close()
        except OSError:
            pass

def _net_connect(host=SERVER_HOST, port=SERVER_PORT):
    _net_disconnect()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((host, int(port)))
        sock.settimeout(None)
    except OSError:
        try:
            sock.close()
        except Exception:
            pass
        return False

    with net_state["lock"]:
        net_state["sock"] = sock
        net_state["enabled"] = True
        net_state["alive"] = True
    return True

SAVE_PATH = os.path.join(os.path.dirname(__file__), "save.json")
LEADERBOARD_PATH = os.path.join(os.path.dirname(__file__), "leaderboard.json")

RANKS = [
    "Бронза 1",
    "Бронза 2",
    "Бронза 3",
    "Сильвер 1",
    "Сильвер 2",
    "Сильвер 3",
    "Золото 1",
    "Золото 2",
    "Золото 3",
    "Легендарний",
    "Элита",
    "Нереальний",
]

player_state = {
    "name": "Player",
    "coins": 0,
    "rank_idx": 0,
    "rank_best_idx": 0,
    "items": {
        "x2": 0,
        "freeze": 0,
    },
}

battle_state = {
    "x2_next": False,
    "freeze_enemy": False,
    "mode": "local",
}

class Navigate(Exception):
    def __init__(self, target: str):
        self.target = target

def _load_state():
    global player_state
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        coins = int(data.get("coins", 0))
        items = data.get("items", {})
        name = str(data.get("name", "Player"))
        rank_idx = int(data.get("rank_idx", 0))
        rank_best_idx = int(data.get("rank_best_idx", 0))
        if rank_idx < 0:
            rank_idx = 0
        if rank_idx >= len(RANKS):
            rank_idx = len(RANKS) - 1
        if rank_best_idx < 0:
            rank_best_idx = 0
        if rank_best_idx >= len(RANKS):
            rank_best_idx = len(RANKS) - 1
        player_state = {
            "name": name,
            "coins": coins,
            "rank_idx": rank_idx,
            "rank_best_idx": max(rank_best_idx, rank_idx),
            "items": {
                "x2": int(items.get("x2", 0)),
                "freeze": int(items.get("freeze", 0)),
            },
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return

def _save_state():
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(player_state, f, ensure_ascii=False, indent=2)
    except OSError:
        return

def _award_win_coins(amount=25):
    try:
        player_state["coins"] = int(player_state.get("coins", 0)) + int(amount)
    except Exception:
        player_state["coins"] = 0
    _save_state()

def _load_leaderboard():
    try:
        with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {}
    return {}

def _save_leaderboard(lb):
    try:
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(lb, f, ensure_ascii=False, indent=2)
    except OSError:
        return

def _rank_name(idx: int) -> str:
    try:
        return RANKS[int(idx)]
    except Exception:
        return RANKS[0]

def _rank_up():
    idx = int(player_state.get("rank_idx", 0))
    if idx < len(RANKS) - 1:
        idx += 1
    player_state["rank_idx"] = idx
    best = int(player_state.get("rank_best_idx", 0))
    if idx > best:
        player_state["rank_best_idx"] = idx
    _save_state()

def _rank_down():
    idx = int(player_state.get("rank_idx", 0))
    if idx > 0:
        idx -= 1
    player_state["rank_idx"] = idx
    _save_state()

def _leaderboard_update_from_state():
    name = str(player_state.get("name", "Player")).strip() or "Player"
    best_idx = int(player_state.get("rank_best_idx", 0))
    lb = _load_leaderboard()
    prev = lb.get(name)
    try:
        prev_i = int(prev) if prev is not None else -1
    except Exception:
        prev_i = -1
    if best_idx > prev_i:
        lb[name] = best_idx
        _save_leaderboard(lb)

_load_state()

#----------------------------------------colors----------------------------------------------
wheat = (245, 222, 179)

button_pressed = False

white = (255, 255, 255)
black = (0, 0, 0)
gray = (150, 150, 150)

blue = (0, 0, 255)

red = (200, 0, 0)
light_red = (255, 0, 0)

yellow = (200, 200, 0)
light_yellow = (255, 255, 0)

green = (34, 177, 76)
light_green = (0, 255, 0)

sky_blue = (135, 206, 235)
dark_green = (0, 155, 0)
brown = (139, 69, 19)

#--------------------------------for picking current time for the frames per second----------------------
clock = pygame.time.Clock()
#--------------------------------geometry of tank and its turret------------------------------------------
tankWidth = 40
tankHeight = 20

turretWidth = 5
wheelWidth = 5

ground_height = 35

def tank(x, y, turPos):
    x = int(x)
    y = int(y)
    possibleTurrets = [
        (x - 27, y - 2),
        (x - 26, y - 5),
        (x - 25, y - 8),
        (x - 23, y - 12),
        (x - 20, y - 14),
        (x - 18, y - 15),
        (x - 15, y - 17),
        (x - 13, y - 19),
        (x - 11, y - 21),
        (x - 8, y - 23),
        (x - 5, y - 25),
        (x - 2, y - 26),
        (x + 1, y - 27),
    ]

    pygame.draw.circle(gameDisplay, black, (x, y), int(tankHeight / 2))
    pygame.draw.rect(gameDisplay, black, (x - tankHeight, y, tankWidth, tankHeight))
    pygame.draw.line(gameDisplay, black, (x, y), possibleTurrets[int(turPos)], turretWidth)

    startX = x - 15
    for _ in range(7):
        pygame.draw.circle(gameDisplay, black, (startX, y + 20), wheelWidth)
        startX += 5

    return possibleTurrets[int(turPos)]

def enemy_tank(x, y, turPos):
    x = int(x)
    y = int(y)
    possibleTurrets = [
        (x + 27, y - 2),
        (x + 26, y - 5),
        (x + 25, y - 8),
        (x + 23, y - 12),
        (x + 20, y - 14),
        (x + 18, y - 15),
        (x + 15, y - 17),
        (x + 13, y - 19),
        (x + 11, y - 21),
        (x + 8, y - 23),
        (x + 5, y - 25),
        (x + 2, y - 26),
        (x - 1, y - 27),
    ]

    pygame.draw.circle(gameDisplay, black, (x, y), int(tankHeight / 2))
    pygame.draw.rect(gameDisplay, black, (x - tankHeight, y, tankWidth, tankHeight))
    pygame.draw.line(gameDisplay, black, (x, y), possibleTurrets[int(turPos)], turretWidth)

    startX = x - 15
    for _ in range(7):
        pygame.draw.circle(gameDisplay, black, (startX, y + 20), wheelWidth)
        startX += 5

    return possibleTurrets[int(turPos)]
#--------------------------------------------fonts with size, for text_object function----------------
smallfont = pygame.font.SysFont("comicsansms", 25)
medfont = pygame.font.SysFont("comicsansms", 50)
largefont = pygame.font.SysFont("Yu Mincho Demibold", 85)
vsmallfont = pygame.font.SysFont("Yu Mincho Demibold", 25)

#--------------------------------------------defining score function----------------------------------
def score(score):
    text = smallfont.render("Score: " + str(score), True, white)
    gameDisplay.blit(text, [0, 0])

def text_objects(text, color, size="small"):
    if size == "small":
        textSurface = smallfont.render(text, True, color)
    if size == "medium":
        textSurface = medfont.render(text, True, color)
    if size == "large":
        textSurface = largefont.render(text, True, color)
    if size == "vsmall":
        textSurface = vsmallfont.render(text, True, color)

    return textSurface, textSurface.get_rect()

def text_to_button(msg, color, buttonx, buttony, buttonwidth, buttonheight, size="vsmall"):
    textSurf, textRect = text_objects(msg, color, size)
    textRect.center = ((buttonx + (buttonwidth / 2)), buttony + (buttonheight / 2))
    gameDisplay.blit(textSurf, textRect)

def message_to_screen(msg, color, y_displace=0, size="small"):
    textSurf, textRect = text_objects(msg, color, size)
    textRect.center = (int(display_width / 2), int(display_height / 2) + y_displace)
    gameDisplay.blit(textSurf, textRect)

def health_bars(player_health, enemy_health):
    if player_health > 75:
        player_health_color = green
    elif player_health > 50:
        player_health_color = yellow
    else:
        player_health_color = red

    if enemy_health > 75:
        enemy_health_color = green
    elif enemy_health > 50:
        enemy_health_color = yellow
    else:
        enemy_health_color = red

    pygame.draw.rect(gameDisplay, player_health_color, (display_width - 20 - player_health, 25, player_health, 25))
    pygame.draw.rect(gameDisplay, enemy_health_color, (20, 25, enemy_health, 25))

def button(text, x, y, width, height, inactive_color, active_color, action=None, size="small"):
    global button_pressed
    cur = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if click[0] == 0:
        button_pressed = False

    if x + width > cur[0] > x and y + height > cur[1] > y:
        pygame.draw.rect(gameDisplay, active_color, (x, y, width, height))
        if click[0] == 1 and action is not None and not button_pressed:
            button_pressed = True
            if action == "quit":
                pygame.quit()
                quit()
            raise Navigate(str(action))
    else:
        pygame.draw.rect(gameDisplay, inactive_color, (x, y, width, height))

    text_to_button(text, black, x, y, width, height, size)

def game_intro():
    while True:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            gameDisplay.fill(black)
            message_to_screen("Tanks", white, -160, size="large")
            message_to_screen(f"Coins: {player_state.get('coins', 0)}", wheat, -60)

            button("Play", 150, 500, 150, 60, wheat, light_green, action="play")
            button("Quit", 600, 500, 150, 60, wheat, light_red, action="quit")

            pygame.display.update()
            clock.tick(30)
        except Navigate as nav:
            if nav.target == "play":
                play_menu()
            
            continue
            raise

def play_menu():
    while True:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            gameDisplay.fill(black)
            message_to_screen("Режим гри", white, -160, size="large")
            message_to_screen(f"Нік: {player_state.get('name','Player')}", wheat, -80)
            message_to_screen(f"Ranked: {_rank_name(player_state.get('rank_idx', 0))}", wheat, -40)

            button("Локально", 120, 500, 200, 60, wheat, light_green, action="local")
            button("Ranked", 350, 500, 200, 60, wheat, light_yellow, action="ranked")
            button("Назад", 580, 500, 200, 60, wheat, light_red, action="main")

            pygame.display.update()
            clock.tick(30)
        except Navigate as nav:
            if nav.target == "main":
                return
            if nav.target == "local":
                battle_state["mode"] = "local"
                gameLoop()
                continue
            if nav.target == "ranked":
                battle_state["mode"] = "ranked"
                gameLoop()
                continue
            raise

def gameLoop():
    x = int(display_width * 0.75)
    y = int(display_height - ground_height - tankHeight)
    enemy_x = int(display_width * 0.25)
    enemy_y = int(display_height - ground_height - tankHeight)

    barrier_width = 55
    xlocation = int((display_width / 2) - (barrier_width / 2))
    randomHeight = int(random.randrange(int(display_height * 0.15), int(display_height * 0.55)))

    x_change = 0
    turretPos = 0
    changeTur = 0
    player_health = 100
    enemy_health = 100

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -6
                elif event.key == pygame.K_RIGHT:
                    x_change = 6
                elif event.key == pygame.K_UP:
                    changeTur = -1
                elif event.key == pygame.K_DOWN:
                    changeTur = 1
                elif event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_SPACE:
                    dmg = 25
                    if battle_state.get("x2_next"):
                        dmg *= 2
                        battle_state["x2_next"] = False
                    enemy_health -= dmg
                    if enemy_health <= 0:
                        _award_win_coins(25)
                        if battle_state.get("mode") == "ranked":
                            _rank_up()
                            _leaderboard_update_from_state()
                        return

                    edmg = random.choice([5, 10, 18, 25])
                    if battle_state.get("freeze_enemy"):
                        battle_state["freeze_enemy"] = False
                        edmg = 0
                    player_health -= edmg
                    if player_health <= 0:
                        if battle_state.get("mode") == "ranked":
                            _rank_down()
                            _leaderboard_update_from_state()
                        return
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    x_change = 0
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    changeTur = 0

        x += x_change
        if x < int(display_width * 0.45):
            x = int(display_width * 0.45)
        if x > display_width - tankWidth:
            x = display_width - tankWidth

        if x - tankHeight < xlocation + barrier_width and x > xlocation:
            x = xlocation + barrier_width + tankHeight

        turretPos += changeTur
        if turretPos < 0:
            turretPos = 0
        if turretPos > 12:
            turretPos = 12

        gameDisplay.fill(sky_blue)
        pygame.draw.rect(gameDisplay, dark_green, (0, display_height - ground_height, display_width, ground_height))
        pygame.draw.rect(
            gameDisplay,
            brown,
            (xlocation, display_height - randomHeight, barrier_width, randomHeight),
        )
        health_bars(player_health, enemy_health)

        tank(x, y, turretPos)
        enemy_tank(enemy_x, enemy_y, 8)
        message_to_screen("Space - постріл | Esc - назад", black, -280, size="vsmall")
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    game_intro()