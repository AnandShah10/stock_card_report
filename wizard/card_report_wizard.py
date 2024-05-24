from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CardReportWizard(models.TransientModel):
    _name = 'stock.report.card.wizard'
    _description = 'Stock Card Report Wizard'
    _inherit = 'report.report_xlsx.abstract'

    start_date = fields.Date(string='Start Date', required=True,help="The starting for the date range of stock's in date")
    end_date = fields.Date(string='End Date', required=True,help="The ending for the date range of stock's in date")

    negative_stock = fields.Boolean(default=False,help='Negative ')
    stock_valuation = fields.Boolean(default=False)
    zero_stock = fields.Boolean(default=False)

    company_id = fields.Many2one('res.company', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', required=True)
    location_ids = fields.Many2many('stock.location')
    product_ids = fields.Many2many('product.product')

    @api.constrains('start_date', 'end_date')
    def _check_date_range(self):
        for i in self:
            if i.start_date > i.end_date:
                raise ValidationError(_("The start date should be greater than end date!"))
            else:
                pass

    # @api.model
    # def default_get(self, fields):
    #     print("In the default get..........")
    #     defaults = super(CardReportWizard, self).default_get(fields)
    #     print("Done super...................", defaults)
    #     # locations = self.env['stock.location'].search([])
    #     # defaults['location_ids'] = [(6, 0, locations.ids)]
    #     # print("location Done...........................", defaults)
    #     domain = self._get_domain_product()
    #     if domain:
    #         stock = self.env['stock.quant'].search(domain)
    #     else:
    #         stock = self.env['stock.quant'].search([])
    #     product_ids = []
    #     for i in stock:
    #         product_ids.append(i.product_id.id)
    #     products = self.env['product.product'].browse(product_ids)
    #     if not products:
    #         products = self.env['product.product'].search([])
    #     defaults['product_ids'] = [(6, 0, products.ids)]
    #     print("products done .....................", defaults)
    #     return defaults

    # -------------------------note:-filter by product,many2many warehouse,

    # def _get_domain_product(self):
    #     for i in self:
    #         domain = []
    #         if i.start_date and i.end_date:
    #             domain = [('last_count_date', '<=', fields.Datetime.to_string(i.end_date)),
    #                       ('last_count_date', '>=', fields.Datetime.to_string(i.start_date))]
    #         if i.zero_stock:
    #             domain.append(('quantity', '!=', 0.00))
    #         domain.append(('company_id', '=', i.company_id.id))
    #         domain.append(('location_id', 'in', self.location_ids.ids))
    #         domain.append(('location_id.location_id', '=', self.warehouse_id.id))
    #         # domain.append(('product_id', 'in', self.product_ids.ids))
    #         print("Domain Done!!!!!!!!!1", domain)
    #         return domain

    def export_to_excel(self):
        print("Export here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        product_list = []
        for location in self.location_ids:
            domain = [('location_id', '=', location.id),
                      ('product_id', 'in', self.product_ids.ids),
                      ('in_date', '<=', fields.Datetime.to_string(self.end_date)),
                      ('in_date', '>=', fields.Datetime.to_string(self.start_date)),
                      ('company_id', '=', self.company_id.id)]
            if self.zero_stock:
                domain.append(('quantity', '!=', 0.00))
            stock = self.env['stock.quant'].search(domain)
            print(stock)
            for record in stock:
                # Collect quantities from stock moves
                # adjustment_qty = 0
                sale_qty = 0
                purchase_qty = 0
                internal_qty = 0

                stock_moves = self.env['stock.move'].search([
                    ('product_id', '=', record.product_id.id),
                    ('location_id', '=', record.location_id.id),
                    ('state', '=', 'done')
                ])

                for move in stock_moves:
                    if move.picking_type_id.code == 'outgoing':
                        sale_qty += move.product_uom_qty
                    elif move.picking_type_id.code == 'incoming':
                        purchase_qty += move.product_uom_qty
                    elif move.picking_type_id.code == 'internal':
                        internal_qty += move.product_uom_qty

                values = {
                    'product_name': record.product_id.name,
                    'location': location.name,
                    'on_hand_qty': record.quantity,
                    'internal_qty': internal_qty,
                    'adjustment_qty': record.inventory_diff_quantity,
                    'purchase_qty': purchase_qty,
                    'sale_qty': sale_qty,
                    'opening_qty': record.inventory_quantity,
                    'ref': record.product_id.default_code,
                    'sale_price': record.product_id.list_price,
                    'cost_price': record.product_id.standard_price, }
                if self.stock_valuation:
                    valuation = self.env['stock.valuation.layer'].search([("product_id", "=", record.product_id.id)])
                    total_valuation = 0
                    for value in valuation:
                        total_valuation += value.value
                    values['valuation'] = total_valuation
                product_list.append(values)

        vals = {
            'company': self.company_id.name,
            'warehouse': self.warehouse_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'product_list': product_list,
            'valuation_check': self.stock_valuation,
            'negative_check': self.negative_stock,

        }
        data = {
            'model': 'report.report_stock_card_xlsx',
            'form_data': self.read()[0],
            'stock': vals,
        }
        self.env.ref('stock_card_report.action_stock_card_report').name = 'StockCardReport-%s:%s' % (
            self.start_date, self.end_date)
        return self.env.ref('stock_card_report.action_stock_card_report').report_action(self, data=data)
