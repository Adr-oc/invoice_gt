# -*- coding: utf-8 -*-
{
    'name': "Agrega tipo de impresiones",

    'summary': """
        Agregar nuevos formatos de impresiones """,

    'description': """
        Agregar nuevos formatos de impresiones
    """,

    'author': "AppSystems, S.A.",
    'website': "http://www.sistemas.com.gt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '19.0.1.1.1',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'purchase', 'sale'],

    # always loaded
    'data': [
        'security/account_menu.xml',
        'security/ir.model.access.csv',
        'views/bank_view.xml',
        'views/account_journal_view.xml',
        'views/report_envio_base.xml',
        'views/report_note_debit.xml',
        'views/report_cuenta_terceros.xml',
        'views/report_commercial_invoice.xml',
        'views/report_credit_note.xml',
        'views/account_view.xml',
        'views/report_receipt_payment.xml',
        'report/report_invoice.xml',
        'views/account_move_view.xml',
        'views/payment_view.xml',
        'report/passwords_proveedor.xml',
        'views/purcharse_order_view.xml',
        'report/password_pdf.xml',
        'report/report_invoice_state_pdf.xml',
        'views/company_view.xml',
        'views/sequence_contrasena.xml',
        'views/asistente_send_mail.xml',
        'report/state_account_details.xml',
        'report/report_sale_order.xml',
        'views/voucher_bi.xml',
        'views/voucher_bi_assukargo.xml',
        'views/res_partner.xml',
        'report/cuenta_ajena_report.xml',
        'report/cuenta_ajena_pdf.xml',
        'views/pricelist.xml',
        'report/reporte_tarifa.xml',
        'report/invoice.xml',
        # 'views/button.xml',
        'views/masive_payments.xml',
    ],
    'css': [
        'invoice_gt/static/src/css/electronic_receipt.css',
        'invoice_gt/static/src/css/ajustes_celda.css',
        'invoice_gt/static/src/css/envio_base.css',
        'invoice_gt/static/src/css/clases.css'
    ],
    
    'assets': {
        'web.assets_backend': [
            # '/invoice_gt/static/src/js/tree_button.js',
            # '/invoice_gt/static/src/xml/tree_button.xml',

        ],
        'web.assets_qweb': [
        ],
    },

    'auto_install': False,
    'installable': True,
}

