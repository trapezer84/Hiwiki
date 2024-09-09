from .tool.func import *

def recent_record_reset(name = 'Test'):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if acl_check('', 'owner_auth', '', '') == 1:
            return re_error(conn, 3)

        if flask.request.method == 'POST':
            acl_check(tool = 'owner_auth', memo = 'record reset ' + name)

            curs.execute(db_change("delete from history where ip = ?"), [name])

            return redirect(conn, '/record/' + url_pas(name))
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [name, wiki_set(conn), wiki_custom(conn), wiki_css(['(' + get_lang(conn, 'record_reset') + ')', 0])],
                data = '''
                    <form method="post">
                        <span>''' + get_lang(conn, 'delete_warning') + '''</span>
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'reset') + '''</button>
                    </form>
                ''',
                menu = [['record/' + url_pas(name), get_lang(conn, 'return')]]
            ))