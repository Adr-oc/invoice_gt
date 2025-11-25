# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
import time
import base64
import os
import requests
import logging
import xlsxwriter
import io
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, ValidationError

class ReporteReportProjectTaskEnvio(models.AbstractModel):
    _name = "report.invoice_gt.invoice_electronic_receipt"
    _description = "Reporte para impresion de nuevo formato"
    _inherit = ['mail.thread']


    @api.model
    def _get_report_values(self, docids, data=None):

        valor = docids
        country = self.env.user.company_id.country_id.name
        objects = self.env['account.move'].search([('id','in',valor)])
        objects_line = self.env['account.move.line'].search([('move_id','in',valor),('product_id','>', 0)])

        # accounts_str = ','.join([str(x) for x in docids])
        # parametros = (accounts_str)

        
        fecha_hoy = datetime.now()
        current_date = fecha_hoy.strftime("%d/%m-%Y %H:%M:%S")
        # time_fin = fecha_hoy.strftime("")
        docargs = {
            "doc_ids": docids,
            # "docs_type_jobs": docs_type_jobs,
            # "doc_model": models,
            "docs": objects,
            "docs_line":objects_line,
            "country": country,
            # "time": time,
            'current_company_id': self.env.company,
            'current_user_id': self.env.user.id,
            'current_user_office': str(self.env.user.partner_id.city),
            'current_date': current_date,
        }
        return docargs

class ReportInvoiceGtNoteDebit(models.AbstractModel):
    _name = "report.invoice_gt.invoice_note_debit"
    _description = "Reporte para impresion de nuevo formato"
    _inherit = ['mail.thread']


    @api.model
    def _get_report_values(self, docids, data=None):

        valor = docids
        country = self.env.user.company_id.country_id.name
        objects = self.env['account.move'].search([('id','in',valor)])
        objects_line = self.env['account.move.line'].search([('move_id','in',valor),('product_id','>', 0)])

        # accounts_str = ','.join([str(x) for x in docids])
        # parametros = (accounts_str)

        
        fecha_hoy = datetime.now()
        current_date = fecha_hoy.strftime("%d/%m-%Y %H:%M:%S")
        # time_fin = fecha_hoy.strftime("")
        docargs = {
            "doc_ids": docids,
            # "docs_type_jobs": docs_type_jobs,
            # "doc_model": models,
            "docs": objects,
            "docs_line":objects_line,
            "country": country,
            # "time": time,
            'current_company_id': self.env.company,
            'current_user_id': self.env.user.id,
            'current_user_office': str(self.env.user.partner_id.city),
            'current_date': current_date,
        }
        return docargs