import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, session
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from ps_herald import db
from ps_herald.main.forms import EditProfileForm, PostForm
from ps_herald.models import User, Post, Log
from ps_herald.translate import translate
from ps_herald.main import bp
from sqlalchemy.sql import or_


import ps
from ps.Basic import Basic
from socket import gethostname
HOSTNAME=gethostname()
Basic("HERALD")






@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()
    #g.locale = str(get_locale())


#@bp.route('/', methods=['GET', 'POST'])
#@bp.route('/index', methods=['GET', 'POST'])
#@login_required
#def index():
#    form = PostForm()
#    if form.validate_on_submit():
#        language = guess_language(form.post.data)
#        if language == 'UNKNOWN' or len(language) > 5:
#            language = ''
#        post = Post(body=form.post.data, author=current_user,
#                    language=language)
#        db.session.add(post)
#        db.session.commit()
#        flash(_('Your post is now live!'))
#        return redirect(url_for('main.index'))
#    page = request.args.get('page', 1, type=int)
#    posts = current_user.followed_posts().paginate(
#        page, current_app.config['POSTS_PER_PAGE'], False)
#    next_url = url_for('main.index', page=posts.next_num) \
#        if posts.has_next else None
#    prev_url = url_for('main.index', page=posts.prev_num) \
#        if posts.has_prev else None
#    return render_template('index.html', title=_('Home'), form=form,
#                           posts=posts.items, next_url=next_url,
#                           prev_url=prev_url)


@bp.route('/',methods=['GET', 'POST'])
@bp.route('/index',methods=['GET', 'POST'])
#@login_required #
def index():
    """ Handle the html-request"""
    import pdb

