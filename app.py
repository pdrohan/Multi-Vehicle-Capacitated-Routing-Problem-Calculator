from flask import Flask, render_template, request, url_for, flash
from or_solver import main
import requests
import json
app = Flask(__name__)
#Needs cleaning before presentation


@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/results/", methods=['GET','POST'])
def results():
    if request.method == 'POST':
        num_vehicles = request.form['num_vehicles']
        vehicle_cap = request.form['vehicle_cap']
        depot_location = request.form['depot_location']
        cpk = request.form['cpk']
        list_dest = request.form.getlist("destination")
        list_dem = request.form.getlist("demand")
        list_destinations = [x for x in list_dest if x]
        list_demands = [int(x) for x in list_dem if x]
        desti_dem = [[i+1, list_destinations[i], list_demands[i]] for i in range(len(list_destinations))]
        output = solve(list_destinations, list_demands, vehicle_cap, num_vehicles, depot_location)
        if output is None:
            print('Could not find address')
            return render_template('home.html')
        else:
            outp = output.splitlines()
            objective = str(int(outp.pop(0)) / 1000) + ' Km'
            total_loads = str(outp.pop(-1))
            total_dist = str(int(outp.pop(-1)) / 1000 * int(cpk)) + ' $'
            out2 = [outp[i:i+4] for i in range(0, len(outp), 4)]
            return render_template('output.html', objective=objective, total_loads=total_loads, 
            total_dist=total_dist, outp=out2, num_vehicles=int(num_vehicles), list_destinations=list_destinations, list_demands=list_demands, desti_dem=desti_dem)




def callAPI(destinations, depot_location):
    list_destinations_str = depot_location
    for desti in destinations:
        list_destinations_str = list_destinations_str + '|' + desti

    list_destinations = [list_destinations_str]
    
    api_key = 'YOUR KEY HERE'
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={list_destinations}&destinations={list_destinations}&mode=driving&language=en&key={api_key}" 

    response = requests.request("GET", url)

    responsed = json.loads(response.content)
    if response.ok:
        distance_matrix = []
        origins_list = responsed['origin_addresses']
        for origins in origins_list:
            dist_list = []
            for elements in responsed['rows'][origins_list.index(origins)]['elements']:
                if elements['status'] == 'NOT_FOUND':
                    return 
                else:
                    dist_list.append(elements['distance']['value'])
            distance_matrix.append(dist_list)
        return distance_matrix


def solve(destinations, demands, capacity, num_trucks, depot_location):
    distance_matrix = callAPI(destinations=destinations, depot_location=depot_location)
    if distance_matrix:
        cap_list = [int(capacity)] * int(num_trucks)
        demands.insert(0, 0)
        return main(distance_matrixx=distance_matrix, demands=demands, capacity=cap_list, num_trucks=int(num_trucks))
    else:
        return
     
if __name__ == "__main__":
    app.run(debug=True)




