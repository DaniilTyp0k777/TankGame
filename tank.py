import pygame
import time
import random
import json
import socket
import threading

pygame.init()

display_width = 800
display_height = 600

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

#----------------------------------------colors----------------------------------------------
wheat=(245,222,179)

button_pressed = False

white = (255, 255, 255)
black = (0, 0, 0)
gray = (150, 150, 150)

blue = (0,0,255)

red = (200, 0, 0)
light_red = (255, 0, 0)

yellow = (200, 200, 0)
light_yellow = (255, 255, 0)

green = (34, 177, 76)
light_green = (0, 255, 0)

#--------------------------------for picking current time for the frames per second----------------------
clock = pygame.time.Clock()
#--------------------------------geometry of tank and its turret------------------------------------------
tankWidth = 40
tankHeight = 20

turretWidth = 5
wheelWidth = 5

ground_height = 35
#--------------------------------------------fonts with size, for text_object function----------------
smallfont = pygame.font.SysFont("comicsansms", 25)
medfont = pygame.font.SysFont("comicsansms", 50)
largefont = pygame.font.SysFont("Yu Mincho Demibold", 85)
vsmallfont = pygame.font.SysFont("Yu Mincho Demibold", 25)

#--------------------------------------------defining score function----------------------------------
def score(score):
    text = smallfont.render("Score: " + str(score), True, white)
    gameDisplay.blit(text, [0, 0])

#---defining function to get the fonts and sizes assigned with them by size names by default size="small"--
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

#---------------------fuction for texts that has to appear over button----------------------------------------
def text_to_button(msg, color, buttonx, buttony, buttonwidth, buttonheight, size="vsmall"):
    textSurf, textRect = text_objects(msg, color, size)
    textRect.center = ((buttonx + (buttonwidth / 2)), buttony + (buttonheight / 2))
    gameDisplay.blit(textSurf, textRect)

#--------------------fuction for texts that has to appear over screen----------------------------------------
def message_to_screen(msg, color, y_displace=0, size="small"):
    textSurf, textRect = text_objects(msg, color, size)
    textRect.center = (int(display_width / 2), int(display_height / 2) + y_displace)
    gameDisplay.blit(textSurf, textRect)

def footer_note(msg):
    textSurf = vsmallfont.render(msg, True, gray)
    textRect = textSurf.get_rect()
    textRect.center = (int(display_width / 2), int(display_height - 15))
    gameDisplay.blit(textSurf, textRect)

#----------------------fuction for players tank , defining turrets positins and wheels dimensions------------
def tank(x, y, turPos):
    x = int(x)
    y = int(y)

    possibleTurrets = [(x - 27, y - 2),
                       (x - 26, y - 5),
                       (x - 25, y - 8),
                       (x - 23, y - 12),
                       (x - 20, y - 14),
                       (x - 18, y - 15),
                       (x - 15, y - 17),
                       (x - 13, y - 19),
                       (x - 11, y - 21)
                       ]

    pygame.draw.circle(gameDisplay, blue, (x, y), int(tankHeight / 2))
    pygame.draw.rect(gameDisplay, blue, (x - tankHeight, y, tankWidth, tankHeight))

    pygame.draw.line(gameDisplay, blue, (x, y), possibleTurrets[turPos], turretWidth)

    pygame.draw.circle(gameDisplay, blue, (x - 15, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x - 10, y + 20), wheelWidth)

    pygame.draw.circle(gameDisplay, blue, (x - 15, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x - 10, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x - 5, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x + 5, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x + 10, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x + 15, y + 20), wheelWidth)

    return possibleTurrets[turPos]

