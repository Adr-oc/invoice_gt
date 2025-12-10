# -*- encoding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
import base64
import logging
import xlsxwriter
import io
import json

class PaymentReportxlsx(models.Model):
    _name = 'excel.reports'
    _description = "Reporte para impresion"

    file = fields.Binary('Archivo')
    file_name = fields.Char('Nombre de archivo')

    @api.model
    def report_payment(self, docids):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        sheet = workbook.add_worksheet("Pagos")
        sheet.set_column('A:A', 24)
        sheet.set_column('B:D', 30)
        sheet.set_column('E:H', 15)
        sheet.set_column('L:L', 30)
        bold = workbook.add_format({'bold': True})
        izquierda = workbook.add_format({'align': 'left'})
        izquierda_detalle = workbook.add_format({'align': 'left', 'text_wrap': True})

        x = 0
        encabezado = ["REFERENCIA", "FECHA", "BOLETA", "NOMBRE", "NIT", "TIPO", "MONTO", "FACTURA", "SERIE", "INTERNO", "DETALLE"]
        for i in encabezado:
            sheet.write(0, x, i, bold)
            x += 1

        y = 1

        for payment in docids:
            # trae la(s) factura(s) relacionadas al pago(s)
            stored_payments = payment.reconciled_invoice_ids
            boleta = payment.boleta
            dates = payment.date.strftime("%d-%m-%Y")

            for record in stored_payments:
                gtq = 0
                usd = 0
                
                
                rates = record.env["res.currency.rate"].search([("name", "=", record.invoice_date)])

                # Manejo de división por cero 0
                if rates and rates.rate:
                    rate = 1 / rates.rate
                else:
                    rate = 1  # Valor por defecto si no se encuentra la tasa o si es cero


                # valida si existe serie de documento
                serie = record.x_studio_serie or ""
                # valida si existe nmro de documento
                doc = record.x_studio_nmero_de_dte or record.name

                for line in record.line_ids:
                    if line.product_id:
                        total = f"{line.currency_id.name} {line.price_total * line.quantity}"
                        sheet.write(y, 0, payment.name, izquierda)
                        sheet.write(y, 1, dates, izquierda)
                        sheet.write(y, 2, boleta, izquierda)
                        sheet.write(y, 3, record.partner_id.name, izquierda)
                        sheet.write(y, 4, boleta, izquierda)
                        sheet.write(y, 5, '{:.2f}'.format(payment.amount), izquierda)
                        sheet.write(y, 6, doc, izquierda)
                        sheet.write(y, 7, serie, izquierda)
                        sheet.write(y, 8, record.name, izquierda)
                        sheet.write(y, 9, line.name, izquierda_detalle)
                        sheet.write(y, 10, total, izquierda_detalle)
                        y += 1

        # Obtener la fecha actual
        fecha_actual = date.today().strftime('%d-%m-%Y')
        name_report = f"Pagos {fecha_actual}.xlsx"

        workbook.close()
        excel_report = self.create({
            'file': base64.b64encode(output.getvalue()),
            'file_name': name_report
        })

        return {
            'type': 'ir.actions.act_url',
            'url': "/web/content/excel.reports/%s/file/%s?download=true" % (excel_report.id, name_report),
            'target': 'self',
        }


    
class AccountPaymentss(models.Model):
    _inherit = 'account.payment'

    def detailed_payment_report(self):
        excel_report = self.env['excel.reports'].create({})
        docids = self
        return excel_report.report_payment(docids)