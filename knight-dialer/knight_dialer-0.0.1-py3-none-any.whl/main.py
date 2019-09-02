
# the i-th item in this array is where you can move on the keypad from i
knight_moves = [[4,6],[6,8],[9,7],[4,8],[3,9,0],[],[1,7,0],[2,6],[1,3],[2,4]]

def KD_pure_recursion(todo, total_length=7):
    """
    The pure KD function is in some ways the easiest and in others the hardest 
    function to explain. It's the easiest in data structure, the input and the 
    output have to match and therefore must both be list of lists 1 deep.  
    Each level calls a dial function, which checks if it needs to dial, 
    and if it does, it keeps on tacking on digits.  It calls all the way down 
    the stack to the final digit, but then, critically, it returns the answer 
    back up the stack.  So at any i level, the function takes in a list of 
    dials of length i and returns a list of dials of length i+1. 

    Advantages to this strategy are that it is relatively easy to explain the 
    concept with handwaving although implementing the code involves some serious 
    thinking, and also that it runs a little bit faster than the other methods, 
    at least on my machine.
    """
    def dial(the_list_of_lists): # since this is a pure recursive function the input and output need to be of the same type.  In this case, a list of lists.
        return_val = [] # start an empty return list.  We will be adding to it later.  The idea is the return will be a list of lists since the input is a list of lists
        for the_list in the_list_of_lists: # we're going to crank through each input item and add to the return list
            if len(the_list) == total_length-1: # if we are 1 away from finished
                for i in knight_moves[the_list[-1]]: # for each possible move we're going to make
                    return_val += [the_list + [i]] # then we want the return list for something like an input of 6 to be [[6,1],[6,7],[6,0]] which we can then pass into the next level of dial(), adding another layer
            else: # if we're not 1 away from finished
                for i in knight_moves[the_list[-1]]: # for each possible move
                    return_val += dial([the_list + [i]]) # THE MAGIC HAPPENS HERE: add to the return list a dial value while maintaining the structure.  You want return_val to stay a two-level deep matrix so you need to add 1D arrays to the return_val, and you do that by adding the return_val onto itself
        return return_val # return the list of lists you generated up to the next level
        
    return dial(todo) # return the list



def KD_recursive_addition(todo,total_length=7):
    """
    This is a hybrid function, somewhere between the pure recursion and the 
    backtrack method. The recursive version of this KD function calls itself, 
    essentially, dial(dial(dial(...))) wherein each of the KD layers adds 
    another digit.  Once it hits the end it starts appending things to a done 
    list (which starts totally empty). The thing that distinguishes this from 
    a pure recursion is that in a pure recursion, we are calling down to the 
    final answer and returning the answer all the way back up the stack.  In 
    this hybrid method, the function calls itself but doesn't really care 
    about the structure of the returns.  Instead, it just cares that the answer, 
    once you make it to the final digit, i.e. dial() layered n deep, is added 
    to a totally separate list. This totally separate list is the answer to 
    each of the branches.  

    This method is pretty compact and at least a bit easier to understand than 
    pure recursion, and since you're not passing back up the stack the answer 
    you have some freedom in how you structure the data.  If you try to use this
    method to directly return the answer from dial, you'll find that you 
    get a nested answer n layers deep, where each level of the array holds
    more close answers.  E.g. [[[1,6,1],[1,6,7],[1,6,0]],[[1,8,1],[1,8,3]]] 
    which is not what you want.  (You could in principle reshape the data with
    numpy, but that's another story for another day.)
    
    """
    done=[] #start an empty done list
    
    def dial(the_list): # actually going to be a nested set of lists, but could be of any depth.  Not like in pure recursion which is specified to be a list of lists of depth 1
        for i in knight_moves[the_list[-1]]: # for each possible move
            if len(the_list) == total_length: # if it's at the end of the dial...
                done.append(the_list + [i]) # add it to the done list
            else:
                dial(the_list + [i]) # otherwise, go another layer deep
    [dial(i) for i in todo] # run the dialing algorithm to generate the done list
    return done



def KD_backtrack(todo,total_length=7):
    """
    This method is the easiest to explain, debug, and use.  This method 
    solves recursion problems using exactly zero recursion, which makes 
    them easy to understand.

    The backtrack version of this dial function creates a todo list. It 
    then enters a while loop, "while there are items on the todo list, then 
    keep running".  Each time it runs it pops one item off the todo list, 
    processes it, and puts the results back on the todo list.  This continues 
    until the stack is done.

    Let's do some example steps: ::
        
        Step:     todo
        0:        [1]
        1:        [1,6] , [1,8]
        2:        [1,6,1] , [1,6,7] , [1,6,0] , [1,8]
        3:        [1,6,1,6] , [1,6,1,6] , [1,6,7] , [1,6,0] , [1,8]

    It keeps on growing the list until it hits length total_length.  Then it 
    doesn't put the item on the todo list, but rather on a done list.  
    This method has the advantage that it is more easily debugged: just 
    print out the todo list to file and you'll get an accurate idea of what 
    is going on. My advice is figure out how this version works, and then 
    use that to solve any recursive problems you may encounter.
    """
    done=[] # done list starts empty
    while len(todo)>0: # while we still have an item on the todo list
        workon = todo.pop() # pop the last item off
        for move in knight_moves[workon[-1]]: # for each possible move
            if len(workon)==total_length: # if we're done
                done.append(workon + [move]) # add that move and put it on the done list
            else:
                todo.append(workon + [move]) # otherwise stick it back on the todo list
    return done # now that the todo list is empty, the done list contains all the answers



# if you run this file directly, you will get a speed test of the three functions
if __name__ == '__main__':
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import time
    except:
        print('if you want to run the tests and show the results, you\'ll need matplotlib and numpy installed')

    else:
        tpur = []
        trad = []
        tbac = []
        for j in range(2,15):
    
            t = time.time()
            pur = KD_pure_recursion([[1],[2],[3],[4],[6],[7],[8],[9]],total_length=j)
            t = time.time()-t
            tpur.append(t)  
            del t
            
            t = time.time()
            rad = KD_recursive_addition([[1],[2],[3],[4],[6],[7],[8],[9]],total_length=j)
            t = time.time()-t
            trad.append(t)  
            del t
            
            t = time.time()        
            bac = KD_backtrack([[1],[2],[3],[4],[6],[7],[8],[9]],total_length=j)
            t = time.time()-t
            tbac.append(t)
            del t
            
            assert rad.sort() == bac.sort()
            assert pur.sort() == rad.sort()
        
        plt.figure()
        plt.plot(np.log(tpur[2:]),label='pure recursion')
        plt.plot(np.log(trad[2:]),label='recursive addition')
        plt.plot(np.log(tbac[2:]),label='backtrack')
        plt.legend()
        plt.xlabel('length of dial'); plt.ylabel('ln(time)')
        plt.show()
    
    
    