SECRET_KEY = 'you-will-never-guess'
CSRF_ENABLED = True
SQLALCHEMY_DATABASE_URI = 'mysql://test:test@localhost/deploy_cd'
DEBUG_TB_INTERCEPT_REDIRECTS = False

GITLAB = dict(
    base_url='http://changemeonhost/api/v3/',
    authorize_url='http://changemeonhost/oauth/authorize',
    access_token_url='http://changemeonhost/oauth/token',
    access_token_method='POST',
    request_token_url=None,
    request_token_params={'scope': 'api'},
    consumer_key='you-will-never-guess',
    consumer_secret='you-will-never-guess'
)