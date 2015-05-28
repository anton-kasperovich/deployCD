from datetime import datetime

from sqlalchemy_utils import IPAddressType, ChoiceType

from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

projects_users = db.Table(
    'project_user',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('is_owner', db.Boolean, default=False)
)

projects_deploys = db.Table(
    'project_deploy',
    db.Column('deploy_id', db.Integer, db.ForeignKey('deploy.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    email = db.Column(db.String(120), index=True, unique=True)
    avatar_url = db.Column(db.String(255), unique=False)
    projects = db.relationship(
        'Project',
        secondary=projects_users,
        primaryjoin=(projects_users.c.user_id == id),
        secondaryjoin=(projects_users.c.project_id == id),
        backref=db.backref('projects_users', lazy='dynamic'),
        lazy='dynamic'
    )
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255), unique=True)
    branch = db.Column(db.String(255), unique=False)
    repo_url = db.Column(db.String(255), unique=True)
    deploy_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    servers = db.relationship(
        'Server',
        backref='project',
        lazy='dynamic'
    )

    def __init__(self, user_id, title, branch, repo_url, deploy_at=None):
        self.user_id = user_id
        self.title = title
        self.branch = branch
        self.repo_url = repo_url
        self.deploy_at = deploy_at
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return '<Project %r>' % self.title


class Deploy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    number = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    projects = db.relationship(
        'Project',
        secondary=projects_deploys,
        primaryjoin=(projects_deploys.c.deploy_id == id),
        secondaryjoin=(projects_deploys.c.project_id == id),
        backref=db.backref('projects_deploys', lazy='dynamic'),
        lazy='dynamic'
    )

    def __init__(self, project_id, number, timestamp):
        self.project_id = project_id
        self.number = number
        self.timestamp = timestamp

    def __repr__(self):
        return '<Deploy %r>' % (self.number)


class Server(db.Model):
    ROLES = [
        (u'demo', u'Demo'),
        (u'staging', u'Staging'),
        (u'production', u'Production')
    ]

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(ChoiceType(ROLES))
    name = db.Column(db.String(255), unique=True)
    provider = db.Column(db.String(255))
    ssh_login = db.Column(db.String(255), default="developer")
    ip_address = db.Column(IPAddressType)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __init__(self, role, name, provider, ssh_login, ip_address, project_id):
        self.role = role
        self.name = name
        self.provider = provider
        self.ssh_login = ssh_login
        self.ip_address = ip_address
        self.project_id = project_id

    def __repr__(self):
        return '<Server %r>' % (self.name)
