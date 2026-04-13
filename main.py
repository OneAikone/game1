import random
from random import choice, random
from classes import Player, Maze, SapphireManager, UI
import pygame as pg

pg.init()
pg.mixer.init()

# Must be odd numbers greater than 1
rows: int = 13
columns: int = 13

d: int = min(pg.display.get_desktop_sizes()[0])

cellSize: int = (d-150) // max(rows, columns)
cellSize -= cellSize % 16  # in pixels
print(cellSize)
uiOffset: int = 100

dimensions: tuple[int, int] = (cellSize * columns + uiOffset * 2, cellSize * rows)

level: int = 3

# Cleaner way to load images
def loadImage(source: str, width: int = cellSize, height: int = cellSize) -> pg.Surface:
    return pg.transform.scale(pg.image.load(source), (width, height))

screen = pg.display.set_mode(dimensions)
pg.display.set_caption("Amaze!")
clock = pg.time.Clock()
ui = UI(screen, level, uiOffset, "sprites/items.png")

bgImg = loadImage("sprites/background.jpeg", dimensions[0] - 2*uiOffset, dimensions[1])
clearSfx = pg.mixer.Sound("sfx/clear.ogg")

player: Player = Player(0, 0, cellSize, cellSize, uiOffset)
player.loadSprites("sprites/playerSprites.png")

maze: Maze = Maze(columns, rows, screen, clock, uiOffset)
maze.loadSprites("sprites/walls.png", cellSize, "sprites/valves.png")
maze.generateMaze(choice(maze.staticPoints), 0, False)
maze.placeValves(3)

sapphires = SapphireManager(3 + (rows * columns > 169), maze, uiOffset)
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
    # if random() < 0.0001: maze.flipValves(1)
    if status:
        clearSfx.play()
        level += 1

    ui.draw(sapphires.score)
    screen.blit(bgImg, (uiOffset, 0))
    sapphires.draw(screen)
    maze.draw()
    player.draw(screen)

    pg.display.flip()
    clock.tick(60)
pg.quit()
