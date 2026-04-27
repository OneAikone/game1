import random
from random import choice, random
from classes import Player, Maze, SapphireManager, UI, SpikeManager
import pygame as pg
from copy import deepcopy

pg.mixer.init()
pg.init()

clearSfx = pg.mixer.Sound("sfx/clear.wav")
deathSfx = pg.mixer.Sound("sfx/death.ogg")
startSfx = pg.mixer.Sound("sfx/start.wav")

# Cleaner way to load images
def loadImage(source: str, width: int, height: int) -> pg.Surface:
    return pg.transform.scale(pg.image.load(source), (width, height))

def levelEasy() -> bool:
    rows: int = 11
    cellSize: int = 80
    uiOffset: int = 75
    fontSize: int = 40
    if pg.display.get_desktop_sizes()[0] == (1280, 720):
        cellSize = 48
        uiOffset = 50
        fontSize = 25
    elif pg.display.get_desktop_sizes()[0] != (1920, 1080):
        d: int = min(pg.display.get_desktop_sizes()[0])
        print(pg.display.get_desktop_sizes()[0])
        cellSize: int = int(d * 0.9) // rows
        cellSize -= cellSize % 16  # in pixels
        print(cellSize)


    screen = pg.display.set_mode((cellSize * rows + uiOffset * 2, cellSize * rows))
    pg.display.set_caption("Amaze!")
    clock = pg.time.Clock()
    ui: UI = UI(screen, 1, uiOffset, "sprites/items.png", fontSize)

    bgImg = loadImage("sprites/background.jpeg", cellSize * rows, cellSize * rows)

    playerEasy: Player = Player(0, 0, cellSize, cellSize, uiOffset)
    playerEasy.loadAssets("sprites/playerSprites.png", "sfx/damage.wav")

    mazeEasy: Maze = Maze(rows, rows)
    mazeEasy.loadAssets("sprites/walls.png", cellSize, "sprites/valves.png", screen, clock, uiOffset)
    mazeEasy.generateMaze(choice(mazeEasy.staticPoints))
    mazeEasy.placeValves(2)

    sapphiresEasy = SapphireManager(3, mazeEasy, uiOffset)
    sapphiresEasy.loadAssets("sprites/items.png", cellSize, "sfx/coin.wav", "sfx/score.wav")
    sapphiresEasy.place(playerEasy)

    mazeEasy.printMaze()
    ui.draw(0, 3)
    playerEasy.draw(screen)
    mazeEasy.loadAnim(bgImg, cellSize)
    for i in range(rows - 1, -1, -1):
        sapphiresEasy.draw(screen, i)
        if i == 0: playerEasy.draw(screen)
        mazeEasy.draw(screen, i)
        clock.tick(mazeEasy.r)
        pg.display.flip()

    startSfx.play()

    while True:
        for event in pg.event.get():
            playerEasy.move(event, mazeEasy.array)
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                return True

        status = sapphiresEasy.detectPickup(playerEasy, 4)
        playerEasy.checkCollision(mazeEasy.array)

        screen.blit(bgImg, (uiOffset, 0))
        sapphiresEasy.draw(screen)
        playerEasy.draw(screen)
        mazeEasy.draw(screen)

        ui.draw(sapphiresEasy.score, playerEasy.health)

        if playerEasy.health == 0:
            pg.display.flip()
            clock.tick(2)
            deathSfx.play()
            clock.tick(1)
            mazeEasy.deathAnim()
            clock.tick(0.5)
            return False

        if status:
            clearSfx.play() 
            pg.display.flip()
            clock.tick(1)
            mazeEasy.clearAnim()
            clock.tick(1)
            return False

        pg.display.flip()
        clock.tick(60)

