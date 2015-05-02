from flask import render_template, url_for, request, redirect, session
from flask_login import login_user, logout_user, current_user, login_required

from app import app, db, gitlab, login_manager
from models import User, Project, ROLE_USER, ROLE_ADMIN


@app.route('/')
@app.route('/projects')
@app.route('/projects/<int:page>')
def index(page = 1):
    if current_user.is_authenticated():
        projects = Project.query.order_by(Project.id).paginate(page, 5, False)
        return render_template('index.html', projects=projects)

    return redirect(url_for('login'))


@app.route('/project/<int:project_id>')
@login_required
def project(project_id):
    project = Project.query.filter_by(id=project_id).first_or_404()
    return render_template('project.html', project=project)


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
        user = User(role=role, email=me.data['email'], avatar_url=me.data['avatar_url'], enabled=True)
        db.session.add(user)
        db.session.commit()

    login_user(user, True)

    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@gitlab.tokengetter
def get_gitlab_token(token=None):
    return session.get('gitlab_token')