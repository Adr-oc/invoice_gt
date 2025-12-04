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
import odoo.addons.l10n_gt_extra.a_letras as a_letras
import re


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    no_negociable = fields.Boolean(string="No Negociable", default=False)
    
    def num_a_letras(self, amount):
        return a_letras.num_a_letras(abs(amount),completo=True)
        
    
    def current_date_format(self, date):
        months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
        month = months[date.month - 1]
        messsage = month

        return messsage
    
    def cuentas_contables(self):
        move_id = self.move_id.id
        cuentas = self.env['account.move.line'].search([('move_id', '=', move_id)], order='id desc')
        
        # Initialize a dictionary to store the account information
        movimientos = {'cuentas': []}
        
        for rec in cuentas:
            # Append each account's details as a list to the 'cuentas' key
            movimientos['cuentas'].append([
                rec.account_id.code,
                rec.account_id.name,
                abs(rec.debit),
                abs(rec.credit)
            ])
        
        return movimientos

    
    def codigo(self):
        codigo = self.move_id.journal_id.default_account_id.name.split()[3]
        return codigo
    
    def tipo(self):
        tipo={'ND':'Nota de Debito','NC':'Nota de Credito','CQ':'Cheque','DE':'Deposito'}
        logging.warning(self.transaction_type)
        if self.transaction_type in tipo:
            texto = tipo[self.transaction_type]
        else:
            texto = ''
        return texto

    def get_facturas_conciliadas(self):
        """Obtiene las facturas conciliadas con esta línea de extracto bancario"""
        facturas = []
        if not self.move_id:
            return facturas

        # Buscar las líneas del asiento que tienen conciliaciones
        for line in self.move_id.line_ids:
            # Buscar en matched_debit_ids y matched_credit_ids
            for partial in line.matched_debit_ids:
                move = partial.debit_move_id.move_id
                if move.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
                    facturas.append({
                        'name': move.name,
                        'partner': move.partner_id.name,
                        'amount_total': move.amount_total,
                        'amount_residual': move.amount_residual,
                        'amount_paid': partial.amount,
                        'currency': move.currency_id.name,
                    })
            for partial in line.matched_credit_ids:
                move = partial.credit_move_id.move_id
                if move.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
                    facturas.append({
                        'name': move.name,
                        'partner': move.partner_id.name,
                        'amount_total': move.amount_total,
                        'amount_residual': move.amount_residual,
                        'amount_paid': partial.amount,
                        'currency': move.currency_id.name,
                    })

        # Eliminar duplicados basados en el nombre de la factura
        seen = set()
        unique_facturas = []
        for f in facturas:
            if f['name'] not in seen:
                seen.add(f['name'])
                unique_facturas.append(f)

        return unique_facturas
    
    
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    descripcion = fields.Char(string="Descripción")
    partner_app = fields.Many2one('res.partner')
    nombre_impreso = fields.Char()
    fecha_aplicacion = fields.Date()
    no_negociable = fields.Boolean(string='No negociable',default=False)
    boleta = fields.Char()

    
    
    def _create_payments(self):
        result = super(AccountPaymentRegister, self)._create_payments()
        result.descripcion = self.descripcion
        result.partner_app = self.partner_app
        result.nombre_impreso = self.nombre_impreso
        result.no_negociable = self.no_negociable
        result.fecha_aplicacion = self.fecha_aplicacion
        result.boleta = self.boleta
    
        return result

            
