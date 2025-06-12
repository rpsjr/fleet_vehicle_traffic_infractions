import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    env = util.env(cr)
    traffic_infractions = env['fleet.vehicle.traffic_infractions'].search([])
    for infraction in traffic_infractions:
        chave_infracao = "{}{}{}".format(
            infraction.codigo_orgao_autuador or '',
            infraction.numero_auto_infracao or '',
            infraction.codigo_infracao or ''
        )
        infraction.write({'chave_infracao': chave_infracao})