from .tool.func import *

from .api_bbs_w_post import api_bbs_w_post
from .go_api_bbs_w_comment import api_bbs_w_comment

from .go_api_topic import api_topic_thread_make, api_topic_thread_pre_render

from .edit import edit_editor

async def bbs_w_post_comment(conn, user_id, sub_code, comment_num, bbs_num_str, post_num_str):
    comment_data = ''
    comment_select = ''

    comment_count = 0
    comment_add_count = 0

    thread_data = orjson.loads((await api_bbs_w_comment(sub_code)).get_data(as_text = True))

    for temp_dict in thread_data:
        if temp_dict['comment_user_id'] != '':
            color = 'default'
            if user_id == temp_dict['comment_user_id']:
                color = 'green'

            sub_code_check = re.sub(r'^[0-9]+-[0-9]+-', '', temp_dict['id'] + '-' + temp_dict['code'])
            margin_count = sub_code_check.count('-')

            if margin_count == 0:
                comment_count += 1
            else:
                comment_add_count += 1

            date = ''
            date += '<a href="javascript:opennamu_change_comment(\'' + sub_code_check + '\');">(' + get_lang(conn, 'comment') + ')</a> '
            date += '<a href="/bbs/tool/' + bbs_num_str + '/' + post_num_str + '/' + sub_code_check + '">(' + get_lang(conn, 'tool') + ')</a> '
            date += temp_dict['comment_date']

            comment_data += '<span style="padding-left: 20px;"></span>' * margin_count
            comment_data += api_topic_thread_make(
                ip_pas(temp_dict['comment_user_id']),
                date,
                render_set(conn, doc_data = temp_dict['comment']),
                sub_code_check,
                color = color,
                add_style = 'width: calc(100% - ' + str(margin_count * 20) + 'px);'
            )

            comment_default = ''
            if comment_num == sub_code_check:
                comment_default = 'selected'

            comment_select += '<option value="' + sub_code_check + '" ' + comment_default + '>' + sub_code_check + '</option>'

    return (comment_data, comment_select, comment_count, comment_add_count)