#----------------------fuction for computers tank , defining turrets positins and wheels dimensions------------
def enemy_tank(x, y, turPos):
    x = int(x)
    y = int(y)

    possibleTurrets = [(x + 27, y - 2),
                       (x + 26, y - 5),
                       (x + 25, y - 8),
                       (x + 23, y - 12),
                       (x + 20, y - 14),
                       (x + 18, y - 15),
                       (x + 15, y - 17),
                       (x + 13, y - 19),
                       (x + 11, y - 21)
                       ]

    pygame.draw.circle(gameDisplay, blue, (x, y), int(tankHeight / 2))
    pygame.draw.rect(gameDisplay, blue, (x - tankHeight, y, tankWidth, tankHeight))

    pygame.draw.line(gameDisplay, blue, (x, y), possibleTurrets[turPos], turretWidth)

    pygame.draw.circle(gameDisplay, blue, (x - 15, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x - 10, y + 20), wheelWidth)

    pygame.draw.circle(gameDisplay, blue, (x - 15, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x - 10, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x - 5, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x + 5, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x + 10, y + 20), wheelWidth)
    pygame.draw.circle(gameDisplay, blue, (x + 15, y + 20), wheelWidth)

    return possibleTurrets[turPos]

def pause():
    paused = True
    message_to_screen("Пауза", white, -100, size="large")
    message_to_screen("Натисніть C, щоб продовжити гру або Q, щоб вийти", wheat, 25)
    pygame.display.update()
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    paused = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        clock.tick(5)

def barrier(xlocation, randomHeight, barrier_width):
    pygame.draw.rect(gameDisplay, green, [xlocation, display_height - randomHeight, barrier_width, randomHeight])

def explosion(x, y, size=50):
    explode = True
    while explode:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        colorChoices = [red, light_red, yellow, light_yellow]
        magnitude = 1
        while magnitude < size:
            exploding_bit_x = x + random.randrange(-1 * magnitude, magnitude)
            exploding_bit_y = y + random.randrange(-1 * magnitude, magnitude)

            pygame.draw.circle(
                gameDisplay,
                colorChoices[random.randrange(0, 4)],
                (exploding_bit_x, exploding_bit_y),
                random.randrange(1, 5),
            )
            magnitude += 1

            pygame.display.update()
            clock.tick(100)

        explode = False

def fireShell(xy, tankx, tanky, turPos, gun_power, xlocation, barrier_width, randomHeight, enemyTankX, enemyTankY):
    fire = True
    damage = 0
    startingShell = list(xy)
    print("Вогонь!", xy)

    while fire:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pygame.draw.circle(gameDisplay, red, (startingShell[0], startingShell[1]), 5)
        startingShell[0] -= (12 - turPos) * 2
        startingShell[1] += int(
            (((startingShell[0] - xy[0]) * 0.015 / (gun_power / 50)) ** 2) - (turPos + turPos / (12 - turPos))
        )

        if startingShell[1] > display_height - ground_height:
            print("Останній снаряд:", startingShell[0], startingShell[1])
            hit_x = int((startingShell[0] * display_height - ground_height) / startingShell[1])
            hit_y = int(display_height - ground_height)
            print("Вплив:", hit_x, hit_y)

            if enemyTankX + 10 > hit_x > enemyTankX - 10:
                print("Критичний влучання!")
                damage = 25
            elif enemyTankX + 15 > hit_x > enemyTankX - 15:
                print("Важке влучання!")
                damage = 18
            elif enemyTankX + 25 > hit_x > enemyTankX - 25:
                print("Середнє влучання")
                damage = 10
            elif enemyTankX + 35 > hit_x > enemyTankX - 35:
                print("Легке влучання")
                damage = 5

            explosion(hit_x, hit_y)
            fire = False

        check_x_1 = startingShell[0] <= xlocation + barrier_width
        check_x_2 = startingShell[0] >= xlocation

        check_y_1 = startingShell[1] <= display_height
        check_y_2 = startingShell[1] >= display_height - randomHeight

        if check_x_1 and check_x_2 and check_y_1 and check_y_2:
            print("Останній снаряд:", startingShell[0], startingShell[1])
            hit_x = int((startingShell[0]))
            hit_y = int(startingShell[1])
            print("Вплив:", hit_x, hit_y)
            explosion(hit_x, hit_y)
            fire = False

        pygame.display.update()
        clock.tick(60)

    return damage

