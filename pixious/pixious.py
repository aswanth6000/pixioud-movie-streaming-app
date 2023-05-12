from flask import Flask, render_template, request, redirect,session
import datetime
from DBConnection import Db
import html


app = Flask(__name__)
app.secret_key="abc"

@app.route('/')
def home():
    db = Db()
    jz=db.select("select movie.*,round(avg(rating.rating),1) as rtng from movie left join  rating on movie.movie_id=rating.movie_id group by movie.movie_id")
    qw=db.select("select * from movie_promo_request where promo_status='approved'")
    return render_template('home.html', data=jz,data2=qw)


@app.route('/login',methods=['get','post'])
def login():
    if request.method=='POST':
        name=request.form['admin_name']
        password=request.form['admin_password']
        db=Db()
        q=db.selectOne("select * from login where username='"+name+"'and password='"+password+"'")
        if q is not None:
            session['utype']=q['usertype']
            if q['usertype']=='admin':
                return redirect('/adminhome')
            elif q['usertype']=='creator':
                session['lid']=q['login_id']
                # session['lid']=q['user_id']
                return redirect('/creatorhome')
            elif q['usertype']=='user':
                session['lid']=q['login_id']
                return redirect('/userhome')
            else:
                return "<script>alert('user not found');window.location='/'</script>"
        else:
            return "<script>alert('user not found');window.location='/'</script>"
    return render_template('loginl.html')

@app.route('/signup', methods=['get', 'post'])
def signup():
    if request.method =="POST":
        email = request.form['emails']
        passw = request.form['pass']
        num = request.form['phones']
        db=Db()
        q=db.insert("insert into login VALUES ('','" + email + "','" + passw + "','user','')")
        db.insert("insert into user VALUES ('"+str(q)+"','','','" + num + "','','active','','user')")
        return '''<script>alert("signup suscessfull redirecting to login page");window.location="/login"</script>'''
    else:
        return render_template('signup.html')




@app.route('/logout')
def logout():
    session.pop('lid', None)
    return redirect('/')

@app.route('/adminhome')
def adminhome():
    return render_template('admin/index.html')

@app.route('/aboutus')
def aboutus():
    return render_template('about page.html')

@app.route('/addevents')
def addevents():
    return render_template('admin/movie course.html')

@app.route('/Approve_movies')
def Approve_movies():
    db=Db()
    t=db.select("select * from movie,creator,user where movie.creator_id=creator.creator_id and creator.user_id=user.user_id")
    return render_template('admin/approve_movies_d.html',data=t)


@app.route('/adm_approve_movie/<mid>')
def adm_approve_movie(mid):
    db = Db()
    db.update("update movie set movie_status='approved' where movie_id='"+mid+"'")
    return '''<script>alert("Approved");window.location="/Approve_movies"</script>'''

@app.route('/movierej/<fid>')
def movierej(fid):
    db = Db()
    db.update("update movie set movie_status='rejected' where movie_id='" + fid + "'")
    return '''<script>alert("rejected");window.location="/Approve_movies"</script>'''


@app.route('/bugs')
def bugs():
    db=Db()
    res=db.select("select * from bugs,user where bugs.sender_id=user.user_id")
    return render_template('admin/bugs_d.html',data=res)

@app.route('/changepass',methods=['get','post'])
def changepass():
    if request.method == 'POST':
        current = request.form['admin_name']
        new = request.form['old_password']
        confirm=request.form['admin_password']
        db = Db()
        a=db.selectOne("select * from login where  password='"+current+"'and usertype='admin'")
        if a is not None:
            if new==confirm:
                db=Db()
                db.update("update login set password='"+confirm+"' where usertype='admin'")
                return "<script>alert('password changed sucessfully');window.location='/changepass'</script>"
            else:
                return "<script>alert('password mis match');window.location='/changepass'</script>"
        else:
            return "<script>alert('password changed sucessfully');window.location='/changepass'</script>"
    else:
        return render_template('admin/Change Password.html')
#------------comment---------------------
@app.route('/comment')
def comment():
    db=Db()
    g=db.select("select * from comment,movie where comment.movie_id=movie.movie_id")
    return render_template('admin/comment_d.html',data=g)

@app.route('/comdelete/<fid>')
def comdelete(fid):
    db = Db()
    db.delete("delete from comment where comment_id='"+fid+"'")
    return '''<script>alert("deleted");window.location="/comment"</script>'''
