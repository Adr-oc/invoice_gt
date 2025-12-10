# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
from datetime import datetime
from datetime import timedelta
import calendar
import logging


class ReportePassword(models.AbstractModel):
    _name = "report.invoice_gt.contrasena_proveedor"
    _description = "Password Purchase Order"
    _inherit = ['mail.thread']

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(self.env.context.get('active_ids', []))
    #crea y valida campo de incremento (contraseña)
        id_order = ','.join([str(x) for x in docids])
        ids_orders = []
        
        for x in docids:
            ids_orders.append(x)
        query_order = self.env['purchase.order'].search([('id', 'in', ids_orders )])
        for x in query_order:
            if x.contrasena != False:
                message = ("La orden " + x.name + " ya tiene una contraseña generada") 
                raise UserError(message)
            if x.contrasena == False:
                correlativo_en_db = self.env['ir.sequence'].next_by_code('purchase.order.contra')
        for x in query_order:
            x.contrasena = correlativo_en_db
            x.state = 'done'
            x.invoice_status = 'invoiced'
    
    #generacion de factura con orden la de compra
        for x in query_order:
            purchase_order_line = self.env['purchase.order.line'].search([('order_id', '=', x.id )])
            purchase_order_factura = self.env['account.move'].create({
                'x_studio_serie':x.Serie,
                'ref': x.partner_ref,
                'x_studio_nmero_de_dte': x.Factura,
                'invoice_payment_term_id': x.Pago,
                'partner_id': x.partner_id,
                'invoice_origin': x.name,
                'company_id':2,
                'currency_id':x.currency_id,
                'contrasena':correlativo_en_db,
                'payment_state': 'not_paid', 
                'state' : 'draft',
                'move_type'  : 'in_invoice',   
                'referencia_bl' : x.referencia_bl,
                'buque_referencia_fel' : x.buque_referencia_fel,
                'invoice_line_ids': [(0, 0, {
                    'product_id': line.product_template_id.id,
                    'quantity': line.product_qty,
                    'price_unit': line.price_unit,
                    'tax_ids':line.taxes_id
                    }) for line in purchase_order_line]              
            })
            
    
    #reporte de constacia para contraseñas    
        query="""select date_order as fecha, "Factura", "Serie", "File", amount_total as total, 
                    rp."name" as proveedor, rp.vat as nit, po."Pago",	 
                    rc.id as moneda
                    from purchase_order po 
                    inner join res_partner rp on po.partner_id = rp.id
                    inner join res_currency rc on po.currency_id = rc.id
                    where po.id in (%s);"""
              
        self.env.cr.execute(query % (id_order))
        list_body={}
        body=[]
        nit=[]
        proveedor=[]
        fecha_pago=[]
        totalQ=0.0
        totalUSD=0.0
        for r in self.env.cr.dictfetchall():
            list_body={
                'total' : r['total'],
                'moneda' : r['moneda'],
                'file' : r['File'],
                'fecha' : r['fecha'].strftime("%d/%m/%Y"),
                'codigo' : r['Serie']+" - "+r['Factura'],
            }
            nit = r['nit']
            proveedor = r['proveedor']
            fecha_pago = r['Pago']
            if list_body['moneda']==170:
                totalQ= float(list_body['total']) + totalQ
            else:
                totalUSD= float(list_body['total']) + totalUSD
            body.append(list_body)
        totalQ="{:.2f}".format(totalQ) 
        totalUSD="{:.2f}".format(totalUSD)   
        fecha_pago=fecha(fecha_pago)  
            
            
        return {
            'doc_ids': self.ids,
            'body' : body,
            'docs': docs,
            'nit' : nit,
            'contra':correlativo_en_db,
            'proveedor' : proveedor,
            'fecha_pago' : fecha_pago,
            'TotalQ': totalQ,
            'TotalUSD':totalUSD,
            'current_company_id': self.env.company,
        }

def valores (lista):
    if len(lista) == 0 or lista[0]== None:
        producto = "inexistente"   
    else:
        for x in lista:
            if x != lista[0]:
                variado=x
                break
            else: 
                variado=""
        producto = "VARIOS" if variado != "" else lista[0]
    return producto    




def fecha(Pago):
    hoy = datetime.now()
    Pago = str(Pago)
    plazo = ''
    dias={'1':0,'10':8,'9':9,'2':15,'3':21,'4':30,'5':45}
    if Pago in dias:
        plazo=dias[Pago]
    if plazo == 0:
        dia= hoy
    else:
        dia = hoy +  timedelta(plazo)  
        num = dia.weekday()

        if num < 4:
            while num < 4 or num > 4:
                dia += timedelta(1)
                num = dia.weekday()
        if num > 4:
            while num > 4:
                dia -= timedelta(1)
                num = dia.weekday()
        
    Pago = str(dia.strftime('%d/%m/%Y'))
    return Pago

