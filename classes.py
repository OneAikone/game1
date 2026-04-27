import pygame as pg
from random import shuffle, random, choice


class Player:
    def __init__(self, x: int, y: int, w: int, h: int, uiOffset: int = 0) -> None:
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h
        self.health: int = 3
        self.noclip: bool = False
        self.sprint: bool = True
        self.uiOffset: int = uiOffset
        self.hurt = False

        self.mode: int = 5
        self.dir: int = 0

        self.img = None
        self.sprites: list[pg.Surface] = []
        self.damageSfx = None

    def loadAssets(self, spriteSource: str, sfxSource: str) -> None:
        _ = pg.transform.scale(pg.image.load(spriteSource), (self.w * 5, self.h * 3))
        for y in range(0, self.h * 3, self.h):
            for x in range(0, self.w * 5, self.w):
                self.sprites.append(_.subsurface((x, y, self.w, self.h)))
        self.damageSfx = pg.mixer.Sound(sfxSource)
        self.damageSfx.set_volume(2)


    def draw(self, screen):
        screen.blit(self.sprites[self.dir + self.mode], (self.x + self.uiOffset, self.y))

    def move(self, event, map: list[list]) -> None:
        x: int = self.x // self.w
        y: int = self.y // self.h
        if event.type == pg.KEYDOWN or (self.sprint and event.type == pg.KEYUP):
            if event.key in (pg.K_a,) and x > 0 and (map[y][x - 1] not in (1, 6) or self.noclip):
                self.x -= self.w
                self.dir = 2
            elif event.key in (pg.K_d,) and x < len(map[0]) - 1 and (map[y][x + 1] not in (1, 6) or self.noclip):
                self.x += self.w
                self.dir = 1
            elif event.key in (pg.K_w,) and y > 0 and (map[y - 1][x] not in (1, 6) or self.noclip):
                self.y -= self.h
                self.dir = 3
            elif event.key in (pg.K_s,) and y < len(map) - 1 and (map[y + 1][x] not in (1, 6) or self.noclip):
                self.y += self.h
                self.dir = 4

    def checkCollision(self, map: list[list]) -> None:
        x: int = self.x // self.w
        y: int = self.y // self.h
        if map[y][x] == 8 and self.hurt is False and self.noclip is False:
            self.damageSfx.play()
            self.health = max(0, self.health - 1)
            self.hurt = True
        elif map[y][x] != 8 and self.hurt is True:
            self.hurt = False

    def applyPotion(self) -> None:
        pass


