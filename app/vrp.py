from networkx import DiGraph, set_node_attributes
from vrpy import VehicleRoutingProblem
import networkx as nx
import openrouteservice
import numpy as np
from database import *
from modifyDict import modifyDict

 
distance_matrix_cache = {}

def init_db_cache():
  
    if is_table_empty("api_coords_cache"):
        init_insert_db_cache()
        print("Table is empty")
        return True
    return False

def solver_vrp():

    G = DiGraph()
    G.add_edge("Source", 1, cost=1)
    G.add_edge("Source", 2, cost=2)
    G.add_edge(1, "Sink", cost=0)
    G.add_edge(2, "Sink", cost=2)
    G.add_edge(1, 2, cost=1)

    G.nodes[1]["demand"] = 2
    G.nodes[2]["demand"] = 9

    prob = VehicleRoutingProblem(G, load_capacity=10)
    prob.solve()

    return (G, prob)


def read_distance_matrix_cache_from_db():
    global distance_matrix_cache
    distance_matrix_cache = read_db_cache()   

'''
Save the distance matrix cache to the database
'''
def save_distance_matrix_cache():
    import time
    while True:
        
        update_db_cache(distance_matrix_cache)
        #time.sleep(86,400)
        time.sleep(10)
             
def draw_graph(G):

    nx.draw(G, pos=nx.spring_layout(G), with_labels=True, node_size=500,
            node_color='#00FF00', edge_color='#0000FF', font_size=10)
    #plt.show()


def openrouteservice_features(coords):
    # Specify your personal API key

    try:

        client = openrouteservice.Client(
            key='5b3ce3597851110001cf62480b20f596bd754e8c9d7da39d3ee98921')
        
        routes = client.directions(
            coords,
            profile="driving-car",
            extra_info=["waytype", "steepness"],
            format='geojson')
        
        
    
    except Exception as e:
        return e

    else:
        return routes    
    # return routes['features'][0]['properties']['segments'][0]['distance']
   


def draw_graph_with_edge_value(G, cases="cost"):

    position = nx.spring_layout(G)

    nx.draw(G, pos=position,
            with_labels=True,
            node_size=500,
            node_color='#00FF00',
            edge_color='#0000FF',
            font_size=10
            )

    if cases == "cost":
        nx.draw_networkx_edge_labels(
            G, pos=position, edge_labels=nx.get_edge_attributes(G, 'cost'))
    elif cases == "duration":
        nx.draw_networkx_edge_labels(
            G, pos=position, edge_labels=nx.get_edge_attributes(G, 'duration'))

    #plt.show()

    set_node_attributes(G, values=TIME_WINDOWS_UPPER, name="upper")
    set_node_attributes(G, values=TIME_WINDOWS_UPPER, name="upper")
    set_node_attributes(G, values=TIME_WINDOWS_UPPER, name="upper")

    set_node_attributes(G, values=TIME_WINDOWS_UPPER, name="upper")

    set_node_attributes(G, values=TIME_WINDOWS_UPPER, name="upper")

    set_node_attributes(G, values=TIME_WINDOWS_UPPER, name="upper")

