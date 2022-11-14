dict = {}
if dict == {}:
    dict[(1,2)]=[]
    dict[(2,3)]=[]
dict[(1,2)].append(2)
dict[(2,3)].append(4)
dict[(1,2)].append(3)
# dict[1].append(3)
l = dict[(1,2)]
l.reverse()
print(dict)