class Maze:
    def __init__(self, columns: int, rows: int) -> None:
        self.c: int = columns
        self.r: int = rows
        self.array: list[list] = [[1 for _ in range(columns)] for _ in range(rows)]
        self.staticPoints: list[tuple[int, int]] = [(i, j) for i in range(0, rows, 2) for j in
                                                    range(0, columns, 2)]  # Points that are always empty
        self.wallSprite = None
        self.directionMap: list[list] = []
        self.sprites: list[pg.Surface] = []
        self.uiOffset = None
        self.wallMap: list[list] = [[0 for _ in range(columns)] for _ in range(rows)]
        self.clock = None
        self.screen = None
        self.valves: list[tuple[int, int, int, int, int, int]] = []
        self.valveSprites: list[pg.Surface] = []
        self.valveW: int = 0

    def reset(self):
        '''Sets all tiles to a wall'''
        self.array: list[list] = [[1 for _ in range(self.c)] for _ in range(self.r)]

    def printMaze(self):
        print()
        for row in self.array:
            for tile in row:
                if tile in (0, 5):
                    print("  ", end="")
                elif tile in (1, 6):
                    print("X ", end="")
                elif tile == 3:
                    print("O ", end="")
                elif tile == 4:
                    print(". ", end="")
                else:
                    print("##", end="")
            print("|")
        print()

    def loadAssets(self, wallSource: str, size: int, valveSource: str, screen, clock, uiOffset: int = 0):
        '''Loads all assets for the maze to use'''
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
        w: float = self.sprites[0].get_width() * self.c / 11
        coords: list[tuple[int, int]] = [(i,j) for i in range(16) for j in range(11)]

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

    def loadAnim(self, bgImg: pg.Surface, w:int):
        for a in range(self.c - 1, -1, -1):
            for b in range(self.r - 2, -1, -1):
                self.screen.blit(bgImg, (self.uiOffset, 0))
                for x in range(self.c):
                    found = False
                    for y in range(self.r):
                        if (x,y) == (a,b):
                            found = ~found
                            break
                        pg.draw.rect(self.screen, "#FFFFFF", (x*w + self.uiOffset, y*w, w, w))
                    if found: break
                self.clock.tick((self.r - 1) * self.c // 1.5)
                pg.display.flip()
        self.clock.tick(1.5)

    def deathAnim(self):
        w = self.sprites[0].get_width()
        coords: list[tuple[int, int]] = [(self.r // 2, self.c // 2)]
        dy: int = -1
        dx: int = -1
        temp: int = 1
        while coords[-1][0] >= 0 and coords[-1][1] >= 0:
            for i in range(abs(dy)):
                coords.append((coords[-1][0] + (dy // abs(dy)), coords[-1][1]))
            dy *= -1
            temp += 1
            if temp == 3:
                temp = 1
                if dx > 0:
                    dx += 1
                else:
                    dx -= 1
                if dy > 0:
                    dy += 1
                else:
                    dy -= 1
            for i in range(abs(dx)):
                coords.append((coords[-1][0], coords[-1][1] + (dx // abs(dx))))
            dx *= -1
            temp += 1
            if temp == 3:
                temp = 1
                if dx > 0:
                    dx += 1
                else:
                    dx -= 1
                if dy > 0:
                    dy += 1
                else:
                    dy -= 1
        coords = coords[::-1]
        for i in range(len(coords)):
            r, c = coords[i]
            pg.draw.rect(self.screen, "#000000", (c * w + self.uiOffset, r * w, w, w))
            self.clock.tick(len(coords) // 6)
            pg.display.flip()
        self.clock.tick(0.5)


    def draw(self, screen=None, up_to: int = -1):
        '''Draws the maze on the screen using 16 wall sprites'''
        w = self.sprites[0].get_width()
        if screen is None: screen = self.screen
        for r in range(self.r - 1, up_to, -1):
            for c in range(self.c):
                if self.array[r][c] == 1:
                    screen.blit(self.sprites[self.wallMap[r][c]], (c * w + self.uiOffset, r * w))

        # Worst 20 lines of code, but I couldn't think of a more optimal solution
        # For every sprite rotation, the sprite gets weirdly offset and specific values (such as 1/16) have to be used for each case to correct placement
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
                screen.blit(pg.transform.rotate(self.valveSprites[i], valve[2]), (self.valveW * (valve[1] - a) + self.uiOffset, self.valveW * (valve[0] - b)))
            if valve[3] > up_to:
                screen.blit(pg.transform.rotate(self.valveSprites[j], valve[5]), (self.valveW * (valve[4] - c) + self.uiOffset, self.valveW * (valve[3] - d)))

    def getOffsets(self, coords: tuple[int, int]) -> list[tuple[int, int]]:
        '''Only called by other functions'''
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
        '''The wall map is an array of indices that tell the draw function which wall sprite to use.'''
        self.wallMap: list[list] = [[0 for _ in range(self.c)] for _ in range(self.r)]

        for y in range(self.r):
            for x in range(self.c):
                if self.array[y][x] != 1: continue

                if x == 0:
                    self.wallMap[y][x] += 1
                else:
                    self.wallMap[y][x] += (self.array[y][x - 1] == 1)

                if x == self.c - 1:
                    self.wallMap[y][x] += 4
                else:
                    self.wallMap[y][x] += (self.array[y][x + 1] == 1) * 4

                if y == 0:
                    self.wallMap[y][x] += 8
                else:
                    self.wallMap[y][x] += (self.array[y - 1][x] == 1) * 8

                if y == self.r - 1:
                    self.wallMap[y][x] += 2
                else:
                    self.wallMap[y][x] += (self.array[y + 1][x] == 1) * 2

    def generateMaze(self, coords: tuple[int, int] = (0, 0), visualise: bool = False) -> None:
        '''Maze generation using Stack-Based Depth First Search Algorithm (no risk of recursion overflow for large mazes).'''
        self.reset()
        stack: list[tuple[int, int, int, int]] = []
        stack.append(coords + coords)
        while len(stack) > 0:
            point: tuple[int, int, int, int] = stack[-1]
            stack.pop()
            if self.array[point[0]][point[1]] == 0: continue
            self.array[point[0]][point[1]] = 0
            self.array[point[2]][point[3]] = 0
            offsets: list[tuple[int, int]] = self.getOffsets((point[0], point[1]))
            shuffle(offsets)
            for offset in offsets:
                if self.array[point[0] + offset[0]][point[1] + offset[1]] == 0: continue
                stack.append((point[0] + offset[0], point[1] + offset[1], point[0] + int(offset[0] / 2),
                              point[1] + int(offset[1] / 2)))
            if visualise:
                w: int = self.sprites[0].get_width()
                self.screen.fill("#AAAAAA")
                self.generateWallMap()
                self.draw(self.screen)
                pg.draw.rect(self.screen, "#FFFFFF", (point[1] * w + self.uiOffset, point[0] * w, w, w))
                self.clock.tick(30)
                pg.display.flip()

    def getDirection(self, point: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
        '''Gets the direction from one point to the other. Useful for knowing where to place valves. Uses DFS'''
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
                    return ((branch[0] + point[0]) // 2, (branch[1] + point[1]) // 2)
                visited[p[0]][p[1]] = True
                for offset in self.getOffsets(p):
                    new: tuple[int, int] = (p[0] + offset[0], p[1] + offset[1])
                    if visited[new[0]][new[1]] == False and self.array[(p[0] + new[0]) // 2][
                        (p[1] + new[1]) // 2] not in (1, 5, 6):
                        stack.append(new)
        return (0, 0)

    def placeValves(self, pairCount: int):
        points: list[tuple[int, int]] = self.staticPoints
        shuffle(points)
        placed: int = 0
        for point in points:
            if placed >= pairCount: break
            new: list[tuple[int, int]] = []
            for offset in self.getOffsets(point):
                v1: tuple[int, int] = (point[0] + offset[0] // 2, point[1] + offset[1] // 2)
                if self.array[v1[0]][v1[1]] == 1:
                    new.append((point[0] + offset[0], point[1] + offset[1]))
            if len(new) == 0: continue
            point2 = choice(new)
            valve1: tuple[int, int] = ((point[0] + point2[0]) // 2, (point[1] + point2[1]) // 2)
            valve2 = self.getDirection(point2, point)
            if valve2 == (0, 0): continue
            if self.array[valve2[0]][valve2[1]] != 0: continue
            placed += 1
            self.array[valve2[0]][valve2[1]] = 6
            self.array[valve1[0]][valve1[1]] = 5
            r1: int = choice((0, 180))
            r2: int = choice((0, 180))
            if valve1[0] > 0 and self.array[valve1[0] - 1][valve1[1]] != 1:
                r1: int = choice((90, -90))
            if valve2[0] > 0 and self.array[valve2[0] - 1][valve2[1]] != 1:
                r2: int = choice((90, -90))

            self.valves.append(valve1 + (r1,) + valve2 + (r2,))
        self.generateWallMap()

    def flipValves(self, count: int):
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
    def __init__(self, count: int, maze: Maze, uiOffset: int = 0):
        self.count: int = count
        self.tempCount: int = count
        self.score = 0
        self.maze: Maze = maze
        self.sapphires: list[tuple[int, int]] = []
        self.sprite: pg.Surface
        self.refillSprite: pg.Surface
        self.uiOffset: int = uiOffset
        self.refills: list[tuple[int, int]] = [(maze.r - 1, maze.c - 1), (0, 0), (0, maze.c - 1), (maze.r - 1, 0)]
        self.i = 0  # Which corner to spawn the new refill in
        self.maze.array[self.refills[self.i][0]][self.refills[self.i][1]] = 4
        self.sfx1 = None
        self.sfx2 = None

    def loadAssets(self, spriteSource: str, size: int, sfx1: str, sfx2: str):
        '''Loads the sapphire and refill point sprites.'''
        image = pg.transform.scale(pg.image.load(spriteSource), (5 * size, size))
        self.sprite = image.subsurface((size * 3, 0, size, size))
        self.refillSprite = image.subsurface((size * 4, 0, size, size))
        self.sfx1 = pg.mixer.Sound(sfx1)
        self.sfx1.set_volume(0.5)
        self.sfx2 = pg.mixer.Sound(sfx2)

    def draw(self, screen, up_to: int = -1):
        size: int = self.sprite.get_width()
        for s in self.sapphires:
            if s[0] <= up_to: continue
            screen.blit(self.sprite, (s[1] * size + self.uiOffset, s[0] * size))
        if self.maze.array[self.refills[self.i][0]][self.refills[self.i][1]] == 4 and self.refills[self.i][1] > up_to:
            screen.blit(self.refillSprite,
                        (self.refills[self.i][1] * size + self.uiOffset, self.refills[self.i][0] * size))

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
                # print(f"Point {point} out: non-empty.")
                continue
            x: int = player.x // player.w
            y: int = player.y // player.h
            if abs(x - point[1]) < (self.maze.c // 3) and abs(y - point[0]) < (self.maze.r // 3):
                # print(f"Point {point} out: too close.")
                continue
            temp: int = 0
            if point[0] + 1 < self.maze.r and self.maze.array[point[0] + 1][point[1]] in (0, 5): temp += 1
            if point[1] + 1 < self.maze.c and self.maze.array[point[0]][point[1] + 1] in (0, 5): temp += 1
            if point[0] > 1 and self.maze.array[point[0] - 1][point[1]] in (0, 5): temp += 1
            if point[1] > 1 and self.maze.array[point[0]][point[1] - 1] in (0, 5): temp += 1
            if temp > 1:  # and self.maze.r * self.maze.c > 81
                # print(f"Point {point} out: not dead end ({temp}).")
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
        x: int = player.x // player.w
        y: int = player.y // player.h
        if self.maze.array[y][x] == 3:
            self.sfx1.play()
            self.sapphires.remove((y, x))
            self.maze.array[y][x] = 0
            # self.maze.shiftMaze(2)
            self.maze.flipValves(max(len(self.maze.valves) - 3, 1))
            self.tempCount -= 1
        if self.maze.array[y][x] == 4 and self.tempCount < 1:
            self.maze.array[y][x] = 0
            if self.score > maxRefills - 2:
                self.score += 1
                return True
            else:
                self.score += 1
                self.sfx2.play()
                self.i = (self.i + 1) % 4
                self.maze.array[self.refills[self.i][0]][self.refills[self.i][1]] = 4
                self.tempCount = self.count
                self.maze.flipValves(len(self.maze.valves) - 2)
                self.place(player)
        return False

class SpikeManager:
    def __init__(self, count: int, maze: Maze) -> None:
        self.count = count
        self.maze = maze
        self.offset = None
        self.sprites: list[pg.Surface] = []
        self.size = 32
        self.ticks = -1
        self.period: int = 120

        self.spikes: list[list[int]] = []
        self.delays: list[int] = []
        self.useExtended = False

    def loadAssets(self, spikeSource: str, size: int, uiOffset: int):
        self.size = size
        self.offset = uiOffset
        for x in (0, 16):
            self.sprites.append(pg.transform.scale(pg.image.load(spikeSource).subsurface((x, 0, 16, 16)), (size, size)))

    def draw(self, screen, up_to: int = -1):
        for spike in self.spikes:
            sprite1 = pg.transform.rotate(self.sprites[self.maze.array[spike[0]][spike[1]] - 7], spike[4])
            sprite2 = pg.transform.rotate(self.sprites[self.maze.array[spike[2]][spike[3]] - 7], spike[4])
            sprite3 = pg.transform.rotate(
                self.sprites[self.maze.array[(spike[2] + spike[0]) // 2][(spike[3] + spike[1]) // 2] - 7], spike[4])
            y1: int = spike[0] * self.size
            x1: int = spike[1] * self.size
            y2: int = spike[2] * self.size
            x2: int = spike[3] * self.size
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
        if count is None:
            count = self.count
        points: list[list[int]] = []
        mods: list[int] = [-1, 1]
        # Scan the board for possible placements
        for y in range(-1, self.maze.r - 2, 2):
            for x in range(1, self.maze.c, 2):
                if (x, y) == (0, 0): continue
                shuffle(mods)
                for mod in mods:
                    if self.maze.array[y + 1][x] == 1 and self.maze.array[y + 3][x] == 1 and self.maze.array[y + 1][
                        x + mod] == 0 and self.maze.array[y + 2][x + mod] == 0 and self.maze.array[y + 3][x + mod] == 0:
                        points.append([y + 1, x + mod, y + 3, x + mod, (-90 if mod == -1 else 90)])
        for y in range(1, self.maze.r, 2):
            for x in range(-1, self.maze.c - 2, 2):
                if (x, y) == (0, 0): continue
                shuffle(mods)
                for mod in mods:
                    if (self.maze.array[y][x + 1] == 1 and
                            self.maze.array[y][x + 3] == 1 and
                            self.maze.array[y + mod][x + 1] == 0 and
                            self.maze.array[y + mod][x + 2] == 0 and
                            self.maze.array[y + mod][x+ 3] == 0):
                        points.append([y + mod, x + 1, y + mod, x + 3, (0 if mod == 1 else 180)])
        shuffle(points)
        i: int = -1
        placed: int = 0
        while placed < min(len(points), count):
            i += 1
            if i >= len(points): break
            point: list[int] = points[i]
            if self.maze.array[point[0]][point[1]] != 0 or self.maze.array[point[2]][point[3]] != 0: continue
            if (point[0], point[1]) == (0,0): continue
            self.maze.array[point[0]][point[1]] = 7
            self.maze.array[point[2]][point[3]] = 7
            self.maze.array[(point[0] + point[2]) // 2][(point[1] + point[3]) // 2] = 7
            self.spikes.append(point)
            placed += 1
        self.period = placed * 15 + 60
        if setPeriod is not None:
            self.period = setPeriod
        for i in range(placed):
            delay: int = choice(range(0, self.period))
            self.delays.append(delay)

    def flip(self, screen):
        self.ticks += 1
        self.ticks %= self.period
        # print(self.ticks, self.delays)
        for i in range(len(self.delays)):
            extendedTicks: int = self.ticks + self.period
            value: int = self.delays[i]
            if self.ticks == value:
                self.maze.array[self.spikes[i][0]][self.spikes[i][1]] %= 2
                self.maze.array[self.spikes[i][0]][self.spikes[i][1]] += 7
            elif self.ticks == value + 15 or extendedTicks == value + 15 and self.useExtended:
                self.maze.array[(self.spikes[i][2] + self.spikes[i][0]) // 2][
                    (self.spikes[i][3] + self.spikes[i][1]) // 2] %= 2
                self.maze.array[(self.spikes[i][2] + self.spikes[i][0]) // 2][
                    (self.spikes[i][3] + self.spikes[i][1]) // 2] += 7
            elif self.ticks == value + 30 or extendedTicks == value + 30 and self.useExtended:
                self.maze.array[self.spikes[i][2]][self.spikes[i][3]] %= 2
                self.maze.array[self.spikes[i][2]][self.spikes[i][3]] += 7
        self.draw(screen)
        if self.ticks == self.period - 1:
            self.useExtended = True


class UI:
    def __init__(self, screen, level: int, offset: int, itemsSource: str, fontSize: int):
        self.level = level
        self.offset = offset
        self.screen = screen
        self.font = pg.font.SysFont("freesans", fontSize)
        self.heart = pg.transform.scale(pg.image.load(itemsSource).subsurface((32, 0, 16, 16)), (offset, offset))

    def draw(self, score: int, health: int, level: int = None):
        '''Draws the UI (sidebars, text).'''
        # This took a long time to figure out and this code is pretty messy (especially calculating text height)
        if level is None:
            level = self.level
        screenHeight: int = self.screen.get_height()
        screenWidth: int = self.screen.get_width()
        textHeight: int = self.font.get_height()
        pg.draw.rect(self.screen, "#4f4f4f", (0, 0, self.offset, screenHeight))
        pg.draw.rect(self.screen, "#4f4f4f", (screenWidth - self.offset, 0, self.offset, screenHeight))
        # pg.draw.line(self.screen, "#000000", (self.offset - 10, 0), (self.offset - 10, screenHeight), 10)
        # pg.draw.line(self.screen, "#000000", (screenWidth - self.offset, 0), (screenWidth - self.offset, screenHeight), 10)
        text: str = f"LEVEL {level}"
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
        if health > 0:
            self.screen.blit(self.heart, (screenWidth - self.offset, 0))
        if health > 1:
            self.screen.blit(self.heart, (screenWidth - self.offset, self.offset))
        if health > 2:
            self.screen.blit(self.heart, (screenWidth - self.offset, self.offset * 2))

