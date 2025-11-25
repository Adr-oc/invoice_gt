# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging


class ResBank(models.Model):
    _inherit = "res.partner.bank"

    iban = fields.Char(string='IBAN')
    bic = fields.Char(string='BIC')
