############################
### IMPORT USED PACKAGES ###
############################

get_ipython().run_line_magic('matplotlib', 'inline')
import networkx as nx
import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from IPython.display import HTML



########################
### USEFUL FUNCTIONS ###
########################

# Given a list of (consecutively adjacent) nodes, returns the list of edges connecting them.
def edges_connecting_nodes(node_list):
    """ 
    INPUT:  list of consecutively adjacent nodes (e.g. nodes of a RW trajectory).
    OUTPUT: list of edges connecting the nodes.                                  
    """
    edge_list = []
    for j in range(len(node_list)-1):
        edge_list.append((node_list[j],node_list[j+1]))
    return edge_list


# Draw the graph with the requested preferences
def draw_net(G, position, node_size, node_color, edgelist, width):
    """ 
    INPUT:  G          = a networkx graph. 
            position   = a dictionary with nodes as keys and corresponding positions as values.   
            node_size  = size of nodes (scalar or list with the same length as G.nodes()).
            node_color = color of nodes (string or rgb(rgba) or list with the same length as G.nodes()).  
            edgelist   = list of edges to be drawn.
            width      = line width of edges.
    """
    nx.draw_networkx(
        G, 
        pos = position, 
        with_labels = False,
        node_size = node_size, 
        node_color = node_color,
        edgelist = edgelist,
        width = width
    )

    
# Auto-positioning of nodes in 2d lattice
def auto_pos(graph2d):
    """
    INPUT:  graph2d = a network 2d grid graph
    OUTPUT: position = dictionary with correct positions of the 2d grid graph
    """
    position = {}
    for node in graph2d.nodes():
        position[node] = node

    return position



##########################
### WILSON'S ALGORITHM ###
##########################

# Wilson's algorithm (RSF modification) for a 2d lattice
def wilson_RSF_grid_2d(dim, q, info=True):
    """
    INPUT:  dim  = 2-tuple (n,m) with dimensions of the 2d lattice.
            q    = killing parameter for the loop-erased RWs of the Wilson's algorithm.
            info = boolean to choose whether or not to show concluding information.
    
    OUTPUT: G            = 2d grid graph.
            RW_node      = list of the node positions of the RWs at each step of the algorithm.
            edge_list    = list of lists, each one containing the edges covered by the LERWs at each step.
            roots        = roots found by the Wilson's algorithm.
            root_indices = iteration indices at which the roots are found. 
    """
    # Create 2d lattice
    G = nx.grid_2d_graph(dim[0], dim[1])
    absorb = q/(q+4)
    
    RW_node = [] # positions of the RWs
    edge_list = [] # lists of the covered edges
    covered_nodes = [] # list of nodes covered by the previous paths
    roots = [] # roots found by the algorithm
    root_indices = [] # iteration indices at which the roots are found

    for start_node in G.nodes(): # 
        
        # Check if the starting node is contained in one of the previous paths
        startcounter = covered_nodes.count(start_node)
        if startcounter>0: 
            continue
        
        # Add starting node to RW_node
        RW_node.append(start_node)
        
        # Add the corresponding edge list (at the initial moment) to edge_list
        if edge_list==[]:
            temp_edge_list = []
        else:
            temp_edge_list = edge_list[-1]
        edge_list.append(temp_edge_list)

        trajectory = [start_node] # nodes of the LERW trajectory
        end_traj_is_root = True

        while random.random() > absorb:
            
            # Choose adjacent node to move toward
            new_node = random.choice(list(G.adj[RW_node[-1]]))
            RW_node.append(new_node)

            if trajectory.count(new_node)==0: # if new node is not in the LERW trajectory
                trajectory.append(new_node)

            else: # if new node is in the LERW trajectory -> LOOP ERASE
                new_node_index = trajectory.index(new_node)
                trajectory = trajectory[:new_node_index+1]
            
            # Update edge_list
            total_edges = temp_edge_list.copy()
            new_edges = edges_connecting_nodes(trajectory)
            total_edges.extend(new_edges)
            edge_list.append(total_edges)

            # Check if new node has yet been covered by one of the previous paths
            counter = covered_nodes.count(new_node)
            if counter > 0:
                end_traj_is_root = False
                break
        
        # Add root (it only happens when 'while' condition fails)
        if end_traj_is_root:
            roots.append(trajectory[-1])
            root_indices.append(len(RW_node)-1)
            
        # Add the new path to the covered nodes of the graph
        covered_nodes.extend(trajectory)
    
    # Show informations
    if info:
        print("The roots are:", roots)
        print("The roots get identified at iteration indices:", root_indices)
        print("The total number of iteration is:", len(RW_node))
    
    return G, RW_node, edge_list, roots, root_indices


