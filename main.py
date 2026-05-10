from random import choice
from classes import *
import pygame as pg

pg.mixer.init()
pg.init()

clearSfx = pg.mixer.Sound("sfx/clear.wav")
deathSfx = pg.mixer.Sound("sfx/death.mp3")
startSfx = pg.mixer.Sound("sfx/start.wav")
startSfx.set_volume(0.3)
switchSfx = pg.mixer.Sound("sfx/switch.mp3")
confirmSfx = pg.mixer.Sound("sfx/confirm.wav")
confirmSfx.set_volume(0.3)

selectedSprite: int = 0
gameBeaten: bool = False
score: int = 4000
bestScore: int = 0

cellSize: int = 80
rows: int = 8

def drawMenu(endScreen: bool = False) -> bool:
    global selectedSprite
    selectedButton: int = 0

    screen = pg.display.set_mode((cellSize * rows, cellSize * rows))
    surface = pg.Surface((cellSize * rows, cellSize * rows), pg.SRCALPHA)
    surface.fill((0, 0, 0, 128))

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
    pg.mixer.music.play(-1)
    maze: Maze = Maze(21, 21)
    maze.loadAssets("sprites/walls.png", cellSize, "sprites/valves.png", screen, clock, 0)
    maze.generateMaze(choice(maze.staticPoints))
    maze.generateWallMap()

    bgImg = loadImage("sprites/background.jpeg", cellSize * maze.r, cellSize * maze.c)
    title = loadImage("sprites/title.png", 64 * 8, 32 * 8)
    buttons1 = loadImage("sprites/buttons.png", 32*8, 32*8)
    buttons2 = loadImage("sprites/buttons2.png", 48 * 7, 48 * 7)
    arrows = loadImage("sprites/arrows.png", 240,80)

    font = pg.font.SysFont("mono", 25)
    smallFont = pg.font.SysFont("mono", 15)
    bottomText1 = font.render("Press Space to Play.", True, "#FFFFFF")
    bottomText2 = font.render("Press A / D to switch Sprites.", True, "#FFFFFF")
    bottomText3 = font.render("Press Space to return to Menu.", True, "#FFFFFF")
    playTitle = font.render("-- Play the Game --", True, "#FFFFFF")
    playTexts: list[str] = ["In order to win, collect sapphires", "and gems. Gems give you points.", "", "You can only collect a gem after", "collecting all sapphires.", "", "You need 4 points to advance", "to the next Level.", "", "Potions can give the player", "increased speed and wall-clipping.", "", "Good Luck! :)"]
    stgsTitle = font.render("- Player Settings -", True, "#FFFFFF")
    stgsTexts: list[str] = ["Customize the appearance of", "the player sprite.", ""]

    def draw():
        screen.blit(bgImg, (-maze.uiX, -maze.uiY))
        # screen.fill("#FFFFFF")
        maze.drawMenu(cellSize)
        maze.moveMenu(rows, cellSize)
        screen.blit(surface, (0, 0))
        if endScreen:
            screen.blit(bottomText3, (rows//2 * cellSize - bottomText3.get_width() // 2, 610))
            screen.blit(buttons2, (rows//2 * cellSize - buttons2.get_width()//2 - 100, rows//2 * cellSize - buttons2.get_height()//2 + 100))
        else:
            screen.blit(title, (cellSize * rows // 2 - 64 * 3, 10))
            screen.blit(buttons1, (10, 300))
            pg.draw.rect(screen, "#00FF00", (4, 304 + 128 * selectedButton, 270, 128), 5, 1)

            if selectedButton == 0:
                screen.blit(bottomText1, (rows // 2 * cellSize - bottomText1.get_width() // 2, 610))
                screen.blit(playTitle, (rows // 4 * 3 * cellSize - playTitle.get_width() // 2, 300))
                for y, text in enumerate(playTexts):
                    playText = smallFont.render(text, True, "#FFFFFF")
                    screen.blit(playText, (rows // 4 * 3 * cellSize - playText.get_width() // 2, 340 + y * 15))
            else:
                screen.blit(bottomText2, (rows // 2 * cellSize - bottomText2.get_width() // 2, 610))
                screen.blit(stgsTitle, (rows // 4 * 3 * cellSize - playTitle.get_width() // 2, 300))
                for y, text in enumerate(stgsTexts):
                    stgsText = smallFont.render(text, True, "#FFFFFF")
                    screen.blit(stgsText, (rows // 4 * 3 * cellSize - stgsText.get_width() // 2, 340 + y * 15))
                screen.blit(sprites[selectedSprite], (rows // 4 * 3 * cellSize - 40, 400))
                screen.blit(arrows, (rows // 4 * 3 * cellSize - 120, 400))
            pg.draw.line(screen, "#FFFFFF", (320, 300), (320, 550), 1)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                return True
            if event.type == pg.KEYDOWN and event.key in (pg.K_s, pg.K_w, pg.K_DOWN, pg.K_UP):
                selectedButton += 1
                selectedButton &= 0b1
                switchSfx.play()
            if selectedButton == 0 and event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                confirmSfx.play()
                if endScreen:
                    endScreen = False
                else:
                    overlaySurface = pg.Surface((cellSize * rows, cellSize * rows), pg.SRCALPHA)
                    overlaySurface.fill("#000000")
                    pg.mixer.music.fadeout(1)
                    for i in range(64):
                        overlaySurface.set_alpha(4*i)
                        draw()
                        screen.blit(overlaySurface, (0,0))
                        pg.display.flip()
                        clock.tick(60)
                    clock.tick(1)
                    return False
            if selectedButton == 1 and event.type == pg.KEYDOWN:
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
    global score
    timer: int = 0
    damageCount: int = 0

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
        case 3 | 4:
            rows = 19
            cellSize = 48
            if pg.display.get_desktop_sizes()[0] == (1280, 720):
                cellSize = 32
                uiOffset = 40
                fontSize = 25
    if pg.display.get_desktop_sizes()[0] not in ((1280, 720), (1920, 1080)):
        d: int = min(pg.display.get_desktop_sizes()[0])
        print(pg.display.get_desktop_sizes()[0])
        cellSize: int = int(d * 0.9) // rows
        cellSize -= cellSize % 16  # in pixels
        print(cellSize)

    screen = pg.display.set_mode((cellSize * rows + uiOffset * 2, cellSize * rows))
    pg.display.set_caption("Amaze!")
    clock = pg.time.Clock()
    ui: UI = UI(screen, level, uiOffset, "sprites/items.png", fontSize)
    pg.mixer.music.load(f"music/{level}.mp3")

    bgImg = loadImage("sprites/background.jpeg", cellSize * rows, cellSize * rows)

    player: Player = Player(0, 0, cellSize, cellSize, uiOffset)
    player.loadAssets("sprites/playerSprites.png", selectedSprite, "sfx/damage.wav")

    maze: Maze = Maze(rows, rows)
    maze.loadAssets("sprites/walls.png", cellSize, "sprites/valves.png", screen, clock, uiOffset)
    maze.generateMaze(choice(maze.staticPoints))
    maze.placeValves(level * 2)

    sapphires = SapphireManager(2 + level, maze, uiOffset)

    if level > 1:
        spikes = SpikeManager(min(level,3) * 2, maze)
        spikes.loadAssets("sprites/spikes.png", cellSize, uiOffset, "sfx/spike1.wav", "sfx/spike2.wav")
        spikes.place()

    sapphires.loadAssets("sprites/items.png", cellSize, "sfx/coin.wav", "sfx/coin2.mp3", "sfx/score.wav")
    sapphires.place(player)

    if level > 2:
        potions = PotionManager(maze, uiOffset)
        potions.loadAssets("sprites/items.png", cellSize, "sfx/potion.wav")

    if level > 1:
        bandaid = Bandaid(uiOffset, player, rows * cellSize, rows * cellSize)
        bandaid.loadAssets("sprites/items.png", int(cellSize * 1.5), "sfx/bandaid.wav")

    if level == 4:
        l: int = cellSize * rows
        playerLight = pg.Surface((l, l), pg.SRCALPHA)
        pg.draw.circle(playerLight, (255, 213, 120, 55), (l/2, l/2), cellSize * 6)
        pg.draw.circle(playerLight, (255, 213, 120, 80), (l/2, l/2), cellSize * 3)
        pg.draw.circle(playerLight, (255, 213, 120, 110), (l / 2, l / 2), cellSize * 2)
        smallLight = pg.Surface((l,l), pg.SRCALPHA)
        pg.draw.circle(smallLight, (255, 213, 120, 25), (l / 2, l / 2), cellSize * 1.5)
        overlaySurface = pg.Surface((l, l), pg.SRCALPHA)
        overlaySurface.fill((0,0,0,240))

    # maze.printMaze()
    ui.draw(0, 3)
    player.draw(screen)
    screen.blit(bgImg, (uiOffset, 0))
    if level == 4:
        screen.blit(overlaySurface, (uiOffset, 0))
    pg.display.flip()
    clock.tick(1.3)

    # Load animation
    for i in range(rows - 1, -1, -1):
        screen.blit(bgImg, (uiOffset, 0))
        sapphires.draw(screen, i)
        if i == 0: player.draw(screen)
        if level > 1:
            spikes.draw(screen, i)
        maze.draw(screen, i)
        if level == 4:
            screen.blit(overlaySurface, (uiOffset, 0))
        clock.tick(maze.r)
        pg.display.flip()
    pg.mixer.music.play(-1)
    startSfx.play()
    while True:
        for event in pg.event.get():
            player.move(event, maze.array)
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                return 2

        status = sapphires.detectPickup(player, 4)
        damageCount = player.detectCollision(maze.array, damageCount)

        screen.blit(bgImg, (uiOffset, 0))

        sapphires.draw(screen)

        maze.draw(screen)

        if level > 1:
            spikes.flip(screen, player)
            spikes.draw(screen)

            bandaid.handleTimer()
            bandaid.move()
            bandaid.draw(screen)
            bandaid.detectCollision()

        if level > 2:
            potions.draw(screen)
            potions.place(player, 2, 0.3, 1 / 1500)
            potions.detectPickup(player)

        if level == 4:
            screen.blit(overlaySurface, (uiOffset, 0))
        player.draw(screen)
        if level == 4:
            l: int = cellSize * rows
            screen.blit(playerLight, (player.x - l//2 + cellSize//2 + uiOffset, player.y - l//2 + cellSize//2))
            for sapphire in sapphires.sapphires:
                screen.blit(smallLight, (sapphire[1] * cellSize - l//2 + cellSize//2 + uiOffset, sapphire[0] * cellSize - l//2 + cellSize//2))
            if bandaid.placed:
                screen.blit(smallLight, (bandaid.x - l//2 + cellSize * 0.75 + uiOffset, bandaid.y - l//2 + cellSize * 0.75))
            if sapphires.tempCount == 0:
                screen.blit(smallLight, (maze.mazeCorners[sapphires.i][1] * cellSize - l//2 + cellSize//2 + uiOffset, maze.mazeCorners[sapphires.i][0] * cellSize - l//2 + cellSize//2))


        ui.draw(sapphires.score, player.health, (player.sprintTimer, player.noclipTimer))

        if player.health == 0:
            pg.display.flip()
            deathSfx.play()
            pg.mixer.music.fadeout(3)
            clock.tick(0.4)
            maze.deathAnim()
            clock.tick(1)
            return 1

        if status:
            score -= min(max(0, timer - min(2, level) * 60 * 60) // 300 * 30 + damageCount * 50, 1000)
            print(score)
            pg.mixer.music.fadeout(2)
            clearSfx.play()
            maze.clearAnim()
            clock.tick(0.7)
            return 0

        pg.display.flip()
        clock.tick(60)
# Cleaner way to load images
def loadImage(source: str, width: int, height: int) -> pg.Surface:
    return pg.transform.scale(pg.image.load(source), (width, height))

while True:
    if drawMenu(): exit()
    pg.quit()
    pg.init()
    score = 4000
    for _ in range(1, 5):
        status: int = playLevel(_)
        if status == 1:
            break
        if status == 2:
            exit()
        pg.quit()
        pg.init()