# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import time
from datetime import datetime
import base64
import logging


class sendMailWizzard(models.Model):
    _name = 'send.mail.wizzard'

    def default_subject(self):
        docs = self.env['account.move'].browse(self.env.context.get('active_ids', []))
        if docs:
            return 'Estado de cuenta ' + docs.partner_id.name

    def default_mail_to(self):
        docs = self.env['account.move'].browse(self.env.context.get('active_ids', []))
        if docs:
            return  docs[0].partner_id
        else:
            partner_id = self.partner_id
        return partner_id
    
    def default_body(self):
        docs = self.env['account.move'].browse(self.env.context.get('active_ids', []))
        body = ''
        if docs:
            body = 'Estimados ' + docs.partner_id.name + '\n <br> Con gusto se adjunta estado de cuenta a la fecha con los saldos pendientes de pago para Asersa De Guatemala, Sociedad Anónima.\n <br> Quedamos atentos a su amable confirmación del pago.\n <br> Cualquier duda o comentario estamos a la orden. \n <br> Saludos cordiales'
        return body
    
    def ir_attachment(self):
        docs = self.env['account.move'].browse(self.env.context.get('active_ids', []))
        if docs:
            report = "invoice_gt.invoice_gt_action_state_account"
            pdf = self.env.ref(report)._render_qweb_pdf(docs.ids)

            #se convierte a base64 y se agrega a la vista
            data_record = base64.b64encode(pdf[0])
            ir_values = {
                'name': 'Estado de cuenta ' + docs.partner_id.name,
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/pdf',
            }
    
            data_id = self.env['ir.attachment'].sudo().create(ir_values)
            return data_id
        
    mail_to = fields.Many2many('res.partner', string="Destinatarios", default=default_mail_to)
    subject = fields.Char(string='Asunto', default=default_subject)
    body = fields.Char(string="Mensaje", default=default_body)
    name_file = fields.Char(string="Nombre Archivo")
    file_mail = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id', 'Attachments', default=ir_attachment)


    def save_new_tmpl_mail(self):
        self.write({'body': self.body})
    

    def send_notifications(self):
        #toma todos los items activos para poder utilizarlos después
        docs = self.env['account.move'].browse(self.env.context.get('active_ids', []))
        
        if docs:
            #se hace referencia al modulo que envía y recepciona correos
            mail_pool = self.env['mail.mail']
            #se arma el correo
            partner_id = docs.partner_id
            mail_from = docs.current_user.email
            mail_to = ",".join([str(x.email) for x in self.mail_to])
            ids = ",".join([str(x.id) for x in docs])
            attach_ids = self.file_mail.ids
           
            body = self.body
            
            values={}
            values.update({'email_from': mail_from})
            values.update({'subject': 'Estado de cuenta ' + partner_id.name})
            values.update({'email_to': mail_to})
            values.update({'body_html': body })
            values.update({'res_id': docs.ids[0]})
            values.update({'notification': True})
            values.update({'model': 'account.move'})
            msg_id = mail_pool.create(values)
            msg_id.attachment_ids = [(6, 0, attach_ids)]


            #se llama a la función que envía el correo
            if msg_id:
                msg_id.send([msg_id])
                msg_id.attachment_ids = [(3, 0, attach_ids)]
                self.unlink()


class AccountMoveNew(models.Model):
    _inherit = 'account.move'

    def open_email(self):
        view_id = self.env.ref('invoice_gt.asistente_send_mail').id

        return {
            'name': 'Enviar correo',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'send.mail.wizzard',
            'target': 'new',
            'type': 'ir.actions.act_window'
        }