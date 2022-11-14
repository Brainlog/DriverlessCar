def transition(self, sample, numrows, numcols):
        spread = 5
        # distribution = [[0.0000000000000000000000000000000000000000000000000000001 for j in range(numcols)] for i in range(numrows)]
        samplerow = sample[0]
        samplecol = sample[1]
        rangerow = [samplerow-spread, samplerow + spread]
        rangecol = [samplecol-spread,samplecol+spread]
        if rangerow[0] < 0:
            rangerow = [0,rangerow[1]]
        if rangerow[1] >= numrows:
            rangerow = [rangerow[0], numrows-1]
        if rangecol[0] < 0:
            rangecol = [0, rangecol[1]]
        if rangecol[1] >= numcols:
            rangecol = [rangecol[0], numcols-1]
        
        t = self.existornot((rangerow[0],rangecol[0]), numrows, numcols)
        t &= self.existornot((rangerow[1], rangecol[1]), numrows, numcols)
        newdistribution = [[0.00000000000000000000000000000000000001 for j in range(0,rangecol[1]-rangecol[0])] for i in range(0,rangerow[1]-rangerow[0])]
        # print(t, " this is t")        
        for i in range(0,rangerow[1]-rangerow[0]):
            for j in range(rangecol[1]-rangecol[1]):
                    if (sample, (i, j)) in self.transProb.keys():
                        p = self.transProb[(sample, (i, j))]
                        newdistribution[i][j] = p
        initials = [rangerow[0], rangecol[0]]
        # newdistribution = [[0 for j in range(rangecol[1]-rangecol[0])] for i in range(rangerow[1]-rangerow[0])]
        # (0, 2*spread)
        # (samplerow-spread, )
        # print(rangerow, " this is range")
        # print(rangecol, " this is column range")
        sample = self.gensamples(1, newdistribution)[0]
        sample = (sample[0]+initials[0], sample[1] + initials[1])
     
        return sample