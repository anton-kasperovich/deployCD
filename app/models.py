from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

projects_users = db.Table('project_user',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
                          )

projects_builds = db.Table('project_build',
                           db.Column('build_id', db.Integer, db.ForeignKey('build.id')),
                           db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
                           )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    email = db.Column(db.String(120), index=True, unique=True)
    avatar_url = db.Column(db.String(255), unique=False)
    projects = db.relationship('Project',
                               secondary=projects_users,
                               primaryjoin=(projects_users.c.user_id == id),
                               secondaryjoin=(projects_users.c.project_id == id),
                               backref=db.backref('projects_users', lazy='dynamic'),
                               lazy='dynamic')
    enabled = db.Column(db.Boolean, default=True)

    def __init__(self, role, email, avatar_url, enabled):
        self.role = role
        self.email = email
        self.avatar_url = avatar_url
        self.enabled = enabled

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.enabled

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % self.email


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.String(255), unique=False)
    title = db.Column(db.String(255), unique=True)

    def __init__(self, title, logo):
        self.title = title
        self.logo = logo

    def __repr__(self):
        return '<Project %r>' % self.title


class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    number = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    projects = db.relationship('Project',
                               secondary=projects_builds,
                               primaryjoin=(projects_builds.c.build_id == id),
                               secondaryjoin=(projects_builds.c.project_id == id),
                               backref=db.backref('projects_builds', lazy='dynamic'),
                               lazy='dynamic')

    def __repr__(self):
        return '<Build %r>' % (self.number)