import util 
from util import Belief, pdf 
from engine.const import Const
import random as rd
import math 

# Class: Estimator
#----------------------
# Maintain and update a belief distribution over the probability of a car being in a tile.
class Estimator(object):
    def __init__(self, numRows: int, numCols: int):
        self.belief = util.Belief(numRows, numCols) 
        self.transProb = util.loadTransProb() 
        self.first = True
            
    ##################################################################################
    # [ Estimation Problem ]
    # Function: estimate (update the belief about a StdCar based on its observedDist)
    # ----------------------
    # Takes |self.belief| -- an object of class Belief, defined in util.py --
    # and updates it *inplace* based onthe distance observation and your current position.
    #
    # - posX: x location of AutoCar 
    # - posY: y location of AutoCar 
    # - observedDist: current observed distance of the StdCar 
    # - isParked: indicates whether the StdCar is parked or moving. 
    #             If True then the StdCar remains parked at its initial position forever.
    # 
    # Notes:
    # - Carefully understand and make use of the utilities provided in util.py !
    # - Remember that although we have a grid environment but \
    #   the given AutoCar position (posX, posY) is absolute (pixel location in simulator window).
    #   You might need to map these positions to the nearest grid cell. See util.py for relevant methods.
    # - Use util.pdf to get the probability density corresponding to the observedDist.
    # - Note that the probability density need not lie in [0, 1] but that's fine, 
    #   you can use it as probability for this part without harm :)
    # - Do normalize self.belief after updating !!

    ###################################################################################
    def changefirst(self):
        self.first = False
        return 
    def gensamples(self, totalsamples, distributions) -> list:
        distribution = []
        numrows = len(distributions)
        numcols = len(distributions[0])
        cells = numrows * numcols
        grid = [i for i in range(cells)]
        for i in range(numrows):
            for j in range(numcols):
                distribution.append(distributions[i][j])  
        new_samples = []      
        random_choice = rd.choices(grid, distribution, k = totalsamples)    
        for i in range(totalsamples):           
            rownumber = random_choice[i] // numcols
            colnumber = random_choice[i] % numcols
            new_samples.append((rownumber, colnumber))
        return new_samples
    
    def probfromsamples(self, samples, numrows, numcols):
        distribution = [[0 for j in range(numcols)] for i in range(numrows)]
        for i in range(len(samples)):
            distribution[samples[i][0]][samples[i][1]] += 1
        cells = numcols*numrows
        for i in range(len(distribution)):
            for j in range(len(distribution[0])):
                distribution[i][j] = distribution[i][j]/len(samples)
        return distribution
    
    def transition(self, sample, numrows, numcols):
        distribution = [[0.0000000000000000000000000000000000000000000000000000001 for j in range(numcols)] for i in range(numrows)]
        for i in range(numrows):
            for j in range(numcols):
                if (sample, (i, j)) in self.transProb.keys():
                    p = self.transProb[(sample, (i, j))]
                    distribution[i][j] = p
        sample = self.gensamples(1, distribution)[0]
     
        return sample
    
    def alltransitions(self, samples, numrows, numcols):
        newsamples = []
        for sample in samples:
            newsamples.append(self.transition(sample, numrows, numcols))
        return newsamples
    
    def weightofsample(self, sample, incidenctvariable, mycoordinate, deviation):
        positionsampleX = util.colToX(sample[1])
        positionsampleY = util.rowToY(sample[0])
        mean = math.sqrt((positionsampleX - mycoordinate[0])**2 + (positionsampleY - mycoordinate[1])**2)
        val = pdf(mean, deviation, incidenctvariable)
        return val
    
    def weightedsamples(self, samples, incidenctvariable, mycoordinate, deviation):
        weightedsamples = []
        for sample in samples:
            newsample = [sample]
            newsample.append(self.weightofsample(sample, incidenctvariable, mycoordinate, deviation))
            weightedsamples.append(newsample)
        return weightedsamples
    
    def wtdistribution(self, samples, numrows, numcols):
        distribution = [[0 for j in range(numcols)] for i in range(numrows)]
        for i in range(len(samples)):
            distribution[samples[i][0][0]][samples[i][0][1]] += samples[i][1]
        sum = 0
        for i in range(numrows):
            for j in range(numcols):
                sum += distribution[i][j]
        for i in range(numrows):
            for j in range(numcols):
                distribution[i][j] = distribution[i][j]/sum
        return distribution
        
            
        
        
        
    def estimate(self, posX: float, posY: float, observedDist: float, isParked: bool) -> None:
        # BEGIN_YOUR_CODE
        totalsamples = 1000
        numrows = self.belief.numRows
        numcols = self.belief.numCols
        # generated samples
        samples = []
        initialdist = [[0 for j in range(numcols)] for i in range(numrows)]

        # if self.first == True:
        #     samples = self.gensamples(10, self.belief.grid)
        #     self.changefirst()
        samples = self.gensamples(totalsamples, self.belief.grid)

        # transitioned samples to new location incoroporating transition probabilities
        transitionsamples = self.alltransitions(samples, numrows, numcols)
        # weight of each sample
        deviation = Const.SONAR_STD
        col = util.xToCol(posX)
        row = util.yToRow(posY)
        wtsamples = self.weightedsamples(transitionsamples, observedDist, (posX, posY), deviation)
        # weighted distribution
        wtdist = self.wtdistribution(wtsamples, numrows, numcols)
        # generating new samples from weighted distribution
        finalsamples = self.gensamples(totalsamples, wtdist)
        # generating final distribution
        finaldistribution = self.probfromsamples(finalsamples, numrows, numcols)
        for i in range(numrows):
            for j in range(numcols):
                self.belief.setProb(i, j, finaldistribution[i][j])
        # for hue in self.belief.grid:
        #     print(hue)
        # print("---------------")
        return
  
    def getBelief(self) -> Belief:
        return self.belief

   