def e_fireShell(xy, tankx, tanky, turPos, gun_power, xlocation, barrier_width, randomHeight, ptankx, ptanky):
    damage = 0
    currentPower = 1
    power_found = False

    while not power_found:
        currentPower += 1
        if currentPower > 100:
            power_found = True

        fire = True
        startingShell = list(xy)

        while fire:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            startingShell[0] += (12 - turPos) * 2
            startingShell[1] += int(
                (((startingShell[0] - xy[0]) * 0.015 / (currentPower / 50)) ** 2) - (turPos + turPos / (12 - turPos))
            )

            if startingShell[1] > display_height - ground_height:
                hit_x = int((startingShell[0] * display_height - ground_height) / startingShell[1])
                hit_y = int(display_height - ground_height)
                if ptankx + 15 > hit_x > ptankx - 15:
                    print("ціль досягнута!")
                    power_found = True
                fire = False

            check_x_1 = startingShell[0] <= xlocation + barrier_width
            check_x_2 = startingShell[0] >= xlocation

            check_y_1 = startingShell[1] <= display_height
            check_y_2 = startingShell[1] >= display_height - randomHeight

            if check_x_1 and check_x_2 and check_y_1 and check_y_2:
                fire = False

    fire = True
    startingShell = list(xy)
    print("Вогонь!", xy)

    while fire:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pygame.draw.circle(gameDisplay, red, (startingShell[0], startingShell[1]), 5)
        startingShell[0] += (12 - turPos) * 2
        gun_power = random.randrange(int(currentPower * 0.90), int(currentPower * 1.10))

        startingShell[1] += int(
            (((startingShell[0] - xy[0]) * 0.015 / (gun_power / 50)) ** 2) - (turPos + turPos / (12 - turPos))
        )

        if startingShell[1] > display_height - ground_height:
            print("Останній снаряд:", startingShell[0], startingShell[1])
            hit_x = int((startingShell[0] * display_height - ground_height) / startingShell[1])
            hit_y = int(display_height - ground_height)
            print("Вплив:", hit_x, hit_y)

            if ptankx + 10 > hit_x > ptankx - 10:
                print("Критичний влучання!")
                damage = 25
            elif ptankx + 15 > hit_x > ptankx - 15:
                print("Важке влучання!")
                damage = 18
            elif ptankx + 25 > hit_x > ptankx - 25:
                print("Середнє влучання")
                damage = 10
            elif ptankx + 35 > hit_x > ptankx - 35:
                print("Легке влучання")
                damage = 5

            explosion(hit_x, hit_y)
            fire = False

        check_x_1 = startingShell[0] <= xlocation + barrier_width
        check_x_2 = startingShell[0] >= xlocation

        check_y_1 = startingShell[1] <= display_height
        check_y_2 = startingShell[1] >= display_height - randomHeight

        if check_x_1 and check_x_2 and check_y_1 and check_y_2:
            print("Останній снаряд:", startingShell[0], startingShell[1])
            hit_x = int((startingShell[0]))
            hit_y = int(startingShell[1])
            print("Вплив:", hit_x, hit_y)
            explosion(hit_x, hit_y)
            fire = False

        pygame.display.update()
        clock.tick(60)

    return damage

def power(level):
    text = smallfont.render("Потужність: " + str(level) + "%", True, wheat)
    gameDisplay.blit(text, [display_width / 2, 0])

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

    pygame.draw.rect(gameDisplay, player_health_color, (680, 25, player_health, 25))
    pygame.draw.rect(gameDisplay, enemy_health_color, (20, 25, enemy_health, 25))

def game_over():
    game_over = True
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(black)
        message_to_screen("Гра закінчена", white, -100, size="large")
        message_to_screen("Ви програли.", wheat, -30)

        button("Зіграти знову", 150, 500, 150, 50, wheat, light_green, action="play")
        button("Керування", 350, 500, 100, 50, wheat, light_yellow, action="controls")
        button("Вийти", 550, 500, 100, 50, wheat, light_red, action="quit")

        pygame.display.update()
        clock.tick(15)

