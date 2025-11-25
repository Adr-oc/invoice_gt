# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging

class estadoCuenta(models.AbstractModel):
    _name = "report.invoice_gt.reporte_estado_cuenta_detallado"
    _description = "estado de cuenta, vencidas y no vencidas"

    @api.model
    def _get_report_values(self, docids, data=None):

        doc_ids = ','.join([str(x) for x in docids])
        
        docs = self.env['account.move'].search([('id', 'in', docids)])               
            
        now = datetime.today().strftime('%d-%m-%Y')

        query = """ select am.x_studio_nmero_de_dte as name, am.name as doc, am.x_studio_serie , am.date, am.ref, am.invoice_date_due,
                        am.amount_total, am.amount_residual, am.id as id_factura, am.journal_id as diario,
                        rc.name as moneda,
                        rp.name as cliente, rp.street2, rp.city, rc2.name as country, rp.email, rp.phone, rp.vat
                        from account_move am
                        inner join res_currency rc on am.currency_id = rc.id
                        inner join res_partner rp on am.partner_id = rp.id
                        left join res_country rc2  on rp.country_id  = rc2.id
                    where am.id in (%s)
                    and am.payment_state in ('not_paid', 'partial') """

        line_query = """SELECT aml.product_id, aml.name as product_name, aml.quantity, aml.price_unit, aml.price_subtotal
                        FROM account_move_line aml
                        WHERE aml.move_id = %s"""

        invoices_by_currency_and_journal = {}
        
        self.env.cr.execute(query % (doc_ids))
        resultado = self.env.cr.dictfetchall()

        for line in resultado:
            id_factura = line['id_factura']
            monto = line['amount_residual'] if line['amount_residual'] else line['amount_total']
            moneda = line['moneda']
            diario = line['diario']

            # Inicializa la estructura para agrupar por moneda y diario si no existe
            if moneda not in invoices_by_currency_and_journal:
                invoices_by_currency_and_journal[moneda] = {}
            if diario not in invoices_by_currency_and_journal[moneda]:
                invoices_by_currency_and_journal[moneda][diario] = {
                    'invoices': [],
                    'total_adeudado': 0,
                    'total_vencido': 0
                }

            due_date = line['invoice_date_due'].strftime("%d-%m-%Y")
            start = datetime.strptime(now, '%d-%m-%Y')
            end = datetime.strptime(due_date, '%d-%m-%Y')
            dias_atraso = max((start.date() - end.date()).days, 0)

            # Obtener las líneas de productos de la factura
            self.env.cr.execute(line_query % (id_factura))
            lineas = self.env.cr.dictfetchall()

            
            invoice_lines = [{
                "product_name": l['product_name'],
                "quantity": l['quantity'],
                "price_unit": '{:,.2f}'.format(l['price_unit']),
                "price_subtotal": '{:,.2f}'.format(l['price_subtotal']),
            } for l in lineas if l.get('product_id')]

            invoice = {
                "id_factura": id_factura,
                "number": line['name'] if line['name'] else line['doc'],
                "serie": line['x_studio_serie'],
                "date": line['date'].strftime("%d/%m/%Y"),
                "invoice_date_due": line['invoice_date_due'].strftime("%d/%m/%Y"),
                "dias_atraso": dias_atraso,
                "communication": line['ref'],
                "currency": moneda,
                "amount_total": '{:,.2f}'.format(monto),
                "lines": invoice_lines  # Detalle de las líneas de la factura
            }

            invoices_by_currency_and_journal[moneda][diario]['invoices'].append(invoice)
            invoices_by_currency_and_journal[moneda][diario]['total_adeudado'] += monto

            if dias_atraso > 0:
                invoices_by_currency_and_journal[moneda][diario]['total_vencido'] += monto
        logging.warning(invoices_by_currency_and_journal)
        # exit()
        return {
            'doc_ids': self.ids,
            'docs': docs,
            'invoices_by_currency_and_journal': invoices_by_currency_and_journal,
            'current_company_id': self.env.company,
            'current_day': now
        }
