# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging


class AccountJournal(models.Model):
    _inherit = "account.journal"


    

    bank_instruccion = fields.Many2one('res.partner.bank', "Instrucción de banco" )
    partner_id = fields.Char(compute="compute_bank_instruccion")


    # @api.depends('bank_instruccion')
    def compute_bank_instruccion(self):
        for line in self:
            line.partner_id = line.company_id.partner_id.id

    