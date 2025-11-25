# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging


class ResPatner(models.Model):
    _inherit = "res.partner"

    nit_hijo = fields.Char()