#------------------------creator verification------------------------------------------------------------
@app.route('/verification')
def verification():

        db = Db()
        w= db.select("select * from user,creator where user.user_id=creator.user_id")
        return render_template('admin/varification_d.html',data=w)

@app.route('/adm_verification/<uid>')
def adm_verification(uid):
    db = Db()
    db.update("update creator set status='approved' where user_id='"+uid+"'")
    db.update("update login set usertype='creator' where login_id='"+uid+"'")
    db.update("update user set user_type='creator' where user_id='"+uid+"'")
    # db.update("update login set usertype='creator' where creator_id='"+uid+"'")
    # db.update("update login set usertype='creator' where user_id='"+uid+"'")
    return '''<script>alert("Approved");window.location="/verification"</script>'''

@app.route('/creator_rej/<fid>')
def creator_rej(fid):
    db = Db()
    db.update("update creator set status='rejected' where user_id='" + fid + "'")
    return '''<script>alert("rejected");window.location="/verification"</script>'''
#----------------------------feed back-----------------------
@app.route('/feedback')
def feedback():
    db=Db()
    b=db.select("select * from feedback,user where feedback.sender_id=user.user_id")

    return render_template('admin/feedback_d.html',data=b)

@app.route('/reply/<fid>',methods=['get','post'])
def reply(fid):
    if request.method == 'POST':
        r= request.form['textarea']
        db=Db()
        db.update("update feedback set reply='"+r+"',reply_date='curdate()' where feedback_id='"+fid+"'")
        return '<script>alert("send successfully");window.location="/feedback"</script>'
    else:
        return render_template("admin/reply_d.html")

@app.route('/report')
def report():
    db = Db()
    p=db.select("select * from report")
    return render_template('admin/Filim Report.html',data=p)

@app.route('/delete/<fid>')
def delete(fid):
    db = Db()
    db.delete("delete from film_report where film_report_id='"+fid+"'")
    return '''<script>alert("deleted");window.location="/report"</script>'''



#-------promo request---------
@app.route('/promorequest')
def promorequest():
    db = Db()
    p = db.select("select * from movie_promo_request,user where movie_promo_request.sender_id=user.user_id")
    return render_template('admin/promoreq_d.html',data=p)

@app.route('/promo_acc/<uid>')
def promo_acc(uid):
    db = Db()
    db.update("update movie_promo_request set promo_status='approved'  where promo_request_id='"+uid+"'")
    return '''<script>alert("Approved");window.location="/promorequest"</script>'''
@app.route('/promo_rej/<uid>')
def promo_rej(uid):
    db = Db()
    db.update("update movie_promo_request set promo_status='rejected' where promo_request_id='"+uid+"'")
    return '''<script>alert("rejected");window.location="/promorequest"</script>'''
@app.route('/promo_del/<uid>')
def prdelete(uid):
    db = Db()
    db.delete("delete from movie_promo_request where promo_request_id='"+uid+"'")
    return '''<script>alert("deleted");window.location="/promorequest"</script>'''

#------------------view users------------------

@app.route('/view',methods=['get','post'])
def view():
    if request.method=="POST":
        s=request.form['select']
        n=request.form['t']
        db = Db()
        p = db.select("select * from user,creator where creator.user_id=user.user_id  and creator.status='"+s+"' and user.name='"+n+"' ")
        return render_template('admin/View users_d.html',data=p)
    else:
        db = Db()
        p = db.select("select * from user ")
        return render_template('admin/View users_d.html',data=p)


@app.route('/user_block/<uid>')
def user_block(uid):
    db = Db()
    db.update("update user set user_status='blocked' where user_id='"+uid+"'")
    return '''<script>alert("blocked");window.location="/view"</script>'''
@app.route('/user_unblock/<uid>')
def user_unblock(uid):
    db = Db()
    db.update("update user set user_status='active' where user_id='"+uid+"'")
    return '''<script>alert("un blocked");window.location="/view"</script>'''

# ======================================================================================================================================
#                                                      CREATOR MODULE
# =====================================================================================================================================


@app.route('/creatorhome')
def creatorhome():
    db=Db()
    jz=db.select("select movie.*,round(avg(rating.rating),1) as rtng from movie left join  rating on movie.movie_id=rating.movie_id group by movie.movie_id")
    qw=db.select("select * from movie_promo_request where promo_status='approved'")
    return render_template('creator/creator_index.html',data=jz,data2=qw)

