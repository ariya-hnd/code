# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SalesOrderLine(models.Model):
    _inherit = "sale.order.line"

    brand = fields.Many2one('product.brand.list', related='product_id.brand', store=True, string="Brand")
    category = fields.Many2one('product.category.list',related='product_id.category', store=True, string="Category")
    sub_category = fields.Many2one('product.sub.category.list',related='product_id.sub_category', store=True, string="Sub-Category")


class SalesReport(models.Model):
    _inherit = "sale.report"

    brand = fields.Many2one('product.brand.list', string="Brand")
    category = fields.Many2one('product.category.list', string="Category")
    sub_category = fields.Many2one('product.sub.category.list', string="Sub-Category")

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
             SELECT min(l.id) as id,
                l.product_id as product_id,
                l.brand as brand,
                l.category as category,
                l.sub_category as sub_category,
                t.uom_id as product_uom,
                sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
                sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
                sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
                sum(l.price_total / COALESCE(cr.rate, 1.0)) as price_total,
                sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as price_subtotal,
                count(*) as nbr,
                s.name as name,
                s.date_order as date,
                s.state as state,
                s.partner_id as partner_id,
                s.user_id as user_id,
                s.company_id as company_id,
                extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                t.categ_id as categ_id,
                s.pricelist_id as pricelist_id,
                s.project_id as analytic_account_id,
                s.team_id as team_id,
                p.product_tmpl_id,
                partner.country_id as country_id,
                partner.commercial_partner_id as commercial_partner_id,
                sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight,
                sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
            sale_order_line l
                  join sale_order s on (l.order_id=s.id)
                  join res_partner partner on s.partner_id = partner.id
                    left join product_product p on (l.product_id=p.id)
                        left join product_template t on (p.product_tmpl_id=t.id)
                left join product_uom u on (u.id=l.product_uom)
                left join product_uom u2 on (u2.id=t.uom_id)
                left join product_pricelist pp on (s.pricelist_id = pp.id)
                left join currency_rate cr on (cr.currency_id = pp.currency_id and
                    cr.company_id = s.company_id and
                    cr.date_start <= coalesce(s.date_order, now()) and
                    (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                l.brand,
                l.category,
                l.sub_category,
                l.order_id,
                t.uom_id,
                t.categ_id,
                s.name,
                s.date_order,
                s.partner_id,
                s.user_id,
                s.state,
                s.company_id,
                s.pricelist_id,
                s.project_id,
                s.team_id,
                p.product_tmpl_id,
                partner.country_id,
                partner.commercial_partner_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
