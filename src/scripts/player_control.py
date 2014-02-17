import bge

from scripts.combat_player import Player

KEY_FIRE = bge.events.QKEY
KEY_DODGE = bge.events.SPACEKEY

def main():
    obj = bge.logic.getCurrentController().owner

    if "class" not in obj.attrDict:
        obj["class"] = Player(obj)


    dt = 1 / bge.logic.getLogicTicRate()
    obj["class"].update(dt)

    obj["hp"] = obj["class"].hp
    obj["stamina"] = obj["class"].stamina

    scene = bge.logic.getCurrentScene()
    targets = [i.name for i in scene.objects if i.name.startswith("Enemy")]
    main = bge.logic.getSceneList()[0].objects.get("Main", None)

    if len(targets) < 1:
        print("You win")
        if main is None:
            bge.logic.restartGame()
        else:
            main["encounter_scene"] = False
            scene.end()
    elif obj["hp"] < 1:
        print("Game Over")
        if main is None:
            obj.endObject()
            bge.logic.restartGame()
        else:
            main["encounter_scene"] = False
            scene.end()
    else:
        keyboard = bge.logic.keyboard

        for key, status in keyboard.active_events.items():
            if (key == KEY_FIRE and
                    status == bge.logic.KX_INPUT_JUST_ACTIVATED):
                fire_point = [i for i in obj.children if i.name == "FirePoint"][0]
                obj["class"].fire(scene, targets[0], fire_point)
            elif (key == KEY_DODGE and
                    status == bge.logic.KX_INPUT_JUST_ACTIVATED):
                obj["class"].dodge()