@app.route('/addmovpromoreq',methods=['get','post'])
def addmovpromo():
    if request.method=="POST":
        moviename=request.form['movie_name']
        tlink =html.escape(request.form['t_link'])
        btkts =html.escape(request.form['book_tickets'])
        banner=request.files['bannerpromo']
        poster=request.files['posterpromo']
        description=request.form['description']
        date = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        banner.save(r"E:\college project\Pixious-project\pixious\static\promo\bannerpromo\\"+date+'.jpg')
        path5="/static/promo/bannerpromo/"+date+'.jpg'
        poster.save(r"E:\college project\Pixious-project\pixious\static\promo\posterpromo\\"+date+'.jpg')
        path6 = "/static/promo/posterpromo/" + date + '.jpg'
        db=Db()
        db.insert("insert into movie_promo_request VALUES('','"+date+"','"+str(session['lid'])+"','"+moviename+"','pending','"+path6+"','"+path5+"','"+ description+"','"+btkts+"','"+tlink+"')")
        if str(session['utype']) =='user':
            return '''<script>alert('Promo Request send succesfully');window.location="/userhome"</script>'''
        else:
            return '''<script>alert('Promo Request send succesfully');window.location="/creatorhome"</script>'''
    else:
        return render_template('creator/promo req d.html')

@app.route('/viewpromoreqs')
def viewpromoreqs():
    db = Db()
    qrys=db.select("select * from movie_promo_request where sender_id='"+str(session['lid'])+"'")
    return render_template('creator/view promo request.html',data=qrys)

@app.route('/addmovie',methods=['get','post'])
def addmovie():
    if request.method=="POST":
        movie=request.files['file']
        moviename=request.form['movie_name']
        description=html.escape(request.form['description'])
        mov_poster=request.files['poster']
        mov_banner=request.files['Banner']
        directorname=request.form['director_name']
        date=datetime.datetime.now().strftime("%y%m%d-%H%M%S")

        movie.save(r"E:\college project\Pixious-project\pixious\static\movie\\"+date+'.mp4')
        path="/static/movie/"+date+'.mp4'

        mov_banner.save(r"E:\college project\Pixious-project\pixious\static\banner\\"+date+'.jpg')
        path2="/static/banner/"+date+'.jpg'

        mov_poster.save(r"E:\college project\Pixious-project\pixious\static\poster\\"+date+'.jpg')
        path3="/static/poster/"+date+'.jpg'

        db=Db()
        db.insert("insert into movie VALUES('','"+moviename+"','"+description+"','"+str(session['lid'])+"','"+directorname+"','"+str(path)+"','pending','"+str(path3)+"','"+str(path2)+"')")
        return '''<script>alert("uploaded successfully");window.location="/creatorhome"</script>'''
    else:
        return render_template('creator/mov upload form.html')


@app.route('/creatorcomment',methods=['get','post'])
def creatorcomment():
    if request.method=="POST":
        comment=request.form['comment']
        return "ok"
    else:
        return render_template('creator/Comment.html')

@app.route('/addcomment/<mid>', methods=['get', 'post'])
def addcomment(mid):
        if request.method == "POST":
            comment = request.form['comment']
            db = Db()
            db.insert("insert into comment VALUES ('','" + comment + "','" + str(session['lid']) + "','"+mid+"',curdate(),'creator','pending','pending')")
            return '''<script>alert("Comment added");window.location="/viewcomment"</script>'''
        else:
            return render_template('creator/view comments.html')

@app.route('/addcomreply/<mid>', methods=['get', 'post'])
def addcomreply(mid):
            if request.method == "POST":
                comreply = request.form['reply']
                db = Db()
                db.update("update comment set reply='"+comreply+"',reply_date=curdate() where comment_id='" + mid + "' ")
                return '''<script>alert("Reply added");window.location="/viewcrmov"</script>'''
            else:
                return render_template('creator/comment reply.html')
#------------------------------------------------------HIring---------------------------

@app.route('/hiring',methods=['get','post'])
def hiring():

    if request.method=="POST":
        subject=request.form['upload_subject']
        hir_description=request.form['hiring_description']
        db = Db()
        db.insert("insert into hiring VALUES ('','"+str(session['lid'])+"','"+hir_description+"','"+subject+"')")
        return '''<script>alert('Hiring added');window.location="/viewmyhr"</script>'''
    else:
        return render_template('creator/add hiring form.html')

@app.route('/hiring_app/<uid>')
def hiring_app(uid):
    db = Db()
    if str(session['utype']) == 'user':
     db.insert("insert into applied_hiring VALUES ('','" + uid + "','" + str(session['lid']) + "','user')")
    else:
        db.insert("insert into applied_hiring VALUES ('','" + uid + "','" + str(session['lid']) + "','creator')")

    return '''<script>alert('Applied');window.location="/viewapphiring"</script>'''