# Draw the outcome of Wilson's algorithm, i.e. a random spanning forest
def draw_RSF(W, standard=(10,"grey"), root=(100,"green"), width=2.0, figsize=(5,5)):
    """
    INPUT:  W        = output of 'wilson_RSF_grid_2d'.
            standard = standard properties of nodes.
            root     = properties of roots.
            width    = line width of edges.
            figsize  = size of the figure.
    """
    # Create the figure
    fig = plt.figure(figsize=figsize)
    
    # Auto-position the 2d graph
    position = auto_pos(W[0])
    
    # Set standard node properties (index, size, color)
    node_property = [[],[],[]]
    for i in W[0].nodes():
        node_property[0].append(i)
        node_property[1].append(standard[0])
        node_property[2].append(standard[1])
    
    # Set root node properties (index, size, color)
    for n in range(len(W[3])):
        root_node_index = node_property[0].index(W[3][n])
        node_property[1][root_node_index] = root[0] 
        node_property[2][root_node_index] = root[1]
            
    draw_net(W[0], position, node_property[1], node_property[2], W[2][-1], width)
    plt.show()

    
# Simulation of the Wilson's algorithm
def wilson_simulation(W, standard=(10,"grey"), movement=(50,"red"), root=(100,"green"), width=2.0, figsize=(5,5), 
                      interval=100, simul=False, save=None, time_count=True, loading=True):
    """
    INPUT:  W          = output of 'wilson_RSF_grid_2d'.
            standard   = standard properties of nodes.
            movement   = properties of moving node
            root       = properties of roots.
            width      = line width of edges.
            figsize    = size of the figure.
            interval   = time between consecutive frames.
            simul      = choose whether to perform the simulation or not (default 'False').
            save       = (string) choose the name of the .mp4 file to save. If 'None' it not saves (default 'None').
            time_count = choose whether to show or not the elapsed time at the end of the animation.
            loading    = choose whether to show or not the progress of the animation.
    """
    start = time.time()
    
    # Create figure 
    fig = plt.figure(figsize=figsize)
    
    # Set number of frames
    n_frames = len(W[1])+1 # the last frame is the final RSF

    # Auto-position the 2d graph
    position = auto_pos(W[0])

    # Set standard node properties (index, size, color)
    node_property = [[],[],[]]
    for i in W[0].nodes():
        node_property[0].append(i)
        node_property[1].append(standard[0])
        node_property[2].append(standard[1])

    # Initial function in animation
    def initial():
        draw_net(W[0], position, node_property[1], node_property[2], W[2][0], width)
        return

    # Update function in animation
    def update(i):

        plt.clf()

        # Set properties of the previous node
        previous_node = W[1][i-1]
        previous_index = node_property[0].index(previous_node)
        node_property[1][previous_index] = standard[0] 
        node_property[2][previous_index] = standard[1]

        # Set properties of roots found so far
        for n in range(len(W[3])):
            if i >= W[4][n]:
                root_node_index = node_property[0].index(W[3][n])
                node_property[1][root_node_index] = root[0] 
                node_property[2][root_node_index] = root[1]
            else: break

        if i < len(W[1]): # Always, except last frame

            #Set properties of the actual node
            actual_node = W[1][i]
            actual_index = node_property[0].index(actual_node)
            node_property[1][actual_index] = movement[0] 
            node_property[2][actual_index] = movement[1]

            draw_net(W[0], position, node_property[1], node_property[2], W[2][i], width)

        else: draw_net(W[0], position, node_property[1], node_property[2], W[2][-1], width) # Last frame
        
        if loading:
            print(i+1, "of", n_frames)

        return

    # Animation
    film = anim.FuncAnimation(fig, update, init_func=initial, frames=n_frames, interval=interval);
    
    # Create simulation or save file
    if simul: HTML(film.to_jshtml())
    if save != None : film.save("%s.mp4" %save)
    
    # Count the time
    end = time.time()
    if time_count: print("Total elapsed time:", end-start)