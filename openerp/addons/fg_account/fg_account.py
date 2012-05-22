# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time


class sale_order(osv.osv):
    _inherit = 'fg_sale.order'
    _columns = {
        'rbill_line': fields.one2many('fg_account.rbill.line', 'rbill_id','收款明细', readonly=True),
    }

class fg_account_rbill_line(osv.osv):
    _name = 'fg_account.rbill.line'
    _description = '收款单明细'
    
    _columns = {
        'name':fields.related('rbill_id', 'name', type='char', string='单号', readonly=True),
        'rbill_id': fields.many2one('fg_account.rbill', '收款单', required=True, ondelete='cascade', select=True),
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True),
        'amount':fields.float('单据金额', digits=(10, 2)),
        'paid':fields.float('已核销金额', digits=(10, 2)),
        'unpaid':fields.float('未核销金额', digits=(10, 2)),
        'note':fields.text('附注'),
    }

class fg_account_rbill(osv.osv):
    _name = 'fg_account.rbill'
    _description = '收款单'
    
    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'date_issue': fields.date('收款日期', required=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True),
        'user_id': fields.many2one('res.users', '制单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('res.users', '审核人', select=True, readonly=True),
        'payment':fields.selection([('cash':'现金'), ('bank','银行转账')], '结算方式', states={'draft': [('readonly', False)]}),
        'bank_account':fields.many2one('res.bank', '银行', states={'draft': [('readonly', False)]}),
        'bill_line': fields.one2many('fg_account.rbill.line', 'rbill_id', '收款单', readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True), 
        'state': fields.selection([('draft', '未审核'), ('done', '已审核'), ('cancel','已取消')], '收款单状态', readonly=True, select=True),
    }
    
    _defaults = {
        'date_issue': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '订单不允许复制.')
    
    def create(self, cr, uid, vals, context=None):
        #
        
        id = super(fg_account_rbill, self).create(cr, uid, vals, context)
        return id


