#!/usr/bin/python

# qjermyn
# voroni region/longest path bot
# try to cross the closest battlefront tile if in the smaller region
# try to survive once in the bigger region

import random, tron
from collections import defaultdict, deque

DEBUG = True
if DEBUG:
    logfile = 'q_battle.txt'
    tron.init_error_log(logfile)

class GraphNode:
    def __init__(self, parent, tile, distance=0):
        self.parent = parent
        self.tile = tile
        self.children = []
        self.distance = distance

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        #self.distances[(to_node, from_node)] = distance
        self.distances[(from_node, to_node)] = distance

def dijkstra(graph, initial):
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            # try:
            weight = current_weight + graph.distances[(min_node, edge)]
            # except:
            #  continue
            if edge not in visited or visited[edge] < weight:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path

def shortest_path(graph, start, end):
    visited, paths = dijkstra(graph, start)

    debug('paths ' + str(paths))

    full_path = deque()

    dest = paths[end]
    while dest != start:
        full_path.appendleft(dest)
        dest = paths[dest]

    full_path.appendleft(start)
    full_path.append(end)

    return None, list(full_path) # visited[end]

def longest_path(G,v,seen=None,path=None):
    if seen is None: seen = []
    if path is None: path = [v]

    seen.append(v)

    paths = []
    for t in G[v]:
        if t not in seen:
            t_path = path + [t]
            paths.append(tuple(t_path))
            paths.extend(longest_path(G, t, seen, t_path))
    return paths

# preference order of directions
ORDER = list(tron.DIRECTIONS)
random.shuffle(ORDER)

def debug(message):
    if DEBUG:
        tron.warn(message)

def compare_tile(tileA, tileB):
    if tileA[0] == tileB[0] and tileA[1] == tileB[1]:
        return True

    return False

def find_battlefield(floorDistancesMe, floorDistancesThem):
    battledfield = []
    minDistance = min(len(floorDistancesMe), len(floorDistancesThem))
    distance = 0

    for i in range(0, minDistance):
        for nodeMe in floorDistancesMe[i]:
            for nodeThem in floorDistancesThem[i]:
                if compare_tile(nodeMe.tile, nodeThem.tile):
                    distanceNode = GraphNode(nodeMe.parent, nodeMe.tile, distance)
                    distanceNode.children = nodeMe.children
                    battledfield.append(distanceNode)

        distance += 1

    return battledfield

def gather_cells(distance, floorDistances, floorTiles, node):
    if distance >= len(floorDistances):
        floorDistances.append([])

    children = []
    floorCells = filter(lambda cell: board[cell] == tron.FLOOR, board.adjacent(node.tile))
    for floorTile in floorCells:
        if floorTile not in floorTiles:
            childNode = GraphNode(node, floorTile)
            node.children.append(childNode)
            children.append(childNode)
            floorTiles.append(floorTile)
            floorDistances[distance].append(childNode)

    for child in children:
        floorDistances, node.children = gather_cells(distance + 1, floorDistances, floorTiles, child)

    return floorDistances, node.children

def which_move(board):
    debug('-----start move ----- ')

    graph = Graph()

    for x in range(0, board.width):
        for y in range(0, board.height):
            if board[(x, y)] == tron.FLOOR or board[(x,y)] == tron.ME :
                graph.add_node((x, y))

    for x in range(0, board.width):
        for y in range(0, board.height):
            if board[(x, y)] == tron.FLOOR or board[(x, y)] == tron.ME:
                adjacentCells = filter(lambda cell: board[cell] == tron.FLOOR or board[cell] == tron.ME, board.adjacent((x, y)))
                for adjacentCell in adjacentCells:
                    #if (x,y) not in graph.edges[adjacentCell] and adjacentCell not in graph.edges[(x,y)]:
                    graph.add_edge((x, y), adjacentCell, -1)

    floorDistancesMe = []
    floorTilesMe = []
    rootMe = GraphNode(None, board.me())
    floorDistancesMe, floorTilesMe = gather_cells(0, floorDistancesMe, floorTilesMe, rootMe)

    floorDistancesThem = []
    floorTilesThem = []
    rootThem = GraphNode(None, board.them())
    floorDistancesThem, floorTilesThem = gather_cells(0, floorDistancesThem, floorTilesThem, rootThem)

    battlefield = find_battlefield(floorDistancesMe, floorDistancesThem)

    nodeMove = None

    #if losing, cut the battlefield
    if len(battlefield)> 0 and len(floorDistancesMe) < len(floorDistancesThem):
         _, full_path = shortest_path(graph, board.me(), battlefield[0].tile)
         if len(full_path) > 1:
             nodeMove = full_path[1]
             debug('shortest path ' + str(full_path))
    else:
        # if winning, find longest path
        all_paths = longest_path(graph.edges, board.me())
        max_len = 0
        max_paths = []
        if len(all_paths) > 0:
            max_len   = max(len(p) for p in all_paths)
            max_paths = [p for p in all_paths if len(p) == max_len]

        if len(max_paths) > 0 and len(max_paths[0]) > 1:
            nodeMove = max_paths[0][1]
            debug('longest path ' + str(max_paths[0]))


    debug('me ' + str(board.me()))

    if nodeMove != None:
        nodeMove = GraphNode(None, nodeMove)

    if nodeMove != None:
        relative = (nodeMove.tile[0] - board.me()[0], nodeMove.tile[1] - board.me()[1])

        debug('rel ' + str(relative))
        debug('moving to ' + str(nodeMove.tile))

        # why is there no util for this?!
        direction = 0
        if relative == (0, 1):
            direction = tron.EAST
        elif relative == (0, -1):
            direction = tron.WEST
        elif relative == (1, 0):
            direction = tron.SOUTH
        elif relative == (-1, 0):
            direction = tron.NORTH

        # if board.passable(nodeMove.tile):
        #    return direction
        isAdjacentToThem = False
        for tile in board.adjacent(board.them()):
            if compare_tile(nodeMove.tile, tile):
                isAdjacentToThem = True
                break

        if direction in board.moves():  # and isAdjacentToThem == False:
            debug('using node move ' + str(direction))
            return direction

    debug('choosing wall')
    decision = board.moves()[0]
    foundMove = False

    return decision

    for dir in ORDER:

        # where we will end up if we move this way
        dest = board.rel(dir)

        # destination is passable?
        if not board.passable(dest):
            continue

        # positions adjacent to the destination
        adj = board.adjacent(dest)

        skip = False
        # if any wall adjacent to the destination
        for pos in adj:
            if board[pos] == tron.THEM:
                skip = True

        if skip == False:
            for pos in adj:
                if board[pos] == tron.WALL:
                    decision = dir
                    foundMove = True
                    debug('using wall hug ' + str(decision))
                    break

    if foundMove == False or not board.passable(board.rel(decision)):
        debug('using first passable')
        for dir in ORDER:

            # where we will end up if we move this way
            dest = board.rel(dir)

            # destination is passable?
            if not board.passable(dest):
                continue

            # decision = dir

            # positions adjacent to the destination
            adj = board.adjacent(dest)

            # if any wall adjacent to the destination
            for pos in adj:
                if board[pos] == tron.THEM:
                    break

                decision = dir
                foundMove = True
                break

    return decision


# make a move each turn
for board in tron.Board.generate():
    tron.move(which_move(board))

