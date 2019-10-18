# -*- coding: utf-8 -*-
# try something like
def index():
    title=''
    if request.vars.plot:
        state=request.vars.state
        if state=='temperature':
            title='Soil Temperature '
            r='[0,10,20,30,40,50]'
        elif state=='ambient':
            title='Ambient Temperature'
            r='[0,10,20,30,40,50]'
        elif state=='mosture':
            title='Soil Moisture'
            r='[0,100,500,700,1000,1200]'
        elif state=='humidity':
            t='Relative Humidity'
            r='[0,10,30,50,70,100]'
        limits=request.vars.plot
        plot="["
        has_data=db.executesql("select ping_time,"+str(state)+",node_ref_id from Collected_Data order by id desc limit "+str(limits)+"")
        if has_data:
            node1=30
            node2=30
            for line in has_data:
                time=line[0]
                i=line[1]
                split_time=str(time).replace("-",",")
                split_time=split_time.replace(":",",")
                split_time=split_time.replace(" ",",")
                if line[2]==7:
                    node1=i
                    plot+="[new Date("+str(split_time)+"),"+str(node1)+","+str(node2)+"],"
                elif line[2]==9:
                    node2=i
                    plot+="[new Date("+str(split_time)+"),"+str(node1)+","+str(node2)+"],"
            plot+="]"
            plot=plot.replace("],]","]]")
    return locals()

def input_data():
    form = SQLFORM(
       db.Collected_Data,
       submit_button = T('Add')
    ).process()
    return locals()

def single_node():
    title=''
    plot = "["
    r='[0,10,20,30,40,50]'
    if request.vars.node:
        node_name = request.vars.node
        title = "Data visualization for Node"+str(node_name)
        if node_name =='700':
            id = 7;
        elif node_name =='800':
            id = 9;
        has_data=db.executesql("select ping_time,temperature,humidity,mosture,ambient from Collected_Data where node_ref_id="+str(id)+" order \
                                by id desc limit 10")
        for line in has_data:
            time = line[0]
            temp = line[1]
            hum = line[2]
            mos = line[3]
            amb = line[4]
            split_time=str(time).replace("-",",")
            split_time=split_time.replace(":",",")
            split_time=split_time.replace(" ",",")
            plot+="[new Date("+str(split_time)+"),"+str(temp)+","+str(hum)+","+str(mos)+","+str(amb)+"],"
        plot+="]"

    elif request.vars.node_id:
        node_name  = request.vars.node_id
        title = "Data visualization for Node"+str(node_name)
        if node_name =='700':
            id = 7;
        elif node_name =='800':
            id = 9;
        start=request.vars.start
        end = request.vars.end
        query="select ping_time,temperature,humidity,mosture,ambient from Collected_Data where node_ref_id="+str(id)+" and ping_time between\
                                '"+str(start)+"' and '"+str(end)+"'"
        has_data=db.executesql(query)
        if has_data:
            for line in has_data:
                time = line[0]
                temp = line[1]
                hum = line[2]
                mos = line[3]
                amb = line[4]
                split_time=str(time).replace("-",",")
                split_time=split_time.replace(":",",")
                split_time=split_time.replace(" ",",")
                plot+="[new Date("+str(split_time)+"),"+str(temp)+","+str(hum)+","+str(mos)+","+str(amb)+"],"
            plot+="]"
    plot = plot.replace("],]","]]")
    return locals()

def form_data():
    if request.post_vars:
        start=request.post_vars.start
        end = request.post_vars.end
        node_id = request.post_vars.node_id
        query="select ping_time,temperature,humidity,mosture,ambient from Collected_Data where node_ref_id="+str(node_id)+" and ping_time between\
                                '"+str(start)+"' and '"+str(end)+"'"
        has_data=db.executesql(query)
        plot = ''
        if has_data:
            for line in has_data:
                time = line[0]
                temp = line[1]
                hum = line[2]
                mos = line[3]
                amb = line[4]
                split_time=str(time).replace("-",",")
                split_time=split_time.replace(":",",")
                split_time=split_time.replace(" ",",")
                plot+="[new Date("+str(split_time)+"),"+str(temp)+","+str(hum)+","+str(mos)+","+str(amb)+"],"
            plot+="]"
            plot = plot.replace("],]","]]")
        else:
            plot="No SQL data found"
    else:
        plot="No data found"
    return plot
