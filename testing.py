
        
def pred_traj (self, currLoc, prevLoc, grid, trajMarknum, trajwidth, debugmode):
        (currx,curry) = currLoc #currx = rownum, #curry = colnum
        (prevx,prevy) = prevLoc
        StopParam = True
        Trajgrid = grid.copy()
        
        sidewidth = trajwidth//2
        travelmode = None
        if(currx==prevx and curry==prevy+1): #moving right #debugged #final
            for i in range(curry,len(Trajgrid[0])):
                for j in range(currx-sidewidth,currx+sidewidth+1):
                    if(j>=0 and j<len(Trajgrid)):
                        Trajgrid[j][i] = trajMarknum                
            StopParam = False
            travelmode = "right"
        elif (currx==prevx and curry==prevy-1): #moving left #debugged #final
            for j in range(curry,-1,-1):
                for i in range(currx-sidewidth,currx+sidewidth+1):
                    if(j>=0 and j<len(Trajgrid[0])):
                        Trajgrid[i][j] = trajMarknum
            StopParam = False
            travelmode = "left"
        elif(curry==prevy and currx==prevx+1): #moving down #debugged #final
            for i in range(currx,len(Trajgrid[0])):
                for j in range(curry-sidewidth,curry+sidewidth+1):
                    if(i>=0 and i<len(Trajgrid)):
                        Trajgrid[i][j] = trajMarknum
            StopParam = False
            travelmode = "down"
        elif(curry==prevy and currx==prevx-1): #moving up #debugged #final
            for i in range(currx,-1,-1):
                for j in range(curry-sidewidth,curry+sidewidth+1):
                    if(i>=0 and i<len(Trajgrid)):
                        Trajgrid[i][j] = trajMarknum
            StopParam = False
            travelmode = "up"
        elif(currx==prevx+1 and curry==prevy+1): #moving down right #debugged #final
            for yshift in range(curry, curry+sidewidth+1):
                for i in range(yshift,len(Trajgrid[0])):
                    j = currx -yshift + i
                    if(j>=0 and j<len(Trajgrid)):
                        Trajgrid[j][i] = trajMarknum
            for xshift in range(currx, currx+sidewidth+1):
                for j in range(xshift,len(Trajgrid)):
                    i = curry + (j-xshift)
                    if(i>=0 and i<len(Trajgrid[0])):
                        Trajgrid[j][i] = trajMarknum                    
            StopParam = False
            travelmode = "downright"
        elif(currx==prevx-1 and curry==prevy-1): #moving up left #debugged #final
            for yshift in range(curry, curry-sidewidth-1,-1):
                for i in range(yshift,-1,-1):
                    j = currx - (yshift-i)
                    if(j>=0 and j<len(Trajgrid[0])):
                        Trajgrid[j][i] = trajMarknum
            for xshift in range(currx, currx-sidewidth-1,-1):
                for j in range(xshift,-1,-1):
                    i = curry - (xshift-j)
                    if(i>=0 and i<len(Trajgrid)):
                        Trajgrid[j][i] = trajMarknum
            StopParam = False
            travelmode = "upleft"
        elif(currx==prevx-1 and curry==prevy+1): #moving up right #debugged #final
            for yshift in range(curry, curry+sidewidth+1):
                for i in range(yshift,len(Trajgrid[0])):
                    j = currx + (yshift-i)
                    if(j>=0 and j<len(Trajgrid)):
                        Trajgrid[j][i] = trajMarknum
            for xshift in range(currx, currx-sidewidth-1,-1):
                for j in range(xshift,-1,-1):
                    i = curry - (j-xshift)
                    if(i>=0 and i<len(Trajgrid[0])):
                        Trajgrid[j][i] = trajMarknum
            StopParam = False
            travelmode = "upright"
        elif(currx==prevx+1 and curry==prevy-1): #moving down left #debugged #final
            for yshift in range(curry, curry-sidewidth-1,-1):
                for i in range(yshift,-1,-1):
                    j = currx - (i-yshift)
                    if(j>=0 and j<len(Trajgrid)):
                        Trajgrid[j][i] = trajMarknum
            for xshift in range(currx, currx+sidewidth+1):
                for i in range(xshift,len(Trajgrid)):
                    j = curry + (xshift-i)
                    if(j>=0 and j<len(Trajgrid[0])):
                        Trajgrid[i][j] = trajMarknum
            StopParam = False 
            travelmode = "downleft"           
        elif(currx==prevx and curry==prevy): #stopped
            StopParam = True
            travelmode = "stop"
        else:
            StopParam = True
            travelmode = "couldn't fetch travel mode"
        if(debugmode):
            print(f'TRAVEL MODE: {travelmode}\n')
            Trajgrid[currx][curry] = 'C'
            Trajgrid[prevx][prevy] = "P"
            printmat(Trajgrid)
        
        return (Trajgrid, StopParam) #stop param true means: stop, false means: continue
def printmat(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(matrix[i][j],end=" ")
        print()
    return
        
matrix1 = [[0 for i in range(10)] for j in range(6)]
# printmat(matrix=matrix1)


matrix2 = pred_traj(self=0, currLoc=(3,5), prevLoc=(3,6), grid=matrix1, trajMarknum=1, trajwidth=3, debugmode=True)