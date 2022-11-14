'''
Licensing Information: Please do not distribute or publish solutions to this
project. You are free to use and extend Driverless Car for educational
purposes. The Driverless Car project was developed at Stanford, primarily by
Chris Piech (piech@cs.stanford.edu). It was inspired by the Pacman projects.
'''
import util
import itertools
from turtle import Vec2D
from engine.const import Const
from engine.vector import Vec2d
from engine.model.car.car import Car
from engine.model.layout import Layout
from engine.model.car.junior import Junior
from configparser import InterpolationMissingOptionError

# Class: Graph
# -------------
# Utility class
class Graph(object):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

# Class: IntelligentDriver
# ---------------------
# An intelligent driver that avoids collisions while visiting the given goal locations (or checkpoints) sequentially. 
class IntelligentDriver(Junior):
    # Funciton: Init
    def __init__(self, layout: Layout):
        self.burnInIterations = 30
        self.layout = layout 
        self.mycheckpoints = []
        # self.worldGraph = None
        self.worldGraph = self.createWorldGraph()
        self.checkPoints = self.layout.getCheckPoints() # a list of single tile locations corresponding to each checkpoint
        self.transProb = util.loadTransProb()
        
    # ONE POSSIBLE WAY OF REPRESENTING THE GRID WORLD. FEEL FREE TO CREATE YOUR OWN REPRESENTATION.
    # Function: Create World Graph
    # ---------------------
    # Using self.layout of IntelligentDriver, create a graph representing the given layout.
    def createWorldGraph(self):
        nodes = []
        edges = []
        # create self.worldGraph using self.layout
        numRows, numCols = self.layout.getBeliefRows(), self.layout.getBeliefCols()

        # NODES #
        ## each tile represents a node
        nodes = [(x, y) for x, y in itertools.product(range(numRows), range(numCols))]
        
        # EDGES #
        ## We create an edge between adjacent nodes (nodes at a distance of 1 tile)
        ## avoid the tiles representing walls or blocks#
        ## YOU MAY WANT DIFFERENT NODE CONNECTIONS FOR YOUR OWN IMPLEMENTATION,
        ## FEEL FREE TO MODIFY THE EDGES ACCORDINGLY.

        ## Get the tiles corresponding to the blocks (or obstacles):
        blocks = self.layout.getBlockData()
        blockTiles = []
        for block in blocks:
            row1, col1, row2, col2 = block[1], block[0], block[3], block[2] 
            # some padding to ensure the AutoCar doesn't crash into the blocks due to its size. (optional)
            row1, col1, row2, col2 = row1-1, col1-1, row2+1, col2+1
            blockWidth = col2-col1 
            blockHeight = row2-row1 

            for i in range(blockHeight):
                for j in range(blockWidth):
                    blockTile = (row1+i, col1+j)
                    blockTiles.append(blockTile)

        ## Remove blockTiles from 'nodes'
        nodes = [x for x in nodes if x not in blockTiles]

        for node in nodes:
            x, y = node[0], node[1]
            adjNodes = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
            
            # only keep allowed (within boundary) adjacent nodes
            adjacentNodes = []
            for tile in adjNodes:
                if tile[0]>=0 and tile[1]>=0 and tile[0]<numRows and tile[1]<numCols:
                    if tile not in blockTiles:
                        adjacentNodes.append(tile)

            for tile in adjacentNodes:
                edges.append((node, tile))
                edges.append((tile, node))
        return Graph(nodes, edges)

    #######################################################################################
    # Function: Get Next Goal Position
    # ---------------------
    # Given the current belief about where other cars are and a graph of how
    # one can driver around the world, chose the next position.
    #######################################################################################
    
    def graphview(self, graph, beliefOfOtherCars: list, parkedCars:list , chkPtsSoFar: int):
        spread = 7
        nodes = graph.nodes
        edges = graph.edges
        rows = max([x[0] for x in nodes]) + 1
        cols = max([x[1] for x in nodes]) + 1
        matrix = [[0 for x in range(cols)] for y in range(rows)]
        
        for edge in edges:
            matrix[edge[0][0]][edge[0][1]] = 1 # we can move from edge[0] to edge[1]
            matrix[edge[1][0]][edge[1][1]] = 1
            
            
        for point in self.checkPoints:
            matrix[point[0]][point[1]] = 2 # 2 is for checkpoints
            
        mylocation = self.getPos()
        col = util.xToCol(mylocation[0])
        row = util.yToRow(mylocation[1])
        matrix[row][col] = 3  # my location
        
        
        obstacles = []
        for car in beliefOfOtherCars:
            maxindex = (0,0)
            carobs = []
            for i in range(len(car.grid)):
                for j in range(len(car.grid[i])):
                    carobs.append((car.grid[i][j],i,j))
            carobs.sort(reverse=True)
            for i in range(spread):
                obstacles.append((carobs[i][1],carobs[i][2]))
                    
        
        for obstacle in obstacles:
            matrix[obstacle[0]][obstacle[1]] = 4 # 4 is for obstacles
              
        return matrix
    
    def existcheck(self, coordinate, matrix):
        numrows = len(matrix)
        numcols = len(matrix[0])
        if coordinate[0] >= 0 and coordinate[0] < numrows and coordinate[1] >= 0 and coordinate[1] < numcols:
            return True
        return False
              
    def safetymatrix(self, matrix):
        numrows = len(matrix)
        numcols  = len(matrix[0])
        safematrix = [[0 for x in range(numcols)] for y in range(numrows)]
        for i in range(len(safematrix)):
            for j in range(len(safematrix[0])):
                if matrix[i][j] == 4: # moving obstacles
                    safematrix[i][j] = 100
                elif matrix[i][j] == 0:
                    safematrix[i][j]= 1000
                # elif i == 0 or j == 0 or j == numcols-1 or i == numrows-1:
                    # safematrix[i][j] = 1000
                elif matrix[i][j] == 2:
                    safematrix[i][j] = 2
                else:
                    safematrix[i][j] = matrix[i][j]
        return safematrix
    
    def blockways(self, matrix, safematrix):
        newmatrix = [[0 for x in range(len(matrix[0]))] for y in range(len(matrix))]
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] == 0:
                    newmatrix[i][j] = -10000
                elif i == 0 or j == 0 or i == len(matrix)-1 or j == len(matrix[0])-1:
                    newmatrix[i][j] = -10000
                else:
                    a = safematrix[i][j]
                    newmatrix[i][j] = a
        return newmatrix
    
    def normalize(self, matrix):
        newmatrix = [[-10000 for x in range(len(matrix[0]))] for y in range(len(matrix))]
        sum = 0
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] != -10000:
                    sum += matrix[i][j]
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] != -10000:
                    newmatrix[i][j] = matrix[i][j]/sum
        return newmatrix
 
    def indexbound(self, maxrow, maxcol, row, col):
        if (row < 0 or row >= maxrow or col < 0 or col >= maxcol):
            return False
        else:
            return True
  
    def printmat(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                val = len(str(matrix[i][j]))
                sp = ' '
                print(matrix[i][j],end=sp*(6-val))
            print()
        return
  
    def neighblist(self, cell):
        crow = cell[0]
        ccol = cell[1]
        neighbours = []
        neighbours.append((crow-1,ccol))
        neighbours.append((crow+1,ccol))
        neighbours.append((crow,ccol-1))
        neighbours.append((crow,ccol+1))
        neighbours.append((crow-1,ccol-1))
        neighbours.append((crow-1,ccol+1))
        neighbours.append((crow+1,ccol-1))
        neighbours.append((crow+1,ccol+1))
        return neighbours

    def shortestpathTraj(self, grid, start, goal, debug, movingconsider): #using bfs, #we can go to 1, 0 means blocked
        (srow,scol)=start
        (grow,gcol)=goal
        printingmatrix = grid.copy() 
        queue = []
        # if(grid[srow][scol]!=1000):
        queue.append((grid[srow][scol],(srow,scol),0))
        traj = []
        pathdict = {}
        pathgot = False
        print(f'QUEUE: {queue} GRID INITIAL:')
        self.printmat(printingmatrix)
        visitdict = {}
        i=0
        while(len(queue)>0 and not(pathgot)):
            cellvalue = queue[0][0]
            currcell = queue[0][1]
            level = queue[0][2]
            queue.pop(0)
            visitdict[currcell] = 1
            neighbours = self.neighblist(currcell)
            for neighbour in neighbours:
                if(neighbour==goal):
                    if(debug):
                        print(f'GOAL REACHED: {neighbour}')
                    pathgot = True
                    destcell = neighbour
                    traj.append(neighbour)
                    printingmatrix[neighbour[0]][neighbour[1]] = 'X.X'
                    destcell = currcell
                    traj.append(currcell)
                    printingmatrix[currcell[0]][currcell[1]] = 'X.X'
                    
                    while(destcell!=start):
                        destcell = pathdict[(level,destcell)]
                        traj.append(destcell)
                        printingmatrix[destcell[0]][destcell[1]] = 'X.X'
                        level -=1
                        
                    traj.reverse()
                    if(debug):
                        print(f'GRID with PATH: ')
                        self.printmat(printingmatrix)
                        print(f'PATH FROM DJIKSTRA: {traj}')
                        
                    return traj
                nr = neighbour[0]
                nc = neighbour[1]
                if(self.indexbound(len(grid),len(grid[0]),nr,nc)):
                    if(neighbour not in visitdict.keys()):
                        if(grid[nr][nc]!=1000):
                            queue.append((grid[nr][nc]+((level+1)*0.1),neighbour,level+1))
                            pathdict[(level+1,neighbour)] = currcell
                            visitdict[neighbour] = 1
                        # elif(grid[nr][nc]==100):
                            
                    else:
                        pass
                        # if(grid[nr][nc]>=0 and grid[nr][nc]!=1000):
                        #     queue.append((grid[nr][nc]+((level+1)*100),neighbour,level+1))
                        #     pathdict[(level+1,neighbour)] = currcell
                        #     visitdict[neighbour] = 1
                            
                                
            queue.sort()
            
            i+=1
                        
        return traj #goal cannot be reached
                
# matrix1 = [[1 for i in range(10)] for j in range(6)]
    
  
    def ispathsafe(self, matrix, path):
        pass
    
    def iswesafe(self, matrix, coordinate):
        pass
 
      
    def getNextGoalPos(self, beliefOfOtherCars: list, parkedCars:list , chkPtsSoFar: int):
        '''
        Input:
        - beliefOfOtherCars: list of beliefs corresponding to all cars
        - parkedCars: list of booleans representing which cars are parked
        - chkPtsSoFar: the number of checkpoints that have been visited so far 
                       Note that chkPtsSoFar will only be updated when the checkpoints are updated in sequential order!
        
        Output:
        - goalPos: The position of the next tile on the path to the next goal location.
        - moveForward: Unset this to make the AutoCar stop and wait.

        Notes:
        - You can explore some files "layout.py", "model.py", "controller.py", etc.
         to find some methods that might help in your implementation. 
        '''
        graph = self.worldGraph
        movingobstacles = True
        states = (self.graphview(graph, beliefOfOtherCars, parkedCars, chkPtsSoFar))

        currPos = self.getPos()
        col  = util.xToCol(currPos[0])
        row  = util.yToRow(currPos[1])
        currloc = (row, col)      
       

            
        
        newmatrix = [[0 for x in range(len(states[0]))] for y in range(len(states))]
        for i in range(len(states)):
            for j in range(len(states[0])):
                newmatrix[i][j] = [states[i][j],0]
        # if self.mycheckpoints == []:
        safetystates = self.safetymatrix(states)
        path = self.shortestpathTraj(safetystates,currloc,self.checkPoints[0],True, False)
        print(f'SEARCHED FROM SRC: {currloc} TO DEST: {self.checkPoints[0]}, obtained path {path}')

        posx = currPos[0]
        posy = currPos[1]


            
        if len(path) == 1:
            posx = util.colToX(path[0][1])
            posy = util.rowToY(path[0][0]) 
        elif path != []:
            # print(path)
            print(f'Obtained path by simple BFS: {path} from src: {currloc} to dest: {self.checkPoints[0]}')
            posx = util.colToX(path[1][1])
            posy = util.rowToY(path[1][0])  
        else:
            return currPos, False   
        
        # if currloc == self.checkPoints[0]:
        #     return (posx, posy), False   
        checkposx = 0
        checkposy = 0
        if len(self.checkPoints) >= 1:
            checkposx =  util.colToX(self.checkPoints[0][1])
            checkposy = util.rowToY(self.checkPoints[0][1])
        if len(self.checkPoints)>1 and currloc == self.checkPoints[0]:
            self.checkPoints.pop(0)
           
            
        return (posx, posy), True
        


        
       
        return goalPos, moveForward

    # DO NOT MODIFY THIS METHOD !
    # Function: Get Autonomous Actions
    # --------------------------------
    
    def djikstra(self, graph, start, end):
        dist = {}
        prev = {}
        for node in graph:
            dist[node] = float('inf')
            prev[node] = None
        dist[start] = 0
        Q = set(graph)
        while Q:
            u = min(Q, key=dist.get)
            Q.remove(u)
            if dist[u] == float('inf'):
                break
            for v in graph[u]:
                alt = dist[u] + graph[u][v]
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
        path = []
        u = end
        while prev[u]:
            path.append(u)
            u = prev[u]
        path.append(u)
        path.reverse()
        return path
    
    
    
    
    def getAutonomousActions(self, beliefOfOtherCars: list, parkedCars: list, chkPtsSoFar: int):
        # Don't start until after your burn in iterations have expired
        if self.burnInIterations > 0:
            self.burnInIterations -= 1
            return[]
       
        goalPos, df = self.getNextGoalPos(beliefOfOtherCars, parkedCars, chkPtsSoFar)
        vectorToGoal = goalPos - self.pos
        wheelAngle = -vectorToGoal.get_angle_between(self.dir)
        driveForward = df
        actions = {
            Car.TURN_WHEEL: wheelAngle
        }
        if driveForward:
            actions[Car.DRIVE_FORWARD] = 1.0
        return actions
    
    