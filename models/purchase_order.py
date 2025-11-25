# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    Serie = fields.Char(string="Serie")
    File = fields.Char(string="File")
    Factura = fields.Char(string="No. Factura")
    Pago = fields.Many2one('account.payment.term', string="Términos de Pago")
    contrasena = fields.Char(string='Contraseña', readonly=True)
    buque_referencia_fel = fields.Char("Buque Referencia", tracking=True)
    referencia_bl = fields.Char("Referencia BL")

    
