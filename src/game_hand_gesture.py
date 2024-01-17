import cv2
import numpy as np
import pygame
from pygame.locals import *
import random
import math


pygame.init()
running = True

width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Ship Survival Game')

level = 1
change=1
# colors
blue = (0, 0, 255)
white = (255, 255, 255)
red = (255, 0, 0)
black=(0,0,0)
# water background
background = pygame.image.load('images/water_background.jpg')
background = pygame.transform.scale(background, screen_size)

# ship size
ship_width = 50
ship_height = 50

# lane coordinates
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# player's starting coordinates
player_x = 250
player_y = 400

# frame settings
clock = pygame.time.Clock()
fps = 60

# game settings
gameover = False
speed = 6
score = 0

# Load custom font
font_path = pygame.font.match_font('freesansbold')
custom_font = pygame.font.Font(font_path, 22)


# Function for image filtering and hand gesture recognition
def imageFiltering(frame, x, y, w, h):
    roi = frame[y:y + h, x:x + w]

    # applying Gaussian blur to reduce the noise
    blur = cv2.GaussianBlur(roi, (5, 5), 0)
    # converting from colored to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # applying a mask which makes skin color white and others black
    mask = cv2.inRange(hsv, np.array([2, 50, 50]), np.array([20, 255, 255]))

    kernel = np.ones((5, 5))
    # reducing noise
    filtered = cv2.GaussianBlur(mask, (3, 3), 0)
    ret, thresh = cv2.threshold(filtered, 127, 255, 0)  # thresholding the image
    thresh = cv2.GaussianBlur(thresh, (5, 5), 0)  # reducing the noise
    # finding contours in the image. Will be used later in complex hull algorithm
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return roi, thresh, contours

