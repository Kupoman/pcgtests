import random

import mathutils

import scripts.dmap as dmap
import scripts.bsp as bsp

def main(cont):
	ob = cont.owner
	scene = ob.scene

	sw = 50
	sh = 50
	dungeon = bsp.gen(sw, sh)

	ob["dmap"] = dmap.init(dungeon)

	ob["teleporters"] = {}

	ob["encounters"] = []

	for y in range(len(dungeon)):
		for x in range(len(dungeon[y])):
			tile = dungeon[y][x]
			if tile in ('#', '*', '$') or tile.isdigit():
				ob.worldPosition = (x - sw / 2, y - sh / 2, -random.random() * 0.1)
				scene.addObject("DungeonTile", ob)

				if tile == '$':
					ob.worldPosition[2] += 1.75
					ob["encounters"].append(scene.addObject("MonsterSpawn", ob))

				if tile == '*':
					ob.worldPosition[2] = 0.75
					ob["player_start_loc"] = (x, y)
					scene.addObject("PlayerStart", ob)
					scene.addObject("Player", ob)

				if tile.isdigit():
					ob.worldPosition[2] = 0.75
					t = scene.addObject("Teleporter", ob)
					t.color = ob["dmap"].add_teleporter((x, y))
