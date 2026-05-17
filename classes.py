import pygame as pg
from random import shuffle, random, choice

# Function used for the Spike Manager
# The distance to a spike is used to determine how loud it should sound
def distance(x, y) -> float:
    return pow(x * x + y * y, 0.5)

# Cleaner way to load images
def loadImage(source: str, width: int, height: int) -> pg.Surface:
    return pg.transform.scale(pg.image.load(source), (width, height))

class Player:
    '''This class implements the Player in a maze.'''
    def __init__(self, x: int, y: int, w: int, h: int, uiOffset: int = 0) -> None:
        '''Initialise the Player by providing (x,y) coordinates, the width and height of the sprite, and the width of the Side Bar UI.'''
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h
        # Max health is 3
        self.health: int = 3
        # Boolean values representing active potion effects
        self.noclip: bool = False
        self.sprint: bool = False
        # Timers representing how long until an effect runs out
        self.noclipTimer: int = 0
        self.sprintTimer: int = 0
        # The offset caused by the sidebar on the left
        self.uiOffset: int = uiOffset

        # Boolean value used for making sure the player takes damage only once per spike
        self.hurt = False

        # Values used for sprite selection, most significant to least significant
        # The color (normal, orange, purple)
        self.mode: int = 0
        # The direction (right, left, up, down)
        self.dir: int = 0

        self.sprites: list[pg.Surface] = []
        self.damageSfx = None

    def loadAssets(self, spriteSource: str, spriteNum: int, sfxSource: str) -> None:
        '''Load all Player assets: the Sprites, and the Sfx for taking damage.'''
        _ = pg.transform.scale(pg.image.load(spriteSource), (self.w * 15, self.h * 3))
        for y in range(0, self.h * 3, self.h):
            for x in range(0, self.w * 5, self.w):
                self.sprites.append(_.subsurface((x + spriteNum * self.w * 5, y, self.w, self.h)))
        self.damageSfx = pg.mixer.Sound(sfxSource)
        self.damageSfx.set_volume(0.5)

    def draw(self, screen):
        '''Draw the Player to the screen.'''
        screen.blit(self.sprites[self.dir + self.mode], (self.x + self.uiOffset, self.y))

    def move(self, event, mazeArray: list[list]) -> None:
        '''Move the Player around the Maze, while checking for valid moves.'''
        # The coordinates on the grid
        x: int = self.x // self.w
        y: int = self.y // self.h
        # Speed potion implementation
        if event.type == pg.KEYDOWN or (self.sprint and event.type == pg.KEYUP):
            # The IF statements check for: Valid Key press, No Boundary crossing, No wall entry (unless noclip potion is active)
            if event.key == pg.K_a and x > 0 and (mazeArray[y][x - 1] not in (1, 6) or self.noclip):
                self.x -= self.w
                self.dir = 2
            elif event.key == pg.K_d and x < len(mazeArray[0]) - 1 and (mazeArray[y][x + 1] not in (1, 6) or self.noclip):
                self.x += self.w
                self.dir = 1
            elif event.key == pg.K_w and y > 0 and (mazeArray[y - 1][x] not in (1, 6) or self.noclip):
                self.y -= self.h
                self.dir = 3
            elif event.key == pg.K_s and y < len(mazeArray) - 1 and (mazeArray[y + 1][x] not in (1, 6) or self.noclip):
                self.y += self.h
                self.dir = 4

    def detectCollision(self, mazeArray: list[list], damageCount: int) -> int:
        '''Detect Player collision with Spikes.'''
        x: int = self.x // self.w
        y: int = self.y // self.h

        # The Player can only take damage again after leaving the spikes
        if mazeArray[y][x] == 8 and self.hurt is False and self.noclip is False:
            self.damageSfx.play()
            # Increments a counter, which then decreases the overall Score
            damageCount += 1
            # Guarantees no negative health
            self.health = max(0, self.health - 1)
            self.hurt = True
        elif mazeArray[y][x] != 8 and self.hurt is True:
            self.hurt = False

        # Potion Timers
        if self.sprintTimer > 0:
            self.sprintTimer -= 1
        if self.noclipTimer > 0:
            self.noclipTimer -= 1

        # Logic for potions ending
        if self.sprintTimer == 0 and self.sprint:
            self.sprint = False
            self.mode = 0
            if self.noclip:
                self.mode = 10
        if self.noclipTimer == 0 and self.noclip:
            self.noclip = False
            self.mode = 0
            if self.sprint:
                self.mode = 5
        return damageCount

    def applyPotion(self, potionType: int) -> None:
        '''Applies a potion effect (0 = sprint, 1 = noclip).'''
        if potionType == 0:
            self.sprintTimer = 60 * 15 # 15 seconds
            if not self.noclip:
                self.mode = 5
            self.sprint = True
        if potionType == 1:
            self.noclipTimer = 60 * 5 # 5 seconds
            self.mode = 10
            self.noclip = True