def solve_vrp_fix(dist_matrix,
              demands,
              load_capacity,
              TIME_WINDOWS_LOWER,
              TIME_WINDOWS_UPPER) -> VehicleRoutingProblem:
    
    G = DiGraph()

    upper_time = {}
    lower_time = {}
    
    dad_child = {}
    

    #Add regular edges
    for i in range(len(dist_matrix) - 1):
        for y in range(i+1, len(dist_matrix) - 1):
            if i != 0:
                G.add_edge(
                    i, y, cost=dist_matrix[i][y][0], duration=dist_matrix[i][y][1])
                G.add_edge(
                    y, i, cost=dist_matrix[i][y][0], duration=dist_matrix[i][y][1])

            else:
                G.add_edge(
                    0, y, cost=dist_matrix[i][y][0], duration=dist_matrix[i][y][1])
                #G.add_edge(y, "Source", cost=dist_matrix[i][y][0], duration=dist_matrix[i][y][1])

    # Add data to the graph from Sink
    for x in range(1, len(dist_matrix[0]) - 1):
        G.add_edge(
            x, "Sink", cost=dist_matrix[0][x][0], duration=dist_matrix[0][x][1])

    

    del demands["0"]

    # Add originals demands to the graph
    #for key, value in demands.items():
    #    G.nodes[int(key)]['demand'] = value


    demands = modifyDict(demands, round(load_capacity*0.9))   

    

    for key, value in demands.items():
        G.nodes[int(key)]['demand'] = value[0]

    # Add data por sub nodes
    for key, value in demands.items():   
        for x in range(1, len(value) - 1):
            key = int(key)
            name = 'Sub_'+ str(key) + 'node_' + str(x)  
            dad_child[name] = key           
            G.add_edge(key, name, cost = 0, duration = 0)
            G.add_edge(name,'Sink', cost = dist_matrix[0][key][0], duration = dist_matrix[0][key][1])
            G.add_edge(0, name, cost = dist_matrix[0][key][0], duration = dist_matrix[0][key][1])
            
            for i in range(1, len(dist_matrix) - 1):
                if i != key:
                    G.add_edge(name, i, cost = dist_matrix[key][i][0], duration = dist_matrix[key][i][1])
            
            G.nodes[name]["demand"] = value[x]       

            upper_time[name] = TIME_WINDOWS_UPPER[str(key)]
            lower_time[name] = TIME_WINDOWS_LOWER[str(key)]

     # Set time windows
    #set_node_attributes(G, values={**TIME_WINDOWS_LOWER, **lower_time}, name="lower")
    #set_node_attributes(G, values={**TIME_WINDOWS_UPPER, **upper_time}, name="upper")

    # Relabel depot
    G = nx.relabel_nodes(G, {0: "Source", len(dist_matrix)-1: "Sink"})

    prob = VehicleRoutingProblem(
        G, load_capacity=load_capacity, time_windows=True)
      
    prob.solve(max_iter=1000, pricing_strategy="Hyper", exact=False)

    best_r = prob.best_routes

    for key, value in best_r.items():
        for i in range(len(value) - 1):
            if value[i] in dad_child:
                best_r[key][i] = dad_child[value[i]]

    print( best_r)

    return best_r

def solve_vrp(dist_matrix,
              demands,
              load_capacity,
              TIME_WINDOWS_LOWER,
              TIME_WINDOWS_UPPER) -> VehicleRoutingProblem:

    G = DiGraph()

    
    for i in range(len(dist_matrix) - 1):
        for y in range(i+1, len(dist_matrix) - 1):
            if i != 0:
                G.add_edge(
                    i, y, cost=dist_matrix[i][y][0], duration=dist_matrix[i][y][1])
                G.add_edge(
                    y, i, cost=dist_matrix[i][y][0], duration=dist_matrix[i][y][1])

            else:
                G.add_edge(
                    0, y, cost=dist_matrix[i][y][0], duration=dist_matrix[i][y][1])
                #G.add_edge(y, "Source", cost=dist_matrix[i][y][0], duration=dist_matrix[i][y][1])

    for x in range(1, len(dist_matrix[0]) - 1):
        G.add_edge(
            x, "Sink", cost=dist_matrix[0][x][0], duration=dist_matrix[0][x][1])

    for x in range(1, len(demands) - 1):
        G.nodes[x]['demand'] = demands[x]

    # Set time windows
    set_node_attributes(G, values=TIME_WINDOWS_LOWER, name="lower")
    set_node_attributes(G, values=TIME_WINDOWS_UPPER, name="upper")

    # Relabel depot
    G = nx.relabel_nodes(G, {0: "Source", len(dist_matrix)-1: "Sink"})

    #draw_graph_with_edge_value(G, cases="cost")

    prob = VehicleRoutingProblem(
        G, load_capacity=load_capacity, time_windows=True)
    #prob.pickup_delivery = True
    #prob.solve(cspy = False)
    
    #prob.drop_penalty = 1000
    
    prob.solve()

    return prob


def dist_btw_coords(coords):

    matrix = np.full((len(coords), len(coords)), 0, dtype=tuple)

    dict_aux = {}

    list_coords = []

    for i in range(len(coords)-1):
        for y in range(i+1, len(coords)):
            
            if not (coords[i], coords[y]) in distance_matrix_cache:
                list_coords.append(coords[i])
                list_coords.append(coords[y])
    
    segments = []

    if len(list_coords) <= 70:

        info = openrouteservice_features(list_coords)
    
        segments = info['features'][0]['properties']['segments']
    else:
        c, r = divmod(len(list_coords), 70)
        for i in range(c):
            list_coords_aux = list_coords[i*70:(i+1)*70]
            info = openrouteservice_features(list_coords_aux)
            segments.extend(info['features'][0]['properties']['segments'])
        if r != 0:
            list_coords_aux = list_coords[c*70:]
            info = openrouteservice_features(list_coords_aux)
            segments.extend(info['features'][0]['properties']['segments'])


    for i in range(len(segments)):
        dict_aux[(list_coords[i], list_coords[i+1])] = (segments[i]['distance'], segments[i]['duration'])


    for i in range(len(coords)-1):
        for y in range(i+1, len(coords)):
            if (coords[i],coords[y]) in dict_aux:
                dist = dict_aux[(coords[i],coords[y])][0]
                data = dict_aux[(coords[i],coords[y])][1]
                matrix[i][y] = (dist, data)
                matrix[y][i] = (dist, data)
            else:
                dist = distance_matrix_cache[(coords[i],coords[y])][0]
                data = distance_matrix_cache[(coords[i],coords[y])][1]
                matrix[i][y] = (dist, data)
                matrix[y][i] = (dist, data)

    return matrix
