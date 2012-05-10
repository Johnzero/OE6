# -*- encoding: utf-8 -*-
import pooler, time
from osv import fields, osv
from tools import DEFAULT_SERVER_DATETIME_FORMAT,get_initial

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'ratio': fields.float('比率', digit=2)
    }

class sale_order(osv.osv):
    _name = "fg_sale.order"
    _description = "富光业务部销售订单"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'amount_total':0.0 }
            amount = 0
            for line in order.order_line:
                #todo: got to decide which one to add. subtotal_amount or, discount_amount
                amount = amount + line.subtotal_amount
            res[order.id]['amount_total'] = amount
        return res
    
    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'sub_name': fields.char('副单号', size=64, select=True, readonly=True),
        'date_order': fields.date('日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True),
        'user_id': fields.many2one('res.users', '制单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('res.users', '审核人', select=True, readonly=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True),        
        'partner_shipping_id': fields.many2one('res.partner.address', '送货地址', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'amount_total': fields.function(_amount_all, string='金额', store=False, multi='sums'),
        #'amount_total': fields.float('金额', digits=(16,4)),
        'order_line': fields.one2many('fg_sale.order.line', 'order_id', '订单明细', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', '未审核'), ('done', '已审核'), ('cancel','已取消')], '订单状态', readonly=True, select=True),
        'minus': fields.boolean('红字', readonly=True, states={'draft': [('readonly', False)]}),
        'note': fields.text('附注'),
        'sales_ids': fields.related('partner_id','sales_ids', type='many2many', relation='res.users', string='负责人',store=False),
        'sync':fields.boolean('备用'),
    }
        
    _defaults = {
        'date_order': fields.date.context_today,
        'state': 'draft',
        'minus': False, 
        'sync':False,
        'user_id': lambda obj, cr, uid, context: uid,
        'partner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['default'])['default'],
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '订单不允许复制.')
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_sale.order')
            
        if not vals.has_key('sub_name'):
            partner_obj = self.pool.get('res.partner')
            partner_name = partner_obj.name_get(cr, uid, [vals['partner_id']])[0][1]
            initial = get_initial(partner_name)
            
            cr.execute("select count(*) from fg_sale_order where partner_id = %s;" % vals['partner_id'] )
            res = cr.fetchone()
            count = res and res[0] or 0
            
            vals['sub_name'] = "FGSO-%s-%s" % ( initial, count+1 )
            
        id = super(sale_order, self).create(cr, uid, vals, context)
        
        return id
    
    
    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value': {'partner_shipping_id': False}}
        partner_obj = self.pool.get('res.partner')
        addr = partner_obj.address_get(cr, uid, [part], ['default'])['default']
        
        
        return {'value': {'partner_shipping_id':addr}}
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    def button_review(self, cr, uid, ids, context=None):
        #1.see if this is discount...
        #2.deal with minus
        
        product_obj = self.pool.get('product.product')
        order_line_obj = self.pool.get('fg_sale.order.line')
        orders = self.browse(cr, uid, ids)
        order_list = []
        for order in orders:
            for line in order.order_line:
                if order.minus:
                    update = {
                        'product_uom_qty':(0-line.product_uom_qty),
                        'aux_qty':(0-line.aux_qty),
                        'subtotal_amount':(0-line.subtotal_amount),
                    }
                    order_line_obj.write(cr, uid, [line.id], update)
                product = product_obj.browse(cr, uid, line.product_id, context=context)
                if product.lst_price > line.unit_price:
                    #notify 
                    order_list.append(order.name)
                    break
        if order_list:
            body = """
            您好, ! 
            这是一封提醒邮件. 
            单据 %s 存在折扣的明细, 请及时查看.
            %s
            """
            mail_message = self.pool.get('mail.message')
            mail_message.schedule_with_attach(cr, uid,
                '富光ERP系统 <fuguang_fg@163.com>',
                ['133120528@qq.com'],
                '[折扣订单提醒]编号:%s' % ','.join(order_list),
                body % (''.join(order_list),  time.strftime('%Y-%m-%d %H:%m')),
                reply_to='fuguang_fg@163.com',
                context=context
            )
        
        self.write(cr, uid, ids, { 
            'state': 'done', 
            'confirmer_id': uid, 
            'date_confirm': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            }
        )
        return True
    
    def button_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'cancel', 
            'confirmer_id': uid, 
            'date_confirmed': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            }
        )
        return True
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', '订单名称不能重复!'),
    ]
    _order = 'date_order desc'
    
class sale_order_line(osv.osv):
    _name = "fg_sale.order.line"
    _description = "富光业务部销售订单明细"
    
    
    _columns = {
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', '产品', domain=[('sale_ok', '=', True)], change_default=True),
        'product_uom': fields.many2one('product.uom', ' 单位', required=True),
        'product_uom_qty': fields.float('数量', required=True),
        'aux_qty': fields.float('只数', required=True),
        'unit_price': fields.float('单价', required=True, digits=(16,4)),
        'subtotal_amount': fields.float('小计', digits=(16,4)),
        'note': fields.char('附注', size=100),
        'sync':fields.boolean('备用'),
    }
    
    _defaults={
        'sync':False,
    }
    
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {'domain': {}, 'value':{'product_uom':'', 'product_uom_qty':0, 
                'aux_qty':0, 'unit_price':0, 'subtotal_amount':0}}
        result = {}
        product_obj = self.pool.get('product.product')
        
        product = product_obj.browse(cr, uid, product_id, context=context)
        result['product_uom'] = product.uom_id.id
        result['unit_price'] = product.lst_price
        return {'value': result}
    
    
    def product_uom_id_change(self, cr, uid, ids, product_id, uom_id, context=None):
        return {'domain': {}, 'value':{'product_uom_qty':0, 
            'aux_qty':0, 'subtotal_amount':0}}
    
    
    def product_uom_qty_change(self, cr, uid, ids, product_id, product_uom, qty, unit_price_new, context=None):
        if product_id and product_uom and qty and unit_price_new:
            product_obj = self.pool.get('product.product')
            #product_uom_obj = self.pool.get('product.uom')
            product = product_obj.browse(cr, uid, product_id, context=context)
            if product:
                price = unit_price_new * product.uom_id.factor * qty
                
                return {'value': {'subtotal_amount':price, 'aux_qty':product.uom_id.factor * qty}}
        return {'value':{}}


    _order = 'sequence, id asc'
