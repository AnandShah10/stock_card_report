from odoo import models


class StockCardXlsx(models.AbstractModel):
    _name = 'report.stock_card_report.report_stock_card_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        print('data,,,,,,,,,,,,,,,,,,,,,,', lines, data)
        format1 = workbook.add_format({'font_size': 14, 'align': 'center',
                                       'valign': 'vcenter', 'bg_color': '#D3D3D3', 'bold': True})
        format2 = workbook.add_format({'font_size': 12, 'align': 'center', 'valign': 'vcenter'})
        format3 = workbook.add_format({'font_size': 12, 'align': 'center', 'font_color': 'red','bg_color':'#FF7F7F'})
        format4 = workbook.add_format({'font_size': 14, 'align': 'center',
                                       'valign': 'vcenter', 'bold': True, 'border': 2})
        sheet = workbook.add_worksheet(f'Stock Card Report-{data["stock"]["start_date"]}:{data["stock"]["end_date"]}')
        row = 0
        col = 0
        sheet.write(row, col, 'Company', format1)
        sheet.write(row, col + 3, 'Start Date', format1)
        sheet.write(row, col + 4, 'End Date', format1)
        sheet.write(row, col + 5, '', format1)
        sheet.write(row, col + 6, '', format1)
        sheet.write(row, col + 7, '', format1)
        sheet.write(row, col + 8, '', format1)
        sheet.write(row, col + 9, '', format1)
        sheet.write(row, col + 10, '', format1)
        sheet.write(row, col + 11, '', format1)

        sheet.merge_range('B1:C1', 'Warehouse', format1)
        row += 1
        sheet.write(row, col, data['stock']['company'], format2)
        sheet.merge_range('B2:C2', data['stock']['warehouse'], format2)
        sheet.write(row, col + 3, data['stock']['start_date'], format2)
        sheet.write(row, col + 4, data['stock']['end_date'], format2)
        row += 1
        if data['stock']['valuation_check']:
            headers = ['Product', 'Internal Ref.', 'Location', 'Cost Price', 'Sale Price', 'Opening', 'Purchase',
                       'Sales', 'Internal', 'Adjustment', 'On Hand', 'valuation']
        else:
            headers = ['Product', 'Internal Ref.', 'Location', 'Cost Price', 'Sale Price', 'Opening', 'Purchase',
                       'Sales', 'Internal', 'Adjustment', 'On Hand']

        for i, header in enumerate(headers):
            sheet.write(row, col + i, header, format1)

        total_valuation = 0
        total_opening = 0
        total_on_hand = 0
        total_purchase = 0
        total_sale = 0
        total_internal = 0
        total_adjustment = 0

        for rec in data['stock']['product_list']:
            row += 1
            if data['stock']['negative_check'] and (float(rec['on_hand_qty']) < 0.00):
                sheet.write(row, col, str(rec['product_name']).strip(), format3)
                sheet.write(row, col + 1, rec['ref'], format3)
                sheet.write(row, col + 2, rec['location'], format3)
                sheet.write(row, col + 4, rec['sale_price'], format3)
                sheet.write(row, col + 3, rec['cost_price'], format3)
                sheet.write(row, col + 5, rec['opening_qty'], format3)
                sheet.write(row, col + 6, rec['purchase_qty'], format3)
                sheet.write(row, col + 7, rec['sale_qty'], format3)
                sheet.write(row, col + 8, rec['internal_qty'], format3)
                sheet.write(row, col + 9, rec['adjustment_qty'], format3)
                sheet.write(row, col + 10, rec['on_hand_qty'], format3)
                if 'valuation' in rec:
                    sheet.write(row, col + 11, rec['valuation'], format3)
                    total_valuation += float(rec['valuation'])
            else:
                sheet.write(row, col, str(rec['product_name']).strip(), format2)
                sheet.write(row, col + 1, rec['ref'], format2)
                sheet.write(row, col + 2, rec['location'], format2)
                sheet.write(row, col + 4, rec['sale_price'], format2)
                sheet.write(row, col + 3, rec['cost_price'], format2)
                sheet.write(row, col + 5, rec['opening_qty'], format2)
                sheet.write(row, col + 6, rec['purchase_qty'], format2)
                sheet.write(row, col + 7, rec['sale_qty'], format2)
                sheet.write(row, col + 8, rec['internal_qty'], format2)
                sheet.write(row, col + 9, rec['adjustment_qty'], format2)
                sheet.write(row, col + 10, rec['on_hand_qty'], format2)
                if 'valuation' in rec:
                    sheet.write(row, col + 11, rec['valuation'], format2)
                    total_valuation += float(rec['valuation'])
            total_opening += float(rec['opening_qty'])
            total_on_hand += float(rec['on_hand_qty'])
            total_sale += float(rec['sale_qty'])
            total_internal += float(rec['internal_qty'])
            total_purchase += float(rec['purchase_qty'])
            total_adjustment += float(rec['adjustment_qty'])

            # Calculate column widths based on data
        max_lengths = [len(header) for header in headers]
        for rec in data['stock']['product_list']:
            max_lengths[0] = max(max_lengths[0], len(str(rec['product_name']).strip()))
            max_lengths[1] = max(max_lengths[1], len(rec['ref']))
            max_lengths[2] = max(max_lengths[2], len(rec['location']))
            max_lengths[3] = max(max_lengths[3], len(str(rec['cost_price'])))
            max_lengths[4] = max(max_lengths[4], len(str(rec['sale_price'])))
            max_lengths[5] = max(max_lengths[5], len(str(rec['opening_qty'])))
            max_lengths[6] = max(max_lengths[6], len(str(rec['purchase_qty'])))
            max_lengths[7] = max(max_lengths[7], len(str(rec['sale_qty'])))
            max_lengths[8] = max(max_lengths[8], len(str(rec['internal_qty'])))
            max_lengths[9] = max(max_lengths[9], len(str(rec['adjustment_qty'])))
            max_lengths[10] = max(max_lengths[10], len(str(rec['on_hand_qty'])))
            if 'valuation' in rec:
                max_lengths[11] = max(max_lengths[11], len(str(rec['valuation'])))

        # Set calculated column widths
        for col_num, length in enumerate(max_lengths):
            sheet.set_column(col_num, col_num, length + 5)  # Add some padding
        row += 1
        sheet.merge_range(f'A{row + 1}:E{row + 1}', "Total", format4)
        sheet.write(row, col + 5, total_opening, format4)
        sheet.write(row, col + 6, total_purchase, format4)
        sheet.write(row, col + 7, total_sale, format4)
        sheet.write(row, col + 8, total_internal, format4)
        sheet.write(row, col + 9, total_adjustment, format4)
        sheet.write(row, col + 10, total_on_hand, format4)

        if data['stock']['valuation_check']:
            sheet.write(row, col + 11, total_valuation, format4)
