from odoo import http
from odoo.http import request

import json

import logging

_logger = logging.getLogger(__name__)

class TrafficInfractionsWebhookController(http.Controller):

    @http.route('/traffic_infractions/webhook', type='json', auth='public', csrf=False, methods=['POST'])
    def traffic_infractions_webhook(self, **kwargs):
            bearerToken = request.env["ir.config_parameter"].sudo().get_param("traffic_infraction.renach_api_token")
            bearerToken = f'Bearer {bearerToken}'
            _logger.info(f"request.httprequest.headers['Authorization']: {request.httprequest.headers['Authorization']}")
            if request.httprequest.headers['Authorization'] == bearerToken:
                data = json.loads(request.httprequest.data)
                _logger.info(f"data: {data}")
                # Process the received JSON data, e.g. create or update records in Odoo
                vehicle = request.env['fleet.vehicle'].sudo().search([('license_plate','=',data['multas'][0]['placa'])])
                request.env['fleet.vehicle.traffic_infractions'].sudo().process_infraction_json(data, vehicle)

                # Return a response
                return json.dumps({
                    'status': 'success',
                    'message': 'Traffic infraction data received and processed.',
                })
            else:
                # Return a response
                return json.dumps({
                                "error": {
                                    "code": 404,
                                    "message": "Auth fails"
                                }
                                })
                 




