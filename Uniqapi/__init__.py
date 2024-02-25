from flask import Flask, request, jsonify, Response, render_template
from tinydb import TinyDB, Query
from time import time
import os
import json
import requests
from .libs.requestHandler import Objector

class Database:
    def __init__(self, db_files: list = []) -> None:
        self.db_files = db_files
        self.query = Query()

    def create_file_if_not_exists(self):
        for db_file in self.db_files:
            file_path = os.path.join(os.path.dirname(__file__), "db", db_file)
            if not os.path.exists(file_path):
                with open(file_path, "w") as file:
                    json.dump({}, file)

    def set_config(self):
        self.create_file_if_not_exists()
        required_files = []
        for db_file in self.db_files:
            file_path = os.path.join(os.path.dirname(__file__), "db", db_file)
            required_files.append(file_path)

        return [TinyDB(file) for file in required_files]


REQUIRED_DB_FILES = [
    "api.json",
    "logs.json"
]

database = Database(REQUIRED_DB_FILES)
apidb, logsdb = database.set_config()


class APIHandler(Flask):
    def __init__(self, *args, **kwargs):
        super(APIHandler, self).__init__(*args, **kwargs)
        self.query = Query()
        self.db_endpoints = apidb.table("routes")
        self.db_visitors = logsdb.table("visitors")
        self.routes = []
        
        self.http_request = requests.session()

    def get_base_api(self):
      """Extracts the protocol and hostname from the current Flask request.

         Returns:
           str: The base API URL constructed from the protocol and hostname.
      """
      # Determine the protocol (http or https) based on request.is_secure
      protocol = 'https' if request.is_secure else 'http'
    
      # Extract the hostname from request.host_url
      # Note: request.host_url already includes the protocol part
      hostname = request.host_url.split('://')[1].strip('/')
    
      # Construct the base API URL
      base_api = f"{protocol}://{hostname}"
      return base_api
    
    def _set_params(self, method: str = "GET", params: list = []):
        """
        Set parameters for the API request.

        Parameters:
            - method (str): HTTP method (default: "GET").
            - params (list): List of required parameters (default: []).

        Returns:
            - tuple: Tuple containing payload and error message.
        """
        supported_methods = ["GET", "POST"]
        if method.upper() not in supported_methods:
            return None, "Method Type Not Supported"

        payload = request.args if method.upper() == "GET" else request.get_json()
        _params = {}
        for param in params:
            if param not in payload:
                return None, f"Required parameter '{param}' is missing..."
            _params[param.strip()] = payload[param]

        return Objector(_params), None

    def _set_response(self,
                      response: str | bytes | None = None,
                      status: int | None = None,
                      headers: dict | None = None,
                      mimetype: str | None = None,
                      content_type: str | None = None,
                      direct_passthrough: bool = False) -> Response:
        """
        Set response attributes and create a Flask Response object.

        Parameters:
            - response (str | bytes | None): The response content.
            - status (int | None): The response status code.
            - headers (dict | None): Additional response headers.
            - mimetype (str | None): The response MIME type.
            - content_type (str | None): The response content type.
            - direct_passthrough (bool): Whether to pass the response directly to the client.

        Returns:
            - Response: The Flask Response object.
        """
        return Response(
            response=response,
            status=status,
            headers=headers,
            mimetype=mimetype,
            content_type=content_type,
            direct_passthrough=direct_passthrough
        )
    
    def _jsonify(self, **json_data) -> Response:
        """
        Convert the provided data into a JSON response.

        Parameters:
            - **json_data: Keyword arguments containing the data to be converted into JSON.

        Returns:
            - Response: The JSON response object.
        """
        return jsonify(json_data)
    
    

    def create_route(self, name:str, info:str, methods:list =["GET"], anti_spam:int=0, params:list = [], tags:list =[], is_private_route: bool = False):
        def decorator(func):
            route_data = {"name": name,
                          "info": info,
                          "anti_spam": anti_spam,
                          "is_private": is_private_route,
                          "methods": methods,
                          "params": params,
                          "tags":tags
                          }
            self.routes.append(route_data)

            # Generate a unique endpoint name based on the route name
            endpoint_name = f"{name}_endpoint"

            @self.route("/" + name, methods=methods, endpoint=endpoint_name)
            def route_handler(*args, **kwargs):  # Use the generated unique endpoint name
                client_ip = request.remote_addr
                if anti_spam > 0:
                    anti_spam_data = self.db_visitors.get(
                        self.query.ip == client_ip)
                    current_timestamp = time()

                    if anti_spam_data:
                        time_passed = current_timestamp - \
                            anti_spam_data["last_used_timestamp"]

                        time_left = int(anti_spam - time_passed)

                        if time_passed < anti_spam and time_left != 0:
                            return {"error": f"API rate-limited. Please wait {time_left}s to make another request."}

                    self.db_visitors.upsert(
                        {"ip": client_ip, "last_used_timestamp": current_timestamp}, self.query.ip == client_ip)

                return func(*args, **kwargs)

            return route_handler  # Return the generated route_handler function
        return decorator


app = APIHandler(__name__)
