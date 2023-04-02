# -*- coding: utf-8 -*-

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]


    invoice_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Invoice Payment Term',
        readonly=False,
        help="Standard invoice payment term to traffic infraction invoice (out) (18 bco inter)",
        config_parameter="traffic_infraction.invoice_payment_term_id",
    )
    
    payment_journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        readonly=False,        
        help="Standard invoice term journal to traffic infraction invoice (out) (30 bco inter)",
        config_parameter="traffic_infraction.payment_journal_id",
    )
    
    product_category = fields.Many2one(
        'product.category',
        string='Product Category',
        readonly=False,        
        help="Standard product category to traffic infraction invoice (out) ",
        config_parameter="traffic_infraction.product_category",
    )
    
    renach_api_url = fields.Char(
        string='Url da API Renach',        
        readonly=False,        
        help="Endpoint da API Renach",
        config_parameter="traffic_infraction.renach_api_url",
    )
    
    renach_api_token = fields.Char(
        string='Token da API Renach',        
        readonly=False,        
        help="Token de acesso da API Renach",
        config_parameter="traffic_infraction.renach_api_token",                           
                                   )

