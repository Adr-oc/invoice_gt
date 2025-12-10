# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
import json
import logging

class estadoCuenta(models.AbstractModel):
    _name = "report.invoice_gt.reporte_estado_cuenta"
    _description = "estado de cuenta, vencidas y no vencidas"

    @api.model
    def _get_report_values(self, docids, data=None):        
        docs = self.env['account.move'].search([('id', 'in', docids)])               
        now = datetime.today().strftime('%d-%m-%Y')
        
        invoices = []
        partner_ids = []
        partners = {}
        datas = {}
        part = []
        gran_total = 0
        curren = []

        # Obtener las cuentas de banco
        qtz_account = self.env['res.company'].search([('id', '=', self.env.company.id)]).cuenta
        usd_account = self.env['res.company'].search([('id', '=', self.env.company.id)]).cuenta_dolar

        # Se recorren todos los documentos activos actualmente
        for record in docs:
            monto = 0
            partner_ids.append(str(record.partner_id.id))
            unique_partners = list(set(partner_ids))
            curren.append(record.currency_id.name)
            currency = list(set(curren))

            due_date = record.invoice_date_due.strftime("%d-%m-%Y")
            start = datetime.strptime(now, '%d-%m-%Y')
            end = datetime.strptime(due_date, '%d-%m-%Y')
            resultado = start.date() - end.date()
            dias_atraso = resultado.days

            if dias_atraso < 0:
                dias_atraso = 0

            if record.amount_residual:
                monto = record.amount_residual
            else:
                monto = record.amount_total

            gran_total += monto

            partners[record.partner_id.id] = {
                "id" : record.partner_id.id,
                "name" : record.partner_id.name,
                "street2" : record.partner_id.street2,
                "city" : record.partner_id.city,
                "country" : record.partner_id.country_id.name,
                "email" : record.partner_id.email,
                "phone" :  record.partner_id.phone,
                "vat" : record.partner_id.vat
            }

            invoice = {
                "name" : record.name,
                "partner_id" : record.partner_id.id,
                "serie" : record.x_studio_serie,
                "date" : record.date.strftime("%d/%m/%Y"),
                "invoice_date_due" : record.invoice_date_due.strftime("%d/%m/%Y"),
                "dias_atraso" : dias_atraso,
                "currency" : record.currency_id.name,
                "journal_id" : record.journal_id.id,
                "journal_name" : record.journal_id.name,
                "amount_total" : monto,
                "amount_total_signed": record.amount_total,
                "amount_residual":record.amount_residual,
                "referencia_2": record.referencia_2  
            }

            invoices.append(invoice)

        invoices.sort(key=lambda r: (-r['dias_atraso'], datetime.strptime(r['date'], '%d/%m/%Y')))
        part.append(partners)
        
        for i in invoices:
            if i['currency'] == 'USD':
                if 'invoices_usd' in datas:
                    if i['journal_id'] in datas['invoices_usd']:
                        datas['invoices_usd'][i['journal_id']].append(i)
                    else:
                        datas['invoices_usd'][i['journal_id']] = [i]
                else:
                    datas['invoices_usd'] = {i['journal_id']: [i]}
            else:
                if 'invoices_gtq' in datas:
                    if i['journal_id'] in datas['invoices_gtq']:
                        datas['invoices_gtq'][i['journal_id']].append(i)
                    else:
                        datas['invoices_gtq'][i['journal_id']] = [i]
                else:
                    datas['invoices_gtq'] = {i['journal_id']: [i]}
        
        datas['qtz_account'] = {
            'bank_name': qtz_account.bank_id.name if qtz_account else '',
            'acc_holder_name': qtz_account.acc_holder_name if qtz_account else '',
            'acc_number': qtz_account.acc_number if qtz_account else ''
        }
        
        datas['usd_account'] = {
            'bank_name': usd_account.bank_id.name if usd_account else '',
            'acc_holder_name': usd_account.acc_holder_name if usd_account else '',
            'acc_number': usd_account.acc_number if usd_account else ''
        }

        return {
            'doc_ids': self.ids,
            'docs': docs,
            "datas" : json.dumps(datas, indent = 4),
            "unique_partners": unique_partners,
            "current_company_id": self.env.company,
            "current_day" : now
        }