async def bbs_w_post(bbs_num = '', post_num = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()

        curs.execute(db_change('select set_data from bbs_set where set_id = ? and set_name = "bbs_name"'), [bbs_num])
        db_data_3 = curs.fetchall()
        if not db_data_3:
            return redirect(conn, '/bbs/main')
        
        bbs_name = db_data_3[0][0]

        bbs_num_str = str(bbs_num)
        post_num_str = str(post_num)
        bbs_comment_acl = acl_check(bbs_num_str, 'bbs_comment')
        ip = ip_check()

        temp_dict = orjson.loads(api_bbs_w_post(bbs_num_str + '-' + post_num_str).data)
        if temp_dict == {}:
            return redirect(conn, '/bbs/main')
        
        curs.execute(db_change('select set_data from bbs_set where set_id = ? and set_name = "bbs_type"'), [bbs_num])
        db_data_2 = curs.fetchall()
        if not db_data_2:
            return redirect(conn, '/bbs/main')
        elif db_data_2[0][0] == 'thread':
            if flask.request.method == 'POST':
                if bbs_comment_acl == 1:
                    return redirect(conn, '/bbs/set/' + bbs_num_str)
                
                if captcha_post(conn, flask.request.form.get('g-recaptcha-response', flask.request.form.get('g-recaptcha', ''))) == 1:
                    return re_error(conn, 13)

                set_id = bbs_num_str + '-' + post_num_str

                curs.execute(db_change('select set_code from bbs_data where set_name = "comment" and set_id = ? order by set_code + 0 desc'), [set_id])
                db_data_4 = curs.fetchall()
                id_data = str(int(db_data_4[0][0]) + 1) if db_data_4 else '1'

                data = flask.request.form.get('content', '')
                if data == '':
                    # re_error로 대체 예정
                    return redirect(conn, '/bbs/w/' + bbs_num_str + '/' + post_num_str)
                
                data = data.replace('\r', '')
                data = api_topic_thread_pre_render(conn, data, id_data, ip, set_id, bbs_name, temp_dict['title'], 'post')
                
                date = get_time()

                curs.execute(db_change("insert into bbs_data (set_name, set_code, set_id, set_data) values ('comment', ?, ?, ?)"), [id_data, set_id, data])
                curs.execute(db_change("insert into bbs_data (set_name, set_code, set_id, set_data) values ('comment_date', ?, ?, ?)"), [id_data, set_id, date])
                curs.execute(db_change("insert into bbs_data (set_name, set_code, set_id, set_data) values ('comment_user_id', ?, ?, ?)"), [id_data, set_id, ip])

                add_alarm(temp_dict['user_id'], ip, 'BBS <a href="/bbs/w/' + bbs_num_str + '/' + post_num_str + '#' + id_data + '">' + html.escape(bbs_name) + ' - ' + html.escape(temp_dict['title']) + '#' + id_data + '</a>')

                return redirect(conn, '/bbs/w/' + bbs_num_str + '/' + post_num_str + '#' + id_data)
            else:
                if acl_check(bbs_num_str, 'bbs_view') == 1:
                    return re_error(conn, 0)

                text = ''

                date = ''
                date += temp_dict['date']

                data = ''
                data += '<h2>' + html.escape(temp_dict['title']) + '</h2>'
                data += api_topic_thread_make(
                    ip_pas(temp_dict['user_id']),
                    date,
                    render_set(conn, doc_data = temp_dict['data'], data_type = 'thread'),
                    '0',
                    color = 'green'
                )

                user_id = temp_dict['user_id']
                count = 0

                thread_data = orjson.loads((await api_bbs_w_comment(bbs_num_str + '-' + post_num_str)).get_data(as_text = True))
                for temp_dict in thread_data:
                    count += 1
                    if user_id == temp_dict['comment_user_id']:
                        color = 'green'
                    else:
                        color = 'default'
                        
                    date = ''
                    date += '<a href="/bbs/tool/' + bbs_num_str + '/' + post_num_str + '/' + str(count) + '">(' + get_lang(conn, 'tool') + ')</a> '
                    date += temp_dict['comment_date']

                    data += api_topic_thread_make(
                        ip_pas(temp_dict['comment_user_id']),
                        date,
                        render_set(conn, doc_data = temp_dict['comment'], data_type = 'thread'),
                        str(count),
                        color = color
                    )

                data += '''
                    <form method="post">
                        ''' + (edit_editor(conn, ip, text, 'bbs_comment') if bbs_comment_acl == 0 else '') + '''
                    </form>
                '''

                return easy_minify(conn, flask.render_template(skin_check(conn),
                    imp = [bbs_name, wiki_set(conn), wiki_custom(conn), wiki_css(['(' + get_lang(conn, 'bbs') + ')', 0])],
                    data = data,
                    menu = [['bbs/in/' + bbs_num_str, get_lang(conn, 'return')], ['bbs/edit/' + bbs_num_str + '/' + post_num_str, get_lang(conn, 'edit')], ['bbs/tool/' + bbs_num_str + '/' + post_num_str, get_lang(conn, 'tool')]]
                ))
        else:
            # db_data_2[0][0] == 'comment'
            if flask.request.method == 'POST':
                if bbs_comment_acl == 1:
                    return redirect(conn, '/bbs/set/' + bbs_num_str)
                
                if captcha_post(conn, flask.request.form.get('g-recaptcha-response', flask.request.form.get('g-recaptcha', ''))) == 1:
                    return re_error(conn, 13)
                
                select = flask.request.form.get('comment_select', '0')
                select = '' if select == '0' else select

                comment_user_name = ''

                if select != '':
                    select_split = select.split('-')
                    if len(select_split) < 2:
                        curs.execute(db_change('select set_data from bbs_data where set_name = "comment_user_id" and set_id = ? and set_code = ? limit 1'), [bbs_num_str + '-' + post_num_str, select_split[0]])    
                        db_data_6 = curs.fetchall()
                        if not db_data_6:
                            # re_error로 변경 예정
                            return redirect(conn, '/bbs/w/' + bbs_num_str + '/' + post_num_str)
                        else:
                            set_id = bbs_num_str + '-' + post_num_str + '-' + select_split[0]
                            comment_user_name = db_data_6[0][0]
                    else:
                        curs.execute(db_change('select set_data from bbs_data where set_name = "comment_user_id" and set_id = ? and set_code = ? limit 1'), [bbs_num_str + '-' + post_num_str + '-' + '-'.join(select_split[0:len(select_split) - 1]), select_split[len(select_split) - 1]])
                        db_data_7 = curs.fetchall()
                        if not db_data_7:
                            return redirect(conn, '/bbs/w/' + bbs_num_str + '/' + post_num_str)
                        else:
                            set_id = bbs_num_str + '-' + post_num_str + '-' + '-'.join(select_split)
                            comment_user_name = db_data_7[0][0]
                else:
                    set_id = bbs_num_str + '-' + post_num_str

                curs.execute(db_change('select set_code from bbs_data where set_name = "comment" and set_id = ? order by set_code + 0 desc limit 1'), [set_id])
                db_data_5 = curs.fetchall()
                id_data = str(int(db_data_5[0][0]) + 1) if db_data_5 else '1'

                data = flask.request.form.get('content', '')
                if data == '':
                    # re_error로 대체 예정
                    return redirect(conn, '/bbs/w/' + bbs_num_str + '/' + post_num_str)

                date = get_time()

                curs.execute(db_change("insert into bbs_data (set_name, set_code, set_id, set_data) values ('comment', ?, ?, ?)"), [id_data, set_id, data])
                curs.execute(db_change("insert into bbs_data (set_name, set_code, set_id, set_data) values ('comment_date', ?, ?, ?)"), [id_data, set_id, date])
                curs.execute(db_change("insert into bbs_data (set_name, set_code, set_id, set_data) values ('comment_user_id', ?, ?, ?)"), [id_data, set_id, ip])
            
                if set_id == '':
                    end_id = id_data
                else:
                    set_id = re.sub(r'^[0-9]+-[0-9]+-?', '', set_id)
                    set_id += '-' if set_id != '' else ''
                    end_id = set_id + id_data

                add_alarm(temp_dict['user_id'], ip, 'BBS <a href="/bbs/w/' + bbs_num_str + '/' + post_num_str + '#' + end_id + '">' + html.escape(bbs_name) + ' - ' + html.escape(temp_dict['title']) + '#' + end_id + '</a>')
                if comment_user_name != '':
                    add_alarm(comment_user_name, ip, 'BBS <a href="/bbs/w/' + bbs_num_str + '/' + post_num_str + '#' + end_id + '">' + html.escape(bbs_name) + ' - ' + html.escape(temp_dict['title']) + '#' + end_id + '</a>')

                return redirect(conn, '/bbs/w/' + bbs_num_str + '/' + post_num_str + '#' + end_id)
            else:
                if acl_check(bbs_num_str, 'bbs_view') == 1:
                    return re_error(conn, 0)
                    
                text = ''
                comment_num = ''

                date = ''
                date += '<a href="javascript:opennamu_change_comment(\'0\');">(' + get_lang(conn, 'comment') + ')</a> '
                date += temp_dict['date']

                data = ''
                data += '<h2>' + html.escape(temp_dict['title']) + '</h2>'
                data += api_topic_thread_make(
                    ip_pas(temp_dict['user_id']),
                    date,
                    render_set(conn, doc_data = temp_dict['data']),
                    '0',
                    color = 'red'
                )

                user_id = temp_dict['user_id']
                comment_data = ''

                comment_select = '<select id="opennamu_comment_select" name="comment_select">'
                comment_select += '<option value="0">' + get_lang(conn, 'normal') + '</option>'

                comment_count = 0
                comment_add_count = 0

                temp_data = await bbs_w_post_comment(conn, user_id, bbs_num_str + '-' + post_num_str, comment_num, bbs_num_str, post_num_str)

                comment_data += temp_data[0]
                comment_select += temp_data[1]
                comment_count += temp_data[2]
                comment_add_count += temp_data[3]

                if comment_data != '':
                    data += '<hr>'

                comment_select += '</select>'
                if comment_data != '':
                    data += get_lang(conn, 'comment') + ' : ' + str(comment_count) + '<hr class="main_hr">'
                    data += get_lang(conn, 'reply') + ' : ' + str(comment_add_count) + '<hr class="main_hr">'
                    data += comment_data
                else:
                    data += '<hr class="main_hr">'

                bbs_comment_form = ''
                if bbs_comment_acl == 0:
                    bbs_comment_form += '''
                        ''' + comment_select + ''' <a href="javascript:opennamu_return_comment();">(''' + get_lang(conn, 'return') + ''')</a>
                        <hr class="main_hr">
                        
                        ''' + edit_editor(conn, ip, text, 'bbs_comment') + '''
                    '''

                data += '''
                    <form method="post">
                        ''' + bbs_comment_form + '''
                    </form>
                    <script defer src="/views/main_css/js/route/bbs_w_post.js''' + cache_v() + '''"></script>
                '''

                return easy_minify(conn, flask.render_template(skin_check(conn),
                    imp = [bbs_name, wiki_set(conn), wiki_custom(conn), wiki_css(['(' + get_lang(conn, 'bbs') + ')', 0])],
                    data = data,
                    menu = [['bbs/in/' + bbs_num_str, get_lang(conn, 'return')], ['bbs/edit/' + bbs_num_str + '/' + post_num_str, get_lang(conn, 'edit')], ['bbs/tool/' + bbs_num_str + '/' + post_num_str, get_lang(conn, 'tool')]]
                ))