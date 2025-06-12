import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Calcula o campo 'chave_infracao' para os registros existentes no modelo
    'fleet.vehicle.traffic_infractions'.
    Este script é compatível com Odoo v13 e versões posteriores.
    """
    # No Odoo 13+, o ambiente (env) é obtido através da API e não do 'util'.
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info("Iniciando migração: calculando 'chave_infracao' para infrações de trânsito.")

    # Para otimizar, buscamos apenas registros onde 'chave_infracao' ainda não foi preenchida.
    # Isso evita o reprocessamento em futuras atualizações do módulo.
    records_to_update = env['fleet.vehicle.traffic_infractions'].search(
        [('chave_infracao', '=', False)]
    )

    if not records_to_update:
        _logger.info("Nenhuma infração de trânsito encontrada para ser atualizada.")
        return

    _logger.info(f"Encontradas {len(records_to_update)} infração(ões) para processar.")

    # Itera sobre os registros e os atualiza.
    for infraction in records_to_update:
        # A lógica para construir a chave permanece a mesma.
        # O uso de 'or '' lida corretamente com valores nulos (None) ou vazios.
        chave_infracao = "{}{}{}".format(
            infraction.codigo_orgao_autuador or '',
            infraction.numero_auto_infracao or '',
            infraction.codigo_infracao or ''
        )
        infraction.write({'chave_infracao': chave_infracao})

    _logger.info("Migração do campo 'chave_infracao' concluída com sucesso.")