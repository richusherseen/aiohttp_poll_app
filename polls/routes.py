from views import index,poll,vote,results
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).parent

def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/poll/{question_id}', poll, name='poll')
    setup_static_routes(app)
    app.router.add_post('/poll/{question_id}/vote', vote, name='vote')
    app.router.add_get('/poll/{question_id}/results', results, name='results')

def setup_static_routes(app):
	app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')