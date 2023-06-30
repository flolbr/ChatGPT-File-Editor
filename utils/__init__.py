# from .Singleton import Singleton
import urllib.parse

import pathspec

from project import Project


def path_to_url(path):
    return urllib.parse.quote(path).replace('/', '%2F')


def url_to_path(url):
    return urllib.parse.unquote(url).replace('%2F', '/')


def file_search(project: Project, search_pattern):
    # Get all files in directory recursively
    all_files = project.path.rglob(search_pattern)
    # Load .gitignore-like file
    ignore_path = project.path / '.gpteditignore'
    print(f'ignore_path: {ignore_path}')
    if ignore_path.exists():

        spec = pathspec.GitIgnoreSpec.from_lines(ignore_path.read_text().splitlines())

        return [(str(f.relative_to(project.path))) for f in all_files
                if not spec.match_file(str(f.relative_to(project.path))) and not f.name.endswith('.gpteditignore')]

    else:
        # Use generator expression instead of list comprehension
        return (str(f.relative_to(project.path)) for f in all_files)
