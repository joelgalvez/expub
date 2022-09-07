# @name: tool.py
# @creation_date: 2021-10-20
# @license: The MIT License <https://opensource.org/licenses/MIT>
# @author: Simon Bowie <ad7588@coventry.ac.uk>
# @purpose: tool route for tool-related functions and pages
# @acknowledgements:
# https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Resource
from .resources import *
from werkzeug.exceptions import abort
from . import db

tool = Blueprint('tool', __name__)

# route for displaying all tools in database
@tool.route('/tools')
def get_tools():
    tools = Resource.query.filter_by(type='tool')
    return render_template('resources.html', resources=tools, type='tool')

# route for displaying a single tool based on the ID in the database
@tool.route('/tools/<int:tool_id>')
def show_tool(tool_id):
    tool = get_resource(tool_id)
    links = get_linked_resources(tool_id)
    return render_template('resource.html', resource=tool, links=links)

# route for editing a single tool based on the ID in the database
@tool.route('/tools/<int:tool_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_tool(tool_id):
    tool = get_resource(tool_id)
    resource_dropdown = Resource.query
    links = get_linked_resources(tool_id)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        projectUrl = request.form['projectUrl']
        repositoryUrl = request.form['repositoryUrl']
        expertiseToUse = request.form['expertiseToUse']
        expertiseToHost = request.form['expertiseToHost']
        dependencies = request.form['dependencies']
        ingestFormats = request.form['ingestFormats']
        outputFormats = request.form['outputFormats']
        status = request.form['status']
        linked_resources = request.form.getlist('linked_resources')
        remove_linked_resources = request.form.getlist('remove_linked_resources')

        if not name:
            flash('Name is required!')
        else:
            tool = Resource.query.get(tool_id)
            tool.name = name
            tool.description = description
            tool.projectUrl = projectUrl
            tool.repositoryUrl = repositoryUrl
            tool.dependencies = dependencies
            tool.expertiseToUse = expertiseToUse
            tool.expertiseToHost = expertiseToHost
            tool.ingestFormats = ingestFormats
            tool.outputFormats = outputFormats
            tool.status = status
            db.session.commit()
            if linked_resources:
                for linked_resource in linked_resources:
                    link = Resource.query.get(linked_resource)
                    if links and link not in links:
                        add_linked_resource(tool_id, linked_resource)
                    elif not links:
                        add_linked_resource(tool_id, linked_resource)
            if remove_linked_resources:
                for remove_linked_resource in remove_linked_resources:
                    delete_relationship(tool_id, remove_linked_resource)
            return redirect(url_for('tool.get_tools',_external=True,_scheme=os.environ.get('SSL_SCHEME')))

    return render_template('edit.html', resource=tool, resource_dropdown=resource_dropdown, links=links)

# route for function to delete a single tool from the edit page
@tool.route('/tools/<int:tool_id>/delete', methods=('POST',))
@login_required
def delete_tool(tool_id):
    delete_resource(tool_id)
    return redirect(url_for('tool.get_tools',_external=True,_scheme=os.environ.get('SSL_SCHEME')))
