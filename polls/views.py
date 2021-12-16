from aiohttp import web
import db
import aiohttp_jinja2

# async def index(request):
#     return web.Response(text='Hello Aiohttp!')

@aiohttp_jinja2.template('index.html')
async def index(request):
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.question.select())
        records = await cursor.fetchall()
        questions = [dict(q) for q in records]
        return {"questions": questions}
        # return web.Response(text=str(questions))

@aiohttp_jinja2.template('detail.html')
async def poll(request):
    async with request.app['db'].acquire() as conn:
        question_id = request.match_info['question_id']
        try:
            question, choices = await db.get_question(conn,
                                                      question_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        
        except Exception as e:
            print('errror',e)
            raise web.HTTPNotFound(text=str(e))

        return {
            'question': question,
            'choices': choices
        }

async def vote(request):
    try:
        async with request.app['db'].acquire() as conn:
            question_id = int(request.match_info['question_id'])	# why int()
            data = await request.post()		# see detail.html -->  the post of <form>.

            try:
                choice_id = int(data['choice'])	# 'choice' is the name of <form><input>, value="{{ choice.id }}".
                print('choice id-',choice_id)
            except (KeyError, TypeError, ValueError) as e:
                raise web.HTTPBadRequest(text='You have not specified choice value') from e
            try:
                await db.vote(conn, choice_id, question_id)
            except db.RecordNotFound as e:
                raise web.HTTPNotFound(text=str(e))

            router = request.app.router		# get router info of app
            url = router['results'].url_for(question_id=str(question_id))
            # router['results']:   router.add_get('/poll/{question_id}/results', results, name='results')
            return web.HTTPFound(location=url)
    except Exception as e:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        raise web.HTTPNotFound(text=str(e) + " Line no : " + str(exc_tb.tb_lineno))

@aiohttp_jinja2.template('results.html')
async def results(request):
	async with request.app['db'].acquire() as conn:
		question_id = request.match_info['question_id']

		try:
			question, choices = await db.get_question(conn, question_id)
		except db.RecordNotFound as e:
			raise web.HTTPNotFound(text=str(e))
		return {
			'question': question,
			'choices': choices
		}

