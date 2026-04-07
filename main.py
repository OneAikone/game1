import random
from random import choice, random
from classes import Player, Maze, SapphireManager
import pygame as pg

pg.init()
pg.mixer.init()

# Must be odd numbers greater than 1
rows: int = 63
columns: int = 63

cellSize: int = 16  # in pixels
dimensions: tuple[int, int] = (cellSize * columns, cellSize * rows)

level: int = 1

# Cleaner way to load images
def loadImage(source: str, width: int = cellSize, height: int = cellSize) -> pg.Surface:
    return pg.transform.scale(pg.image.load(source), (width, height))

screen = pg.display.set_mode(dimensions)
pg.display.set_caption("Amaze!")
clock = pg.time.Clock()

bgImg = loadImage("sprites/background.jpeg", dimensions[0], dimensions[1])
clearSfx = pg.mixer.Sound("sfx/clear.ogg")

player: Player = Player(0, 0, cellSize, cellSize)
player.loadSprites("sprites/playerSprites.png")

maze: Maze = Maze(columns, rows, screen, clock)
maze.loadSprites("sprites/walls.png", cellSize, "sprites/valves.png")
maze.generateMaze(choice(maze.staticPoints), 0, True)
maze.placeValves(5)

sapphires = SapphireManager(3 + (rows * columns > 169), maze)
sapphires.loadAssets("sprites/items.png", cellSize, "sfx/coin.wav", "sfx/refill.wav")
sapphires.place(player)

pg.mixer.Sound("sfx/refill.wav").play()
maze.printMaze()

run: bool = True
status: bool = False

while run:
    for event in pg.event.get():
        player.move(event, maze.array)
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            run = False
        # if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
        #     maze.shiftMaze(20)
    status = sapphires.detectPickup(player, 4)
    if random() < 0.0001: maze.flipValves(1)
    if status:
        clearSfx.play()
        level += 1

    screen.blit(bgImg, (0, 0))
    sapphires.draw(screen)
    maze.draw()
    player.draw(screen)

    pg.display.flip()
    clock.tick(60)
pg.quit()
