# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging


class AccountMove(models.Model):
    _inherit = "account.move"

    currency_rate_id = fields.Many2one('res.currency.rate',string='Current Rate',  compute='_compute_current_rate')
    comercial_id = fields.Many2one(string="Comercial", related='partner_id.user_id', readonly=True, store=True)
    contrasena = fields.Char(string='Contraseña', readonly=True)
    current_user = fields.Many2one('res.users','Current User', compute="_get_current_user")
    shipment_logistaas = fields.Char(string="Shipment Logistaas")
    po_cliente = fields.Char(string="PO Cliente")

    def _get_current_user(self):
        self.current_user = self.env.uid

    def current_date_format(self, date):
        months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
        month = months[date.month - 1]
        message = f"Guatemala, {date.day} de {month} de {date.year}"

        return message
    
    def primera_mayuscula(self,letras):
        frase = letras[0].upper()+letras[1:]
        return frase
        
    def _compute_current_rate(self):
        for line in self:
            date = line.date
            currency_id = line.currency_id.id
            company_id = line.company_id.id

            rate = self.env['res.currency.rate'].search([('name', '=', date),('currency_id', '=', currency_id),('company_id', '=', company_id) ],  order="name desc ",limit=1)
            line.currency_rate_id = rate.id