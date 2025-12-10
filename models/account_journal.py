# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging


class AccountJournal(models.Model):
    _inherit = "account.journal"


    

    bank_instruccion = fields.Many2one('res.partner.bank', "Instrucción de banco")
    # NOTA: partner_id ya existe como Many2one en account.journal base
    # No se debe redefinir como Char. Campo eliminado para evitar conflictos.