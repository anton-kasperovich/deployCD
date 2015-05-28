from flask import render_template, flash, url_for, request, redirect, session
from flask_login import login_user, logout_user, current_user, login_required

from app import app, db, gitlab, login_manager
from forms import ProjectForm
from models import User, Project, ROLE_USER, ROLE_ADMIN

import copy
import ansible.runner
import ansible.inventory
import ansible.callbacks
import ansible.utils

@app.route('/')
@app.route('/projects')
@app.route('/projects/<int:page>')
def index(page=1):
    if current_user.is_authenticated():
        projects = Project.query.order_by(Project.deploy_at.desc(), Project.updated_at.desc()).paginate(page, 10, False)
        return render_template('index.html', projects=projects)

    return redirect(url_for('login'))


@app.route('/project/create', methods=["GET", "POST"])
@login_required
def project_create():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = Project(
            title=form.title.data,
            branch=form.branch.data,
            user_id=current_user.get_id(),
            repo_url=form.repo_url.data
        )
        db.session.add(new_project)
        db.session.commit()

        flash('Project has been created successfully.', 'success')
        return redirect(url_for('project', project_id=new_project.id))

    return render_template('project/form.html', form=form, action_url=url_for('project_create'))


@app.route('/project/<int:project_id>/edit', methods=["GET", "POST"])
@login_required
def project_edit(project_id):
    project = Project.query.filter_by(id=project_id).first_or_404()
    form = ProjectForm(obj=project)

    if request.method == 'POST' and form.validate():
        form.populate_obj(project)
        db.session.commit()

        flash('Project has been updated successfully.', 'success')
        return redirect(url_for('project', project_id=project.id))

    return render_template('project/form.html', form=form, action_url=url_for('project_edit', project_id=project.id))


@app.route('/project/<int:project_id>')
@login_required
def project(project_id):
    project = Project.query.filter_by(id=project_id).first_or_404()
    return render_template('project/show.html', project=project)


@app.route('/project/<int:project_id>/servers')
@login_required
def project_servers(project_id):
    project = Project.query.filter_by(id=project_id).first_or_404()
    return render_template('servers/list.html', project=project)


@app.route('/project/<int:project_id>/deploy')
@login_required
def project_deploy(project_id):
    project = Project.query.filter_by(id=project_id).first_or_404()

    hosts = ["localhost"]
    ansible.utils.VERBOSITY = 1

    inventory = ansible.inventory.Inventory(hosts)
    base_runner = ansible.runner.Runner(
        pattern='all',
        transport='local',
        inventory=inventory,
        # callbacks=runner_cb,
        check=False,
        background=1
    )

    runner = copy.copy(base_runner)
    runner.module_name = 'git'
    runner.module_args = 'repo=git@github.com:iniweb/ansible-vagrant-sf2.git'

    result = runner.run()
    print result

    return render_template('project/deploy.html', project=project)



@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/gitlab')
def login_gitlab():
    if current_user.is_authenticated():
        return redirect(url_for('index'))

    return gitlab.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    logout_user()
    session.pop('gitlab_token', None)
    return redirect(url_for('index'))


@app.route('/oauth-authorized')
def authorized():
    if current_user.is_authenticated():
        return redirect(url_for('index'))

    resp = gitlab.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )

    session['gitlab_token'] = (resp['access_token'], '')
    me = gitlab.get('user')

    user = User.query.filter_by(email=me.data['email']).first()
    if not user:
        role = ROLE_ADMIN if me.data['is_admin'] else ROLE_USER
        user = User(
            role=role,
            email=me.data['email'],
            avatar_url=me.data['avatar_url'],
            enabled=True
        )
        db.session.add(user)
        db.session.commit()

    login_user(user, True)

    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error():
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error():
    db.session.rollback()
    return render_template('500.html'), 500


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@gitlab.tokengetter
def get_gitlab_token():
    return session.get('gitlab_token')
