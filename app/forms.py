from flask_wtf import Form
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

class ProjectForm(Form):
    title = StringField("Title", validators=[DataRequired()])
    repo_url = StringField(
        "Repository",
        validators=[
            DataRequired(),
            Regexp(
                regex='((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?',
                message="Not valid Git url"
            )
        ]
    )
    branch = StringField(
        "Branch",
        default="master",
        validators=[DataRequired()]
    )
    submit = SubmitField()