'''
Distance between a list of coordinates 
returns the distance in meters
'''
def distace_between_coords(coords):
    matrix = np.full((len(coords), len(coords)), 0, dtype=tuple)
    

    for i in range(len(coords)-1):
        for y in range(i+1, len(coords)):

            
            if (coords[i],coords[y]) in distance_matrix_cache:
                dist = distance_matrix_cache[(coords[i],coords[y])][0]
                data = distance_matrix_cache[(coords[i],coords[y])][1]
                matrix[i][y] = (dist, data)
                matrix[y][i] = (dist, data)

            else:    

                dist = openrouteservice_features((coords[i], coords[y]))
                data = (dist['features'][0]['properties']['segments'][0]['distance'],
                    dist['features'][0]['properties']['segments'][0]['duration'])
                matrix[i][y] = data
                matrix[y][i] = data

                distance_matrix_cache[(coords[i], coords[y])] = data

    return matrix


'''
Convert dict to list
'''


def convert_dict_to_list(dict_data, flag=True):
    list_data = []
    for _, value in dict_data.items():
        if flag:
            list_data.append(int(value))
        else:
            list_data.append(tuple(map(float,value.split(','))))
    return list_data


'''
Calculate route of list of coordinates
'''
def get_route(coords,best_routes):
    
    resp = {}
    aux_coords = []
    filter = {}


    for key, value in best_routes.items():
        aux_coords.append(coords[0])
        for i in range(1, len(value)-1):
            if  not value[i] in filter.keys():                    
                aux_coords.append(coords[value[i]])
                filter[value[i]] = True
        aux_coords.append(coords[0])        
        geojson = openrouteservice_features(aux_coords)
        resp[key] = [geojson, aux_coords]        
        aux_coords = []
        filter.clear()
    
    
    return resp

def parse_input(json_data):

    load_capacity = int(json_data['load_capacity'])

    dict_resp = {}

    for key, value in json_data["coords"]:
        if value > load_capacity:
            fix_demands(json_data, dict_resp)
            return dict_resp

    return dict_resp

def fix_demands(json_data, dict_resp):
    pass





if __name__ == '__main__':

    #G, solve = solver_vrp()
    # print(solve.best_value)

    # print(solve.best_routes)
    # draw_graph(G)
    #coords = ((-70.69929, 19.46078),(-70.69551, 19.45833))
    #dist = openrouteservice_distace(coords)
    # print(dist)

    #coords = [[-69.94733, 18.48913], [-69.94944, 18.48205], [-69.9415, 18.48559], [-69.94442, 18.47749],
    #          [-69.96591, 18.49284], [-69.95879, 18.46434], [-69.91924, 18.48189], [-69.94733, 18.48913]]

    coords = [(-69.94733, 18.48913), (-69.94944, 18.48205), (-69.9415, 18.48559)]
    #coords: list = [[-70.69929, 19.46078],[-70.69551, 19.45833], [-70.69543, 19.46179], [-70.68715, 19.46841],[-70.6804, 19.4733], [-70.6870, 19.4840],[-70.69929, 19.46078]]
    demands = [2, 9, 10, 4, 5, 2, 2, 10]

    TIME_WINDOWS_LOWER = {
        # 0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        # 7: 0
    }

    TIME_WINDOWS_UPPER = {
        0: 10,
        1: 10,
        2: 10,
        3: 10,
        4: 10,
        5: 10,
        6: 10,
        7: 10
    }

    #resp = solve_vrp(distace_between_coords(coords), demands, 12)

    # print(resp.best_value)

    # print(resp.best_routes)

    # print(resp.arrival_time)
    #var = convert_dict_to_list(
       # {'0': '-70.69929, 19.46078', '1': '-70.69551, 19.45833', '2': '-70.69543, 19.46179'}, flag=False)
    #print(var)

    #var = get_route([[-69.94733, 18.48913], [-69.94944, 18.48205], [-69.9415, 18.48559]], {1:["Source", 2, 1, "Sink"],2:["Source", 1, 2, "Sink"]})
    
    #var = openrouteservice_features([[ -69.93144, 18.4928],[-69.93401,18.48514],[-69.93247,18.47228]])    
    #print(var)

    print(dist_btw_coords(coords))