from Uniqapi import app, jsonify, render_template, request
from collections import defaultdict
import datetime

@app.create_route(name="ip", tags=['Network'], methods=["POST"], info="Returns ip address", anti_spam=2)
def ip_lookup():
    
    return jsonify(ip=request.remote_addr)


@app.create_route(name="routes", tags=['basic'], info="Returns all the available routes", anti_spam=2)
def get_routes():
    
    return jsonify(message="running...", routes=app.routes, base_api=app.get_base_api())

@app.route("/")
def render_index():
    routes = [route for route in app.routes if not route['is_private']]
    categorized_routes = defaultdict(list)

    for route in routes:
     tags = route["tags"]
     if not tags:
        # del route['tags']
        categorized_routes["unknown"].append(route)
     else:
        for tag in tags:
            # del route['tags']
            categorized_routes[tag].append(route)
    routes = [{"tag": tag, "routes": routes} for tag, routes in categorized_routes.items()]
    year = datetime.datetime.now().year
    data = {
       "base_api": app.get_base_api(),
        "title":"UniqAPI",
        "logo":{
            "title":"Uniq",
            "subtitle": "API"
        },
        "version":"0.0.3",
        "routes": routes,
        "report":{
           "title":"If you encounter any bugs or glitches while using this endpoint, we encourage you to reach out to us via email at support@rapidapi.tech"
        },
        "copyright":{
           "text": f"Made with Flask By @imuniq | All rights reserved © {year}"
        }
    }
    return render_template("app.html", data=data)
