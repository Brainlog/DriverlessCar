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
            spread = 5
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
    

    
    def backuputils(self, originalmatrix, matrix, iterations):
        backupmatrix = [[0 for j in range(len(matrix[0]))] for i in range(len(matrix))]
        backupmatrix = matrix.copy()
        for k in range(iterations):
            for i in range(len(matrix)):
                for j in range(len(matrix[0])):
                    if originalmatrix[i][j] != 0 and originalmatrix[i][j] != 4 and originalmatrix[i][j] != 2:
                        lis = [(i+1,j), (i+1,j+1), (i+1,j-1), (i-1,j), (i-1,j+1), (i-1,j-1), (i,j+1), (i,j-1)]
                        for elem in lis:
                            if self.existcheck(elem, matrix) == True:
                                if (elem, (i,j)) in self.transProb.keys():
                                    p = self.transProb[(elem, (i,j))]
                                    a = (0.1*p*backupmatrix[elem[0]][elem[1]])
                                    backupmatrix[i][j] += a
                                else:
                                    discount = 0.001
                                    a = (discount*backupmatrix[elem[0]][elem[1]])
                                    backupmatrix[i][j] += a

            
        return backupmatrix
    
    def recursematrix(self, matrix, safematrix, discount, coordinate):
        newmatrix = safematrix.copy()
        def recurse(discount, coordinate):
            if self.existcheck(coordinate, safematrix) == True:
                    lis = [(coordinate[0]+1,coordinate[1]), (coordinate[0]+1,coordinate[1]+1), (coordinate[0]+1,coordinate[1]-1), (coordinate[0]-1,coordinate[1]), (coordinate[0]-1,coordinate[1]+1), (coordinate[0]-1,coordinate[1]-1), (coordinate[0],coordinate[1]+1), (coordinate[0],coordinate[1]-1)]
                    for elem in lis:
                        if self.existcheck(elem, safematrix) == True:
                            if newmatrix[elem[0]][elem[1]] == 0 and matrix[elem[0]][elem[1]] == 1:
                                newmatrix[elem[0]][elem[1]] += newmatrix[coordinate[0]][coordinate[1]]*discount
                                recurse(discount, elem)
            return 
        recurse(discount, coordinate)
        return newmatrix
    
    def recursematrixfull(self, matrix, safematrix, discount):
        newmatrix = safematrix.copy()
        for i in range(len(safematrix)):
            for j in range(len(safematrix[0])):
                if safematrix[i][j] != 0:
                    newmatrix = self.recursematrix(matrix, newmatrix, discount, (i,j))
        return newmatrix
        
                    
                    
                       
    def rewardforstates(self, matrix):
        numrows = len(matrix)
        numcols  = len(matrix[0])
        safematrix = [[0 for x in range(numcols)] for y in range(numrows)]
        for i in range(len(safematrix)):
            for j in range(len(safematrix[0])):
                if matrix[i][j] == 2: # goals
                    safematrix[i][j] = 1000
                if matrix[i][j] == 2 and (i,j) == self.checkPoints[0]:
                    safematrix[i][j] = 10000
        for i in range(len(safematrix)):
            for j in range(len(safematrix[0])):
                if matrix[i][j] == 4: # moving obstacles
                    safematrix[i][j] = -1000
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
    
    def bfs(self, matrix, u, end):
        queue = []
        dict = {}
        dict[0] = u
        curr = 0
        allnodes = []
        queue.append([u, curr])
        allnodes.append(u)
        while len(queue) != 0:
            element = queue.pop(0)
            level = element[1]+1
            node = element[0]
            if node == end:
                print("found")
                return dict
            matrix[node[0]][node[1]][1] = 1
            print(matrix[node[0]][node[1]])
            lis = [(node[0]+1,node[1]), (node[0]+1,node[1]+1), (node[0]+1,node[1]-1), (node[0]-1,node[1]), (node[0]-1,node[1]+1), (node[0]-1,node[1]-1), (node[0],node[1]+1), (node[0],node[1]-1)]
            for elem in lis:
                if self.existcheck(elem, matrix) == True:
                    if matrix[elem[0]][elem[1]][0] == 1 and matrix[elem[0]][elem[1]][1] == 0:
                        queue.append([elem, level])
                        if level in dict.keys():
                            dict[level].append(elem)
                        else:
                            dict[level] = [elem]
                   
        return None
    
    
    def indexbound(self, maxrow, maxcol, row, col):
        if (row < 0 or row >= maxrow or col < 0 or col >= maxcol):
            return False
        else:
            return True
  
    def printmat(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                print(matrix[i][j],end=" ")
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

    def shortestpathTraj(self, grid, start, goal, debug): #using bfs, #we can go to 1, 0 means blocked
        (srow,scol)=start
        (grow,gcol)=goal
        printingmatrix = grid.copy() 
        queue = []
        queue.append(((srow,scol),0))
        traj = []
        pathdict = {}
        pathgot = False
        # 
        i=0
        visitdict = {}
        # while(i<10):
        while(len(queue)>0 or not(pathgot)):
            print(queue[0])
            currcell = queue[0][0]
            level = queue[0][1]
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
                    printingmatrix[neighbour[0]][neighbour[1]] = 'X'
                    destcell = currcell
                    traj.append(currcell)
                    printingmatrix[currcell[0]][currcell[1]] = 'X'
                    
                    while(destcell!=start):
                        destcell = pathdict[(level,destcell)]
                        traj.append(destcell)
                        printingmatrix[destcell[0]][destcell[1]] = 'X'
                        level -=1
                        
                    traj.reverse()
                    if(debug):
                        self.printmat(printingmatrix)
                        print(traj)
                    return traj
                nr = neighbour[0]
                nc = neighbour[1]
                if(self.indexbound(len(grid),len(grid[0]),nr,nc)):
                    if(grid[nr][nc]==1):
                        if(neighbour not in visitdict.keys()):
                            queue.append((neighbour,level+1))
                            pathdict[(level+1,neighbour)] = currcell
                            visitdict[neighbour] = 1
            i+=1
                        
        return None #goal cannot be reached
                
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
        states = (self.graphview(graph, beliefOfOtherCars, parkedCars, chkPtsSoFar))
        
        safematrix = self.rewardforstates(states)
        backupmatrix = self.recursematrixfull(states, safematrix, 0.9)
        finalmatrix = self.blockways(states, backupmatrix)
        # print(self.checkPoints)
        # # finalmatrix = self.normalize(finalmatrix2)
        # for line in finalmatrix:
        #     print(line)
        # print("-----------------------")
        currPos = self.getPos()
        col  = util.xToCol(currPos[0])
        row  = util.yToRow(currPos[1])
        currloc = (row, col)      
        lis = [(row+1,col), (row+1,col+1), (row+1,col-1), (row-1,col), (row-1,col+1), (row-1,col-1), (row,col+1), (row,col-1)]
        
        maxindex = lis[0]
        for elem in lis:
            if self.existcheck(elem, finalmatrix) == True:
                if finalmatrix[elem[0]][elem[1]] >= finalmatrix[maxindex[0]][maxindex[1]]:
                    maxindex = elem  
        print(maxindex , "    THIS IS THE MAX INDEX")
        posx = util.colToX(maxindex[1])
        posy = util.rowToY(maxindex[0])
        if currloc == self.checkPoints[0]:
            self.checkPoints.pop(0)
        newmatrix = [[0 for x in range(len(states[0]))] for y in range(len(states))]
        for i in range(len(states)):
            for j in range(len(states[0])):
                newmatrix[i][j] = [states[i][j],0]
        path = self.shortestpathTraj(states,currloc,self.checkPoints[0],True)
        print(path)
        
        
        # path = (self.dfs(states, currloc, self.checkPoints[0]))
        # print(currloc)
        # print(self.checkPoints[0])
        # print(path)
        
        if len(path) == 1:
            posx = util.colToX(path[0][1])
            posy = util.rowToY(path[0][0]) 
        else:
            posx = util.colToX(path[1][1])
            posy = util.rowToY(path[1][0])     
        
        if currloc == self.checkPoints[0]:
            return (posx, posy), False      
            
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
    
    