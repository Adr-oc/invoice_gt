# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging


class AccountJournal(models.Model):
    _inherit = "account.journal"


    bank_instruccion = fields.Many2one('res.partner.bank', "Instrucción de banco")
    partner_id = fields.Many2one('res.partner', string="Partner", help="Partner for this journal")

    