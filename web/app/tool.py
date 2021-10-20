from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Tool
from werkzeug.exceptions import abort
from . import db

def get_tool(tool_id):
    tool = Tool.query.filter_by(id=tool_id).first()
    if tool is None:
        abort(404)
    return tool

tool = Blueprint('tool', __name__)

@tool.route('/tools')
def get_tools():
    tools = Tool.query
    return render_template('tools.html', tools=tools)

@tool.route('/tools/<int:tool_id>')
def show_tool(tool_id):
    tool = get_tool(tool_id)
    return render_template('tool.html', tool=tool)

@tool.route('/tools/<int:tool_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_tool(tool_id):
    tool = get_tool(tool_id)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if not name:
            flash('Name is required!')
        else:
            tool = Tool.query.get(tool_id)
            tool.name = name
            tool.description = description
            db.session.commit()
            return redirect(url_for('tool.get_tools'))

    return render_template('edit.html', tool=tool)

@tool.route('/tools/create', methods=('GET', 'POST'))
@login_required
def create_tool():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Name is required!')
        else:
            tool = Tool.query.filter_by(name=name).first() # if this returns a tool, then the name already exists in database

            if tool: # if a tool is found, we want to redirect back to create page
                flash('Tool with same name already exists')
                return redirect(url_for('tool.create'))

            # create a new tool with the form data
            new_tool = Tool(name=name, description=description)

            # add the new user to the database
            db.session.add(new_tool)
            db.session.commit()

    return render_template('create.html')

@tool.route('/tools/<int:tool_id>/delete', methods=('POST',))
@login_required
def delete_tool(tool_id):
    tool = get_tool(tool_id)
    deletion = Tool.query.get(tool_id)
    db.session.delete(deletion)
    db.session.commit()
    flash('Successfully deleted!')
    return redirect(url_for('tool.get_tools'))
