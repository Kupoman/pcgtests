import bge

def main():
    bar = bge.logic.getCurrentController().owner

    player = bge.logic.getSceneList()[-2].objects.get("CombatPlayer", None)
    main = bge.logic.getSceneList()[0].objects.get("Main", None)

    bar.localScale[0] = player["stamina"] if player else 0.0

    if main and not main["encounter_scene"]:
        bge.logic.getCurrentScene().end()