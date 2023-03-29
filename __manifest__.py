# Copyright 2023 Babur Ltda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Fleet Vehicle Brazilian Traffic Infractions',
    'summary': """
        This modules consume Senatran RPA API to fetch multas de transito and generate invoices and bills.""",
    'version': '13.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Babur Ltda',
    'website': 'babur.com.br',
    "application": True,
    "installable": True,
    "auto_install": True,
    'depends': [
        'fleet',
        'account',
        'base',
    ],
    'data': [
        "views/fleet_vehicle.xml",
        "security/fleet_vehicle_traffic_infractions.xml",
        "views/orgao_autuador_views.xml",
        "views/fleet_vehicle_traffic_infractions.xml",
        "data/fleet_vehicle_traffic_infractions.xml",
        'views/config_settings_views.xml',
        "security/ir.model.access.csv",
        "data/traffic_infractions_data.xml",
    ],
    'demo': [
    ],
    'post_init_hook': 'populate_table_orgao_autuador',
}
