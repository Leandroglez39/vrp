from flask import Flask, request, make_response, jsonify
import json
from vrp import convert_dict_to_list, distace_between_coords, solve_vrp

var_json = {
    "coords": {0: (-70.69929, 19.46078),
               1: (-70.69551, 19.45833),
               2: (-70.69543, 19.46179)},

    "demands": {0: 1,
                1: 2,
                2: 3},

    "upper_time_windows": {0: 10,
                           1: 20,
                           2: 30},

    "lower_time_windows": {1: 0,
                           2: 0},
    "load_capacity": 5

}

app = Flask(__name__)

PORT = 3030
HOST = '0.0.0.0'


@app.route('/')
def home():
    return "<h1 style='color:red'>This is home!</h1>"


@app.route('/data', methods=['POST'])
def events():

    event_data = request.json

    dump_data = json.dumps(event_data)
    
    json_data = json.loads(dump_data)    
    

    
    list_coors = convert_dict_to_list(json_data["coords"], flag=False)
    
    list_coors.append(list_coors[0])
    print(list_coors)
    
    list_demands = convert_dict_to_list(json_data["demands"])
    list_demands.append(0)

    TIME_WINDOWS_LOWER = json_data["lower_time_windows"]
  

    TIME_WINDOWS_UPPER = json_data["upper_time_windows"]
    TIME_WINDOWS_UPPER[len(list_coors)-1] = 0

    capacity = int(json_data["load_capacity"])

    dist_matrix = distace_between_coords(list_coors)

    pro = solve_vrp(dist_matrix, list_demands, capacity,
                    TIME_WINDOWS_LOWER, TIME_WINDOWS_UPPER)

    return make_response(jsonify(pro.best_routes), 200)


if __name__ == '__main__':
    print("Server Running app in port %s"%(PORT))
    app.run(host=HOST, port=PORT, debug=True)
    
