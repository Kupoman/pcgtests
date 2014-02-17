import bge

def main():
    proj = bge.logic.getCurrentController().owner

    target = bge.logic.getCurrentScene().objects.get(proj["target"], None)

    if target:
        vec = target.worldPosition - proj.worldPosition
        distance = vec.length
        vec.normalize()
        vec *= 0.1
        
        proj.worldPosition += vec