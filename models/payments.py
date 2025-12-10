# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import logging
import base64
import io
import pandas as pd


class WizzardUploadPayments(models.TransientModel):
    _name = "invoice.wizzard.payments"
    _description = "Wizzard para subir pagos"

    lineas = fields.One2many('invoice.wizzard.list.payments', 'wizzard_id', string='Lineas')
    partner_id = fields.Many2one('res.partner', string="Partner")
    upload_file = fields.Binary(string ='Subir archivo', required=True)
    payment_method_id = fields.Many2one('account.payment.method.line', string='Método de Pago', required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True)
    journal_id = fields.Many2one('account.journal', string='Diario', required=True)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            # Filtrar solo métodos de pago entrantes (inbound)
            return {
                'domain': {
                    'payment_method_id': [
                        ('journal_id', '=', self.journal_id.id),
                        ('payment_type', '=', 'inbound')
                    ]
                }
            }
        else:
            # Si no hay diario seleccionado, eliminar el dominio
            return {
                'domain': {
                    'payment_method_id': []
                }
            }

    # @api.depends('move_type')
    # def 
    
    def read_file(self):
        # Leer el archivo subido
        file = base64.b64decode(self.upload_file)
        io_file = io.BytesIO(file)
        df = pd.read_excel(io_file, engine='openpyxl')

        # Verificar que existan las columnas necesarias
        if 'Referencia' not in df.columns:
            raise ValidationError('No se encontró la columna Referencia')
        if 'Importe' not in df.columns:
            raise ValidationError('No se encontró la columna Importe')

        # Iterar sobre las filas
        lines = []
        facturas = []
        id_factura = False
        nombre_factura = False
        id_ficticio = -1
        referencias_no_encontradas = []  # Lista para referencias sin factura
        client = self.partner_id
        for index, row in df.iterrows():
            if row['Referencia']:
                references = str(row['Referencia']).split(' ')
                factura_encontrada = False  # Variable para saber si alguna factura fue encontrada
                for reference in references:
                    # Buscar factura por las líneas de factura (account_move_line)
                    self.env.cr.execute("""
                        SELECT aml.*
                        FROM account_move_line aml
                        JOIN account_move am ON aml.move_id = am.id
                        WHERE aml.name ILIKE %s
                        AND am.move_type = 'out_invoice'
                        AND am.payment_state != 'paid'
                        AND am.state != 'cancel'
                        AND (am.partner_id = %s OR am.partner_id IS NULL)
                    """, ('%{}%'.format(reference), client.id))
                    factura = self.env.cr.dictfetchall()


                    if factura:
                        id_factura = factura[0]['move_id']
                        nombre_factura = self.env['account.move'].search([('id', '=', id_factura), ('move_type', '=', 'out_invoice')], limit=1)
                        factura_encontrada = True
                        break
                    else:
                        # Si no se encuentra en las líneas, buscar directamente en account_move
                        self.env.cr.execute("""
                            SELECT *
                            FROM account_move
                            WHERE (x_studio_serie ILIKE %s
                            OR ref ILIKE %s
                            OR referencia_1 ILIKE %s
                            OR referencia_2 ILIKE %s)
                            AND move_type = 'out_invoice'
                            AND payment_state != 'paid'
                            AND state != 'cancel'
                            AND (partner_id = %s OR partner_id IS NULL)
                        """, tuple('%{}%'.format(reference) for _ in range(5)) + (client.id,))

                        factura = self.env.cr.dictfetchall()
                        

                        if factura:
                            id_factura = factura[0]['id']
                            nombre_factura = self.env['account.move'].search([('id', '=', id_factura), ('move_type', '=', 'out_invoice')], limit=1)
                            factura_encontrada = True
                            break

                # Si no se encontró una factura para la referencia
                if not factura_encontrada:
                    id_factura = id_ficticio
                    id_ficticio -= 1  # Decremento para asegurar que sea único
                    nombre_factura = False  # No se encontró factura real
                    referencias_no_encontradas.append(reference)  # Agregar referencia a la lista

            # Agrupar pagos si ya se encontró la factura
            if id_factura in facturas:
                lines[facturas.index(id_factura)]['amount_company_currency_signed'] += row['Importe']
                lines[facturas.index(id_factura)]['boleta'] += ' ' + str(row['Pago'])
            else:
                lines.append({
                    'ref': nombre_factura.id if nombre_factura else False,
                    'date': row['Fecha'],
                    'boleta': str(row['Pago']),
                    'amount_company_currency_signed': row['Importe'],
                    'state': 'draft',
                })
                facturas.append(id_factura)

        # Crear las líneas
        for line in lines:
            # Buscar el registro de la factura usando el ID almacenado en line['ref']
            factura = self.env['account.move'].browse(line['ref']) if line['ref'] else False
            monto_adeudado = factura.amount_residual if factura else 0.0
            context = self.env.context
            if context.get('from_test_click'):
                boleta = line['boleta']
            elif context.get('from_new_button_click'):
                boleta = ""
                #aqui se deberia agregar el campo del monto total
            self.env['invoice.wizzard.list.payments'].create({
                'wizzard_id': self.id,
                'ref': line['ref'],
                'date': line['date'] if line['date'] else datetime.now(),
                'amount_company_currency_signed': line['amount_company_currency_signed'],
                'amount_total_ade': monto_adeudado, 
                'partner_id': factura.partner_id.id if factura else 0,
                'boleta': boleta,
            })



        # Si no hay referencias no encontradas, evitar que se cierre el wizzard al presionar botón
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.wizzard.payments',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }




    def action_generate_payments(self):
        total_adeudado = sum(line.amount_total_ade for line in self.lineas if line.ref)
        if round(total_adeudado, 2) == 0.0:
            raise ValidationError(_("No se pueden generar pagos porque todas las facturas seleccionadas ya están completamente pagadas."))
        
        context = self.env.context

        if context.get('from_test_click'):
            # Llamada a la función para pagos individuales
            return self._generate_individual_payments()
        elif context.get('from_new_button_click'):
            # Llamada a la función para pago agrupado
            return self._generate_grouped_payment()
        else:
            # Error en caso de no tener el contexto adecuado
            raise ValidationError("No se especificó el contexto adecuado para la generación de pagos.")

    def _generate_individual_payments(self):
        pagos = []
        for line in self.lineas:
            if not line.ref:
                raise ValidationError(_('No se encontró la referencia en la fila ') + str(line.id))

            if round(line.amount_total_ade, 2) == 0.0:
                raise ValidationError(_('No se puede aplicar pago a la factura %s porque ya está completamente pagada.') % line.ref.name)
            # Crear el pago individual para cada línea
            payment = self.env['account.payment'].create({
                'ref': line.ref.name,
                'date': line.date,
                'amount': line.amount_company_currency_signed,
                'state': 'draft',
                'journal_id': self.journal_id.id,
                'payment_method_line_id': self.payment_method_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'boleta': line.boleta,
            })

            payment.action_post()
            pagos.append(payment)

            # Llamar a la reconciliación parcial solo para la factura de esta línea
            self.apply_payment_to_invoice(payment, line.ref)

        # Recargar vista después de crear pagos
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        
        
    def apply_payment_to_invoice(self, new_payment, invoice):
        # Aquí solo vamos a aplicar el pago a la factura específica pasada como parámetro (invoice)

        # Buscar la línea de débito correspondiente al pago
        debit_line = new_payment.move_id.line_ids.filtered(
            lambda l: l.account_id.id == new_payment.destination_account_id.id
        )

        # Buscar la línea de crédito correspondiente en la factura (término de pago)
        credit_line = invoice.line_ids.filtered(
            lambda l: l.display_type == 'payment_term'
        )

        if not debit_line or not credit_line:
            raise ValidationError('No se encontraron líneas de débito o crédito para conciliar.')

        # Crear la reconciliación parcial
        self.env['account.partial.reconcile'].create({
            'debit_amount_currency': new_payment.amount,
            'credit_amount_currency': new_payment.amount, 
            'amount': new_payment.amount,  
            'debit_move_id': credit_line.id,
            'credit_move_id': debit_line.id,
        })
        
    def _generate_grouped_payment(self):
        total_adeudado = sum(line.amount_total_ade for line in self.lineas if line.ref)
        if round(total_adeudado, 2) == 0.0:
            raise ValidationError(_("No se pueden generar pagos porque todas las facturas seleccionadas ya están completamente pagadas."))
        # Verificación de referencia y cálculo del monto total
        total_amount = sum(line.amount_company_currency_signed for line in self.lineas if line.ref)
        if any(not line.ref for line in self.lineas):
            raise ValidationError(_('Todas las líneas deben tener una referencia para agrupar pagos.'))

        # Obtener la lista de referencias de facturas
        factura_refs = ', '.join(line.ref.name for line in self.lineas)

        # unicamente primer boleta
        boleta_unica = self.lineas[0].boleta

        # Crear un solo pago agrupado con el monto total
        payment = self.env['account.payment'].create({
            'ref': f'Pago Agrupado: {factura_refs}',
            'date': self.lineas[0].date,
            'amount': total_amount,
            'state': 'draft',
            'journal_id': self.journal_id.id,
            'payment_method_line_id': self.payment_method_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'boleta': boleta_unica,  # Asignar la boleta única si todas son iguales
        })

        payment.action_post()

        # Aplicar el monto de cada línea de factura a la factura específica mediante la reconciliación parcial
        for line in self.lineas:
            self.apply_partial_payment_to_invoice(payment, line.ref, line.amount_company_currency_signed)

        # Recargar vista después de crear el pago agrupado
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def apply_partial_payment_to_invoice(self, payment, invoice, amount):
        # Aplicar reconciliación parcial de un monto específico para una factura
        debit_line = payment.move_id.line_ids.filtered(
            lambda l: l.account_id.id == payment.destination_account_id.id
        )

        credit_line = invoice.line_ids.filtered(
            lambda l: l.display_type == 'payment_term'
        )

        if not debit_line or not credit_line:
            raise ValidationError('No se encontraron líneas de débito o crédito para conciliar.')

        # Crear la reconciliación parcial solo por el monto especificado
        self.env['account.partial.reconcile'].create({
            'debit_amount_currency': amount,
            'credit_amount_currency': amount,
            'amount': amount,
            'debit_move_id': credit_line.id,
            'credit_move_id': debit_line.id,
        })