@app.route('/viewapphiring')
def viewhiring():
    db=Db()
    j=db.select("select * from hiring,applied_hiring WHERE applied_hiring.sender_id='" + str(session['lid']) + "' and hiring.hiring_id=applied_hiring.hiring_id")
    return render_template('creator/view hiring and apply d.html',data=j)

@app.route('/viewhiringandapply')
def viewhiringandapply():
    db = Db()
    qry=db.select("select * from hiring,user where hiring.user_id=user.user_id and user.user_id!='" + str(session['lid']) + "' ")
    return render_template('creator/view hiring and apply d.html',data=qry)

@app.route('/viewmyhr')
def viewmyhr():
    db = Db()
    qrys=db.select("select * from hiring where hiring.user_id='"+str(session['lid'])+"'")
    return render_template('creator/view my hirings.html',data=qrys)

@app.route('/viewmyhrapp')
def viewmyhrapp():
    db = Db()
    qrys=db.select("select * from applied_hiring,user where applied_hiring.sender_id=user.user_id")
    return render_template('creator/view who applied.html',data=qrys)

@app.route('/deletemyhr/<fid>')
def deletemyhr(fid):
    db = Db()
    db.delete("delete from hiring where hiring_id='"+fid+"'")
    return '''<script>alert("deleted");window.location="/viewmyhr"</script>'''

#--------------------------------------------------------------------------------------------------



@app.route('/sendfeedback',methods=['get','post'])
def sendfeedback():
    if request.method=="POST":
        feedback=request.form['feedback']
        db=Db()
        db.insert("insert into feedback VALUES ('','"+str(session['lid'])+"','"+feedback+"',curdate(),'pending','pending','creator')")
        return redirect(request.referrer)
    else:
      return render_template('creator/feedback d.html')



@app.route('/creatorbug',methods=['get','post'])
def creatorbug():
    if request.method=="POST":
        heading=request.form['heading']
        description=request.form['bug_desc']
        db = Db()
        db.insert("insert into bugs VALUES ('','"+str(session['lid'])+"',curdate(),'"+heading+"','"+description+"','creator','pending','pending')")
        return redirect(request.referrer)
    else:
        return render_template('creator/bugs form.html')




@app.route('/viewcomment/<mid>')
def viewcomment(mid):
    db = Db()
    h=db.select("select * from comment,user where comment.sender_id=user.user_id and comment.movie_id='"+mid+"'")
    return render_template('creator/view comments.html',data=h,m=mid)

@app.route('/rep_comment/<fid>')
def rep_comment(fid):
    db = Db()
    db.insert("insert into report VALUES ('','" + str(session['lid']) + "','"+fid+"','creator','comment')")
    return redirect(request.referrer)


@app.route('/viewfollowers')
def followers():
    db = Db()
    f=db.select("select * from followers,user where followers.from_id=user.user_id and followers.to_id='"+str(session['lid'])+"'")
    lst = []
    for i in f:
        fcnt = {}
        res = db.selectOne("select count(followers_id) as cnt from followers where to_id='" + str(
            i['to_id']) + "' and `status`='followed'")
        mn = db.selectOne("select count(movie_id) as mno from movie where creator_id='"+str(i['to_id'])+"' and `movie_status`='approved'")
        fcnt['cnt']=res['cnt']
        fcnt['toid']= i['to_id']
        fcnt['mc']= mn['mno']
        lst.append(fcnt)
#    session['p']=f[0]['photo']
    return render_template('creator/view followers d.html',data=f,lst1=lst)

@app.route('/follow/<uid>')
def follow(uid):
    db = Db()
    qry=db.selectOne("select * from followers where to_id='"+uid+"' and from_id='"+str(session['lid'])+"' and status='unfollowed'")
    if qry is not None:
        db.update("update followers set status='followed' where to_id='" + uid + "'")
        return redirect('/viewothercreator')

    else:
        db.insert("insert into followers VALUES ('','" + str(session['lid']) + "','creator','"+uid+"',curdate(),'followed')")
        return redirect('/viewothercreator')

@app.route('/unfollow/<uid>')
def unfollow(uid):
    db = Db()
    db.update("update followers set status='unfollowed' where to_id='" + uid + "'")
    return redirect('/viewothercreator')

