from collections import namedtuple
import random
import dfs

MIN_ROOM_X = 5
MIN_ROOM_Y = 5

EROSION = 0.1

Room = namedtuple('Room', 'x y sw sh')


def split(startx, starty, endx, endy):
    rangex = endx - startx
    rangey = endy - starty

    if rangex <= MIN_ROOM_X * 2 or rangey <= MIN_ROOM_Y * 2:
        return [Room(startx, starty, endx, endy)]
    
    if rangex > rangey:
        # Split x
        part = random.randint(int(rangex * 0.25), int(rangex * 0.75))
        return split(startx, starty, startx + part, endy) + \
            split(startx + part, starty, endx, endy)
    else:
        # Split y
        part = random.randint(int(rangey * 0.25), int(rangey * 0.75))
        return split(startx, starty, endx, starty + part) + \
            split(startx, starty + part, endx, endy)

def gen(sw, sh):
    # random.seed(22)
    dungeon = [['.' for _ in range(sw)] for _ in range(sh)]
    rooms = []

    rooms = split(1, 1, sw - 1, sh - 1)

    # Remove half the rooms at random
    rooms = random.sample(rooms, len(rooms)//2)

    num_tiles = 0
    for room in rooms:
        for y in range(room.y, room.sh):
            for x in range(room.x, room.sw):
                dungeon[y][x] = '#'
                num_tiles += 1

    # Erosion
    # Remove x% of tiles
    remaining = int(num_tiles * EROSION)
    #print("Eroding", remaining, "tiles")
    while remaining != 0:
        rx = random.randint(0, sw - 1)
        ry = random.randint(0, sh - 1)

        tile = dungeon[ry][rx]
        if tile != '#':
            continue

        factor = 0.5
        if ry > 0 and dungeon[ry - 1][rx] == '.':
            factor += 1
        if ry < sh - 1 and dungeon[ry + 1][rx] == '.':
            factor += 1
        if rx > 0 and dungeon[ry][rx - 1] == '.':
            factor += 1
        if rx < sw - 1 and dungeon[ry][rx + 1] == '.':
            factor += 1

        if random.random() * factor > 0.5:
            dungeon[ry][rx] = '.'
            remaining -= 1

    # Connected components
    ccl = dfs.dfs(dungeon)
    #print(len(ccl))
    #for cc in ccl:
    #    for tile in cc:
    #        dungeon[tile.coord[0]][tile.coord[1]] = str(tile.cc)

    # Remove islands that are too small
    for cc in ccl[:]:
        if len(cc) < 5:
            ccl.remove(cc)

    # Pick a start tile
    cc = random.choice(ccl)
    coord = random.choice(cc).coord
    dungeon[coord[0]][coord[1]] = '*'
    
    return dungeon

if __name__ == '__main__':
   d = gen(50, 50)

   for y in d:
       for x in y:
           print(x, end=" ")
       print()


