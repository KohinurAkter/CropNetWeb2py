# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
import gluon.contrib.simplejson as json
from datetime import datetime, timedelta
from time import localtime, strftime
import calendar, random
import pytz

#After Login Which page is redirected by server
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to Electrical and Electronic Engineering!'))
    #return locals()

#Get value from Node
def send_sensor_data():
    response.headers['content-type'] = 'text/json'
    req = request.body.read()
    doc = json.loads(req)
    current_time = datetime.now()
    dt = datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%Y-%m-%d %H:%M:%S")
    node_id=doc['node_id']
    temperature=doc['soil temperature']
    humidity=doc['relative humidity']
    mosture=doc['soil moisture']
    ambient=doc['ambient temperature']
    #ping_time=doc['ping_time']
    findNodeRefId=db.executesql("select id from Node where node_id='"+str(node_id)+"'")
    node_ref_id=findNodeRefId[0][0]
    db.Collected_Data.insert(node_ref_id=node_ref_id,temperature=temperature,humidity=humidity,mosture=mosture,ambient=ambient,ping_time=dt)
    db.commit()



def getjson():
    n1=db.executesql("select temperature,humidity,mosture from Collected_Data where node_ref_id=9 order by ping_time desc limit 10")
    temp=0
    hum=0
    mos=0
    for i in n1:
        temp0=i[0]
        hum0 = i[1]
        mos0=i[2]
        temp=temp+temp0
        mos=mos+mos0
        hum=hum+hum0
    temp=temp/10
    hum=hum/10
    mos = mos/10
    selectdata=db.executesql("select state,cstate from motor_state order by id desc limit 1")
    rstate=selectdata[0][0]
    cstate=selectdata[0][1]
    gejson= '{"avg_temp" : '+ str(temp)+',"avg_hum" : ' + str(hum) + ',"avg_mos" : '+ str(mos)+ ' , "requested_state" : "'+ str(rstate) + '","previous_state" : "' + str(cstate)+ ' "  }'
    return gejson

#For testing a function only
def test():
    return locals()

#All Nodes Data will show from here
@auth.requires_login()
def data_set():
    auth_Ref_id=auth.user.id
    sql="select cd.node_ref_id,n.node_id, cd.temperature, cd.humidity,cd.mosture, cd.ambient, cd.ping_time from Collected_Data as cd \
        join Node as n \
        on cd.node_ref_id=n.id \
        join Auth_Node as an \
        on an.node_ref_id=cd.node_ref_id\
        where an.auth_Ref_id="+str(auth_Ref_id)+" order by cd.ping_time desc"
    data=db.executesql(sql)
    return locals()

#Show individual nodes records
def units():
    id=request.vars.id
    node=db.executesql("select node_id from Node where id="+str(id))
    selectedNode=node[0][0]
    sql="select cd.node_ref_id,n.node_id, cd.temperature,cd.ambient, cd.humidity,cd.mosture,cd.ping_time from Collected_Data as cd \
        join Node as n \
        on cd.node_ref_id=n.id \
        join Auth_Node as an \
        on an.node_ref_id=cd.node_ref_id\
        where an.node_ref_id="+str(id)+" order by cd.ping_time desc"
    data=db.executesql(sql)
    return locals()

# Show all nodes at a glance
@auth.requires_login()
def all_devices():
    auth_Ref_id=auth.user.id
    sql="select n.id,n.node_id from Node as n \
            join Auth_Node as an \
            on an.node_ref_id=n.id \
            join auth_user as au \
            on an.auth_Ref_id=au.id\
            where au.id="+str(auth_Ref_id)
    data=db.executesql(sql)
    return locals()

#Creating a Node
@auth.requires_login()
def add_node():
    add=request.vars.add
    return locals()

#Delete a Node
@auth.requires_login()
def delete_node():
    id=request.vars.id
    chkNode=db.executesql("delete from Collected_Data where node_ref_id='"+str(id)+"'")
    redirect(URL('default', 'all_devices'))

#Save node posted by add_node()
@auth.requires_login()
def post_add_node():
    auth_Ref_id=auth.user.id
    add=request.vars.add
    node_id=request.vars.node_id
    node_name=request.vars.node_name
    node_location=request.vars.node_location
    chkNode=db.executesql("select id from Node where node_id='"+str(node_id)+"'")
    if not chkNode:
        db.executesql("insert into Node (node_id,node_name,node_location) values ('"+str(node_id)+"','"+str(node_name)+"','"+str(node_location)+"')")
        data=db.executesql("select id from Node where node_id='"+str(node_id)+"'")
        db.executesql("insert into Auth_Node (auth_Ref_id,node_ref_id) values ("+str(auth_Ref_id)+","+str(data[0][0])+")")
        data=db.executesql("select id from Node where node_id='"+str(node_id)+"'")
        node_ref_id=data[0][0]
        db.Collected_Data.insert(node_ref_id=node_ref_id,temperature=0,humidity=0,mosture=0,light=0,co2gas=0,ping_time="00-00-00 00:00:00")

        redirect(URL('default', 'add_node?add=1'))
    else:
        redirect(URL('default','add_node?add=2'))