def levelMedium() -> bool:
    rows: int = 15
    cellSize: int = 64
    uiOffset: int = 75
    fontSize: int = 40
    if pg.display.get_desktop_sizes()[0] == (1280, 720):
        cellSize = 32
        uiOffset = 50
        fontSize = 25
    elif pg.display.get_desktop_sizes()[0] != (1920, 1080):
        d: int = min(pg.display.get_desktop_sizes()[0])
        print(pg.display.get_desktop_sizes()[0])
        cellSize: int = int(d * 0.9) // rows
        cellSize -= cellSize % 16  # in pixels
        print(cellSize)

    screen = pg.display.set_mode((cellSize * rows + uiOffset * 2, cellSize * rows))
    pg.display.set_caption("Amaze!")
    clock = pg.time.Clock()
    ui: UI = UI(screen, 2, uiOffset, "sprites/items.png", fontSize)

    bgImg = loadImage("sprites/background.jpeg", cellSize * rows, cellSize * rows)

    playerMedium: Player = Player(0, 0, cellSize, cellSize, uiOffset)
    playerMedium.loadAssets("sprites/playerSprites.png", "sfx/damage.wav")

    mazeMedium: Maze = Maze(rows, rows)
    mazeMedium.loadAssets("sprites/walls.png", cellSize, "sprites/valves.png", screen, clock, uiOffset)
    mazeMedium.generateMaze(choice(mazeMedium.staticPoints))
    mazeMedium.placeValves(4)

    sapphiresMedium = SapphireManager(4, mazeMedium, uiOffset)

    spikesMedium = SpikeManager(4, mazeMedium)
    spikesMedium.loadAssets("sprites/spikes.png", cellSize, uiOffset)
    spikesMedium.place()

    sapphiresMedium.loadAssets("sprites/items.png", cellSize, "sfx/coin.wav", "sfx/score.wav")
    sapphiresMedium.place(playerMedium)

    mazeMedium.printMaze()
    ui.draw(0, 3)
    playerMedium.draw(screen)
    mazeMedium.loadAnim(bgImg, cellSize)
    for i in range(rows - 1, -1, -1):
        sapphiresMedium.draw(screen, i)
        if i == 0: playerMedium.draw(screen)
        spikesMedium.draw(screen, i)
        mazeMedium.draw(screen, i)
        clock.tick(mazeMedium.r)
        pg.display.flip()

    startSfx.play()

    while True:
        for event in pg.event.get():
            playerMedium.move(event, mazeMedium.array)
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                return True

        status = sapphiresMedium.detectPickup(playerMedium, 1)
        playerMedium.checkCollision(mazeMedium.array)

        screen.blit(bgImg, (uiOffset, 0))
        sapphiresMedium.draw(screen)
        playerMedium.draw(screen)
        spikesMedium.flip(screen)
        spikesMedium.draw(screen)
        mazeMedium.draw(screen)

        ui.draw(sapphiresMedium.score, playerMedium.health)

        if playerMedium.health == 0:
            pg.display.flip()
            clock.tick(2)
            deathSfx.play()
            clock.tick(1)
            mazeMedium.deathAnim()
            clock.tick(0.5)
            return False

        if status:
            clearSfx.play()
            mazeMedium.clearAnim()
            clock.tick(1)
            return False

        pg.display.flip()
        clock.tick(60)

def levelHard() -> bool:
    rows: int = 21
    cellSize: int = 48
    uiOffset: int = 75
    fontSize: int = 40
    if pg.display.get_desktop_sizes()[0] == (1280, 720):
        cellSize = 32
        uiOffset = 50
        fontSize = 25
    elif pg.display.get_desktop_sizes()[0] != (1920, 1080):
        d: int = min(pg.display.get_desktop_sizes()[0])
        print(pg.display.get_desktop_sizes()[0])
        cellSize: int = int(d * 0.9) // rows
        cellSize -= cellSize % 16  # in pixels
        print(cellSize)

    screen = pg.display.set_mode((cellSize * rows + uiOffset * 2, cellSize * rows))
    pg.display.set_caption("Amaze!")
    clock = pg.time.Clock()
    ui: UI = UI(screen, 3, uiOffset, "sprites/items.png", fontSize)

    bgImg = loadImage("sprites/background.jpeg", cellSize * rows, cellSize * rows)

    playerHard: Player = Player(0, 0, cellSize, cellSize, uiOffset)
    playerHard.loadAssets("sprites/playerSprites.png", "sfx/damage.wav")

    mazeHard: Maze = Maze(rows, rows)
    mazeHard.loadAssets("sprites/walls.png", cellSize, "sprites/valves.png", screen, clock, uiOffset)
    mazeHard.generateMaze(choice(mazeHard.staticPoints))
    mazeHard.placeValves(7)

    sapphiresHard = SapphireManager(5, mazeHard, uiOffset)

    spikesHard = SpikeManager(7, mazeHard)
    spikesHard.loadAssets("sprites/spikes.png", cellSize, uiOffset)
    spikesHard.place()

    sapphiresHard.loadAssets("sprites/items.png", cellSize, "sfx/coin.wav", "sfx/score.wav")
    sapphiresHard.place(playerHard)

    mazeHard.printMaze()
    ui.draw(0, 3)
    playerHard.draw(screen)
    mazeHard.loadAnim(bgImg, cellSize)
    for i in range(rows - 1, -1, -1):
        sapphiresHard.draw(screen, i)
        if i == 0: playerHard.draw(screen)
        spikesHard.draw(screen, i)
        mazeHard.draw(screen, i)
        clock.tick(mazeHard.r)
        pg.display.flip()

    startSfx.play()

    while True:
        for event in pg.event.get():
            playerHard.move(event, mazeHard.array)
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                return True

        status = sapphiresHard.detectPickup(playerHard, 1)
        playerHard.checkCollision(mazeHard.array)

        screen.blit(bgImg, (uiOffset, 0))
        sapphiresHard.draw(screen)
        playerHard.draw(screen)
        spikesHard.flip(screen)
        spikesHard.draw(screen)
        mazeHard.draw(screen)

        ui.draw(sapphiresHard.score, playerHard.health)

        if playerHard.health == 0:
            pg.display.flip()
            clock.tick(2)
            deathSfx.play()
            clock.tick(1)
            mazeHard.deathAnim()
            clock.tick(0.5)
            return False

        if status:
            clearSfx.play()
            mazeHard.clearAnim()
            clock.tick(1)
            return False

        pg.display.flip()
        clock.tick(60)

levelEasy()
pg.quit()
pg.init()
levelMedium()
pg.quit()
pg.init()
levelHard()

