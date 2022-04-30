from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
import json
from vrp import convert_dict_to_list, distace_between_coords, solve_vrp, openrouteservice_features, get_route


app = Flask(__name__)
CORS(app)

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
    
    
    list_demands = convert_dict_to_list(json_data["demands"])
    list_demands.append(0)

    TIME_WINDOWS_LOWER = json_data["lower_time_windows"]
  

    TIME_WINDOWS_UPPER = json_data["upper_time_windows"]
    TIME_WINDOWS_UPPER[len(list_coors)-1] = 0

    capacity = int(json_data["load_capacity"])

    

    dist_matrix = distace_between_coords(list_coors)

    

    pro = solve_vrp(dist_matrix, list_demands, capacity,
                    TIME_WINDOWS_LOWER, TIME_WINDOWS_UPPER)

    

    #print(pro.best_routes)

    return make_response(jsonify(get_route(list_coors,pro.best_routes)), 200)

@app.route('/route', methods=['POST'])
def routes():

    event_data = request.json

    dump_data = json.dumps(event_data)
    
    json_data = json.loads(dump_data)       
   
    var = openrouteservice_features(json_data["coordinates"])
   
    if type(var) == dict:
        return make_response(json.dumps(var), 200)
    else:
        return make_response(jsonify(var.message['error']['message']), var.status)

if __name__ == '__main__':
    print("Server Running app in port %s"%(PORT))
    app.run(host=HOST, port=PORT, debug=True)
    
