import random

import bge

from scripts.combat_player import Player

FIRE_CHANCE = 0.0035

def main():
    obj = bge.logic.getCurrentController().owner

    if "class" not in obj.attrDict:
        obj["class"] = Player(obj)


    dt = 1 / bge.logic.getLogicTicRate()
    obj["class"].update(dt)

    if obj["class"].hp < 1:
        obj.endObject()
    elif random.random() < FIRE_CHANCE:
        scene = bge.logic.getCurrentScene()
        fire_point = obj.children[0]
        obj["class"].fire(scene, "CombatPlayer", fire_point)