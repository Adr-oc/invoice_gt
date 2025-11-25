# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round

from datetime import datetime
import base64
from lxml import etree
import requests
import re
#from import XMLSigner

import logging
import odoo.addons.l10n_gt_extra.a_letras as a_letras

class AccountPaymentR(models.Model):
    _inherit = "account.payment"

    boleta = fields.Char(string="Boleta")
    banco = fields.Char(string="Banco")

    def num_a_letras(self, amount):
        return a_letras.num_a_letras(amount,completo=True)
    