class Maze:
    '''This complex class implements the in-game Maze.'''
    def __init__(self, columns: int, rows: int) -> None:
        '''Initialise the Maze by proving the amount of rows and columns. In the final version of the game, they are the same number, as the map is a square.'''
        self.c: int = columns
        self.r: int = rows

        # The maze is stored as a 2D grid of numbers
        # 0 - nothing | 1 - wall | 3 - sapphire | 4 - gem | 5 - closed Valve | 6 - open Valve | 7 - deactivated Spikes | 8 - active Spikes | 9 - sprint potion | 10 - noclip potion
        self.array: list[list] = [[1 for _ in range(columns)] for _ in range(rows)]
        # Points that are always empty, no matter the generated maze
        self.staticPoints: list[tuple[int, int]] = [(i, j) for i in range(0, rows, 2) for j in
                                                    range(0, columns, 2)]

        self.sprites: list[pg.Surface] = []
        self.uiOffset = None
        # A map that is used for Wall rendering
        self.wallMap: list[list] = [[0 for _ in range(columns)] for _ in range(rows)]

        # The clock and screen are passed to allow for animations
        self.clock = None
        self.screen = None
        # The valves are stored in a list of tuples
        # Format: X coordinate of Valve 1, Y coordinate of Valve 1, Rotation (-90,0,90,180) of Valve 1, X coordinate of Valve 2, Y coordinate of Valve 2, Rotation of Valve 2,
        self.valves: list[tuple[int, int, int, int, int, int]] = []
        self.valveSprites: list[pg.Surface] = []
        # Width of the sprite
        self.valveW: int = 0

        # Values used for drawing the Maze in the main menu
        self.uiX: int = 0
        self.uiY: int = 0
        self.dx: int = 2
        self.dy: int = 1

        # List of corners; exists because Spikes shouldn't spawn there
        self.mazeCorners: list[tuple[int, int]] = [(rows - 1, columns - 1), (0, 0), (0, columns - 1), (rows - 1, 0)]

    def reset(self):
        '''Sets all tiles to a wall.'''
        self.array: list[list] = [[1 for _ in range(self.c)] for _ in range(self.r)]

    def loadAssets(self, wallSource: str, size: int, valveSource: str, screen, clock, uiOffset: int = 0):
        '''Loads all Maze assets: the sprites for Walls and Valves, the pixel size, the screen, the clock, and the width of the Left Side Bar in the UI.'''
        _ = pg.transform.scale(pg.image.load(wallSource), (16 * size, size))
        for x in range(0, 16 * size, size):
            self.sprites.append(_.subsurface((x, 0, size, size)))
        _ = pg.transform.scale(pg.image.load(valveSource), (2 * size, size * 19 / 16))
        self.valveSprites = [_.subsurface((0, 0, size, size * 19 / 16)), _.subsurface((size, 0, size, size * 19 / 16))]
        self.valveW = size
        self.screen = screen
        self.clock = clock
        self.uiOffset = uiOffset

    def clearAnim(self):
        '''The animation played when the player beats a level.'''
        w: float = self.sprites[0].get_width() * self.c / 11
        coords: list[tuple[int, int]] = [(i, j) for i in range(16) for j in range(11)]

        for i in range(len(coords)):
            r, c = coords[i]
            pg.draw.rect(self.screen, "#000000", (c * w + self.uiOffset, r * w, w + 1, w + 1))
            if i > 10:
                r1, c1 = coords[i - 11]
                pg.draw.rect(self.screen, "#555555", (c1 * w + self.uiOffset, r1 * w, w + 1, w + 1))
            if i > 30:
                r1, c1 = coords[i - 31]
                pg.draw.rect(self.screen, "#AAAAAA", (c1 * w + self.uiOffset, r1 * w, w + 1, w + 1))
            if i > 50:
                r1, c1 = coords[i - 51]
                pg.draw.rect(self.screen, "#FFFFFF", (c1 * w + self.uiOffset, r1 * w, w + 1, w + 1))
            self.clock.tick(60)
            pg.display.flip()

    def deathAnim(self):
        '''The animation played when the player dies.'''
        w = self.sprites[0].get_width()
        coords: list[tuple[int, int]] = [(i, j) for i in range(6) for j in range(6)]
        w = self.c * w / 6
        shuffle(coords)
        for x, y in coords:
            pg.draw.rect(self.screen, "#000000", (x * w + self.uiOffset, y * w, w + 1, w + 1))
            pg.display.flip()
            self.clock.tick(30)

    def draw(self, screen=None, up_to: int = -1):
        '''Draws the maze on the screen using 16 wall sprites'''
        w = self.sprites[0].get_width()
        if screen is None: screen = self.screen
        for row in range(self.r - 1, up_to, -1):
            for column in range(self.c):
                if self.array[row][column] == 1:
                    screen.blit(self.sprites[self.wallMap[row][column]], (column * w + self.uiOffset, row * w))

        # Handle Valve drawing, which is unfortunately messy. This is because Pygame rotates sprites in a weird way
        for valve in self.valves:
            i: int = self.array[valve[0]][valve[1]] == 6
            j: int = (i + 1) % 2

            a: float = 0.0
            if valve[2] != 0:
                a = 180 // abs(valve[2]) / 16
            b: float = 0.0
            if valve[2] in (0, 180):
                b = 2 / 16
            elif valve[2] == 90:
                b = 1 / 16

            c: float = 0.0
            if valve[5] != 0:
                c = 180 // abs(valve[5]) / 16
            d: float = 0.0
            if valve[5] in (0, 180):
                d = 2 / 16
            elif valve[5] == 90:
                d = 1 / 16

            if valve[0] > up_to:
                screen.blit(pg.transform.rotate(self.valveSprites[i], valve[2]),
                            (self.valveW * (valve[1] - a) + self.uiOffset, self.valveW * (valve[0] - b)))
            if valve[3] > up_to:
                screen.blit(pg.transform.rotate(self.valveSprites[j], valve[5]),
                            (self.valveW * (valve[4] - c) + self.uiOffset, self.valveW * (valve[3] - d)))

    def drawMenu(self, cellSize: int, screen=None):
        '''Draws the Maze in such a way that only a 8x8 region is ever visible on screen.'''
        if screen is None: screen = self.screen
        for r in range(self.uiY // cellSize, min(self.uiY // cellSize + 9, self.r)):
            for c in range(self.uiX // cellSize, min(self.uiX // cellSize + 9, self.c)):
                if self.array[r][c] == 1:
                    screen.blit(pg.transform.scale(self.sprites[self.wallMap[r][c]], (cellSize, cellSize)),
                                (c * cellSize - self.uiX, r * cellSize - self.uiY))

    def moveMenu(self, rows: int, cellSize: int):
        '''Moves the 8x8 window around, and bounces it if it hits the maze boundary.'''
        self.uiX += self.dx
        self.uiY += self.dy

        if self.uiX + rows * cellSize > self.c * cellSize or self.uiX < 0:
            self.dx = -self.dx

        if self.uiY + rows * cellSize > self.r * cellSize or self.uiY < 0:
            self.dy = -self.dy

    def getOffsets(self, coords: tuple[int, int]) -> list[tuple[int, int]]:
        '''Only called by other functions. Returns possible moves from a position.'''
        offsets: list[tuple[int, int]] = []
        if coords[0] > 0:
            offsets.append((-2, 0))
        if coords[0] < self.r - 2:
            offsets.append((2, 0))
        if coords[1] > 0:
            offsets.append((0, -2))
        if coords[1] < self.c - 2:
            offsets.append((0, 2))
        return offsets

    def generateWallMap(self):
        '''Generates the wall map, which is an array of indices that tell the draw function which wall sprite to use.'''
        self.wallMap: list[list] = [[0 for _ in range(self.c)] for _ in range(self.r)]

        for y in range(self.r):
            for x in range(self.c):
                if self.array[y][x] != 1: continue

                self.wallMap[y][x] += (x == 0 or self.array[y][x - 1] == 1)
                self.wallMap[y][x] += (x == self.c - 1 or self.array[y][x + 1] == 1) * 4

                self.wallMap[y][x] += (y == 0 or self.array[y - 1][x] == 1) * 8
                self.wallMap[y][x] += (y == self.r - 1 or self.array[y + 1][x] == 1) * 2

    def generateMaze(self, coords: tuple[int, int] = (0, 0), visualise: bool = False) -> None:
        '''Maze generation using Depth First Search Algorithm. Based on a stack, not recursion (no risk of recursion overflow for large mazes).'''
        # First, reset the Maze.
        self.reset()
        # Define the stack, and add the starting coordinates to it.
        stack: list[tuple[int, int, int, int]] = [coords + coords]
        # Loop as long as there's coordinates on the stack
        while len(stack) > 0:
            # Get the most recently appended coordinates (the basis of DFS)
            point: tuple[int, int, int, int] = stack[-1]
            stack.pop()

            # Continue if the coordinates were already visited
            if self.array[point[0]][point[1]] == 0: continue

            # Mark the coordinates as visited
            self.array[point[0]][point[1]] = 0
            self.array[point[2]][point[3]] = 0

            # Get all possible moves and shuffle them, to create random paths
            offsets: list[tuple[int, int]] = self.getOffsets((point[0], point[1]))
            shuffle(offsets)

            # Loop through all possible moves
            for offset in offsets:
                # Append the new coordinates to the stack
                stack.append((point[0] + offset[0], point[1] + offset[1], point[0] + offset[0] // 2, point[1] + offset[1] // 2))

            # maze generation visualisation, which isn't used in-game, but is fun to watch
            if visualise:
                w: int = self.sprites[0].get_width()
                self.screen.fill("#AAAAAA")
                self.generateWallMap()
                self.draw(self.screen)
                pg.draw.rect(self.screen, "#FFFFFF", (point[1] * w + self.uiOffset, point[0] * w, w, w))
                self.clock.tick(30)
                pg.display.flip()

    def getDirection(self, point: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
        '''Gets the direction from one point to the other. Useful for knowing where to place valves. Uses DFS.'''
        stack: list[tuple[int, int]] = []
        visited: list[list] = [[False for _ in range(self.c)] for _ in range(self.r)]
        visited[point[0]][point[1]] = True
        for offset in self.getOffsets(point):
            branch = (point[0] + offset[0], point[1] + offset[1])
            if self.array[(point[0] + branch[0]) // 2][(point[1] + branch[1]) // 2] not in (1, 5, 6):
                stack.append(branch)
            while len(stack) > 0:
                p: tuple[int, int] = stack[-1]
                stack.pop()
                if p == target:
                    # Return the direction if it's possible to reach
                    return (branch[0] + point[0]) // 2, (branch[1] + point[1]) // 2
                visited[p[0]][p[1]] = True
                for newOffset in self.getOffsets(p):
                    new: tuple[int, int] = (p[0] + newOffset[0], p[1] + newOffset[1])
                    if visited[new[0]][new[1]] == False and self.array[(p[0] + new[0]) // 2][
                        (p[1] + new[1]) // 2] not in (1, 5, 6):
                        stack.append(new)
        # Return 0,0 if the point isn't reachable
        return 0, 0

    def placeValves(self, pairCount: int):
        '''Places pairCount valves in the Maze. Uses a technique called Origin Shift, to place valves in such a way that never creates softlocks.'''
        points: list[tuple[int, int]] = self.staticPoints
        shuffle(points)
        placed: int = 0
        # Loop through empty squares
        for point in points:
            if placed >= pairCount: break
            new: list[tuple[int, int]] = []
            # Get all possible moves, such that they hit a wall
            for offset in self.getOffsets(point):
                v1: tuple[int, int] = (point[0] + offset[0] // 2, point[1] + offset[1] // 2)
                if self.array[v1[0]][v1[1]] == 1:
                    new.append((point[0] + offset[0], point[1] + offset[1]))
            if len(new) == 0: continue
            # Selects a random point2, such that between point2 and point, there is a wall
            point2 = choice(new)
            # The coordinates of the wall
            valve1: tuple[int, int] = ((point[0] + point2[0]) // 2, (point[1] + point2[1]) // 2)
            # The location of the second valve
            valve2 = self.getDirection(point2, point)
            # The first valve is placed where a wall originally stood, and the second is placed where there was originally an empty square.

            # Continue if, for whatever reason, it's impossible to reach - softlock prevention
            if valve2 == (0, 0): continue
            # Continue if something is already placed at the same location as the second valve
            if self.array[valve2[0]][valve2[1]] != 0: continue

            placed += 1
            self.array[valve2[0]][valve2[1]] = 6
            self.array[valve1[0]][valve1[1]] = 5
            # Random rotation
            r1: int = choice((0, 180))
            r2: int = choice((0, 180))
            if valve1[0] > 0 and self.array[valve1[0] - 1][valve1[1]] != 1:
                r1: int = choice((90, -90))
            if valve2[0] > 0 and self.array[valve2[0] - 1][valve2[1]] != 1:
                r2: int = choice((90, -90))

            self.valves.append(valve1 + (r1,) + valve2 + (r2,))
        self.generateWallMap()

    def flipValves(self, count: int):
        '''Flips count valves; causes count valves to open and count valves to close.'''
        temp = self.valves
        shuffle(temp)
        for i in range(count):
            if i >= len(self.valves): return
            valve = temp[i]
            self.array[valve[0]][valve[1]] %= 2
            self.array[valve[0]][valve[1]] += 5
            self.array[valve[3]][valve[4]] %= 2
            self.array[valve[3]][valve[4]] += 5

class SapphireManager:
    '''This class defines the manager class for sapphires in the maze.'''
    def __init__(self, count: int, maze: Maze, uiOffset: int = 0):
        '''Initialises the sapphires by providing the Max count, the Maze, and the ui offset.'''

        # Count - how many can be placed
        self.count: int = count
        # TempCount - how many are currently placed. Equal to 0 -> player picked up all sapphires
        self.tempCount: int = count

        self.score = 0
        self.maze: Maze = maze

        # List of coordinates of all the sapphires
        self.sapphires: list[tuple[int, int]] = []

        # Sapphire sprite and gem sprite
        self.sprite = None
        self.refillSprite = None
        self.uiOffset: int = uiOffset
        self.i = 0  # Which corner to spawn the new gem in
        self.maze.array[maze.mazeCorners[self.i][0]][maze.mazeCorners[self.i][1]] = 4
        self.sfx1 = None # Sapphire pickup
        self.sfx2 = None # Last sapphite pickup
        self.sfx3 = None # Gem pickup

    def loadAssets(self, spriteSource: str, size: int, sfx1: str, sfx2: str, sfx3: str):
        '''Loads all assets: the sapphire and gem sprites, the pixel size, the pickup sfx, the last pickup sfx, and the gem pickup sfx.'''
        image = pg.transform.scale(pg.image.load(spriteSource), (6 * size, size))
        self.sprite = image.subsurface((size * 3, 0, size, size))
        self.refillSprite = image.subsurface((size * 4, 0, size, size))
        self.sfx1 = pg.mixer.Sound(sfx1)
        self.sfx1.set_volume(0.5)
        self.sfx2 = pg.mixer.Sound(sfx2)
        self.sfx3 = pg.mixer.Sound(sfx3)

    def draw(self, screen, up_to: int = -1):
        '''Draws the sapphires on screen.'''
        size: int = self.sprite.get_width()
        for s in self.sapphires:
            if s[0] <= up_to: continue
            screen.blit(self.sprite, (s[1] * size + self.uiOffset, s[0] * size))
        if self.tempCount == 0 and self.maze.array[self.maze.mazeCorners[self.i][0]][self.maze.mazeCorners[self.i][1]] == 4 and \
                self.maze.mazeCorners[self.i][1] > up_to:
            screen.blit(self.refillSprite,
                        (self.maze.mazeCorners[self.i][1] * size + self.uiOffset, self.maze.mazeCorners[self.i][0] * size))

    def place(self, player: Player, count=None):
        '''Places some amount of sapphires in the maze.
        Requires player as parameter, to ensure that a sapphire does not spawn too close (would be too easy).'''
        if count is None: count = self.count
        points: list[tuple[int, int]] = []

        # for r in range(self.maze.r):
        #     for c in range(self.maze.c):
        #         if self.maze.array[r][c] == 3:
        #             self.maze.array[r][c] = 0

        # Generate all valid sapphire spawn locations first
        for point in self.maze.staticPoints:
            if self.maze.array[point[0]][point[1]] != 0:
                # print(f"Point {point} excluded: non-empty.")
                continue
            x: int = player.x // player.w
            y: int = player.y // player.h
            if abs(x - point[1]) < (self.maze.c // 3) and abs(y - point[0]) < (self.maze.r // 3):
                # print(f"Point {point} excluded: too close to the player.")
                continue
            # Temp represents how many empty squares are around a square. Sapphires must spawn in a dead end -> temp must be 1
            temp: int = 0
            if point[0] + 1 < self.maze.r and self.maze.array[point[0] + 1][point[1]] in (0, 5): temp += 1
            if point[1] + 1 < self.maze.c and self.maze.array[point[0]][point[1] + 1] in (0, 5): temp += 1
            if point[0] > 1 and self.maze.array[point[0] - 1][point[1]] in (0, 5): temp += 1
            if point[1] > 1 and self.maze.array[point[0]][point[1] - 1] in (0, 5): temp += 1
            if temp > 1:  # and self.maze.r * self.maze.c > 81
                # print(f"Point {point} excluded: not a dead end ({temp}).")
                continue
            # print(f"Point {point} chosen.")
            points.append(point)
        # print(points)
        shuffle(points)
        for i in range(count):
            if i < len(points):
                self.sapphires.append(points[i])
                self.maze.array[points[i][0]][points[i][1]] = 3
            else:
                self.tempCount -= 1

    def detectPickup(self, player: Player, maxRefills: int) -> bool:
        '''Checks for player interaction with sapphires.'''
        x: int = player.x // player.w
        y: int = player.y // player.h
        # Sapphire pickup logic
        if self.maze.array[y][x] == 3:
            self.sapphires.remove((y, x))
            self.maze.array[y][x] = 0
            # Flips valves in the maze (always at least 1)
            self.maze.flipValves(max(len(self.maze.valves) - 3, 1))
            self.tempCount -= 1
            self.sfx1.play()
            if self.tempCount <= 0:
                self.sfx2.play()
        # Gem pickup logic
        if self.maze.array[y][x] == 4 and self.tempCount < 1:
            self.maze.array[y][x] = 0
            if self.score > maxRefills - 2:
                self.score += 1
                # Player picked up all gems
                return True
            else:
                self.score += 1
                self.sfx3.play()
                self.i = (self.i + 1) % 4
                self.maze.array[self.maze.mazeCorners[self.i][0]][self.maze.mazeCorners[self.i][1]] = 4
                self.tempCount = self.count
                self.maze.flipValves(len(self.maze.valves) - 2)
                self.place(player)
        return False

class SpikeManager:
    '''This class defines the manager class for the Spikes in a maze.'''
    def __init__(self, count: int, maze: Maze) -> None:
        '''Initialise the manager by providing the Spike count and the target maze.'''
        self.count = count
        self.maze = maze
        self.offset = None
        self.sprites: list[pg.Surface] = []
        self.size = 0

        # Values used for spike flipping
        # Ticks is a number that counts up from 0 to self.period every frame.
        # Period is the amount of time (in ticks) between a spike's activation and deactivation
        self.ticks = -1
        self.period: int = 120

        # List of spikes
        # Format: Y coordinate of spike 1, X coordinate of spike 1, Y coordinate of spike 3, X coordinate of spike 3, rotation
        self.spikes: list[tuple[int, int, int, int, int]] = []
        # List of delays for each spike
        self.delays: list[int] = []
        # Only used at the very beginning
        self.useExtended = False

        # This is a list because the sound is randomly selected each time
        self.sfxs: list = []

    def loadAssets(self, spikeSource: str, size: int, uiOffset: int, sfx1: str, sfx2: str):
        '''Loads assets: the sprites, the pixel size, the UI offset, and the 2 slightly different sound effects'''
        self.size = size
        self.offset = uiOffset
        for x in (0, 16):
            self.sprites.append(pg.transform.scale(pg.image.load(spikeSource).subsurface((x, 0, 16, 16)), (size, size)))
        self.sfxs.append(pg.mixer.Sound(sfx1))
        self.sfxs.append(pg.mixer.Sound(sfx2))

    def draw(self, screen, up_to: int = -1):
        '''Draws the spikes on screen.'''
        for spike in self.spikes:
            sprite1 = pg.transform.rotate(self.sprites[self.maze.array[spike[0]][spike[1]] - 7], spike[4])
            sprite2 = pg.transform.rotate(self.sprites[self.maze.array[spike[2]][spike[3]] - 7], spike[4])
            sprite3 = pg.transform.rotate(self.sprites[self.maze.array[(spike[2] + spike[0]) // 2][(spike[3] + spike[1]) // 2] - 7], spike[4])
            y1: int = spike[0] * self.size
            x1: int = spike[1] * self.size
            y2: int = spike[2] * self.size
            x2: int = spike[3] * self.size

            # A hardcoded fix to offset the sprite a set amount for each rotation
            match spike[4]:
                case 0:
                    y1 -= 1 / 8 * self.size
                    y2 -= 1 / 8 * self.size
                case 180:
                    y1 += 1 / 16 * self.size
                    y2 += 1 / 16 * self.size
                case 90:
                    x1 -= 1 / 8 * self.size
                    x2 -= 1 / 8 * self.size
                case -90:
                    x1 += 1 / 16 * self.size
                    x2 += 1 / 16 * self.size

            if spike[0] > up_to:
                screen.blit(sprite1, (x1 + self.offset, y1))
            if spike[2] > up_to:
                screen.blit(sprite2, (x2 + self.offset, y2))
            if (spike[0] + spike[2]) // 2 > up_to:
                screen.blit(sprite3, ((x1 + x2) // 2 + self.offset, (y1 + y2) // 2))

    def place(self, count: int = None, setPeriod: int = None):
        '''Places count triplets of spikes in the Maze.'''
        if count is None:
            count = self.count
        points: list[tuple[int, int, int, int, int]] = []
        mods: list[int] = [-1, 1] # This is a list because it needs to be shuffled.
        # Scan the board for possible vertical placements
        for y in range(-1, self.maze.r - 2, 2):
            for x in range(1, self.maze.c, 2):
                shuffle(mods)
                for mod in mods:
                    # Horrendous if statement
                    if (self.maze.array[y + 1][x] == 1 and
                            self.maze.array[y + 3][x] == 1 and
                            self.maze.array[y + 1][x + mod] == 0 and
                            self.maze.array[y + 2][x + mod] == 0 and
                            self.maze.array[y + 3][x + mod] == 0 and
                            (y + 1, x + mod) not in self.maze.mazeCorners and
                            (y + 3, x + mod) not in self.maze.mazeCorners):
                        points.append((y + 1, x + mod, y + 3, x + mod, (-90 if mod == -1 else 90)))
        # Scan the board for possible horizontal placements
        for y in range(1, self.maze.r, 2):
            for x in range(-1, self.maze.c - 2, 2):
                shuffle(mods)
                for mod in mods:
                    # Another horrendous if statement
                    if (self.maze.array[y][x + 1] == 1 and
                            self.maze.array[y][x + 3] == 1 and
                            self.maze.array[y + mod][x + 1] == 0 and
                            self.maze.array[y + mod][x + 2] == 0 and
                            self.maze.array[y + mod][x + 3] == 0 and
                            (y + mod, x + 1) not in self.maze.mazeCorners and
                            (y + mod, x + 3) not in self.maze.mazeCorners):
                        points.append((y + mod, x + 1, y + mod, x + 3, (0 if mod == 1 else 180)))
        shuffle(points)
        placed: int = 0
        for point in points:
            # Breaks the loop if it has already placed the adequate number of spikes
            if placed >= min(len(points), count): break

            # Prevents spike overlapping
            if self.maze.array[point[0]][point[1]] != 0 or self.maze.array[point[2]][point[3]] != 0: continue

            # Prevents spikes from spawning on the player starting square
            if (point[0], point[1]) == (0, 0): continue

            self.maze.array[point[0]][point[1]] = 7
            self.maze.array[point[2]][point[3]] = 7
            self.maze.array[(point[0] + point[2]) // 2][(point[1] + point[3]) // 2] = 7
            self.spikes.append(point)
            placed += 1

        # The amount of time (in ticks) between a spike's activation and deactivation
        self.period = placed * 15 + 60
        if setPeriod is not None:
            self.period = setPeriod

        # Randomizes the delay for spike activation for different triplets
        for i in range(placed):
            delay: int = choice(range(0, self.period))
            self.delays.append(delay)

    def flip(self, screen, player: Player, useSound: bool = True):
        '''Activates and deactivates any spikes that should be flipped according to the timer. Uses player coordinates to make the flipping sound louder when the player is closer.'''
        self.ticks += 1
        self.ticks %= self.period
        x: int = player.x // player.w
        y: int = player.y // player.h
        # print(self.ticks, self.delays)

        # Loops through all triplets of spikes
        for i in range(len(self.delays)):
            dy: int = max(7 - abs(self.spikes[i][0] - y), 0)
            dx: int = max(7 - abs(self.spikes[i][1] - x), 0)

            # This is very useful but long to explain
            # Basically, without this, there would be a long period of time during which every single spike in the maze is activated, and deactivated
            extendedTicks: int = self.ticks + self.period

            value: int = self.delays[i]
            # Checks if the first spike should flip
            if self.ticks == value:
                self.maze.array[self.spikes[i][0]][self.spikes[i][1]] %= 2
                self.maze.array[self.spikes[i][0]][self.spikes[i][1]] += 7
                if dx > 0 and dy > 0 and useSound:
                    sfx = choice(self.sfxs)
                    sfx.set_volume(distance(dx, dy) * 0.03)
                    sfx.play()

            dy = max(7 - abs((self.spikes[i][2] + self.spikes[i][0]) // 2 - y), 0)
            dx = max(7 - abs((self.spikes[i][3] + self.spikes[i][1]) // 2 - x), 0)

            # Checks if the second spike should flip
            if self.ticks == value + 15 or extendedTicks == value + 15 and self.useExtended:
                self.maze.array[(self.spikes[i][2] + self.spikes[i][0]) // 2][(self.spikes[i][3] + self.spikes[i][1]) // 2] %= 2
                self.maze.array[(self.spikes[i][2] + self.spikes[i][0]) // 2][(self.spikes[i][3] + self.spikes[i][1]) // 2] += 7
                if dx > 0 and dy > 0 and useSound:
                    sfx = choice(self.sfxs)
                    sfx.set_volume(distance(dx, dy) * 0.03)
                    sfx.play()

            dy = max(7 - abs(self.spikes[i][2] - y), 0)
            dx = max(7 - abs(self.spikes[i][3] - x), 0)

            # Checks if the third spike should flip
            if self.ticks == value + 30 or extendedTicks == value + 30 and self.useExtended:
                self.maze.array[self.spikes[i][2]][self.spikes[i][3]] %= 2
                self.maze.array[self.spikes[i][2]][self.spikes[i][3]] += 7
                if dx > 0 and dy > 0 and useSound:
                    sfx = choice(self.sfxs)
                    sfx.set_volume(distance(dx, dy) * 0.03)
                    sfx.play()
        self.draw(screen)
        if self.ticks == self.period - 1:
            self.useExtended = True

class PotionManager:
    '''This class manages potion spawning and collision.'''
    def __init__(self, maze: Maze, uiOffset: int):
        '''Initialise the class by providing the maze and ui offset.'''
        self.maze = maze
        self.sprites: list[pg.Surface] = []
        # Format: Y coordinate of potion, X coordinate of potion, potion type (either 0 or 1)
        self.potions: list[tuple[int, int, int]] = []
        self.placed: int = 0
        self.offset = uiOffset
        self.pickupSfx = None

    def loadAssets(self, potionSource: str, size: int, sfxSource: str):
        '''Load assets: the potion sprites, pixel size and pickup sfx.'''
        self.sprites.append(pg.transform.scale(pg.image.load(potionSource).subsurface((0, 0, 16, 16)), (size, size)))
        self.sprites.append(pg.transform.scale(pg.image.load(potionSource).subsurface((16, 0, 16, 16)), (size, size)))
        self.pickupSfx = pg.mixer.Sound(sfxSource)

    def place(self, player: Player, count: int, rareChance: float, spawnChance: float = 0.00002):
        '''Places count potions, far away from the player.'''
        # The function simply returns if it doesn't pass the check
        if random() >= spawnChance: return

        points: list[tuple[int, int]] = self.maze.staticPoints
        shuffle(points)
        for point in points:
            x: int = player.x // player.w
            y: int = player.y // player.h
            # Discard a point if it's a corner, or it's not empty
            if self.maze.array[point[0]][point[1]] != 0 or point in self.maze.mazeCorners:
                continue
            # Discard a point if it's too close
            if abs(x - point[1]) < (self.maze.c // 3) and abs(y - point[0]) < (self.maze.r // 3):
                continue
            # Potion placement logic
            if self.placed < count:
                self.potions.append((point[0], point[1], 1 if random() <= rareChance else 0))
                self.maze.array[point[0]][point[1]] = 9 + self.potions[-1][2]
                self.placed += 1
                return

    def detectPickup(self, player: Player):
        '''Detects and handles player interaction with potions.'''
        x: int = player.x // player.w
        y: int = player.y // player.h
        if self.maze.array[y][x] in (9, 10):
            potion = None
            for p in self.potions:
                if (p[0], p[1]) == (y, x):
                    potion = p
                    break
            # If it encounters a 9 in the array, but it isn't in the potion list, nothing happens (bug prevention)
            if potion is not None:
                self.maze.array[y][x] = 0
                self.potions.remove(potion)
                self.pickupSfx.play()
                self.placed -= 1
                player.applyPotion(potion[2])

    def draw(self, screen, up_to: int = -1):
        '''Draws potions on the screen.'''
        size: int = self.sprites[0].get_width()
        for potion in self.potions:
            if potion[0] <= up_to: continue
            screen.blit(self.sprites[potion[2]], (potion[1] * size + self.offset, potion[0] * size))

class Bandaid:
    '''This class implements the bandaid, the only way for the player to recover health.'''
    def __init__(self, uiOffset: int, player: Player, boundaryX: int, boundaryY: int):
        '''Initialise the class by providing a specific player, and the maze boundaries.'''
        self.offset = uiOffset
        self.player = player
        self.x: int = 0
        self.y: int = 0
        self.size: int = 0
        self.sprite = None
        self.xMax: int = boundaryX
        self.yMax: int = boundaryY

        # Value representing whether the bandaid is falling down or not
        self.placed: bool = False
        self.dx: int = 0
        self.sfx = None
        # A timer is used for determining when to spawn the bandaid, rather than a random check
        # This is because the spawning of the bandaid should be guaranteed, given enough time
        # But with random checks, it's possible that the bandaid never spawns
        self.timer: int = 0

    def loadAssets(self, source: str, size: int, sfxSource: str):
        '''Loads the bandaid sprite, its size, and the pickup sfx.'''
        self.sprite = pg.transform.scale(pg.image.load(source).subsurface((80, 0, 16, 16)), (size, size))
        self.size = size
        self.sfx = pg.mixer.Sound(sfxSource)
        self.sfx.set_volume(3)

    def draw(self, screen):
        '''Draws the sprite.'''
        if not self.placed: return
        screen.blit(self.sprite, (self.x + self.offset, self.y))

    def handleTimer(self):
        '''Handles the timer logic.'''

        # If the player Hp is full, do nothing.
        if self.player.health == 3:
            return

        # If the timer runs out -> place the bandaid
        if self.timer == 1 and not self.placed:
            self.placed = True
            # It stars falling from a random position
            self.x = choice(range(self.size, self.xMax - self.size))
            self.y = -self.size
            self.dx = (random() - 0.5) * 2
            self.timer -= 1
        # When the player fails to pick up the bandaid
        elif self.timer == 0 and not self.placed:
            self.timer = choice(range(18, 50)) * 60 # Anywhere between 18 and 50 seconds
        # Decrement the timer
        elif self.timer > 1:
            self.timer -= 1

    def move(self):
        '''Move the bandaid down the screen and bounce it off the maze boundaries.'''
        if not self.placed: return
        self.x += self.dx
        self.y += 2

        if self.y > self.yMax + self.size:
            self.placed = False

        if self.x < 0 or self.x > self.xMax - self.size:
            self.dx = -self.dx

    def detectCollision(self):
        '''Checks for player interaction with the bandaid.'''
        if not self.placed: return
        rect = pg.Rect(self.x, self.y, self.size, self.size)
        playerRect = pg.Rect(self.player.x, self.player.y, self.size, self.size)
        if rect.colliderect(playerRect):
            self.player.health += 1
            self.placed = False
            self.sfx.play()

class UI:
    '''This class defines the Side Bar UI.'''
    def __init__(self, screen, offset: int, itemsSource: str, fontSize: int):
        '''Initialise the class by providing the screen, UI offset, sprite source and font size.'''
        self.offset = offset
        self.screen = screen
        self.font = pg.font.SysFont("freesans", fontSize)
        self.heart = pg.transform.scale(pg.image.load(itemsSource).subsurface((32, 0, 16, 16)), (offset, offset))
        self.sprintPotion = pg.transform.scale(pg.image.load(itemsSource).subsurface((0, 0, 16, 16)), (offset, offset))
        self.noclipPotion = pg.transform.scale(pg.image.load(itemsSource).subsurface((16, 0, 16, 16)), (offset, offset))

    def draw(self, score: int, health: int, level: int, timers: tuple[int, int] = None):
        '''Draws the UI (sidebars, text, timers).'''
        screenHeight: int = self.screen.get_height()
        screenWidth: int = self.screen.get_width()
        textHeight: int = self.font.get_height()
        pg.draw.rect(self.screen, "#4f4f4f", (0, 0, self.offset, screenHeight))
        pg.draw.rect(self.screen, "#4f4f4f", (screenWidth - self.offset, 0, self.offset, screenHeight))
        # pg.draw.line(self.screen, "#000000", (self.offset - 10, 0), (self.offset - 10, screenHeight), 10)
        # pg.draw.line(self.screen, "#000000", (screenWidth - self.offset, 0), (screenWidth - self.offset, screenHeight), 10)
        text: str = f"LEVEL {level}"

        # Logic for drawing the text vertically
        h: int = screenHeight // 2 - (len(text)) * textHeight // 2
        for char in text:
            t = self.font.render(char, True, "#FFFFFF")
            self.screen.blit(t, (self.offset // 2 - t.get_width() // 2, h))
            h += textHeight
        text = f"{score}-4"
        h = screenHeight // 2 - (len(text)) * textHeight // 2
        for char in text:
            if char == "-":
                t = self.font.render("--", True, "#FFFFFF")
            else:
                t = self.font.render(char, True, "#FFFFFF")
            self.screen.blit(t, (screenWidth - self.offset // 2 - t.get_width() // 2, h))
            h += textHeight

        # Heart drawing logic
        if health > 0:
            self.screen.blit(self.heart, (screenWidth - self.offset, 0))
        if health > 1:
            self.screen.blit(self.heart, (screenWidth - self.offset, self.offset))
        if health > 2:
            self.screen.blit(self.heart, (screenWidth - self.offset, self.offset * 2))

        # Timers logic
        if timers is not None:
            t1 = self.font.render(str(round(timers[0] / 60, 1)), True, "#FFFFFF")
            t2 = self.font.render(str(round(timers[1] / 60, 1)), True, "#FFFFFF")
            w1 = t1.get_width() // 2
            w2 = t2.get_width() // 2

            if timers[0] > 0:
                self.screen.blit(self.sprintPotion, (screenWidth - self.offset, screenHeight - 3 * self.offset))
                self.screen.blit(t1, (screenWidth - self.offset // 2 - w1, screenHeight - 2 * self.offset - textHeight))
            if timers[1] > 0:
                self.screen.blit(self.noclipPotion, (screenWidth - self.offset, screenHeight - 2 * self.offset))
                self.screen.blit(t2, (screenWidth - self.offset // 2 - w2, screenHeight - self.offset - textHeight))
