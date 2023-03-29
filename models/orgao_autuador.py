from odoo import models, fields, api, SUPERUSER_ID

class OrgaoAutuador(models.Model):
    _name = 'traffic_infractions.orgao_autuador'
    _description = 'Tabela de Orgãos Autuadores'

    code = fields.Char(string='Code', required=True, index=True, unique=True)
    description = fields.Char(string='Description', required=True)


    def uninstall_hook(self):
        cr = self.env.cr
        cr.execute('DROP TABLE IF EXISTS traffic_infractions_orgao_autuador')

    def populate_table_from_raw_text(self, raw_text):
        lines = raw_text.strip().split('\n')
        for line in lines:
            code, description = line.strip().split(' - ', maxsplit=1)
            orgao_autuador = self.create([{    'code': code,    
                                           'description': description}])