def temp():
    selectdata=db.executesql("select ping_time,node_ref_id,temperature from Collected_Data where (node_ref_id=9 OR node_ref_id=7 )  AND DATE(ping_time)=CURDATE() \
    order by ping_time desc")
    tjson='{ "feeds" : ['
    for row in selectdata:
        ptime=row[0]
        ref_id=row[1]
        node=db.executesql("select node_id from Node where id=%s",[ref_id])
        node_name=node[0][0]
        temp=row[2]
        tjson+= '{"ptime" : "'+ str(ptime) + '","node" : "' + str(node_name) + '","temp" : "' + str(temp) +' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson

def humidity():
    selectdata=db.executesql("select ping_time,node_ref_id,humidity from Collected_Data where (node_ref_id=9 OR node_ref_id=7 )  AND DATE(ping_time)=CURDATE() \
    order by ping_time desc")
    tjson='{ "feeds" : ['
    for row in selectdata:
        ptime=row[0]
        ref_id=row[1]
        node=db.executesql("select node_id from Node where id=%s",[ref_id])
        node_name=node[0][0]
        hum=row[2]
        tjson+= '{"ptime" : "'+ str(ptime) + '","node" : "' + str(node_name) + '","humidity" : "' + str(hum) +' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson


def ambient():
    selectdata=db.executesql("select ping_time,node_ref_id,ambient from Collected_Data where (node_ref_id=9 OR node_ref_id=7 )  AND DATE(ping_time)=CURDATE() \
    order by ping_time desc")
    tjson='{ "feeds" : ['
    for row in selectdata:
        ptime=row[0]
        ref_id=row[1]
        node=db.executesql("select node_id from Node where id=%s",[ref_id])
        node_name=node[0][0]
        ambient_temp=row[2]
        tjson+= '{"ptime" : "'+ str(ptime) + '","node" : "' + str(node_name) + '","ambient_temp" : "' + str(ambient_temp) +' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson

def mosture():
    selectdata=db.executesql("select ping_time,node_ref_id,mosture from Collected_Data where (node_ref_id=9 OR node_ref_id=7 )  AND DATE(ping_time)=CURDATE() \
    order by ping_time desc")
    tjson='{ "feeds" : ['
    for row in selectdata:
        ptime=row[0]
        ref_id=row[1]
        node=db.executesql("select node_id from Node where id=%s",[ref_id])
        node_name=node[0][0]
        mos=row[2]
        tjson+= '{"ptime" : "'+ str(ptime) + '","node" : "' + str(node_name) + '","mosture" : "' + str(mos) +' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson

def wtemp():
    selectdata=db.executesql("select ping_time,node_ref_id,temperature from Collected_Data where (node_ref_id=9 OR node_ref_id=7 ) AND DATE(ping_time) >= CURDATE()-7 \
    order by ping_time desc")
    tjson='{ "feeds" : ['
    for row in selectdata:
        ptime=row[0]
        ref_id=row[1]
        node=db.executesql("select node_id from Node where id=%s",[ref_id])
        node_name=node[0][0]
        temp=row[2]
        tjson+= '{"ptime" : "'+ str(ptime) + '","node" : "' + str(node_name) + '","temp" : "' + str(temp) +' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson

def wambient():
    selectdata=db.executesql("select ping_time,node_ref_id,ambient from Collected_Data where (node_ref_id=9 OR node_ref_id=7 ) AND DATE(ping_time) >= CURDATE()-7 \
    order by ping_time desc")
    tjson='{ "feeds" : ['
    for row in selectdata:
        ptime=row[0]
        ref_id=row[1]
        node=db.executesql("select node_id from Node where id=%s",[ref_id])
        node_name=node[0][0]
        ambient_temp=row[2]
        tjson+= '{"ptime" : "'+ str(ptime) + '","node" : "' + str(node_name) + '","ambient_temp" : "' + str(ambient_temp) +' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson

