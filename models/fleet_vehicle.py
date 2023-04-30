# Copyright 2023 - TODAY, Raimundo Junior - Babur https://www.babur.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import datetime
import json
import logging

_logger = logging.getLogger(__name__)

class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    traffic_infractions_ids = fields.One2many(
        "fleet.vehicle.traffic_infractions", "vehicle_id", "Traffic Infractions Logs"
    )

    traffic_infractions_count = fields.Integer(
        compute="_compute_traffic_infractions_count", string="Traffic Infractions Count"
    )

    @api.depends("traffic_infractions_ids")
    def _compute_traffic_infractions_count(self):
        for rec in self:
            rec.traffic_infractions_count = len(rec.traffic_infractions_ids)

    def action_view_traffic_infractions(self):
        
        action = self.env.ref(
            "fleet_vehicle_traffic_infractions.fleet_vehicle_traffic_infractions_act_window"
        ).read()[0]
        if self.traffic_infractions_count > 1:
            action["domain"] = [("id", "in", self.traffic_infractions_ids.ids)]
        else:
            action["views"] = [
                (
                    self.env.ref(
                        "fleet_vehicle_traffic_infractions.fleet_vehicle_traffic_infractions_form_view"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = (
                self.traffic_infractions_ids and self.traffic_infractions_ids.ids[0] or False
            )
        return action

    def fetch_traffic_infractions(self):
        params = self.env["ir.config_parameter"].sudo()
        renach_api_url=params.get_param("traffic_infraction.renach_api_url")
        #renach_api_token=params.get_param("traffic_infraction.renach_api_token")
        for vehicle in self:
            company_type = vehicle.vehicle_owner.partner_id.company_type
            if company_type == 'person': 
                role = 'pf' 
            elif company_type == 'company': 
                role = 'pj'
            response = requests.get(f"{renach_api_url}/traffic_infractions?role={role}&plate={vehicle.license_plate}")
            if response.status_code == 200:
                data = response.json()
                _logger.info(f"response.json(): {data}")
                #self.process_infraction_json(data, vehicle)
            else:
                raise UserError(_("Unable to fetch data from API for vehicle %s") % vehicle.license_plate)

    def _batch_fetch_traffic_infractions(self):
        for vehicle in self.search([('active','=',True)]):
            _logger.info("Starting fetch_traffic_infractions...")
            _logger.info(f"vehicle: {vehicle.name}")
            vehicle.fetch_traffic_infractions()

    @api.model
    def get_driver_on_date(self, vehicle_id, target_date):
        """
        Retrieve the driver of a vehicle on a specific date
        based on fleet.vehicle.assignation.log model.

        :param vehicle_id: int
            The ID of the vehicle to check
        :param date: str
            The date to check in 'YYYY-MM-DD' format
        :return: recordset
            The driver (res.partner) recordset or empty recordset if no driver found
        """

        # Search for the vehicle's assignation logs up to the target date
        assignation_logs = self.env['fleet.vehicle.assignation.log'].search([
            ('vehicle_id', '=', vehicle_id),
            ('date_start', '<=', target_date),
        ], order='date_start desc', limit=1)

        # Return the driver if a log is found, otherwise return an empty recordset
        return assignation_logs.driver_id if assignation_logs else self.env['res.partner']