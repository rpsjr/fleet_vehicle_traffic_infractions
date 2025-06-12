from odoo import api, SUPERUSER_ID

def compute_chave_infracao(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    traffic_infractions = env['fleet.vehicle.traffic_infractions'].search([])
    for infraction in traffic_infractions:
        chave_infracao = "{}{}{}".format(
            infraction.codigo_orgao_autuador or '',
            infraction.numero_auto_infracao or '',
            infraction.codigo_infracao or ''
        )
        infraction.write({'chave_infracao': chave_infracao})