def whumidity():
    selectdata=db.executesql("select ping_time,node_ref_id,humidity from Collected_Data where (node_ref_id=9 OR node_ref_id=7 ) AND DATE(ping_time) >= CURDATE()-7 \
    order by ping_time desc")
    tjson='{ "feeds" : ['
    for row in selectdata:
        ptime=row[0]
        ref_id=row[1]
        node=db.executesql("select node_id from Node where id=%s",[ref_id])
        node_name=node[0][0]
        hum=row[2]
        tjson+= '{"ptime" : "'+ str(ptime) + '","node" : "' + str(node_name) + '","humidity" : "' + str(hum) +' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson


def wmosture():
    selectdata=db.executesql("select ping_time,node_ref_id,mosture from Collected_Data where (node_ref_id=9 OR node_ref_id=7 ) AND DATE(ping_time) >= CURDATE()-7 \
    order by ping_time desc")
    tjson='{ "feeds" : ['
    for row in selectdata:
        ptime=row[0]
        ref_id=row[1]
        node=db.executesql("select node_id from Node where id=%s",[ref_id])
        node_name=node[0][0]
        mos=row[2]
        tjson+= '{"ptime" : "'+ str(ptime) + '","node" : "' + str(node_name) + '","mosture" : "' + str(mos) +' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson


def conditionanalysis():
    data= db.executesql("select temperature,humidity,mosture,ambient from Collected_Data where (node_ref_id=9 OR node_ref_id=7 ) order by ping_time desc limit 10");
    soil_temperature = 0
    humidity = 0
    moisture = 0
    ambient_temperature = 0
    for each in data:
        soil_temperature = soil_temperature + each[0]
        humidity = humidity + each[1]
        moisture = moisture + each[2]
        ambient_temperature = ambient_temperature + each[3]

    soil_temperature = soil_temperature/10
    humidity = humidity/10
    moisture = (moisture/10)
    ambient_temperature = ambient_temperature/10
    selectdata=db.executesql("select state,cstate from motor_state order by id desc limit 1")
    ostate=selectdata[0][0]
    cstate=selectdata[0][1]
    if str(ostate)=="on":
        setr="off"
        cs="Motor On"
    elif str(ostate)=="off":
        setr="on"
        cs="Motor OFF"
    else:
        setr="on"
        cs="Motor OFF"
    ajson='{ "feeds" : { "ambient" : ' + str(ambient_temperature) + ',"humidity" : ' + str(humidity) + ',"soil_temp" : ' + str(soil_temperature) + ',"moisture" : ' + str(moisture) + ', "rs" : "'+setr + '","cs" : "' +cs+'"  }}'
    return ajson



def post_suggestion():
    opentopic=SQLFORM(db.suggestion).process()
    pt=db.executesql("select Name,Description,id from suggestion")
    return locals()


def get_post():
    selectdata=db.executesql("select Name,Description from suggestion")
    tjson='{ "feeds" : ['
    for row in selectdata:
        name=row[0]
        suggestion=row[1]
        tjson+= '{"name" : "'+ str(name) + '","suggestion" : "' + str(suggestion)+ ' "  },'

    tjson+=']}'
    tjson=tjson.replace("},]","}]")
    return tjson



def post_state():
    if request.vars:
        state=request.vars.state
        cstate=request.vars.cstate
        db.executesql("insert into motor_state (state,cstate) values(%s,%s) ",(state,cstate))
        db.commit()
    return locals()

def motorcontrol():
    selectdata=db.executesql("select state,cstate from motor_state order by id desc limit 1")
    rstate=selectdata[0][0]
    cstate=selectdata[0][1]
    tjson= '{ "feeds" : {"requested_state" : "'+ str(rstate) + '","previous_state" : "' + str(cstate)+ ' "  }}'
    return tjson

def get_state():
    selectdata=db.executesql("select state,cstate from motor_state order by id desc limit 1")
    rstate=selectdata[0][0]
    cstate=selectdata[0][1]
    tjson= '{"requested_state" : "'+ str(rstate) + '","previous_state" : "' + str(cstate)+ ' "  }'
    return tjson

def chat():
    pid=request.args[0]
    issue=db.executesql("select Name,Description from suggestion where id=%s",[pid])
    pby=issue[0][0]
    topic=issue[0][1]
    chat=db.executesql("select Name,Comment from chat where topic_ref_id=%s",[pid])
    chat1=SQLFORM(db.chat).process()
    return locals()

def phdata():
    if request.vars:
        s1 = request.vars.s1
        s2 = request.vars.s2
        s3 = request.vars.s3
        s4 = request.vars.s4
        response = '{"sample_1" : '+str(s1)+', "sample_2" : '+str(s2)+',"sample_3" : '+str(s3)+',"sampe_4" : '+str(s4)+'}'
    else:
        response = "Please Ckeck Json format. Server didn't receive any data"
    return response

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
