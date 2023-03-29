# Copyright <2023> <Raimundo Pereira da Silva Junior <raimundopsjr@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
import requests
from pydantic import BaseModel

class DetranMultasBA(models.Model):
    _name = 'fleet.vehicle.multas.ba'
    _description = 'Gerenciamento de Multas'

    name = fields.Char(compute="_compute_multa_name", store=True)

    data = fields.Date(string="Data da ocorrência")
    descricao = fields.Char('Descrição da Infração')
    situacao = fields.Char('Situação da Infração')
    local = fields.Char('Local da Infração')
    municipio = fields.Char('Município da Infração')
    valor = fields.Char('Valor da Infração')
    orgao_cod = fields.Char('Código do Orgão Autuador')
    orgao_desc = fields.Char('Descrição Orgão')


    @api.depends('descricao', 'orgao_desc', 'data')
    def _compute_multa_name(self):
        for record in self:
            record.name = (record.descricao or '') + '/' + (record.orgao_desc or '') + '/' + (record.data or '')


    def fetch_multas(self, renavam):
        url = f"https://servicosaocidadao.ba.gov.br/api/utilidade/v1/api/respbuilder/v1/detran-multas/consultar?renavam={renavam}&"

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://sacdigital.ba.gov.br',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'servicosaocidadao.ba.gov.br',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': 'https://sacdigital.ba.gov.br/',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Connection': 'keep-alive',
            'x-canal': 'Portal'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")

# Example usage
#renavam = "00554162210"
#multas = fetch_multas(renavam)
#print(multas)