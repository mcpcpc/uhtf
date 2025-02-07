from quart import Quart
from quart import render_template

__version__ = "0.0.1"


def create_app(test_config: dict = None) -> Quart:
    app = Quart(__name__)
    
    @app.get("/")
    async def index():
        return await render_template("index.html")
    
    return app