def you_win():
    win = True
    while win:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(black)
        message_to_screen("Ви виграли!", white, -100, size="large")
        message_to_screen("Вітання!", wheat, -30)

        button("Зіграти знову", 150, 500, 150, 50, wheat, light_green, action="play")
        button("Керування", 350, 500, 100, 50, wheat, light_yellow, action="controls")
        button("Вийти", 550, 500, 100, 50, wheat, light_red, action="quit")

        pygame.display.update()
        clock.tick(15)

#-----------------------------------------Game control Screen------------------------------------------------
def game_controls():
    gcont = True

    while gcont:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(black)
        message_to_screen("Керування", white, -100, size="large")
        message_to_screen("Вогонь: Пробіл", wheat, -30)
        message_to_screen("Переміщення гармати: Вгору і вниз стрілки", wheat, 10)
        message_to_screen("Переміщення танка: Ліва і права стрілки", wheat, 50)
        message_to_screen("Натисніть D, щоб збільшити потужність % AND натисніть A, щоб зменшити потужність % ", wheat, 140)
        message_to_screen("Пауза: P", wheat, 90)

        button("Грати", 150, 500, 100, 50, green, light_green, action="play")
        button("Головне меню", 350, 500, 100, 50, yellow, light_yellow, action="main")
        button("Вийти", 550, 500, 100, 50, red, light_red, action="quit")

        pygame.display.update()

        clock.tick(15)

#--------------function for buttons having action calls and text on it callings---------------------------
def button(text, x, y, width, height, inactive_color, active_color, action=None,size=" "):
    global button_pressed
    cur = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    # print(click)

    if click[0] == 0:
        button_pressed = False

    if x + width > cur[0] > x and y + height > cur[1] > y:
        pygame.draw.rect(gameDisplay, active_color, (x, y, width, height))
        if click[0] == 1 and action != None and not button_pressed:
            button_pressed = True
            if action == "quit":
                pygame.quit()
                quit()

            if action == "controls":
                game_controls()

            if action == "play":
                play_menu()

            if action == "main":
                game_intro()

            if action == "local":
                _net_disconnect()
                gameLoop()

            if action == "server":
                _net_disconnect()
                try:
                    _net_connect()
                except OSError:
                    print(f"[Мережа] Не вдалося підключитися до {SERVER_HOST}:{SERVER_PORT}")
                    return
                _wait_for_match_screen()
                gameLoop()

    else:
        pygame.draw.rect(gameDisplay, inactive_color, (x, y, width, height))

    text_to_button(text, black, x, y, width, height)

def _net_send(obj):
    with net_state["lock"]:
        sock = net_state.get("sock")
    if sock is None:
        return
    try:
        data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
        sock.sendall(data)
    except OSError:
        return

def _net_reader():
    buf = bytearray()
    while True:
        with net_state["lock"]:
            alive = net_state["alive"]
            sock = net_state["sock"]
        if not alive or sock is None:
            return
        try:
            chunk = sock.recv(4096)
        except OSError:
            chunk = b""
        if not chunk:
            with net_state["lock"]:
                net_state["alive"] = False
            return
        buf.extend(chunk)
        while True:
            idx = buf.find(b"\n")
            if idx == -1:
                break
            line = buf[:idx]
            del buf[: idx + 1]
            try:
                msg = json.loads(line.decode("utf-8"))
            except Exception:
                continue
            with net_state["lock"]:
                net_state["messages"].append(msg)

def _net_connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.settimeout(5)
    s.connect((SERVER_HOST, SERVER_PORT))
    s.settimeout(None)
    with net_state["lock"]:
        net_state["sock"] = s
        net_state["alive"] = True
        net_state["messages"].clear()
        net_state["seed"] = None
    t = threading.Thread(target=_net_reader, daemon=True)
    with net_state["lock"]:
        net_state["rx_thread"] = t
    t.start()

def _net_disconnect():
    with net_state["lock"]:
        sock = net_state.get("sock")
        net_state["sock"] = None
        net_state["alive"] = False
        net_state["enabled"] = False
    if sock is not None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            sock.close()
        except OSError:
            pass

