# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging


class companybank(models.Model):
    _inherit = "res.company"

    cuenta = fields.Many2one('res.partner.bank', string="Cuenta")
    cuenta_dolar = fields.Many2one('res.partner.bank', string="Cuenta Dolares")