@app.route('/viewcrmov/<uid>')
def viewcrmov(uid):
    db = Db()
    d=db.select("select * from movie where movie.creator_id='" + uid + "' and movie_status='approved'")
    return render_template('creator/my movies.html', data=d)

@app.route('/unfollowb/<uid>')
def unfollowb(uid):
    db = Db()
    db.update("update followers set status='unfollowed' where from_id='" + uid + "'")
    return redirect(request.referrer)

@app.route('/followb/<uid>')
def followb(uid):
    db = Db()
    db.update("update followers set status='followed' where from_id='" + uid + "'")
    return redirect(request.referrer)

@app.route('/addrating/<mid>',methods=['get','post'])
def addrating(mid):
    if request.method=="POST":
        rt=request.form['rating']
        db = Db()
        db.insert("insert into rating VALUES ('','" + rt+ "','" + mid+ "','" + str(session['lid']) + "',curdate())")
        return '''<script>alert("Added");window.location="/viewplaylist"</script>'''

    return render_template('creator/rate now.html')

@app.route('/addtoplaylist/<mid>')
def addtoplaylist(mid):
    db = Db()
    db.insert("insert into playlist VALUES ('','"+mid+"','" + str(session['lid']) + "','creator')")
    return '''<script>alert("Added to playlist");window.location="/viewplaylist"</script>'''


@app.route('/viewplaylist')
def viewplaylist():
    db = Db()
    d=db.select("select * from playlist,movie where playlist.movie_id=movie.movie_id")
    return render_template('creator/view play list_d.html',data=d)

@app.route('/rmplaylist/<fid>')
def rmplaylist(fid):
    db = Db()
    db.delete("delete from playlist where movie_id='"+fid+"'")
    return '''<script>alert("Movie removed from playlist");window.location="/viewplaylist"</script>'''




@app.route('/viewmovie')
def viewmovie():
    db = Db()
    b=db.select("select * from movie where creator_id='"+str(session['lid'])+"'")
    return render_template('creator/my movies.html', data=b)


@app.route('/watchmovie/<mid>')
def watchmovie(mid):
    db = Db()
    bz=db.select("select * from movie,user where movie_id='"+mid+"' and user.user_id=movie.creator_id")
    bd=db.select("select * from comment,user,movie where '"+mid+"'=comment.movie_id and user.user_id=comment.sender_id")
    return render_template('creator/anime-watching.html',data=bz,data4=bd)

@app.route('/delete_movie/<fid>')
def deletemovie(fid):
    db = Db()
    db.delete("delete from movie where movie_id='"+fid+"'")
    return '''<script>alert("deleted");window.location="/viewmovie"</script>'''


@app.route('/viewmoviereqvideo')
def viewmoviereqvideo():
    db = Db()
    a=db.select("select * from movie_promo ")
    return render_template('creator/view movie req video.html',data=a)



@app.route('/creatorpro')
def creatorpro():
    db = Db()
    bz = db.select("select * from user where user_id='"+str(session['lid'])+"'")
    return render_template('creator/creator_profile_section.html', data=bz)

@app.route('/othcrpro/<mid>')
def othcrpro(mid):
    db = Db()
    sid=db.selectOne("select user_id from user where user_id='"+str(session['lid'])+"'")
    bc = db.select("select * from user WHERE  user_id='"+mid+"'")
    ck = db.select("select * from followers WHERE  followers.from_id='"+str(session['lid'])+"' and followers.to_id='"+mid+"'")
    return render_template('creator/other users profile section.html', data=bc,data3=ck,s_id=sid['user_id'])

@app.route('/othcrfol/<mid>')
def othcrfol(mid):
    db = Db()
    bcp = db.select("SELECT * FROM user JOIN followers ON user.user_id = followers.from_id WHERE followers.to_id='"+mid+"'")
    return render_template('creator/view other user followers d.html', data=bcp)

@app.route('/editcreatordetails',methods=['get','post'])
def editcreatordetails():
    if request.method=="POST":
        cname=request.form['upname']
        cbio=request.form['upbio']
        cemail = request.form['upemail']
        profilepic=request.files['upfile']
        date=datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        profilepic.save(r"E:\college project\Pixious-project\pixious\static\profile\\"+date+'.jpg')
        db=Db()
        qry = db.selectOne("select * from user where user_id='" + str(session['lid']) + "'")
        if qry is not None:
            db.update("update user set name='" + cname + "',email='"+cemail+"',bio='"+cbio+"',photo='"+date+".jpg'where user.user_id='"+str(session['lid'])+"' ")
        return '''<script>alert("uploaded successfully");window.location="/creatorpro"</script>'''
    else:
        return render_template('creator/edit creator details.html')

