from classes import *
import pygame as pg

pg.mixer.init()
pg.init()

# All main Sound Effects used in the game
clearSfx = pg.mixer.Sound("sfx/clear.wav")
deathSfx = pg.mixer.Sound("sfx/death.mp3")
startSfx = pg.mixer.Sound("sfx/start.wav")
startSfx.set_volume(0.3)
# Switching between options in the UI
switchSfx = pg.mixer.Sound("sfx/switch.mp3")
confirmSfx = pg.mixer.Sound("sfx/confirm.wav")
confirmSfx.set_volume(0.3)

# Number from 0-2 dictating which player was selected (ghost, mushroom, ant)
selectedSprite: int = 0
gameBeaten: bool = False
# Final score used to determine the rank
# My best score was 3860
score: int = 4000
bestScore: int = 0
colors: list = [("A*", "#069e38"), ("A", "#3afcb1"), ("B", "#fc4b4e"), ("C", "#fcf641"), ("D", "#f232ac"), ("E", "#70bcef"), ("F", "#676767")]

# Cell size and row amount in the Main Menu, not the levels!
cellSize: int = 80
rows: int = 8

def drawMenu(endScreen: bool = False) -> bool:
    '''Draws the starting / ending screen, depending on the parameter.'''
    global selectedSprite
    selectedButton: int = 0

    screen = pg.display.set_mode((cellSize * rows, cellSize * rows))
    surface = pg.Surface((cellSize * rows, cellSize * rows), pg.SRCALPHA)
    # Surface used to overlay the maze in the background
    surface.fill((0, 0, 0, 128))

    # Loading the 3 main sprites representing each character choice
    sprites: list = []
    img = loadImage("sprites/playerSprites.png", 240, 48)
    sprites.append(img.subsurface((0, 0, 16, 16)))
    sprites.append(img.subsurface((80, 0, 16, 16)))
    sprites.append(img.subsurface((160, 0, 16, 16)))
    for _ in range(3):
        sprites[_] = pg.transform.scale(sprites[_], (80,80))

    pg.display.set_caption("Amaze!")
    clock = pg.time.Clock()
    pg.mixer.music.load("music/menu.mp3")
    # Loops indefinitely
    pg.mixer.music.play(-1)
    # 21 x 21 maze displayed in the background of the menu
    maze: Maze = Maze(21, 21)
    maze.loadAssets("sprites/walls.png", cellSize, "sprites/valves.png", screen, clock, 0)
    # Generate the maze using DFS
    maze.generateMaze(choice(maze.staticPoints))
    # Manually generate the wall map for the maze (usually done after valve placement)
    maze.generateWallMap()

    # Load the main images
    bgImg = loadImage("sprites/background.jpeg", cellSize * maze.r, cellSize * maze.c)
    title = loadImage("sprites/title.png", 64 * 8, 32 * 8)
    buttons1 = loadImage("sprites/buttons.png", 32*8, 32*8)
    buttons2 = loadImage("sprites/buttons2.png", 48 * 7, 48 * 7)
    arrows = loadImage("sprites/arrows.png", 240,80)

    # Load all the text beforehand
    bigFont = pg.font.SysFont("mono", 80, bold=True)
    font = pg.font.SysFont("mono", 25)
    smallFont = pg.font.SysFont("mono", 15)
    bottomText1 = font.render("Press Space to Play.", True, "#FFFFFF")
    bottomText2 = font.render("Press A / D to switch Sprites.", True, "#FFFFFF")
    bottomText3 = font.render("Press Space to return to Menu.", True, "#FFFFFF")
    bottomText4 = font.render(f"Best Score: {bestScore}", True, "#FFFFFF")
    playTitle = font.render("-- Play the Game --", True, "#FFFFFF")
    # List of text to draw, making it easier to draw paragraphs of texts at once
    playTexts: list[str] = ["In order to win, collect sapphires", "and gems. Gems give you points.", "", "You can only collect a gem after", "collecting all sapphires.", "", "You need 4 points to advance", "to the next Level.", "", "Your Final Score is a value from", "0 to 4000 and is determined by", "your overall performance.", "", "Good Luck! :)"]
    # Stgs = Settings
    stgsTitle = font.render("- Player Settings -", True, "#FFFFFF")
    stgsTexts: list[str] = ["Customize the appearance of", "the player sprite.", ""]

    scoreText = pg.font.SysFont("mono", 40, bold=True).render(f"{score}/4000", True, "#FFFFFF")
    bestScoreText = bigFont.render(str(bestScore), True, "#FFFFFF")

    # Rank calculation
    i: int = 0 # A* tier (4000)
    if score < 4000: i+= 1 # A tier (3750-3999)
    if score < 3750: i+= 1 # B tier (3300-3749)
    if score < 3300: i+= 1 # C tier (2500-3299)
    if score < 2500: i+= 1 # D tier (2000-2499)
    if score < 2000: i+= 1  # E tier (1500-1999)
    if score < 1500: i+= 1  # F tier (0-1499)

    rankText = pg.font.SysFont("mono", 90, bold=True).render(colors[i][0], True, colors[i][1])

    # Draw the main menu
    # It is a function because it has to be called from multiple places
    def draw():
        screen.blit(bgImg, (-maze.uiX, -maze.uiY))
        # Function to draw the maze in such a way, that it can go off-screen
        maze.drawMenu(cellSize)
        # Moves the camera. The 'rows' is passed, so that the function can detect when to bounce off the boundary
        maze.moveMenu(rows, cellSize)
        # Draws over the maze, making it darker
        screen.blit(surface, (0, 0))
        screen.blit(title, (cellSize * rows // 2 - 64 * 3, 10))

        # Draws the end screen UI
        if endScreen:
            screen.blit(bottomText3, (rows//2 * cellSize - bottomText3.get_width() // 2, 610))
            screen.blit(buttons2, (rows//2 * cellSize - buttons2.get_width()//2 - 100, rows//2 * cellSize - buttons2.get_height()//2 + 100))

            x: int = (rows//2 * cellSize + buttons2.get_width()//2 - 100 + rows * cellSize) // 2 - scoreText.get_width()//2
            y: int = rows//2 * cellSize - buttons2.get_height()//2 + 116
            screen.blit(scoreText, (x,y + 20))
            x = (rows//2 * cellSize + buttons2.get_width()//2 - 100 + rows * cellSize) // 2 - rankText.get_width()//2
            screen.blit(rankText, (x, y + 105))
            x = (rows//2 * cellSize + buttons2.get_width()//2 - 100 + rows * cellSize) // 2 - bestScoreText .get_width()//2
            screen.blit(bestScoreText, (x, y + 225))

        # Draws the starting screen UI
        else:
            screen.blit(buttons1, (10, 300))
            # Draws the border around the selected button
            pg.draw.rect(screen, "#00FF00", (4, 304 + 128 * selectedButton, 270, 128), 5, 1)

            # Displays the side text when the 'Play' button is selected
            if selectedButton == 0:
                screen.blit(playTitle, (rows // 4 * 3 * cellSize - playTitle.get_width() // 2, 300))
                if gameBeaten:
                    screen.blit(bottomText4, (rows // 2 * cellSize - bottomText4.get_width() // 2, 610))
                else:
                    screen.blit(bottomText1, (rows // 2 * cellSize - bottomText1.get_width() // 2, 610))
                # Draws all text automatically from the list
                for y, text in enumerate(playTexts):
                    playText = smallFont.render(text, True, "#FFFFFF")
                    screen.blit(playText, (rows // 4 * 3 * cellSize - playText.get_width() // 2, 340 + y * 15))

            # Displays the side text when the 'Stgs' button is selected
            else:
                screen.blit(stgsTitle, (rows // 4 * 3 * cellSize - playTitle.get_width() // 2, 300))
                if gameBeaten:
                    screen.blit(bottomText4, (rows // 2 * cellSize - bottomText4.get_width() // 2, 610))
                else:
                    screen.blit(bottomText2, (rows // 2 * cellSize - bottomText2.get_width() // 2, 610))
                # Draws all text automatically from the list
                for y, text in enumerate(stgsTexts):
                    stgsText = smallFont.render(text, True, "#FFFFFF")
                    screen.blit(stgsText, (rows // 4 * 3 * cellSize - stgsText.get_width() // 2, 340 + y * 15))
                screen.blit(sprites[selectedSprite], (rows // 4 * 3 * cellSize - 40, 400))
                screen.blit(arrows, (rows // 4 * 3 * cellSize - 120, 400))
            pg.draw.line(screen, "#FFFFFF", (320, 300), (320, 550), 1)

    # Main loop that runs the menu
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                # Return True -> player quit -> exit program
                return True
            # Button selection logic
            if event.type == pg.KEYDOWN and event.key in (pg.K_s, pg.K_w, pg.K_DOWN, pg.K_UP) and not endScreen:
                selectedButton += 1
                # This line does the same thing as 'selectedButton %= 2', but I think that the AND operation takes less CPU cycles
                selectedButton &= 0b1
                switchSfx.play()
            # Logic for starting the levels
            if selectedButton == 0 and event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                confirmSfx.play()
                # if the player is on the end screen, they must have pressed the play button earlier
                # so if the End Screen is active, 'selectedButton' must be equal to 0
                # this simplifies the logic for detecting the Space Bar in both the Start and End screens
                if endScreen:
                    endScreen = False
                else:
                    # An animation for starting the game
                    overlaySurface = pg.Surface((cellSize * rows, cellSize * rows), pg.SRCALPHA)
                    overlaySurface.fill("#000000")
                    pg.mixer.music.fadeout(1)
                    for i in range(64):
                        # Slowly makes the overlay more visible, creating a fade effect
                        overlaySurface.set_alpha(4*i)
                        draw()
                        screen.blit(overlaySurface, (0,0))
                        pg.display.flip()
                        clock.tick(60)
                    clock.tick(1)
                    # Returns false -> the game should continue
                    return False
            # Sprite switching logic
            if selectedButton == 1 and event.type == pg.KEYDOWN and not endScreen:
                if event.key in (pg.K_d, pg.K_RIGHT):
                    switchSfx.play()
                    selectedSprite += 1
                    selectedSprite %= 3
                if event.key in (pg.K_a, pg.K_LEFT):
                    switchSfx.play()
                    selectedSprite -= 1
                    if selectedSprite < 0:
                        selectedSprite = 2
        draw()
        pg.display.flip()
        clock.tick(60)

def playLevel(level: int) -> int:
    '''Allows for playing a level, where the parameter is an integer in the range 1-4.'''
    # Allows the function to modify the global score
    global score
    # A timer used for giving time penalty
    timer: int = 0
    # A counter for how many times the player took damage
    damageCount: int = 0

    # Default numbers for level 1
    rows: int = 11
    cellSize: int = 80
    uiOffset: int = 75
    fontSize: int = 40

    match level:
        case 1:
            if pg.display.get_desktop_sizes()[0] == (1280, 720):
                cellSize = 48
                uiOffset = 50
                fontSize = 25
        case 2:
            rows = 15
            cellSize = 64
            if pg.display.get_desktop_sizes()[0] == (1280, 720):
                cellSize = 32
                uiOffset = 50
                fontSize = 25
        # Level 3 and 4 have the same maze size
        case 3 | 4:
            rows = 19
            cellSize = 48
            if pg.display.get_desktop_sizes()[0] == (1280, 720):
                cellSize = 32
                uiOffset = 40
                fontSize = 25

    screen = pg.display.set_mode((cellSize * rows + uiOffset * 2, cellSize * rows))
    pg.display.set_caption("Amaze!")
    clock = pg.time.Clock()
    ui: UI = UI(screen, uiOffset, "sprites/items.png", fontSize)

    # A clever way to play the background music for any given level
    pg.mixer.music.load(f"music/{level}.mp3")

    bgImg = loadImage("sprites/background.jpeg", cellSize * rows, cellSize * rows)

    player: Player = Player(0, 0, cellSize, cellSize, uiOffset)
    player.loadAssets("sprites/playerSprites.png", selectedSprite, "sfx/damage.wav")

    maze: Maze = Maze(rows, rows)
    maze.loadAssets("sprites/walls.png", cellSize, "sprites/valves.png", screen, clock, uiOffset)
    maze.generateMaze(choice(maze.staticPoints))
    # Places valves in the maze
    maze.placeValves(level * 2)


    # Initialises Spikes if the level isn't the first one
    if level > 1:
        spikes = SpikeManager(min(level,3) * 2, maze)
        spikes.loadAssets("sprites/spikes.png", cellSize, uiOffset, "sfx/spike1.wav", "sfx/spike2.wav")
        spikes.place()

    # Initialises the sapphire manager
    sapphires = SapphireManager(min(2 + level, 5), maze, uiOffset)
    sapphires.loadAssets("sprites/items.png", cellSize, "sfx/coin.wav", "sfx/coin2.mp3", "sfx/score.wav")
    # Places the sapphires such that no sapphire is very close to the player
    sapphires.place(player)

    # Initialises potions for levels 3 and 4
    if level > 2:
        potions = PotionManager(maze, uiOffset)
        potions.loadAssets("sprites/items.png", cellSize, "sfx/potion.wav")

    # Initialises the bandaid if the level isn't the first one
    if level > 1:
        # On initialisation, a bandaid is linked to a specific player (multiplayer would need 2 bandaid instances)
        bandaid = Bandaid(uiOffset, player, rows * cellSize, rows * cellSize)
        bandaid.loadAssets("sprites/items.png", int(cellSize * 1.5), "sfx/bandaid.wav")

    # Setup level 4
    if level == 4:
        # Width of the screen
        l: int = cellSize * rows
        # The surface that will be drawn on the player
        playerLight = pg.Surface((l, l), pg.SRCALPHA)
        # The surface consists of 3 separate circles
        pg.draw.circle(playerLight, (255, 213, 120, 55), (l/2, l/2), cellSize * 6)
        pg.draw.circle(playerLight, (255, 213, 120, 80), (l/2, l/2), cellSize * 3)
        pg.draw.circle(playerLight, (255, 213, 120, 110), (l / 2, l / 2), cellSize * 2)
        # Initialises a surface containing a smaller light
        # This light is used for sapphires and the bandage
        smallLight = pg.Surface((l,l), pg.SRCALPHA)
        pg.draw.circle(smallLight, (255, 213, 120, 25), (l / 2, l / 2), cellSize * 1.5)
        # The surface responsible for the darkness effect
        overlaySurface = pg.Surface((l, l), pg.SRCALPHA)
        overlaySurface.fill((0,0,0,240))

    # maze.printMaze()
    ui.draw(0, 3, level)
    player.draw(screen)
    screen.blit(bgImg, (uiOffset, 0))
    if level == 4:
        screen.blit(overlaySurface, (uiOffset, 0))
    pg.display.flip()
    clock.tick(1.3)

    # Level load animation
    for i in range(rows - 1, -1, -1):
        screen.blit(bgImg, (uiOffset, 0))
        sapphires.draw(screen, i)
        # Only draws the player once the starting square is visible
        if i == 0: player.draw(screen)
        if level > 1:
            spikes.draw(screen, i)
        maze.draw(screen, i)
        if level == 4:
            screen.blit(overlaySurface, (uiOffset, 0))
        clock.tick(maze.r)
        pg.display.flip()

    # Only starts the music after the loading animation
    pg.mixer.music.play(-1)
    startSfx.play()

    while True:
        for event in pg.event.get():
            player.move(event, maze.array)
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                # Return 2 -> Quit detected -> do not continue to other levels
                return 2

        # Runs sapphire pickup detection logic and returns True if the player cleared the entire Level
        status = sapphires.detectPickup(player, 4)
        # Runs player collision with Spikes, handles the Potion timers, increments the damage count if the player touches spikes
        damageCount = player.detectCollision(maze.array, damageCount)

        screen.blit(bgImg, (uiOffset, 0))
        sapphires.draw(screen)
        maze.draw(screen)

        if level > 1:
            spikes.flip(screen, player)

            # Manages the bandaid's internal timer, which tells it when to start falling
            bandaid.handleTimer()
            # Moves the bandaid down the screen (only if it's placed)
            bandaid.move()
            bandaid.draw(screen)
            # Checks for bandaid pickup
            bandaid.detectCollision()

        if level > 2:
            potions.draw(screen)
            # Every frame (60 times per second) there is a 1/1500 chance of spawning a potion somewhere, and that potion has a 30% chance to give noclip
            potions.place(player, 2, 0.3, 1 / 1500)
            potions.detectPickup(player)
        if level == 4:
            screen.blit(overlaySurface, (uiOffset, 0))
        player.draw(screen)
        # Handles the darkness effect
        if level == 4:
            l: int = cellSize * rows
            # Draws the main light on top of the player
            screen.blit(playerLight, (player.x - l//2 + cellSize//2 + uiOffset, player.y - l//2 + cellSize//2))
            # Draws a small light on top of all sapphires
            for sapphire in sapphires.sapphires:
                screen.blit(smallLight, (sapphire[1] * cellSize - l//2 + cellSize//2 + uiOffset, sapphire[0] * cellSize - l//2 + cellSize//2))
            # Draws a small light on the bandaid, assuming that it is falling down
            if bandaid.placed:
                screen.blit(smallLight, (bandaid.x - l//2 + cellSize * 0.75 + uiOffset, bandaid.y - l//2 + cellSize * 0.75))
            # Draws a small light on the gem, assuming the player collected all sapphires
            if sapphires.tempCount == 0:
                screen.blit(smallLight, (maze.mazeCorners[sapphires.i][1] * cellSize - l//2 + cellSize//2 + uiOffset, maze.mazeCorners[sapphires.i][0] * cellSize - l//2 + cellSize//2))

        ui.draw(sapphires.score, player.health, level, (player.sprintTimer, player.noclipTimer))

        # Death logic
        if player.health == 0:
            pg.display.flip()
            deathSfx.play()
            pg.mixer.music.fadeout(3)
            clock.tick(0.4)
            maze.deathAnim()
            clock.tick(1)
            # Return 1 -> player died -> return to menu
            return 1

        # Level completion logic
        if status:
            maxTime: int = 0
            match level:
                case 1: maxTime = 60 * 60 # 1 minute
                case 2 | 3: maxTime = 120 * 60 # 2 minutes
                case 4: maxTime = 140 * 60 # 2 minutes, 20 seconds
            # Implementation for time penalty and damage penalty
            score -= min(max(0, timer - maxTime) // 300 * 30 + damageCount * 50, 1000)

            # print(f"{score} ({timer}/{maxTime}) [{timer//3600}:{(timer//60) % 60} / {maxTime//3600}:{(maxTime//60) % 60}]")
            pg.mixer.music.fadeout(2)
            clearSfx.play()
            maze.clearAnim()
            clock.tick(0.7)
            # Return 0 -> level cleared -> play next level
            return 0

        timer += 1
        pg.display.flip()
        clock.tick(60)

# Function returns True -> exit
if drawMenu(): exit()
# Main game function
while True:
    pg.quit()
    pg.init()
    # Score is reset for every run
    score = 4000

    # Loops through all 4 levels
    for _ in range(1, 5):
        status: int = playLevel(_)
        # Player died; this needs to always lead to the starting screen, regardless of whether the player has beaten the game earlier
        if status == 1:
            pg.quit()
            pg.init()
            if drawMenu(): exit()
            break
        # Player exit
        if status == 2:
            exit()
        # If status == 0, none of the IF conditions are met, so the game proceeds to the next level
        pg.quit()
        pg.init()
    # If the player never died
    else:
        gameBeaten = True
        bestScore = max(bestScore, score)
        # Needs to always lead to the end screen
        if drawMenu(True): exit()
