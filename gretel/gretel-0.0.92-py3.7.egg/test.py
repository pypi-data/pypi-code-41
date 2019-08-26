
path = "_hello"
for i in range(0, len(path)-1):
    for j in range(0, i+1+1):
        if i == j:
            continue
        else:
            print(path[i], path[j], i, j)
print('#', path[-1], '_', i, i+1)

print("***")

path = "_hello"
#for j in range(1, len(path)):
#    for i in range(0, j):
#        print(path[i], path[j], i, j)
#
for i in range(len(path)-1):
    print(path[i], path[i+1], i, i+1)
for j in range(1, len(path)):
    for i in range(0, j-1):
        #print(path[i], path[j], i, j)
        print(path[j], path[i], j, i)
