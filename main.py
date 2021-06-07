import pygame
import random

pygame.init()

display_width = 800
display_height = 600

display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('My little Morty')

loss_sound = pygame.mixer.Sound('loss.wav')
fall_sound = pygame.mixer.Sound('Bdish.wav')
jump_sound = pygame.mixer.Sound('hihi.wav')
heart_plus_sound = pygame.mixer.Sound('pow5.wav')
button_sound = pygame.mixer.Sound('button.wav')

icon = pygame.image.load('favicon_32x32.png')
pygame.display.set_icon(icon)

obstacle_img = [pygame.image.load(r'blockerMad.png'), pygame.image.load('pokerMad.png'),
                pygame.image.load(r'Cactus2.png')]
obstacle_options = [69, 449, 37, 410, 40, 420]

stone_img = [pygame.image.load('Stone0.png'), pygame.image.load('Stone1.png')]
cloud_img = [pygame.image.load('Cloud0.png'), pygame.image.load('Cloud1.png')]

morty_img = [pygame.image.load('p1_walk01.png'),
             pygame.image.load('p1_walk02.png'),
             pygame.image.load('p1_walk03.png'),
             pygame.image.load('p1_walk04.png'),
             pygame.image.load('p1_walk05.png')]

health_img = pygame.image.load('heart.png')
health_img = pygame.transform.scale(health_img, (30, 30))

img_counter = 0
health = 2


class Object:
    def __init__(self, x, y, width, image, speed):
        self.x = x
        self.y = y
        self.width = width
        self.image = image
        self.speed = speed

    def move(self):
        if self.x >= -self.width:
            display.blit(self.image, (self.x, self.y))
            self.x -= self.speed
            return True
        else:
            return False

    def return_self(self, radius, y, width, image):
        self.x = radius
        self.y = y
        self.width = width
        self.image = image
        display.blit(self.image, (self.x, self.y))


class Button:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.inactive_color = (13, 162, 58)
        self.active_color = (23, 204, 58)

    def draw(self, x, y, message, action=None, font_size=30):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(display, self.active_color, (x, y, self.width, self.height))

            if click[0] == 1:
                pygame.mixer.Sound.play(button_sound)
                pygame.time.delay(300)
                if action is not None:
                    if action == quit:
                        pygame.quit()
                        quit()
                    else:
                        action()
        else:
            pygame.draw.rect(display, self.inactive_color, (x, y, self.width, self.height))

        print_text(message=message, x=x + 10, y=y + 10, font_size=font_size)


morty_width = 60
morty_height = 100
morty_x = display_width // 3
morty_y = display_height - morty_height - 95

clock = pygame.time.Clock()

cactus_width = 20
cactus_height = 70
cactus_x = display_width - 50
cactus_y = display_height - cactus_height - 75

make_jump = False
jump_counter = 30

scores = 0
max_scores = 0
max_above = 0


def show_menu():
    menu_bckgr = pygame.image.load('Menu.png')

    start_btn = Button(288, 70)
    quit_btn = Button(120, 70)

    show = True
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        display.blit(menu_bckgr, (0, 0))
        start_btn.draw(270, 200, 'Start game', start_game, 50)
        quit_btn.draw(358, 300, 'Quit', quit, 50)

        pygame.display.update()
        clock.tick(60)


def start_game():
    global scores, make_jump, jump_counter, morty_y, health
    while game_cycle():
        scores = 0
        make_jump = False
        jump_counter = 30
        morty_y = display_height - morty_height - 100
        health = 2


def game_cycle():
    global make_jump

    game = True
    cactus_arr = []
    create_obstacle_arr(cactus_arr)
    land = pygame.image.load('Land.png')

    stone, cloud = open_random_objects()
    heart = Object(display_width, 280, 30, health_img, 4)

    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            make_jump = True

        count_scores(cactus_arr)

        display.blit(land, (0, 0))
        print_text('scores: ' + str(scores), 600, 10)

        draw_array(cactus_arr)
        move_objects(stone, cloud)

        draw_morty()

        if keys[pygame.K_ESCAPE]:
            pause()

        heart.move()
        hearts_plus(heart)

        if make_jump:
            jump()

        if check_collision(cactus_arr):
            game = False

        show_health()

        pygame.display.update()
        clock.tick(70)
    return game_over()


def jump():
    global morty_y, jump_counter, make_jump
    if jump_counter >= -30:
        if jump_counter == 30:
            pygame.mixer.Sound.play(jump_sound)
        if jump_counter == -30:
            pygame.mixer.Sound.play(fall_sound)

        morty_y -= jump_counter / 2.5
        jump_counter -= 1
    else:
        jump_counter = 30
        make_jump = False


def create_obstacle_arr(array):
    choice = random.randrange(0, 3)
    img = obstacle_img[choice]
    width = obstacle_options[choice * 2]
    height = obstacle_options[choice * 2 + 1]
    array.append(Object(display_width + 20, height, width, img, 4))

    choice = random.randrange(0, 3)
    img = obstacle_img[choice]
    width = obstacle_options[choice * 2]
    height = obstacle_options[choice * 2 + 1]
    array.append(Object(display_width + 300, height, width, img, 4))

    choice = random.randrange(0, 3)
    img = obstacle_img[choice]
    width = obstacle_options[choice * 2]
    height = obstacle_options[choice * 2 + 1]
    array.append(Object(display_width + 600, height, width, img, 4))


def find_radius(array):
    maximum = max(array[0].x, array[1].x, array[2].x)

    if maximum < display_width:
        radius = display_width
        if radius - maximum < 20:
            radius += 270
    else:
        radius = maximum

    choice = random.randrange(0, 5)
    if choice == 0:
        radius += random.randrange(10, 15)
    else:
        radius += random.randrange(230, 370)

    return radius