#game story description
def display_game_story():
    # Display game story with background image
    story_background = pygame.image.load('images/game_story_background.jpg')  # Replace with your background image
    story_background = pygame.transform.scale(story_background, screen_size)
    screen.blit(story_background, (0, 0))

    # Display game story text
    story_text = [
        "Once upon a time there was a pirate",
        "(who wants to become king of the pirates)",
        "For achieving that he must have to find the the treasure",
        "hidden by the last king of ",
        "the pirates","(it's been 22 years since "
        "last king of the pirate death",
        "and in this time the pirate era started)",
        "Pirates from all around the world start to find ",
        "the treasure hidden by king if the pirate",
        "You are the controller of the pirate ship ",
        "it's your job to reach to the treasure without ",
        "colliding with other pirates",
        "and creature (which are also on search for treasure)",
        "you are currently in east sea and the treasure is most likely in ",
        "kractius current (a current stream running in middle of world ",
        "connected by east,south,north,west sea)",
    ]

    y_position = 50
    line_spacing=25
    for line in story_text:
        text = custom_font.render(line, True, white)
        text_rect = text.get_rect(center=(width // 2, y_position))
        screen.blit(text, text_rect)
        y_position += line_spacing

    pygame.display.update()
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                waiting_for_input = False

#level_2 game story description
def display_game_story_1():
    story_background = pygame.image.load('images/game_story_background.jpg')  # Replace with your background image
    story_background = pygame.transform.scale(story_background, screen_size)
    screen.blit(story_background, (0, 0))

    # Display game story text
    story_text = [
        "you have now successfully cross the east sea ",
        "it's time to enter into kractius current",
        "through this fast,sharp flowing river which",
        "has lot of dangerous creature and pirates",
        "your job is to cross this river ",
        "without colliding with anyone",
        "....."
    ]

    y_position = 50
    line_spacing = 30
    for line in story_text:
        text = custom_font.render(line, True, black)
        text_rect = text.get_rect(center=(width // 2, y_position))
        screen.blit(text, text_rect)
        y_position += line_spacing

    pygame.display.update()
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                waiting_for_input = False

#main menu
def display_main_menu():
    # Display main menu with background image
    menu_background = pygame.image.load('images/main_menu_background.jpg')  # Replace with your background image
    menu_background = pygame.transform.scale(menu_background, screen_size)
    screen.blit(menu_background, (0, 0))

    # Display game title
    font_title = pygame.font.Font(font_path, 40)
    title_text = font_title.render('Ship Survival Game', True, white)
    title_rect = title_text.get_rect(center=(width // 2, height // 4))
    screen.blit(title_text, title_rect)

    # Display play button
    font_button = pygame.font.Font(font_path, 30)
    play_button_text = font_button.render('Play', True, white)
    play_button_rect = play_button_text.get_rect(center=(width // 2, height // 2))
    pygame.draw.rect(screen, red, play_button_rect, border_radius=10)
    screen.blit(play_button_text, play_button_rect)

    pygame.display.update()

    # Wait for user to click the play button
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    waiting_for_input = False

display_main_menu()
display_game_story()
class Ship(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (ship_width, ship_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerShip(Ship):
    def __init__(self, x, y):
        image = pygame.image.load('images/ship1.png')
        super().__init__(image, x, y)


# sprite groups
player_group = pygame.sprite.Group()
ship_group = pygame.sprite.Group()

# create the player's ship
player_ship = PlayerShip(player_x, player_y)
player_group.add(player_ship)

# load the ship images
ship_filenames = ['enemy_ship1.png', 'enemy_ship2.png', 'enemy_ship3.png']
ship_images = []
for ship_filename in ship_filenames:
    image = pygame.image.load('images/' + ship_filename)
    ship_images.append(image)

# load the explosion image
explosion = pygame.image.load('images/crash.png')
explosion_rect = explosion.get_rect()

# OpenCV initialization
cap = cv2.VideoCapture(0)

# dimensions of the box
x = 100
y = 100
w = 200
h = 200

# Game loop
while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Get hand gesture information from OpenCV
    # Assuming you have a variable `count_defects` representing the number of defects in the hand gesture
    ret, frame = cap.read()
    cv2.rectangle(frame, (y, x), (y + h, x + w), (0, 255, 0), 2)
    try:
        roi, thresh, contours = imageFiltering(frame, x, y, w, h)

        drawing = np.zeros(roi.shape, np.uint8)

        # finding contour with max area
        contour = max(contours, key=lambda x: cv2.contourArea(x), default=None)

        if contour is not None:
            # convex hull. This creates a convex polygon.
            hull = cv2.convexHull(contour)

            # draw contours
            cv2.drawContours(drawing, [contour], -1, (0, 255, 0), 0)
            cv2.drawContours(drawing, [hull], -1, (0, 0, 255), 0)

            # finding defects in the convex polygon formed using convex hull algorithm
            hull = cv2.convexHull(contour, returnPoints=False)
            defects = cv2.convexityDefects(contour, hull)

            count_defects = 0  # defaults initially set to 0

            # finding defects and displaying them on the image
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]  # defect returns 4 arguments
                # using start, end, far to find the defects location
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])

                # finding the angle of the defect using cosine law
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14

                # we know, angle between 2 fingers is within 90 degrees.
                # so anything greater than that isn't considered
                if angle <= 90:
                    count_defects += 1
                    cv2.circle(drawing, far, 5, [0, 0, 255], -1)  # displaying defect

                cv2.line(drawing, start, end, [0, 255, 0], 2)

            # Check for a fist based on contour area and number of defects
            if cv2.contourArea(contour) > 1000 and count_defects <= 7:
                cv2.putText(frame, "Fist", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "Open Hand", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)



        # Move ship left if gesture indicates left movement
        if count_defects > 0 and player_ship.rect.x > left_lane:
            player_ship.rect.x -= 10  # Adjust the movement speed as needed

        # Move ship right if gesture indicates right movement
        elif count_defects == 0 and player_ship.rect.x < right_lane:
            player_ship.rect.x += 10  # Adjust the movement speed as needed

    except Exception as e:
        print(f"Error: {e}")
    cv2.imshow("thresh", thresh)
    cv2.imshow("drawing", drawing)
    cv2.imshow("img", frame)
    screen.blit(background, (0, 0))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert OpenCV BGR to RGB
    frame = np.rot90(frame)  # Rotate the frame if needed
    frame = pygame.surfarray.make_surface(frame)  # Convert frame to Pygame surface
    screen.blit(frame, (width, 0))  # Display the frame on the screen
    # draw the player's ship
    player_group.draw(screen)

    # add an enemy ship
    if len(ship_group) < 3:
        # ensure there's enough gap between enemy ships
        add_ship = True
        for enemy_ship in ship_group:
            if enemy_ship.rect.top < enemy_ship.rect.height * 1.5:
                add_ship = False

        if add_ship:
            # select a random lane
            lane = random.choice(lanes)

            # select a random enemy ship image
            ship_image = random.choice(ship_images)
            enemy_ship = Ship(ship_image, lane, height / -2)
            ship_group.add(enemy_ship)

    # make the enemy ships move
    for enemy_ship in ship_group:
        enemy_ship.rect.y += speed

        # remove enemy ship once it goes off screen
        if enemy_ship.rect.top >= height:
            enemy_ship.kill()
            score += 1
            # if score > 0 and score % 5 == 0:
            # speed += 1

    # draw the enemy ships
    ship_group.draw(screen)

    # display the score
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Score: ' + str(score), True, white)
    text_rect = text.get_rect()
    text_rect.center = (50, 20)
    screen.blit(text, text_rect)

    # check if there's a collision with an enemy ship
    if pygame.sprite.spritecollide(player_ship, ship_group, True):
        gameover = True
        explosion_rect.center = [player_ship.rect.center[0], player_ship.rect.top]

    if score == 2 and change == 1:
        gameover = True  # Pause the game
        display_game_story_1()  # Display game story
        level += 1
        change += 1
        score = 0
        speed = 6
        background = pygame.image.load(f'images/game_story_background_2.jpg')  # Adjust the filename accordingly
        background = pygame.transform.scale(background, screen_size)
        player_ship.rect.center = [player_x, player_y]  # Reset player's position
        ship_group.empty()  # Clear enemy ships
        pygame.time.delay(2000)
    # display game over
    if gameover:
        screen.blit(explosion, explosion_rect)
        pygame.draw.rect(screen, red, (0, 200, width, 100))

        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Game over. Play again? (Enter Y or N)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 250)
        screen.blit(text, text_rect)

    pygame.display.update()

    while gameover:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False

            # get the user's input (y or n)
            if event.type == KEYDOWN:
                if event.key == K_y:
                    # reset the game
                    gameover = False
                    speed = 6
                    score = 0
                    ship_group.empty()
                    player_ship.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    # exit the loops
                    gameover = False
                    running = False

# Release resources
cap.release()
cv2.destroyAllWindows()
pygame.quit()
