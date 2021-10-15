import numpy as np

def get_cc(grid):
    '''
    https://www.careercup.com/question?id=14948781
    '''
    
    # First, convert the 1/0 grid into an adjacency grid represented by a map
    graph = {}
    for row in range(0, len(grid), 2): 
        for column in range(0, len(grid[0]), 2):
            key = (row, column)
            # adding the home key
            if grid[row][column] == 0:
                graph[key] = []
                graph[key].append(key)
                # (1) checking if within bounds (2) checking if no adjacent border (3) checking if adjacent square is empty
                if column < len(grid[0]) - 1 and grid[row][column+1] == 7 and grid[row][column+2] == 0: 
                    graph[key].append((row, column+2))
                if column >= 1 and grid[row][column-1] == 7 and grid[row][column-2] == 0: 
                    graph[key].append((row, column-2))
                if row < len(grid) - 1 and grid[row+1][column] == 7 and grid[row+2][column] == 0: 
                    graph[key].append((row+2, column))
                if row >= 1 and grid[row-1][column] == 7 and grid[row-2][column] == 0: 
                    graph[key].append((row-2, column))

    # Counting the connected components 
    # Can also use BFS, too. 
    def dfs(visited, graph, node):
        if node not in visited:
            connected_components[counter].append(node)
            visited.add(node)
            for neighbour in graph[node]:
                dfs(visited, graph, neighbour)

    counter = 0
    visited = set()
    connected_components = []
    for node in graph.keys(): 
        if node not in visited and len(graph[node]) > 0:
            connected_components.append([])
            dfs(visited, graph, node)
            counter += 1

    return np.array(connected_components, dtype=object)


def merge(grid, rows, cols):
    # inserting rows
    out1 = np.zeros([grid.shape[0]*2-1, grid.shape[1]], dtype=int)
    out1[0::2,:] = grid
    out1[1::2,:] = rows

    # inserting columns
    out2 = np.zeros([out1.shape[0], out1.shape[1]*2-1], dtype=int)
    out2[:,0::2] = out1
    out2[0::2,1::2] = cols

    # overwritting corners
    out2[1::2,1::2] = 9
    return out2


def split(grid):
    return grid[0::2,0::2], grid[1::2,0::2], grid[0::2,1::2]


def list_columns(obj, rows=12, gap=2):
    '''
    This function takes in a list of values and transforms it
    into another list which looks like several columns stacked
    together as such:
    
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    >>>
    [' 1   7  13',
     ' 2   8  14',
     ' 3   9    ',
     ' 4  10    ',
     ' 5  11    ',
     ' 6  12    ']
    
    'row' parameter controls the maximum length of each column
    'gap' parameter controls the spacing between columns
    
    Adapted from https://stackoverflow.com/questions/1524126/how-to-print-a-list-more-nicely/25048690
    '''
    gap = 2 if len(obj)>rows else 0
    
    if len(obj)>0:
        sobj = [str(item) for item in obj]
        max_len = max([len(item) for item in sobj])

        plist = [sobj[i: i+rows] for i in range(0, len(sobj), rows)]
        if not len(plist[-1]) == rows:
            plist[-1].extend(['']*(len(sobj) - len(plist[-1])))
        plist = zip(*plist)
        printer = [''.join([c.rjust(max_len + gap) for c in p]) for p in plist]
        printer = [x[gap:] for x in printer]
    else:
        printer = ['']
    
    return printer