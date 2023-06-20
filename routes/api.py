import quart
from quart import Blueprint, request

api_routes = Blueprint('api', __name__)


@api_routes.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@api_routes.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        response = quart.Response(text, mimetype="text/json")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"  # Or any other directive you need
    return response


@api_routes.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


@api_routes.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all(path):
    print(f"Path: /{path}")
    print(f"Request: {request}")
    print(f"Request headers: {request.headers}")
    print(f"Request query args: {request.args}")
    print(f"Request body: {await request.get_data()}")

    return quart.Response(response="OK", status=200)
