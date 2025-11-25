# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class priceList(models.Model):
    _inherit = 'product.pricelist'
    _description = "Mejoras para tarifas y cobros"

    notas_importantes = fields.Html(
        string="Notas",
        default="""
            <ul>
                <li>Se hace un recargo por línea adicional de <strong>Q200.00</strong> por múltiples de 100 líneas a partir de la línea 21.</li>
                <li>Se hace un recargo de <strong>Q350.00</strong> cuando el monto desembolsado por pagos a terceros supera los <strong>Q3500.00</strong>.</li>
            </ul>
            <p>De ser aceptada la presente propueta de servicios, requeriremos que los honorarios sean cancelados de la siguiente forma: </p>
            <ul>
                <li><strong>15 días crédito</strong> a partir de que la Administración Tributaria autorice el levante de las mercancías, de los desembolsos realizados por Megapólizas por parte de importador o exportador (pagos a terceros).</li>
                <li><strong>15 días crédito</strong> por honorarios que cobra Megapólizas.</li>
            </ul>
        """
    )
    datos_asesor=fields.Html(string="Datos del Asesor", 
            default="""<p>
                <strong>Lic. Humberto Vásquez Montufar</strong><br>
                Magister Artium en Economía e Impuestos<br>
                Especializado en Aduanas y Comercio Internacional Abogado y Notario; CPA.<br>
                Móvil: 5017-0781
                </p>
        """)
    firmar = fields.Boolean(string="Firmar", default=False)
    firma = fields.Html(
        string="Firma",
        default="""
            <p class="cuerpo2">Firma de aceptación: 
                <span style="display: inline-block; width: 70%; border-bottom: 1px solid black;"></span>
            </p>
            <br /><br/><br/>
            <p class="cuerpo2">Nombre del ejecutivo que firma: 
                <span style="display: inline-block; width: 60%; border-bottom: 1px solid black;"></span>
            </p>
        """
    )
    
    partner_id = fields.Many2one('res.partner', string="Cliente")
    # start_date= fields.Date(string="Fecha de Inicio")
    # end_date= fields.Date(string="Fecha Final")
    # quanty_min=fields.Float(string="Cantidad Minima")
    exp_date=fields.Date(string="Fecha de expiración")
    # price=fields.Float(string="Precio")
    partner_contact=fields.Many2one('res.partner',string="Contacto")
    partner_contact1=fields.Char(string="Contacto")
    email=fields.Char(string="Email")
    nit=fields.Char(string="NIT")
    phone=fields.Char(string="Teléfono")
    # partner_name=fields.Char(related='partner_contact.name')
    # partner_phone = fields.Char(related='partner_contact.phone')
    # partner_email= fields.Char(related='partner_contact.email')
    template_id = fields.Many2one('mail.template', string="Plantilla de correo")
    # date_start = fields.Date(readonly=False)  # Ahora el campo es editable.

    start_date = fields.Date(string="Fecha de Inicio")
    end_date = fields.Date(string="Fecha de Fin")
    quanty_min = fields.Float(string="Cantidad Mínima")
    price = fields.Float(string="Precio")

   
    # @api.model
    # def create(self, vals):
    #     if 'notas_importantes' not in vals or not vals['notas_importantes']:
    #         vals['notas_importantes'] = """
    #             <ul>
    #                 <li>Se hace un recargo por línea adicional de <strong>Q200.00</strong> por múltiples de 100 líneas a partir de la línea 21.</li>
    #                 <li>Se hace un recargo de <strong>Q350.00</strong> cuando el monto desembolsado por pagos a terceros supera los <strong>Q3,500.00</strong>.</li>
    #                 <li><strong> 15 días crédito </strong> a partir de que la Administración Tributaria autorice el levante de las mercancías, de los desembolsos realizados por Megapolizas por parte del importador o exportador (pagos a terceros).</li>
    #                 <li><strong> 15 días crédito </strong> por honorarios que cobra Megapolizas.</li>
    #             </ul>
    #         """
    #     return super(priceList, self).create(vals)
    
    @api.onchange('partner_id')
    def copy_name(self):
        for price in self:
            price.name = price.partner_id.name
            
    @api.onchange('start_date', 'end_date', 'quanty_min', 'price')
    def _onchange_dates(self):
        if self.start_date and self.end_date:
            # Buscar registros
            pricelists = self.env['product.pricelist.item'].search([])
            if pricelists:
                pricelists.write({
                    'date_start': self.start_date,
                    'date_end': self.end_date,
                })
            else:
                _logger.warning("No se encontraron registros en 'product.pricelist.item'")


    def get_letter(self):
        template_obj = self.template_id or self.env['mail.template'].sudo().search(
            [('model', '=', 'product.pricelist')], limit=1)

        if template_obj:
            ctx = dict() 

            ctx.update({
                'default_model': 'product.pricelist',
                'default_use_template': bool(template_obj),
                'default_template_id': template_obj.id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
            })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    # def action_print_message(self):
    #     pricelist = self.env['product.pricelist'].browse(self.env.context.get('active_id'))
    #     template = self.env['mail.template'].browse(pricelist.template_id.id)
        
    #     # Renderizar el contenido del correo electrónico
    #     email_body = template._render_template(template.body_html, 'product.pricelist', [pricelist.id], post_process=True).encode('base64')
        
        
    #     # Preparar el archivo PDF para la descarga
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': 'data:application/pdf;base64,%s' % email_body,
    #         'target': 'self',
    #     }
