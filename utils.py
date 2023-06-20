import urllib.parse

from gitignore_parser import parse_gitignore


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def path_to_url(path):
    return urllib.parse.quote(path).replace('/', '%2F')


def url_to_path(url):
    return urllib.parse.unquote(url).replace('%2F', '/')


def file_search(project, search_pattern):
    # Get all files in directory recursively
    all_files = project.path.rglob(search_pattern)
    # Load .gitignore-like file
    ignore_path = project.path / '.gpteditignore'
    print(f'ignore_path: {ignore_path}')
    if ignore_path.exists():
        ignore_patterns = parse_gitignore(ignore_path)

        print('ignore_patterns:', ignore_patterns)

        # Filter files based on .gitignore-like file
        files = []
        try:
            for f in all_files:
                if not ignore_patterns((project.path / f).relative_to(project.path)) and \
                        not f.name.endswith('.gpteditignore'):
                    if f.is_dir():
                        # append file path with trailing slash
                        files.append(f / '')
                    else:
                        files.append(f)
        except ValueError:
            pass
        return [(str(f.relative_to(project.path))) for f in files]
    else:
        return [(str(f.relative_to(project.path))) for f in all_files]
