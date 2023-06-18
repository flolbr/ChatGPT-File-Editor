import json
import os
import subprocess
import tempfile
from pathlib import Path

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# set env to development
app.config["ENV"] = "development"

CODE_FILES = {
    "main.py": "main.py",
    "main-copy.py": "main-copy.py",
    "ai-plugin.json": "./.well-known/ai-plugin.json",
    "openapi.yaml": "openapi.yaml",
}


class Project:
    """
    A class representing a project.

    Attributes:
        full_name (str): The full name of the project.
        slug (str): The slug of the project.
        path (str): The path of the project.
    """

    def __init__(self, full_name, slug, path):
        """
        Initialize a Project instance.

        Args:
            full_name (str): The full name of the project.
            slug (str): The slug of the project.
            path (str): The path of the project.
        """
        self.full_name = full_name
        self.slug = slug
        self.path = Path(path)


projects = {
    "default": Project("Project 1", "default", "examples/default"),
    "code": Project("Code", "code", "."),
}


@app.get("/<string:project>/files")
async def get_files(project):
    """
    Get the list of files in a project.

    Args:
        project (str): The name of the project.

    Returns:
        quart.Response: A response object with the list of files.
    """
    print(f'Querying files for project "{project}"')

    # handle code project using CODE_FILES
    if project == "code":
        files = CODE_FILES.keys()
    else:
        # list all files' names in the project directory
        files = [f.name for f in (projects[project].path.iterdir()) if f.is_file()]

    return quart.Response(response=json.dumps(files), status=200)


@app.post("/<string:project>/file/read")
async def get_file(project):
    """
    Get the contents of a file in a project.

    Args:
        project (str): The name of the project.

    Returns:
        quart.Response: A response object with the file contents.
    """
    data = await quart.request.get_json(force=True)
    filename = data["filename"]

    print(f'Querying file "{filename}" for project "{project}"')

    if project not in projects:
        return quart.Response(response=json.dumps({
            "error": f"Project {project} not found",
        }), status=404)

    if project == "code":
        files = {
            "main.py": "main.py",
            "ai-plugin.json": "./.well-known/ai-plugin.json",
            "openapi.yaml": "openapi.yaml",
        }
        file = Path(CODE_FILES[filename])
    else:
        file = projects[project].path / filename

    contents = file.read_text().splitlines()

    # Add a line number to each line
    contents = [f"{i + 1}: {line}" for i, line in enumerate(contents)]

    return quart.Response(response=json.dumps({
        "full_path": str(file.absolute()),
        "last_modified": file.stat().st_mtime,
        "created": file.stat().st_ctime,
        "contents": contents,
    }), status=200)


@app.post("/<string:project>/file/write")
async def set_file_contents(project):
    """
    Set the contents of a file in a project.

    Args:
        project (str): The name of the project.

    Returns:
        quart.Response: A response object indicating the success of the operation.
    """
    data = await quart.request.get_json(force=True)
    filename = data["filename"]

    print(f'Setting file "{filename}" for project "{project}"')

    if project == "code":
        file = Path(CODE_FILES[filename])
    else:
        file = projects[project].path / filename

    print(data)

    body = data["contents"]

    file.write_text(body)
    return quart.Response(response='OK', status=200)


@app.post("/<string:project>/file/lines")
async def edit_file_lines(project):
    """
    Edit specific lines in a file in a project.

    Args:
        project (str): The name of the project.

    Returns:
        quart.Response: A response object indicating the success of the operation.
    """
    data = await quart.request.get_json(force=True)
    filename = data["filename"]

    print(f'Editing file "{filename}" for project "{project}"')
    file_path = projects[project].path / filename

    first_line = data["first_line"]
    last_line = data["last_line"]
    content = data["content"]

    print(f'Editing lines {first_line} to {last_line} with:\n\n"{content}"')

    with file_path.open() as f:
        lines = f.readlines()

    # Replace the specified lines with the new content
    lines[first_line - 1:last_line] = ['\n'.join(content) + '\n']

    with file_path.open('w') as f:
        f.writelines(lines)

    return quart.Response(response='OK', status=200)


@app.post("/<string:project>/file/patch")
async def patch_file(project):
    """
    Apply a patch to a file in a project.

    Args:
        project (str): The name of the project.

    Returns:
        quart.Response: A response object indicating the success of the operation.
    """
    print(f'Patching file for project "{project}"')
    data = await quart.request.get_json(force=True)

    print(data)

    file_path = projects[project].path / data["filename"]

    # Check if the destination file exists
    if not file_path.exists():
        return quart.Response(response='Destination file does not exist', status=400)

    # Create a temporary file and write the patch data to it
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(data["patch"])
        temp_file_name = temp.name

    try:
        # Use the 'patch' command to apply the patch
        command = ['patch', '-u', str(file_path), '-i', temp_file_name]
        print(f'Running command: "{" ".join(command)}"')
        subprocess.run(command, check=True)
    finally:
        pass
        # Delete the temporary file
        # os.remove(temp_file_name)

    return quart.Response(response='OK', status=200)


@app.get("/logo.png")
async def plugin_logo():
    """
    Serve the plugin logo.

    Returns:
        quart.Response: A response object with the logo image.
    """
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    """
    Serve the plugin manifest.

    Returns:
        quart.Response: A response object with the plugin manifest.
    """
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        response = quart.Response(text, mimetype="text/json")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"  # Or any other directive you need
    return response


@app.get("/openapi.yaml")
async def openapi_spec():
    """
    Serve the OpenAPI specification.

    Returns:
        quart.Response: A response object with the OpenAPI specification.
    """
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all(path):
    """
    This route is used for testing purposes.
    It will print the request and return a 200 response.

    Args:
        path (str): The request path.

    Returns:
        quart.Response: A response object with a 200 status.
    """
    print(f"Path: /{path}")
    print(f"Request: {request}")
    print(f"Request headers: {request.headers}")
    print(f"Request body: {await request.get_data()}")

    return quart.Response(response="OK", status=200)


def main():
    """
    Main function to start the application.
    The application will be run in debug mode and will listen on all interfaces at port 5003.
    """
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