class WizzardListPayments(models.TransientModel):
    _name = "invoice.wizzard.list.payments"
    _description = "Líneas de pagos en el asistente de pagos"

    wizzard_id = fields.Many2one('invoice.wizzard.payments', string='Wizzard')
    ref = fields.Many2one('account.move', string='Referencia')
    amount_company_currency_signed = fields.Float(string='Monto en moneda de la compañía')
    monto_total = fields.Many2one('account.move',string='Monto en moneda de la compañía')
    suitable_journal_ids = fields.Many2many('account.journal', string='Diarios adecuados')
    date = fields.Date(string='Fecha', required=True)
    name = fields.Char(string='Número')
    boleta = fields.Char(string='Boleta')
    fecha_anulacion = fields.Date(string='Fecha de anulación')
    amount_signed = fields.Float(string='Monto')
    amount_total_ade = fields.Float(string='Monto total adeudado', store=True)
    company_currency_id = fields.Many2one('res.currency', string='Moneda' )
    partner_id = fields.Many2one('res.partner', string='Partner')  # Agregando el campo partner_id
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Publicado'),
        ('cancel', 'Cancelado'),
    ], string='Estado', default='draft')

    # Campo computado para la moneda
    currency_id = fields.Many2one('res.currency', string='Moneda', compute='_compute_currency_id', store=True)

    @api.depends('ref')
    def _compute_amount_total_ade(self):
        for record in self:
            record.amount_total_ade = record.ref.amount_residual if record.ref else 0.0

    @api.onchange('ref')
    def _onchange_ref(self):
        for record in self:
            if record.ref:
                # Obtener siempre el valor actual del campo amount_residual
                record.amount_total_ade = record.ref.amount_residual
            else:
                record.amount_total_ade = 0.0

    @api.depends('ref', 'suitable_journal_ids')
    def _compute_currency_id(self):
        for record in self:
            # Si no hay referencia, se obtiene la moneda del primer diario en suitable_journal_ids
            if record.suitable_journal_ids:
                record.company_currency_id = record.suitable_journal_ids[0].currency_id
            elif record.ref:
                record.company_currency_id = record.ref.currency_id
            else:
                record.company_currency_id = record.company_currency_id
            # Calculamos la moneda de referencia dependiendo de la compañía o la referencia
            if record.ref:
                record.currency_id = record.ref.currency_id
            else:
                record.currency_id = record.company_currency_id


    def create_payment(self):
        currency_id = self.currency_id.id
        # Crear el pago
        payment = self.env['account.payment'].create({
            'date': self.date,
            'name': self.name,
            'boleta': self.boleta,
            'fecha_anulacion': self.fecha_anulacion,
            'journal_id': self.journal_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'partner_id': self.partner_id.id,  # Usar el campo partner_id correctamente
            'amount_signed': self.c,
            'currency_id': currency_id,  # Usar la moneda calculada automáticamente
            'amount_company_currency_signed': self.amount_company_currency_signed,
            'monto_total': self.monto_total,
            'state': self.state,
        })
        
        # Validar el pago
        payment.post()
        
        # Retornar el pago
        return payment