@app.route('/message/<toid>')
def message(toid):
    # session['toid']=toid
    db = Db()
    # dp = db.selectOne("select `photo`,name from `user` where user_id='"+str(toid)+"'")
    # session['p']=dp['photo']


    # session['n']=dp['name']
    nm = db.selectOne("select `name` from `user` where user_id='"+str(toid)+"'")
    dcp=db.select("SELECT DISTINCT user.photo FROM message JOIN user ON user.user_id = message.to_id and user.user_id!='"+str(session['lid'])+"'")
    d = db.select("select * from  message ORDER BY message_id ASC")
    print("kkkkkkkkkkkkkkkkkkkkk","select `photo` from `user` where user_id='"+str(toid)+"'")
    return render_template('creator/messages.html', data=d,t=toid,nam=nm['name'],data2=dcp)
    # return render_template('creator/messages.html', data=d,nam=dp['name'],profile=dp['photo'],t=toid)
#

@app.route('/msgsnd/<t>',methods=['post'])
def msgsnd(t):
    cmt = request.form['chat']
    db = Db()
    db.insert("insert into message(from_id,to_id,message,date) values('"+str(session['lid'])+"','"+str(t)+"','"+str(cmt)+"',curdate())")
    return redirect("/message/"+str(t))




@app.route('/addcmt/<m>',methods=['post'])
def addcmt(m):
    mv = m
    cmt = request.form['comment']
    db = Db()
    db.insert("insert into comment VALUES ('','"+cmt+"','" + str(session['lid']) + "','"+mv+"',curdate(),'creator','','pending')")
    return '''<script>alert("Insetted");window.location="/viewcomment/'''+m+'''"</script>'''



@app.route('/search',methods=['post'])
def search():
    cmt = request.form['searchh']
    db = Db()
    c=db.select("select * from movie WHERE  movie_name='"+cmt+"'")
    return render_template('creator/serch mov.html', data=c)





# --------------------------------USER----------------------------------------USER------------------
# ---------------------------------------------------------------------------USER------------------

@app.route('/userhome')
def userhome():
    db=Db()
    jz=db.select("select movie.*,round(avg(rating.rating),1) as rtng from movie left join  rating on movie.movie_id=rating.movie_id group by movie.movie_id")
    qw=db.select("select * from movie_promo_request where promo_status='approved'")
    return render_template('user/user_index.html',data=jz,data2=qw)


@app.route('/rfv/<vid>')
def rfv(vid):
    db = Db()
    db.insert("insert into creator VALUES ('','" + vid + "','pending',curdate())")
    return '''<script>alert("Requested");window.location="/userhome"</script>'''

@app.route('/feedbackreply')
def feedbackreply():
    db = Db()
    d=db.select("select * from feedback,user where sender_id='"+str(session['lid'])+"' and user_id='"+str(session['lid'])+"'")
    return render_template('creator/feedback reply.html',data=d)

@app.route('/viewallusers')
def viewallusers():
    db = Db()
    d=db.select("select * from user where user_id !='"+str(session['lid'])+"'")
    o=db.select("select * from followers ")
    return render_template('creator/view all users.html',data=d,d2=o)

@app.route('/msghead')
def msghead():
    db = Db()
    d=db.select("SELECT DISTINCT message.to_id,message.from_id, user.name, user.photo FROM message JOIN user ON user.user_id = message.to_id and user.user_id!='"+str(session['lid'])+"'")
    return render_template('creator/message head.html',data=d)

@app.route('/pay',methods=['get','post'])
def pay():
    if request.method=="POST":
        nam=request.form['name']
        upi = request.form['upi']
        description=request.form['pay_desc']
        db = Db()
        qry = db.selectOne("select * from payment where user_id='" + str(session['lid']) + "'")
        if qry is not None:
            db.update("update payment set name='" + nam + "',upi='" + upi + "',description='" + description + "'")
        else:
            db.insert("insert into payment VALUES ('','"+nam+"','"+upi+"','"+description+"','"+str(session['lid'])+"')")

        return redirect(request.referrer)
    else:
        return render_template('creator/payment.html')


@app.route('/paym/<m>')
def paym(m):
    db=Db()
    jz=db.select("select * from payment where payment.user_id='"+m+"'")
    return render_template('creator/pay ind.html',data8=jz)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
