# Copyright 2023 RPSJR raimundops.jr@gmail.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Fleet Vehicle Brazilian Traffic Infractions',
    'summary': """
        This modules consume Senatran Renach Data trough API to fetch brazilian traffic tickets and generate invoices and bills.""",
    'version': '13.0.1.2.2',
    'license': 'AGPL-3',
    'author': 'RPSJR',
    'website': 'https://github.com/rpsjr/fleet_vehicle_traffic_infractions',
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