def _net_pop_messages():
    with net_state["lock"]:
        msgs = list(net_state["messages"])
        net_state["messages"].clear()
    return msgs

def play_menu():
    menu = True
    while menu:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(black)
        message_to_screen("Режим гри", white, -120, size="large")
        message_to_screen("Локально: гра проти бота", wheat, -20)
        message_to_screen("Сервер: пошук суперника", wheat, 20)
        footer_note("Мережевий режим (server.py) додано окремим файлом. Оберіть: Локально / Сервер")

        button("Локально", 120, 500, 160, 50, wheat, light_green, action="local")
        button("Сервер", 320, 500, 160, 50, wheat, light_yellow, action="server")
        button("Назад", 520, 500, 160, 50, wheat, light_red, action="main")

        pygame.display.update()
        clock.tick(15)

def _wait_for_match_screen():

    print("[Мережа] Пошук суперника...")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _net_disconnect()
                pygame.quit()
                quit()

        for msg in _net_pop_messages():
            if msg.get("type") == "match":
                with net_state["lock"]:
                    net_state["role"] = int(msg.get("role", 1))
                    net_state["enabled"] = True
                    net_state["seed"] = int(msg.get("seed", 0))
                print(f"[Мережа] Знайдено суперника. Роль: {net_state['role']}")
                waiting = False
                break
            if msg.get("type") == "status" and msg.get("state") == "searching":
                pass

        gameDisplay.fill(black)
        message_to_screen("Пошук суперника...", white, -50, size="medium")
        message_to_screen(f"Сервер: {SERVER_HOST}:{SERVER_PORT}", wheat, 20)
        footer_note("Потрібно запустити server.py на хості або в локальній мережі")
        pygame.display.update()
        clock.tick(30)

def _fire_shell_dir(xy, tankx, tanky, turPos, gun_power, direction, xlocation, barrier_width, randomHeight, enemyTankX, enemyTankY):
    fire = True
    damage = 0
    startingShell = list(xy)
    print("[Бій] Постріл!")

    while fire:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pygame.draw.circle(gameDisplay, red, (startingShell[0], startingShell[1]), 5)
        startingShell[0] += direction * (12 - turPos) * 2
        startingShell[1] += int(
            (((startingShell[0] - xy[0]) * 0.015 / (gun_power / 50)) ** 2) - (turPos + turPos / (12 - turPos)))

        if startingShell[1] > display_height - ground_height:
            hit_x = int((startingShell[0] * display_height - ground_height) / startingShell[1])
            hit_y = int(display_height - ground_height)

            if enemyTankX + 10 > hit_x > enemyTankX - 10:
                damage = 25
            elif enemyTankX + 15 > hit_x > enemyTankX - 15:
                damage = 18
            elif enemyTankX + 25 > hit_x > enemyTankX - 25:
                damage = 10
            elif enemyTankX + 35 > hit_x > enemyTankX - 35:
                damage = 5

            explosion(hit_x, hit_y)
            fire = False

        check_x_1 = startingShell[0] <= xlocation + barrier_width
        check_x_2 = startingShell[0] >= xlocation
        check_y_1 = startingShell[1] <= display_height
        check_y_2 = startingShell[1] >= display_height - randomHeight

        if check_x_1 and check_x_2 and check_y_1 and check_y_2:
            hit_x = int((startingShell[0]))
            hit_y = int(startingShell[1])
            explosion(hit_x, hit_y)
            fire = False

        pygame.display.update()
        clock.tick(60)

    return damage

