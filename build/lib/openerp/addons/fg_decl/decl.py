# -*- encoding: utf-8 -*-

from osv import osv, fields
import time
from datetime import datetime
from time import strptime, strftime
import datetime




class fg_decl_company(osv.osv):

    _name = 'fg_decl.company'
    _description = "经销商"
    _sql_constraints=[('name_values','unique(name)','法定代表人姓名不能重复!')]

    _columns = {
        'company_name': fields.char('经销商公司名',size=64,select=True),
        'name':fields.char('法定代表人姓名',size=64,select=True,required=True),
        'decl_tel':fields.char('法定代表人手机号',size=64),
        'decl_license':fields.char('营业执照号',size=64),
        'decl':fields.char('法定代表人身份证',size=64),
        'address':fields.char('公司地址',size=128),
        'tel':fields.char('责任人电话',size=64),
        'qq':fields.char('QQ',size=128),
        'e_mail':fields.char('Email',size=64),
        'fax': fields.char('Fax', size=64),
        'decl_date': fields.date('创建日期', readonly=True),
        'store_name':fields.char('店名',size=64),
        'store_address':fields.char('实体店地址',size=128),
        'store': fields.selection([('True','是'),('False','否')],'是否有实体店铺'),
        'store_year':fields.integer('经营年限'),
        'on_charge':fields.char('该店负责人',size=64),
        'note':fields.text('备注'),
        'service':fields.integer('实体店人数'),
        'saleroom':fields.float('预计年销售额',digits=[16,2]),
        'stores':fields.one2many('fg_decl.store', 'decl_id', '网店'),
        'web': fields.selection([('True','是'),('False','否')],'是否有独立运行的网站'),
        "web_address":fields.char("网络链接",size=64)
    }

    _defaults = {
        'decl_date': fields.date.context_today,
        'store':'True',
        "web":"False",
        
    }
  
    

class fg_decl_decl(osv.osv):
    _name = 'fg_decl.store'
    _description = "网店"
    
    _sql_constraints=[('name_unique','unique(name)','网店名称不能重复!')]
    
    def cal_date(self,cr,uid,ids, name,args=None,context={}):
            res={}
            for date in self.browse(cr, uid, ids,context=context):
                if date.authdate and date.authenddate:
                    a=strptime(date.authdate, '%Y-%m-%d')
                    b=strptime(date.authenddate, '%Y-%m-%d')
                    m=datetime.datetime(*a[:3])
                    n=datetime.datetime(*b[:3])
                    f=(n-m).days/30
                    if f<12:
                        f="%s"%f
                        f=f+"个月"
                    else :
                        if f%12:
                            mon="%s"%(f%12)
                            f="%s"%(f/12)
                            f=f+"年"+mon+"月"
                        else :
                            f="%s"%(f/12)
                            f=f+"年"
                    res[date.id]={"validity":f}
                else:
                    res[date.id]={"validity":0}
            return res
    def on_change_date(self, cr, uid, ids,authdate,authenddate, context=None):
        if authdate and authenddate:
            a=strptime(authdate, '%Y-%m-%d')
            b=strptime(authenddate, '%Y-%m-%d')
            m=datetime.datetime(*a[:3])
            n=datetime.datetime(*b[:3])
            f=n-m
            f=f.days/30
            if f<12:
                f="%s"%f
                f=f+"个月"
            else :
                if f%12:
                    mon="%s"%(f%12)
                    f="%s"%(f/12)
                    f=f+"年"+mon+"月"
                else :
                    f="%s"%(f/12)
                    f=f+"年"
        else:
            f=0
        return {'value': {'validity': f}}
    
    
    _columns = {
        'decl_id': fields.many2one('fg_decl.company','经销商法人',select=True),
        'name': fields.char("网店名称",size=64,select=True),
        'online_store': fields.boolean('是否有网络店铺'),
        'year':fields.char('经营年限',size=64),
        'online_store_address':fields.char('网店网址',size=128),
        'online_store_level':fields.char('店铺等级',size=32),
        'store_fund':fields.char('店铺储备资金',size=32),
        #'warehouse':fields.boolean('是否有专属仓库'),
        'warehouse_size':fields.char('仓储面积',size=64),
        'warehouse_money':fields.char('库存量(金额)',size=32),
        'customer_service':fields.char('网店客服人数',size=32),
        'art_design':fields.char('美术设计人数',size=64),
        'warehouse_person':fields.char('库房发货人数',size=64),
        'online_store_operation':fields.char('网店运营人数',size=64),
        'total_staff':fields.char('公司员工总数',size=64),
        'chief_degree':fields.char('负责人学历',size=32),
        'online_store_belong':fields.char('网店所属网站',size=64),
        'online_store_pro':fields.selection([('Personal', '个人'), ('Company', '商城')],'店铺性质'),       
        'chief':fields.char('责任人',size=64),
        'brand':fields.char('预计经营品牌',size=128,help='包括非富光的请详细写清楚'),
        'saleroom':fields.char('预计年销售额',size=32),
        'note':fields.text('附注'),
        "illegal":fields.one2many("fg_decl.illegal","name","违规记录"),
        "authnum":fields.char("授权书编号",size=64,select=True),
        "authdate":fields.date("授权日期"),
        "authenddate":fields.date("截止日期"),
        "validity":fields.function(cal_date,type="char",string="有效期",store = {
                'fg_decl.store': (cal_date,['authdate',"authenddate"], 10),
            },
            multi='cal_date'),
        "supplier":fields.char("供货商/备注",size=32),
        "contact":fields.char("联系方式",size=32),
        
        
    }
    _defaults = {
        'online_store': lambda *a: 'True',
        'online_store_pro': lambda *a: 'Personal',
    }
    
  


class fg_decl_illegal(osv.osv):
    _name = "fg_decl.illegal"
    _description = "违规记录"


    
    _columns= {
        'chief':fields.char("该店负责人",size=64),
        "name":fields.many2one("fg_decl.store","违规网店",select=True,change_default=True),
        "illegal_date":fields.date("记录时间"),
        "record_man":fields.char("记录人",size=64),
        "handle_man":fields.char("处理人",size=64),
        "illegal_info":fields.char("违规项目",help="未批准折扣，隐形折扣",size=64),
        "URL":fields.text("页面URL地址",size=300),
        "pic":fields.binary("违规页面截图"),
        "product":fields.one2many("product.info","name_id","违规产品")        
        
        
    }

    _defaults={
        'illegal_date':fields.date.context_today,

    }
    
        
    def onchange_name(self, cr, uid, ids, name):


        if not name:
            return {'value': {'chief':0.0}}
        chief_id = self.pool.get('fg_decl.store').browse(cr, uid, name).chief
        return {'value': {'chief': chief_id}}
        
        
class product_info(osv.osv):
    _name = "product.info"
    _description = '违规产品信息'
    
    
    _columns = {
        "name_id":fields.integer("num"),
        "name":fields.char("货号",size=64,required=True),
        "barcode":fields.char("条码",size=64),
        "size":fields.char("容量",size=64),
        "category_name":fields.char("FGA富光产品类型",size=64),
        "note":fields.char("备注",size=64),
    }
    
    





# end of this file.
