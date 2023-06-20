import quart
from quart import Blueprint, render_template, request

from project.project import projects, Project

dashboard_routes = Blueprint('dashboard_routes', __name__)


@dashboard_routes.get('/dashboard')
async def dashboard():
    print(projects.get_all())
    return await render_template('dashboard.html', projects=projects.get_all())


@dashboard_routes.post('/dashboard/project')
async def create_project():
    form = await request.form
    if form['slug'] in projects:
        return quart.redirect('/dashboard')
    full_name = form.get('full_name')
    slug = form.get('slug')
    path = form.get('path')
    # Add your logic for creating a new project here
    projects[slug] = Project(full_name, slug, path)
    return quart.redirect('/dashboard')


@dashboard_routes.put('/dashboard/project/<slug>')
async def update_project(slug):
    # body is json
    body = await request.get_json(force=True)

    # Find the project with the given slug
    project = projects[slug]

    # Update the project's full_name and path and slug
    project.full_name = body['full_name']
    project.path = body['path']
    project.slug = body['slug']

    return quart.redirect('/dashboard')


@dashboard_routes.delete('/dashboard/project/<slug>')
async def delete_project(slug):
    # Add your logic for deleting a project here
    del projects[slug]
    return '', 204


@dashboard_routes.route('/favicon.ico')
async def favicon():
    return await quart.send_file('logo.png', mimetype='image/vnd.microsoft.icon')