#    pdb.set_trace()

    #                                              hosts in the haufe-net all start
    #                                              with vl_, we do not need a login here
    dev_stage=Basic.dev_stage

    if  not current_user.is_authenticated and not HOSTNAME.startswith("rs") :
        print("NOE")
        return redirect(url_for('auth.login'))
    #Basic.logger.debug("web interface got a request", extra={"package_version":herald_package_version.version})
    Basic.logger.debug("web interface got a request")
    if not 'pattern'      in session:
                             session["pattern"]      = ""
    if not 'starting_at'  in session:
                             session["starting_at"]   = \
                                                      str(datetime.datetime.now() + \
                                                          datetime.timedelta(days=-5)) # Five days before Today
    if not 'notify_level' in session:
                             session["notify_level"] = 30 #30 is error
    if not 'max_rows'     in session:
                             session["max_rows"]     = 1000
    if not 'old_row_first'in session:
                             session["old_row_first"]= 1
    if not 'PRODUKT_ID'        in session:     session["PRODUKT_ID"]        = "None"
    if not 'SYSTEM_ID'         in session:     session["SYSTEM_ID"]         = "None"
    if not 'SUB_SYSTEM_ID'     in session:     session["SUB_SYSTEM_ID"]     = "None"
    if not 'SUB_SUB_SYSTEM_ID' in session:     session["SUB_SUB_SYSTEM_ID"] = "None"
    if not 'USER_SPEC_1'       in session:     session["USER_SPEC_1"]       = "None"
    if not 'USER_SPEC_2'       in session:     session["USER_SPEC_2"]       = "None"

    if request.method == 'POST':
        session["pattern"]           = request.form['pattern'].strip()
        session["starting_at"]       = request.form['starting_at'].strip()
        session["notify_level"]      = request.form['notify_level']
        session["max_rows"]          = request.form['max_rows']
        session["old_row_first"]     = request.form['old_row_first']
        session["PRODUKT_ID"]               = request.form['PRODUKT_ID'].strip()
        session["SYSTEM_ID"]         = request.form['SYSTEM_ID'].strip()
        session["SUB_SYSTEM_ID"]     = request.form['SUB_SYSTEM_ID'].strip()
        session["SUB_SUB_SYSTEM_ID"] = request.form['SUB_SUB_SYSTEM_ID'].strip()
        session["USER_SPEC_1"]       = request.form['USER_SPEC_1'].strip()
        session["USER_SPEC_2"]       = request.form['USER_SPEC_2'].strip()
    pattern           = session["pattern"]
    starting_at       = session["starting_at"]
    notify_level      = session["notify_level"]
    max_rows          = session["max_rows"]
    old_row_first     = session['old_row_first']
    PRODUKT_ID        = session["PRODUKT_ID"]
    SYSTEM_ID         = session["SYSTEM_ID"]
    SUB_SYSTEM_ID     = session["SUB_SYSTEM_ID"]
    SUB_SUB_SYSTEM_ID = session["SUB_SUB_SYSTEM_ID"]
    USER_SPEC_1       = session["USER_SPEC_1"]
    USER_SPEC_2       = session["USER_SPEC_2"]
    if int(old_row_first) == 1:  user_interface_time_order_of_rows="asc"
    else:                        user_interface_time_order_of_rows="desc"

    def isset(param1,param2):
       """jinjas equalto did not work at this point in time. So this wrapper function
          enables the jinja-template do check if a value within a option was selected
          by the user interface.
          If another way is found to set an <option> value im the jinja template,
          this workaround should be eliminated.
       """
       if str(param1)==str(param2):
             return {"value":param1,"selected":True}
       return {"value":param1,"selected":False}

    unset={'selected': False, 'value': 'None'}
    sset ={'selected': True, 'value': 'None'}
    # The kind, how values for the userinterface are choosen is computing intensive - but generic
    # I am no t quite shure if this approach satisfies future performance requirements
    # An easy way to eliminate the queries (on each call) would be to define the
    # values in a config file.
    pid_query         = db.session.query(Log.produkt_id.distinct().label("produkt_id"))
    pids              = [ isset(row.produkt_id,PRODUKT_ID)                              for row in pid_query.all() ]
    sid_query         = db.session.query(Log.system_id.distinct().label("system_id"))
    system_ids        = [ isset(row.system_id,SYSTEM_ID)                  for row in sid_query.all() ]
    sub_sid_query     = db.session.query(Log.sub_system_id.distinct().label("sub_system_id"))
    sub_system_ids    = [ isset(row.sub_system_id,SUB_SYSTEM_ID)          for row in sub_sid_query.all() ]
    sub_sub_sid_query = db.session.query(Log.sub_sub_system_id.distinct().label("sub_sub_system_id"))
    sub_sub_system_ids= [ isset(row.sub_sub_system_id, SUB_SUB_SYSTEM_ID) for row in sub_sub_sid_query.all() ]
    u1_query          = db.session.query(Log.user_spec_1.distinct().label("user_spec_1"))
    user_spec_1_ids   = [ isset(row.user_spec_1,USER_SPEC_1)              for row in u1_query.all() ]
    u2_query          = db.session.query(Log.user_spec_2.distinct().label("user_spec_2"))
    user_spec_2_ids   = [ isset(row.user_spec_2,USER_SPEC_2)              for row in u2_query.all() ]

    #print sid_query.all()
    #print system_ids

    records = Log.query.filter(
                        Log.created  >=  session["starting_at"],
                        Log.levelno  >=  int(session["notify_level"]),
                        Log.module.like("%"+session["pattern"]+"%"),
                        Log.summary.like("%"+session["PRODUKT_ID"]+"%"),
                        Log.summary.like("%"+session["SYSTEM_ID"]+"%"),
                        Log.summary.like("%"+session["SUB_SYSTEM_ID"]+"%"),
                        Log.summary.like("%"+session["SUB_SUB_SYSTEM_ID"]+"%"),
                        Log.summary.like("%"+session["USER_SPEC_1"]+"%"),
                        Log.summary.like("%"+session["USER_SPEC_2"]+"%"),
                        or_(Log.message.like("%"+session["pattern"]+"%"),
                                Log.module.like("%"+session["pattern"]+"%"),
                                Log.funcname.like("%"+session["pattern"]+"%")
                                ),
                      ).order_by("created %s"%(user_interface_time_order_of_rows)).limit(int(session["max_rows"])).all()
    num_records = len(records)
    return render_template("index.html", **locals())



@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})



@bp.route('/reset_database',methods=[ 'GET'])
@login_required
def reset_database():
    start_date = str(datetime.datetime.now() -  datetime.timedelta(days=30)) # 30 days before Today
    to_del = Log.query.filter(Log.created < start_date).delete()
    return "OK: %s rows deleted"%(to_del)

@bp.route('/shutdown')
def server_shutdown():
   shutdown = request.environ.get('werkzeug.server.shutdown')
   if not shutdown: abort(500)
   shutdown()
   return "Shutting down server"



