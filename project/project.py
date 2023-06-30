from pathlib import Path

import yaml

from Singleton import Singleton

PROJECTS_YAML = 'projects.yaml'


class Project:
    """
    A class representing a project.

    Attributes:
        full_name (str): The full name of the project.
        slug (str): The slug of the project.
        path (Path): The path of the project.
        file_cache (list[str]): A list of files in the project.
    """

    file_cache: list[str]

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
        self.path = Path(path).absolute()
        self.file_cache = []

    def to_dict(self):
        return {
            'full_name': self.full_name,
            'slug': self.slug,
            'path': str(self.path),
        }


class Projects(metaclass=Singleton):
    """
    Projects Singleton
    Stores the projects in a dictionary
    Can load / save projects to a yaml file
    """
    projects = {}

    def __init__(self):
        self._load_projects()

    def _load_projects(self):
        # Create projects.yaml if it doesn't exist
        if not Path(PROJECTS_YAML).exists():
            with open(PROJECTS_YAML, 'w') as f:
                yaml.dump({}, f)
        with open(PROJECTS_YAML, 'r') as f:
            pj = yaml.load(f, Loader=yaml.FullLoader)
        self.projects = {slug: Project(**project) for slug, project in pj.items()}

    def _save_projects(self):
        with open(PROJECTS_YAML, 'w') as f:
            yaml.dump({slug: project.to_dict() for slug, project in self.projects.items()}, f)

    def add(self, slug, project):
        self.projects[slug] = project
        self._save_projects()

    def delete(self, slug):
        del self.projects[slug]
        self._save_projects()

    def get_all(self):
        return self.projects

    def get(self, slug):
        return self.projects[slug]

    def __getitem__(self, slug):
        return self.projects[slug]

    def __setitem__(self, key, value):
        self.projects[key] = value
        self._save_projects()

    def __delitem__(self, key):
        del self.projects[key]
        self._save_projects()

    def __contains__(self, slug):
        return slug in self.projects


projects = Projects()
