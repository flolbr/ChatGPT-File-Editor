import json
from pathlib import Path

import quart
from quart import Blueprint

from project import projects
from utils import file_search

projects_routes = Blueprint('projects', __name__)


@projects_routes.get("/projects/<string:project_name>/files")
async def get_files(project_name):
    """
    Get the list of files in a project.

    Args:
        project_name (str): The name of the project.

    Returns:
        quart.Response: A response object with the list of files.
    """
    print(f'Querying files for project "{project_name}"')
    try:
        project = projects[project_name]
    except KeyError:
        return quart.Response(response=json.dumps({
            "error": f"Project {project_name} not found",
        }), status=404)

    project.file_cache = file_search(project, '*')
    print(project.file_cache[:20])
    print(len(project.file_cache))

    return quart.Response(response=json.dumps(project.file_cache), status=200)


CHUNK_SIZE = 20_000


@projects_routes.get("/projects/<string:project>/file")
async def get_file(project):
    """
    Get the contents of a file in a project.

    Args:
        project (str): The name of the project.

    Returns:
        quart.Response: A response object with the file contents.
    """
    filename = quart.request.args.get("filename")

    print(f'Querying file "{filename}" for project "{project}"')

    if project not in projects.get_all():
        return quart.Response(response=json.dumps({
            "error": f"Project {project} not found",
        }), status=404)

    file: Path = projects[project].path / filename

    if not file.exists():
        return quart.Response(response=json.dumps({
            "error": f"File {filename} not found",
        }), status=404)

    next_line = int(quart.request.args.get("next_line", 0))

    lines = file.read_text().splitlines()
    contents = lines[next_line:]

    nb_chars = 0
    for i, line in enumerate(contents):
        nb_chars += len(line) + 1
        if nb_chars > CHUNK_SIZE:
            contents = contents[:i]
            break

    # Add a line number to each line
    contents = [f"{i + next_line + 1}: {line}" for i, line in enumerate(contents)]

    return quart.Response(response=json.dumps({
        "full_path": str(file.absolute()),
        "last_modified": file.stat().st_mtime,
        "created": file.stat().st_ctime,
        "nb_lines": len(lines),
        "contents": contents,
    }), status=200)


@projects_routes.post("/projects/<string:project>/file")
async def set_file_contents(project):
    """
    Set the contents of a file in a project.

    Args:
        project (str): The name of the project.

    Returns:
        quart.Response: A response object indicating the success of the operation.
    """
    data = await quart.request.get_json(force=True)

    print(data)

    filename = quart.request.args.get("filename")

    print(f'Setting file "{filename}" for project "{project}"')

    file = projects[project].path / filename

    print(data)

    contents = '\n'.join(data["contents"])

    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(contents)
    return quart.Response(response='OK', status=200)


@projects_routes.put("/projects/<string:project>/file")
async def edit_file(project):
    """
    Edit specific lines in a file in a project.

    Args:
        project (str): The name of the project.

    Returns:
        quart.Response: A response object indicating the success of the operation.
    """
    data = await quart.request.get_json(force=True)

    filename = quart.request.args.get("filename")

    print(f'Editing file "{filename}" for project "{project}"')
    file_path = projects[project].path / filename

    first_line = data["first_line"]
    last_line = data["last_line"]
    content = data["content"]

    # append newlines to the content
    content = [f"{line}\n" for line in content]

    print(f'Editing lines {first_line} to {last_line} with:\n\n"{content}"')

    with file_path.open() as f:
        lines = f.readlines()

    # Replace the specified lines with the new content
    lines[first_line - 1:last_line] = content

    with file_path.open('w') as f:
        f.writelines(lines)

    return quart.Response(response='OK', status=200)