def draw_array(array):
    for cactus in array:
        check = cactus.move()
        if not check:
            object_return(array, cactus)


def object_return(objects, obj):
    radius = find_radius(objects)

    choice = random.randrange(0, 3)
    img = obstacle_img[choice]
    width = obstacle_options[choice * 2]
    height = obstacle_options[choice * 2 + 1]

    obj.return_self(radius, height, width, img)


def open_random_objects():
    choice = random.randrange(0, 2)
    img_of_stone = stone_img[choice]

    choice = random.randrange(0, 2)
    img_of_cloud = cloud_img[choice]

    stone = Object(display_width, display_height - 80, 10, img_of_stone, 4)
    cloud = Object(display_width, 80, 70, img_of_cloud, 2)

    return stone, cloud


def move_objects(stone, cloud):
    check = stone.move()
    if not check:
        choice = random.randrange(0, 2)
        img_of_stone = stone_img[choice]
        stone.return_self(display_width, 500 + random.randrange(10, 80), stone.width, img_of_stone)

    check = cloud.move()
    if not check:
        choice = random.randrange(0, 2)
        img_of_cloud = cloud_img[choice]
        cloud.return_self(display_width, random.randrange(10, 200), stone.width, img_of_cloud)


def draw_morty():
    global img_counter
    if img_counter == 25:
        img_counter = 0

    display.blit(morty_img[img_counter // 5], (morty_x, morty_y))
    img_counter += 1


def print_text(message, x, y, font_color=(0, 0, 0), font_type='PingPong.ttf', font_size=30):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_color)
    display.blit(text, (x, y))


def pause():
    paused = True

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        print_text('Paused. Press Enter to continue', 160, 300)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            paused = False

        pygame.display.update()
        clock.tick(15)


def check_collision(barriers):
    for barrier in barriers:
        if barrier.y == 449:
            if not make_jump:
                if barrier.x <= morty_x + morty_width - 35 <= barrier.x + barrier.width:
                    if check_health():
                        object_return(barriers, barrier)
                        return False
                    else:
                        return True
            elif jump_counter >= 0:
                if morty_y + morty_height - 5 >= barrier.y:
                    if barrier.x <= morty_x + morty_width - 25 <= barrier.x + barrier.width:
                        if check_health():
                            object_return(barriers, barrier)
                            return False
                        else:
                            return True
            else:
                if morty_y + morty_height - 10 >= barrier.y:
                    if barrier.x <= morty_x <= barrier.x + barrier.width:
                        if check_health():
                            object_return(barriers, barrier)
                            return False
                        else:
                            return True
        else:
            if not make_jump:
                if barrier.x <= morty_x + morty_width - 5 <= barrier.x + barrier.width:
                    if check_health():
                        object_return(barriers, barrier)
                        return False
                    else:
                        return True
            elif jump_counter == 10:
                if morty_y + morty_height - 5 >= barrier.y:
                    if barrier.x <= morty_x + morty_width - 5 <= barrier.x + barrier.width:
                        if check_health():
                            object_return(barriers, barrier)
                            return False
                        else:
                            return True
            elif jump_counter >= -1:
                if morty_y + morty_height - 5 >= barrier.y:
                    if barrier.x <= morty_x + morty_width - 25 <= barrier.x + barrier.width:
                        if check_health():
                            object_return(barriers, barrier)
                            return False
                        else:
                            return True
                else:
                    if morty_y + morty_height - 10 >= barrier.y:
                        if barrier.x <= morty_x + 5 <= barrier.x + barrier.width:
                            if check_health():
                                object_return(barriers, barrier)
                                return False
                            else:
                                return True
    return False


def count_scores(barriers):
    global scores, max_above
    above_cactus = 0

    if -20 <= jump_counter < 25:
        for barrier in barriers:
            if morty_y + morty_height - 5 <= barrier.y:
                if barrier.x <= morty_x <= barrier.x + barrier.width:
                    above_cactus += 1
                elif barrier.x <= morty_x + morty_width <= barrier.x + barrier.width:
                    above_cactus += 1

        max_above = max(max_above, above_cactus)
    else:
        if jump_counter == -30:
            scores += max_above
            max_above = 0


def game_over():
    global scores, max_scores
    if scores > max_scores:
        max_scores = scores

    stopped = True
    while stopped:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        print_text('game over. Press Enter to play again or esc to exit', 15, 300)
        print_text('max scores: ' + str(max_scores), 300, 350)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            return True
        if keys[pygame.K_ESCAPE]:
            return False

        pygame.display.update()
        clock.tick(15)


def show_health():
    global health
    show = 0
    x = 20
    while show != health:
        display.blit(health_img, (x, 20))
        x += 40
        show += 1


def check_health():
    global health
    health -= 1
    if health == 0:
        pygame.mixer.Sound.play(loss_sound)
        return False
    else:
        pygame.mixer.Sound.play(fall_sound)
        return True


def hearts_plus(heart):
    global health, morty_x, morty_y, morty_width, morty_height

    if heart.x <= -heart.width:
        radius = display_width + random.randrange(800, 1800)
        heart.return_self(radius, heart.y, heart.width, heart.image)

    if morty_x <= heart.x <= morty_x + morty_width:
        if morty_y <= heart.y <= morty_y + morty_height:
            pygame.mixer.Sound.play(heart_plus_sound)
            if health < 5:
                health += 1

            radius = display_width + random.randrange(800, 1800)
            heart.return_self(radius, heart.y, heart.width, heart.image)


show_menu()
pygame.quit()
quit()
