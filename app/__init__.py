from flask import Flask, g
from .app_factory import create_app
from .db_connect import close_db, get_db

app = create_app()
app.secret_key = 'my-secret'

# Register Blueprints
from app.blueprints.sales import sales
from app.blueprints.regions import regions
from app.blueprints.reports import reports
from app.blueprints.visualization import visualization

app.register_blueprint(sales)
app.register_blueprint(regions)
app.register_blueprint(reports)
app.register_blueprint(visualization)

from . import routes

@app.before_request
def before_request():
    g.db = get_db()

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)
