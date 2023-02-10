import socket
import pygame
import os
import sys
import errno
import time

pygame.init()

width = 800
height = 493
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (113, 165, 24)
lime = (147, 217, 28)

font = pygame.font.Font('UbuntuMono-Regular.ttf', 30)
small_font = pygame.font.Font('UbuntuMono-Regular.ttf', 20)
screen = pygame.display.set_mode((width, height))

base_path = os.path.dirname(__file__)
dude_path = os.path.join(base_path, 'sounds/Two Finger Johnny.mp3')
pygame.mixer.music.load(dude_path)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

HOST = 'localhost'
PORT = 8000
leaderboard = ''

def setup_screen():
    pygame.display.set_caption('Wisielec')
    titlefont = pygame.font.SysFont('c059', 120)
    base_path = os.path.dirname(__file__)
    dude_path = os.path.join(base_path, 'images/loop.png')
    img = pygame.image.load(dude_path)
    screen.blit(img, (width - img.get_width() - 20, 0))

    title = titlefont.render('Wisi_l_c', True, white)
    screen.blit(title, (width // 2 - title.get_width() // 2, 30))

    clock = pygame.time.Clock()
    base_font = pygame.font.Font(None, 32)
    user_text = ''
    
    set_username = font.render('Podaj nazwę użytkownika:', True, white)
    screen.blit(set_username, (width // 2 - set_username.get_width() // 2, 180))

    input_rect = pygame.Rect(200, 250, 400, 32)
    color_active = pygame.Color('lightskyblue3')
    color_passive = pygame.Color('chartreuse4')
    color = color_passive

    play_ypos = 400
    play = font.render('GRAJ', True, white)
    play_rect = play.get_rect(topleft=(width // 2 - play.get_width() // 2, play_ypos))
    screen.blit(play, play_rect)
    
    active = False
    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

                if play_rect.collidepoint(event.pos) and len(user_text) > 0:
                    return user_text

                if play_rect.collidepoint(event.pos) and len(user_text) == 0:
                    no_username = font.render('Wprowadź nazwę użytkownika', True, red)
                    screen.blit(no_username, (width // 2 - no_username.get_width() // 2, 320))

            if event.type == pygame.MOUSEMOTION:
                m = pygame.mouse.get_pos()
                left = width // 2 - play.get_width() // 2
                right = width // 2 + play.get_width() // 2
                
                if m[0] > left and m[0] < right and m[1] > play_ypos and m[1] < play_ypos + play.get_height():
                    play = font.render('GRAJ', True, red)
                    screen.blit(play, (width // 2 - play.get_width() // 2, play_ypos))
                else:
                    play = font.render('GRAJ', True, white)
                    screen.blit(play, (width // 2 - play.get_width() // 2, play_ypos))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
    
                elif len(user_text) < 16:
                    user_text += event.unicode

        if active:
            color = color_active
        else:
            color = color_passive
        
        pygame.draw.rect(screen, color, input_rect)
        text_surface = base_font.render(user_text, True, (255, 255, 255))
        screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        input_rect.width = max(input_rect.width, text_surface.get_width()+10)
        pygame.display.flip()
        clock.tick(60)


def load_letters(let_ok, let_not_ok):
    alphabet = ['A', 'Ą', 'B', 'C', 'Ć', 'D', 'E', 'Ę', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Ł', 'M', 'N', 'Ń', 'O', 'Ó', 'P', 'Q', 'R', 'S', 'Ś', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ź', 'Ż']
    c = 0
    for i in range(189, 414, 45):
        for j in range(470, 785, 45):

            if alphabet[c].lower() in let_ok or alphabet[c].upper() in let_ok:
                color = lime
            elif alphabet[c].lower() in let_not_ok or alphabet[c].upper() in let_not_ok:
                color = red
            else:
                color = white

            pygame.draw.rect(screen, color, (j, i, 38, 38), 2)
            screen.blit(font.render(alphabet[c], True, color), (j + 11, i + 5))
            c += 1


def run_game(s, category, clue):
    global leaderboard
    s.setblocking(False)

    newWidth = 1123
    newHeight = 600
    screen = pygame.display.set_mode((newWidth, newHeight))
    fails = 0
    winV = 0
    t = 0
    let = []
    let_ok = []
    correct = True
    clue = clue.upper()
    clue = clue[:-1]
    in_game = True

    endFontD = pygame.font.SysFont('verdana', 38, bold=True)
    endFontC = pygame.font.SysFont('verdana', 25, bold=True)

    screen.fill(black)
    dude_path = os.path.join(base_path, 'images/s{}.jpg'.format(fails))
    img = pygame.image.load(dude_path)
    screen.blit(img, (0, height // 3 - 30))

    cat = small_font.render('Kategoria: ' + category, True, white)
    screen.blit(cat, (10, 10))

    hidden = []
    for i in range(len(clue)):
        if clue[i] == ' ':
            hidden.append(' ')
        else:
            hidden.append('-')

    hiddenT = font.render(''.join(hidden), True, white)
    screen.blit(hiddenT, (width // 2 - hiddenT.get_width() // 2, 60))

    while True:
        screen.blit(small_font.render('Kategoria: ' + category, True, white), (10, 10))
        pygame.draw.line(screen, white, (width, 0), (width, newHeight))
        screen.blit(small_font.render('Tablica wyników:', True, white), (width + 10, 10))
        lives = small_font.render('Pozostałych żyć: ' + str(9 - fails), True, white)
        if (fails < 9):
            screen.blit(lives, (width // 2 - lives.get_width() // 2, height))

        if (fails == 9):
            s.setblocking(True)
            try:
                leaderboard = str(s.recv(256).decode()).strip()[:-1]
            except socket.error as e:
                if e.args[0] == errno.EWOULDBLOCK: 
                    print('EWOULDBLOCK')
                    time.sleep(1)
                else:
                    print(e)
                    break

        if len(leaderboard) > 0:
            y = 40
            players = leaderboard.split(";")
            players = list(dict.fromkeys(players))
            if (len(players) > 1):
                for player in players:
                    name, lives = player.split(":")
                    screen.blit(small_font.render(name + ': ' + lives, True, white), (width + 10, y))
                    y += 30
            elif(len(players) == 1):
                winner = endFontC.render('Wygrał gracz ' + name, True, red)
                screen.blit(winner, (width // 2 - winner.get_width() // 2, height + 40))
                in_game = False

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and in_game == True:

                correct = False
                x = event.unicode
                if len(x) != 1:
                    correct = True

                for i in range(len(clue)):
                    if (x == clue.lower()[i] or x == clue[i]) and x not in let_ok:
                        t = 1
                        hidden[i] = clue[i]
                        correct = True
                        dude_path = os.path.join(base_path, 'sounds/yes.wav')
                        yes = pygame.mixer.Sound(dude_path)
                        yes.play()
                
                if t:
                    let_ok.append(x)
                    t = 0

                if not correct and x not in let and x not in let_ok:
                    fails += 1
                    s.sendall(str(9 - fails).encode())
                    let.append(x)
                    dude_path = os.path.join(base_path, 'sounds/ghf.wav')
                    no = pygame.mixer.Sound(dude_path)
                    no.play()
                    try:
                        leaderboard = str(s.recv(256).decode()).strip()[:-1]
                    except socket.error as e:
                        if e.args[0] == errno.EWOULDBLOCK: 
                            print('EWOULDBLOCK')
                            time.sleep(1)
                        else:
                            print(e)
                            break

                if '-' not in hidden:
                    winV = 1
                    s.sendall('w'.encode())
                    
                    screen.fill(black)
                    dude_path = os.path.join(base_path, 'images/s{}.jpg'.format(fails))
                    img = pygame.image.load(dude_path)
                    screen.blit(img, (0, height // 3 - 30))
                    clueT = font.render(clue, True, white)
                    screen.blit(clueT, (width // 2 - clueT.get_width() // 2, 60))

                    win1 = endFontD.render('Tak jest, wygrywasz!', True, lime)
                    screen.blit(win1, (3 * width // 4 - win1.get_width() // 2, 180))
                    pygame.display.flip()
                    
                    dude_path = os.path.join(base_path, 'sounds/win.ogg')
                    win = pygame.mixer.Sound(dude_path)
                    pygame.mixer.music.stop()
                    win.play()
                    pygame.time.wait(2000)
                    pygame.mixer.music.play(-1)
                    

                if fails < 9 and winV == 0:
                    screen.fill(black)
                    dude_path = os.path.join(base_path, 'images/s{}.jpg'.format(fails))
                    img = pygame.image.load(dude_path)
                    screen.blit(img, (0, height // 3 - 30))
                    hiddenT = font.render(''.join(hidden), True, white)
                    screen.blit(hiddenT, (width // 2 - hiddenT.get_width() // 2, 60))

                elif fails == 9 and winV == 0:
                    dude_path = os.path.join(base_path, 'sounds/gameover.ogg')
                    gameOverSound = pygame.mixer.Sound(dude_path)

                    screen.fill(black)
                    dude_path = os.path.join(base_path, 'images/s{}.jpg'.format(fails))
                    img = pygame.image.load(dude_path)
                    screen.blit(img, (0, height // 3 - 30))
                    hiddenT = font.render(''.join(hidden), True, white)
                    youDied = endFontD.render('GINIESZ!', True, red)
                    correctClueText = endFontC.render('Prawidłowe hasło:', True, white)
                    correctClue = endFontC.render(clue, True, white)
                    screen.blit(youDied, (3 * width // 4 - youDied.get_width() // 2, 180))
                    screen.blit(correctClueText, (3 * width // 4 - correctClueText.get_width() // 2, 280))
                    screen.blit(correctClue, (width // 2 - correctClue.get_width() // 2, height))
                    screen.blit(hiddenT, (width // 2 - hiddenT.get_width() // 2, 60))

                    screen.blit(small_font.render('Kategoria: ' + category, True, white), (10, 10))
                    pygame.draw.line(screen, white, (width, 0), (width, newHeight))
                    screen.blit(small_font.render('Tablica wyników:', True, white), (width + 10, 10))

                    in_game = False
                    pygame.display.flip()
                    pygame.mixer.music.stop()
                    gameOverSound.play()
                    pygame.time.wait(5000)
                    pygame.mixer.music.play(-1)
                
        if not winV and in_game == True:
            load_letters(let_ok, let)

        pygame.display.flip()


def play(s):
    global leaderboard
    screen.fill(black)
    waiting = font.render('Czekam na użytkowników...', True, white)
    screen.blit(waiting, (width // 2 - waiting.get_width() // 2, height // 2 - waiting.get_height() // 2))
    pygame.display.flip()

    data = str(s.recv(2).decode()).strip()
    leaderboard = str(s.recv(256).decode()).strip()[:-1]
    print('message ', data)
    if len(data) == 2 and ord(data[0]) >= 48 and ord(data[0]) <= 51 and ord(data[1]) >= 97 and ord(data[1]) <= 122:
        counter = 0
        category = int(data[0])
        clue = ord(data[1]) - 97
        filename = ''
        clue_txt = ''
        category_txt = ''

        if category == 0:
            filename = 'clues/fizyka.txt'
            category_txt = 'Fizyka'
        elif category == 1:
            filename = 'clues/inne.txt'
            category_txt = 'Inne'
        elif category == 2:
            filename = 'clues/muzykaifilm.txt'
            category_txt = 'Muzyka i film'
        elif category == 3:
            filename = 'clues/przyslowia.txt'
            category_txt = 'Przysłowia'

        with open(filename) as file:
            for line in file:
                if counter == clue:
                    clue_txt = line
                    break
                else:
                    counter += 1

        run_game(s, category_txt, clue_txt)
    else:
        print('else')
        main()


def main():
    screen.fill(black)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        setup = 1

        while setup:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            username = setup_screen()
            s.sendall(username.encode())
            
            message = str(s.recv(128).decode()).strip()
            
            if message == 'taken':
                username_taken = font.render('Nazwa użytkownika jest zajęta', True, red)
                screen.blit(username_taken, (width // 2 - username_taken.get_width() // 2, 320))
                pygame.display.flip()
            else:
                play(s)


main()