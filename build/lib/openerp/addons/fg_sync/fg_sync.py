# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time
import xmlrpclib, pooler
from time import strptime, strftime
import datetime

server = {'server_url':'localhost','server_port':8000, 'login':'admin', 'password':'123',"server_db":"DEMO"},

import xmlrpclib,pooler


class RPCProxyOne(object):
    def __init__(self, server, ressource):
        self.server = server
        local_url = 'http://%s:%d/xmlrpc/common'%(server.server_url,server.server_port)
        rpc = xmlrpclib.ServerProxy(local_url)
        self.uid = rpc.login(server.server_db, server.login, server.password)
        local_url = 'http://%s:%d/xmlrpc/object'%(server.server_url,server.server_port)
        self.rpc = xmlrpclib.ServerProxy(local_url)
        self.ressource = ressource
    def __getattr__(self, name):
        return lambda cr, uid, *args, **kwargs: self.rpc.execute(self.server.server_db, self.uid, self.server.password, self.ressource, name, *args)

class RPCProxy(object):
    def __init__(self, server):
        self.server = server
    def get(self, ressource):
        return RPCProxyOne(self.server,ressource)
        

class Config(object):
    def __init__(self, su, sp, sd, lo, ps):
        self.server_url = su
        self.server_port = sp
        self.server_db = sd
        self.login = lo
        self.password = ps
        
        
        
        
class fg_sync_scheduler(osv.osv):
    _name = "fg_sync.scheduler"
    _description = "order importing."
    
    _columns = {

    }

    def do_push(self, cr, uid, ids, model):
        pass

    def do_pull(self, cr, uid, ids, model):
        pass
    
    def do_run_scheduler(self, cr, uid, ids=None, context=None):
        """Scheduler for event reminder
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of whatever’s IDs.
        @param context: A standard dictionary for contextual values
        """
        #通过xmlrpc读取数据库中表
        pool1= RPCProxy(Config('localhost', 8000, 'fga', 'admin','123'))
        pool2= RPCProxy(Config('localhost', 8069, 'DEMO', 'admin','123'))
        
        
#表
        box=["lunch.category","lunch.product","lunch.cashbox","lunch.cashmove","lunch.order","report.lunch.amount"]
        for classes in box:
            user_obj1= pool1.get(classes)
            user_obj2=pool2.get(classes)
            user2_ids = user_obj2.search(cr, uid,[], offset=0, limit=None, order=None,context=None, count=False)
            user1_ids = user_obj1.search(cr, uid,[], offset=0, limit=None, order=None,context=None, count=False)
            #更新辅数据库增删操作  放在主数据库中，因为cr.execute只能在该数据库中执行，排序，找出最大日期
            create_date2=user_obj2.perm_read(cr,uid,user2_ids)
            create_date1=user_obj1.perm_read(cr,uid,user1_ids)
            maxdate1={}
            maxdate2={}
            user1_ids.sort()
            user2_ids.sort()
            for a in create_date2:
                if a["create_date"]>maxdate2:
                    maxdate2=a["create_date"]
            for b in create_date1:
                if b["create_date"]>maxdate1:
                    maxdate1=b["create_date"]
            #遍历表1（辅数据库）
            for id1 in user1_ids:
                        if id1 not in user2_ids:
                            create_date1=user_obj1.perm_read(cr,uid,[id1])
                            print create_date1[0]["create_date"]
                            if create_date1[0]["create_date"]>maxdate2:
                                        val = user_obj1.read(cr,uid,id1,[])
                                        for a in val:
                                            if type(val[a])==list:
                                                val[a]=val[a][0]
                                        b=user_obj2.create(cr,uid,val,context=context)
                                        cr.commit()
                                        classes=classes.replace(".","_")
                                        print classes
                                        cr.execute('update classes SET id=%s,create_date=%s WHERE id=%s',(id1,create_date1[0]["create_date"],b))
                                        cr.commit()
                            else :
                                        user_obj1.unlink(cr,uid,id1,context=context)
            #将最大日期改成一致（创建时改不掉createdate,等第二次调用时同步最大ID的时间）
            #cr.execute('update lunch_category set create_date=%s where id=%s',(maxdate1,user1_ids[-1]))
        
        
        
    
        
        
        return True
