from .tool.func import *

def give_delete_admin_group_2(name = 'test'):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if name in get_default_admin_group():
            return redirect(conn, '/auth/list')

        if acl_check('', 'owner_auth', '', '') == 1:
            return re_error(conn, 3)

        if flask.request.method == 'POST':
            curs.execute(db_change("select name from user_set where name = 'acl' and data = ? limit 1"), [name])
            if not curs.fetchall():
                acl_check(tool = 'owner_auth', memo = 'auth list delete (' + name + ')')

                curs.execute(db_change("delete from alist where name = ?"), [name])

                return redirect(conn, '/auth/list')
            else:
                return re_error(conn, 47)
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, "delete_admin_group"), wiki_set(conn), wiki_custom(conn), wiki_css(['(' + name + ')', 0])],
                data = '' + \
                    '<form method="post">' + \
                        '<button type="submit">' + get_lang(conn, 'delete') + '</button>' + \
                    '</form>' + \
                '',
                menu = [['auth/list', get_lang(conn, 'return')]]
            ))