def gameLoop():
    gameExit = False
    gameOver = False
    FPS = 15

    player_health = 100
    enemy_health = 100

    barrier_width = 50

    mainTankX = display_width * 0.9
    mainTankY = display_height * 0.9
    tankMove = 0
    currentTurPos = 0
    changeTur = 0

    enemyTankX = display_width * 0.1
    enemyTankY = display_height * 0.9

    fire_power = 50
    power_change = 0

    if net_state.get("enabled") and net_state.get("seed") is not None:
        random.seed(int(net_state.get("seed")))

    xlocation = int(display_width / 2) + random.randint(int(-0.1 * display_width), int(0.1 * display_width))
    randomHeight = random.randrange(int(display_height * 0.1), int(display_height * 0.6))

    remoteMove = 0
    remoteChangeTur = 0
    remotePowerChange = 0
    remoteTurPos = 8

    while not gameExit:

        if gameOver == True:
            # gameDisplay.fill(white)
            message_to_screen("Game Over", red, -50, size="large")
            message_to_screen("Press C to play again or Q to exit", black, 50)
            pygame.display.update()
            while gameOver == True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameExit = True
                        gameOver = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_c:
                            gameLoop()
                        elif event.key == pygame.K_q:

                            gameExit = True
                            gameOver = False

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                gameExit = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tankMove = -5
                    print("[Рух] Рух вліво")
                    if net_state.get("enabled"):
                        _net_send({"type": "move", "v": -5})

                elif event.key == pygame.K_RIGHT:
                    tankMove = 5
                    print("[Рух] Рух вправо")
                    if net_state.get("enabled"):
                        _net_send({"type": "move", "v": 5})

                elif event.key == pygame.K_UP:
                    changeTur = 1
                    print("[Башта] Повернути вгору")
                    if net_state.get("enabled"):
                        _net_send({"type": "tur", "v": 1})

                elif event.key == pygame.K_DOWN:
                    changeTur = -1
                    print("[Башта] Повернути вниз")
                    if net_state.get("enabled"):
                        _net_send({"type": "tur", "v": -1})

                elif event.key == pygame.K_p:
                    pause()

                elif event.key == pygame.K_SPACE:
                    print("[Бій] Постріл")
                    if net_state.get("enabled"):
                        _net_send({"type": "fire", "tur": currentTurPos, "power": fire_power})
                    else:
                        damage = fireShell(gun, mainTankX, mainTankY, currentTurPos, fire_power, xlocation, barrier_width,
                                           randomHeight, enemyTankX, enemyTankY)
                        enemy_health -= damage

                        possibleMovement = ['f', 'r']
                        moveIndex = random.randrange(0, 2)

                        for x in range(random.randrange(0, 10)):

                            if display_width * 0.3 > enemyTankX > display_width * 0.03:
                                if possibleMovement[moveIndex] == "f":
                                    enemyTankX += 5
                                elif possibleMovement[moveIndex] == "r":
                                    enemyTankX -= 5

                                gameDisplay.fill(black)
                                health_bars(player_health, enemy_health)
                                gun = tank(mainTankX, mainTankY, currentTurPos)
                                enemy_gun = enemy_tank(enemyTankX, enemyTankY, 8)
                                fire_power += power_change

                                power(fire_power)

                                barrier(xlocation, randomHeight, barrier_width)
                                gameDisplay.fill(green,
                                                 rect=[0, display_height - ground_height, display_width, ground_height])
                                pygame.display.update()

                                clock.tick(FPS)

                        damage = e_fireShell(enemy_gun, enemyTankX, enemyTankY, 8, 50, xlocation, barrier_width,
                                             randomHeight, mainTankX, mainTankY)
                        player_health -= damage

                elif event.key == pygame.K_a:
                    power_change = -1
                    print("[Потужність] -")
                    if net_state.get("enabled"):
                        _net_send({"type": "power", "v": -1})
                elif event.key == pygame.K_d:
                    power_change = 1
                    print("[Потужність] +")
                    if net_state.get("enabled"):
                        _net_send({"type": "power", "v": 1})

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    tankMove = 0
                    if net_state.get("enabled"):
                        _net_send({"type": "move", "v": 0})

                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    changeTur = 0
                    if net_state.get("enabled"):
                        _net_send({"type": "tur", "v": 0})

                if event.key == pygame.K_a or event.key == pygame.K_d:
                    power_change = 0
                    if net_state.get("enabled"):
                        _net_send({"type": "power", "v": 0})

        if net_state.get("enabled"):
            for msg in _net_pop_messages():
                t = msg.get("type")
                if t == "move":
                    remoteMove = int(msg.get("v", 0))
                elif t == "tur":
                    remoteChangeTur = int(msg.get("v", 0))
                elif t == "power":
                    remotePowerChange = int(msg.get("v", 0))
                elif t == "fire":
                    rt = int(msg.get("tur", 8))
                    rp = int(msg.get("power", 50))
                    remoteTurPos = rt
                    role = int(net_state.get("role", 1))
                    if role == 1:
                        remote_gun = enemy_tank(enemyTankX, enemyTankY, remoteTurPos)
                        damage = _fire_shell_dir(remote_gun, enemyTankX, enemyTankY, remoteTurPos, rp, 1, xlocation, barrier_width, randomHeight, mainTankX, mainTankY)
                        player_health -= damage
                    else:
                        remote_gun = tank(enemyTankX, enemyTankY, remoteTurPos)
                        damage = _fire_shell_dir(remote_gun, enemyTankX, enemyTankY, remoteTurPos, rp, -1, xlocation, barrier_width, randomHeight, mainTankX, mainTankY)
                        player_health -= damage
                elif t == "opponent_left":
                    print("[Мережа] Суперник вийшов")
                    _net_disconnect()

        mainTankX += tankMove

        currentTurPos += changeTur

        if currentTurPos > 8:
            currentTurPos = 8
        elif currentTurPos < 0:
            currentTurPos = 0

        if mainTankX - (tankWidth / 2) < xlocation + barrier_width:
            mainTankX += 5

        if net_state.get("enabled"):
            role = int(net_state.get("role", 1))

            if role == 2:
                mainTankX, enemyTankX = enemyTankX, mainTankX
                mainTankY, enemyTankY = enemyTankY, mainTankY

            enemyTankX += remoteMove
            remoteTurPos += remoteChangeTur
            if remoteTurPos > 8:
                remoteTurPos = 8
            elif remoteTurPos < 0:
                remoteTurPos = 0

        gameDisplay.fill(black)
        health_bars(player_health, enemy_health)

        role = int(net_state.get("role", 1))
        if net_state.get("enabled") and role == 2:
            gun = enemy_tank(mainTankX, mainTankY, currentTurPos)
            enemy_gun = tank(enemyTankX, enemyTankY, remoteTurPos)
        else:
            gun = tank(mainTankX, mainTankY, currentTurPos)
            enemy_gun = enemy_tank(enemyTankX, enemyTankY, remoteTurPos if net_state.get("enabled") else 8)

        fire_power += power_change

        if fire_power > 100:
            fire_power = 100
        elif fire_power < 1:
            fire_power = 1

        power(fire_power)

        barrier(xlocation, randomHeight, barrier_width)
        gameDisplay.fill(green, rect=[0, display_height - ground_height, display_width, ground_height])
        pygame.display.update()

        if player_health < 1:
            game_over()
        elif enemy_health < 1:
            you_win()
        clock.tick(FPS)

    pygame.quit()
    quit()

def game_intro():
    intro = True

    while intro:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    intro = False
                elif event.key == pygame.K_q:

                    pygame.quit()
                    quit()

        gameDisplay.fill(black)
        message_to_screen("Welcome to Tanks!", white, -100, size="large")
        message_to_screen("The objective is to shoot and destroy", wheat, 15)
        message_to_screen("the enemy tank before they destroy you.", wheat, 60)
        message_to_screen("The more enemies you destroy, the harder they get.", wheat, 110)

        button("Play", 150, 500, 100, 50, wheat, light_green, action="play",size="vsmall")
        button("Controls", 350, 500, 100, 50, wheat, light_yellow, action="controls",size="vsmall")
        button("Quit", 550, 500, 100, 50, wheat, light_red, action="quit",size="vsmall")

        pygame.display.update()

        clock.tick(15)

game_intro()
gameLoop()