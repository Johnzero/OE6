#!/usr/bin/env python

import xmlrpclib,pooler

server = {'server_url':'localhost','server_port':8069, 'login':'admin', 'password':'admin',"server_db":"DEMO"},
login="admin"
url = 'http://localhost:8069/xmlrpc/common'
sock = xmlrpclib.ServerProxy(url)

class RPCProxyOne(object):
    def __init__(self, server, ressource):
        self.server = server
        local_url = 'http://localhost:8069/xmlrpc/common'
        rpc = xmlrpclib.ServerProxy(local_url)
        self.uid = rpc.login("DEMO","admin","admin")
        print "Logged in as %s (uid:%d)" % (login,self.uid)
        self.rpc = xmlrpclib.ServerProxy(local_url)
        self.ressource = ressource
    def __getattr__(self, name):                          
        return lambda cr, uid, *args, **kwargs: self.rpc.execute("DEMO", self.uid,"admin", self.ressource, name, *args)

class RPCProxy(object):
    def __init__(self, server):
        self.server = server
    def get(self, ressource):
        return RPCProxyOne(self.server, ressource)
        
        
        
pool1 = RPCProxy(server)
partner_obj = pool1.get('idea.idea')
id = partner_obj.create(cr,uid,{"user_id":'1',"name":"vip"})
