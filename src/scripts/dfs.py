class V:
    __slots__ = "vstate", "tile", "coord", "cc"

    def __init__(self, vstate, tile, coord, cc):
        self.vstate = vstate
        self.tile = tile
        self.coord = coord
        self.cc = cc

def dfs(dmap):
    G = {}

    for iy, vy in enumerate(dmap):
        for ix, vy in enumerate(vy):
            if vy in ('#', '$'):
                coord = (iy, ix)
                G[coord] = V(0, vy, coord, -1)

    cc = 0
    connected_components = []
    for v in G.values():
        if v.vstate == 0:
            connected_components.append(dfs_visit(dmap, G, v, cc))
            cc += 1

    return connected_components

def dfs_visit(dmap, G, V, cc):
    def adj(dmap, G, V):
        vl = []

        if dmap[V.coord[0] + 1][V.coord[1]] in ('#', '$'):
            vl.append(G[(V.coord[0] + 1, V.coord[1])])
        if dmap[V.coord[0]][V.coord[1] + 1] in ('#', '$'):
            vl.append(G[(V.coord[0], V.coord[1] + 1)])
        if dmap[V.coord[0] - 1][V.coord[1]] in ('#', '$'):
            vl.append(G[(V.coord[0] - 1, V.coord[1])])
        if dmap[V.coord[0]][V.coord[1] - 1] in ('#', '$'):
            vl.append(G[(V.coord[0], V.coord[1] - 1)])

        return vl

    retval = []
    
    V.vstate = 1
    for v in adj(dmap, G, V):
        if v.vstate == 0:
            retval += dfs_visit(dmap, G, v, cc)

    V.cc = cc
    V.vstate = 2
    return retval + [V]   

