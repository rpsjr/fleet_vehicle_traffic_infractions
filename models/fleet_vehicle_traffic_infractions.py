# Copyright 2023 - TODAY, Raimundo Junior - Babur https://www.babur.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FleetVehicletrafficInfractions(models.Model):

    _name = "fleet.vehicle.traffic_infractions"
    _description = "Fleet Vehicle Traffic Infractions"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    READONLY_STATES = {
        "processed": [("readonly", True)],
        "cancel": [("readonly", True)],
    }

    name = fields.Char(
        "Reference", required=True, index=True, copy=False, default="New"
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("invoice", "Generate Invoice"),
            ("bill", "Generate Bill"),
            ("processed", "Processed"),
            ("cancel", "Canceled"),
        ],
        string="Status",
        copy=False,
        index=True,
        readonly=True,
        track_visibility="onchange",
        default="invoice",
        help=" * Draft: not confirmed yet.\n"
        " * Confirmed: Traffic Infractions has been confirmed.\n"
        " * Cancelled: has been cancelled, can't be confirmed anymore.",

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        "Vehicle",
        help="Fleet Vehicle",
        required=True,
        states=READONLY_STATES,
    )

    note = fields.Html("Notes", states=READONLY_STATES)

    driver_id = fields.Many2one(
        "res.partner", "Driver", tracking=True, help="Driver of the vehicle", copy=False
    )
    traffic_agency = fields.Many2one(
        "res.partner",
        "Traffic Agency",
        tracking=True,
        help="Traffic Agency of the infraction",
        copy=False,
        compute="_compute_traffic_agency",
    )

    chave_infracao = fields.Char(
 string="Chave Infracao",
        compute='_compute_chave_infracao',
        store=True,
        unique=True,
 )
    codigo_infracao = fields.Char(string="Codigo Infracao")
    codigo_orgao_autuador = fields.Char(string="Codigo Orgao Autuador")
    data_hora_infracao = fields.Datetime(string="Data Hora Infracao")
    data_registro_pagamento = fields.Date(string="Data Registro Pagamento")
    data_vencimento = fields.Date(string="Data Vencimento")
    descricao_infracao = fields.Char(string="Descricao Infracao")
    numero_auto_infracao = fields.Char(string="Numero Auto Infracao")
    numero_identificacao_proprietario = fields.Char(
        string="Numero Identificacao Proprietario"
    )
    permite_boleto_sne = fields.Boolean(string="Permite Boleto SNE")
    placa = fields.Char(string="Placa")
    situacao = fields.Char(string="Situacao")
    valor_multa = fields.Float(string="Valor Multa")

    out_invoice_ids = fields.Many2one(
        "account.move",
        "Invoice",
        readonly=True,
        help="Driver invoice generated for the traffic infraction",
        copy=False,
    )
    in_invoice_ids = fields.Many2one(
        "account.move",
        "Invoice",
        readonly=True,
        help="Goverment fine invoice generated for the traffic infraction",
        copy=False,
 )

 @api.depends('codigo_orgao_autuador', 'numero_auto_infracao', 'codigo_infracao')
 def _compute_chave_infracao(self):
 for rec in self:
 if rec.codigo_orgao_autuador and rec.numero_auto_infracao and rec.codigo_infracao:
 rec.chave_infracao = f"{rec.codigo_orgao_autuador}{rec.numero_auto_infracao}{rec.codigo_infracao}"
 else:
 rec.chave_infracao = False
    )

    timeline_ids = fields.One2many(
        "fleet.vehicle.traffic_infractions.timeline", "infraction_id", string="Timeline"
    )

    def action_view_out_invoices(self):
        self.ensure_one()

        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action["domain"] = [("id", "=", self.out_invoice_ids.id)]
        action["context"] = {
            "default_move_type": "out_invoice",
        }
        return action

    out_invoices_count = fields.Integer(
        compute="_compute_out_invoices_count",
        string="Traffic Infractions Out Invoice Count",
    )

    @api.depends("codigo_orgao_autuador")
    def _compute_traffic_agency(self):
        for rec in self:
            rec.traffic_agency = rec._get_partner_orgao_autuador()

    @api.depends("out_invoice_ids")
    def _compute_out_invoices_count(self):
        for rec in self:
            rec.out_invoices_count = len(rec.out_invoice_ids)

    def action_view_in_invoices(self):
        self.ensure_one()

        action = self.env.ref("account.action_move_in_invoice_type").read()[0]
        action["domain"] = [("id", "=", self.in_invoice_ids.id)]
        action["context"] = {
            "default_move_type": "in_invoice",
        }
        return action

    in_invoices_count = fields.Integer(
        compute="_compute_in_invoices_count",
        string="Traffic Infractions In Invoice Count",
    )

    @api.depends("in_invoice_ids")
    def _compute_in_invoices_count(self):
        for rec in self:
            rec.in_invoices_count = len(rec.in_invoice_ids)

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code(
                    "fleet.vehicle.traffic_infractions"
                )
                or "/"
            )

        return super(FleetVehicletrafficInfractions, self).create(vals)

    def button_cancel(self):
        records = self.filtered(
            lambda rec: rec.state in ["draft", "invoice", "bill", "processed"]
        )
        return records.write({"state": "cancel"})

    def button_confirm(self):
        if any(rec.state not in ["draft", "cancel"] for rec in self):
            raise ValidationError(
                _(
                    "Only traffic_infractionss in 'draft' or 'cancel' states can be confirmed"
                )
            )
        return self.write({"state": "processed"})

    def button_draft(self):
        return self.write({"state": "draft"})

    def create_invoice(self):
        account_move_obj = self.env["account.move"]
        product_obj = self.env["product.product"]

        params = self.env["ir.config_parameter"].sudo()
        invoice_payment_term_id = int(
            params.get_param("traffic_infraction.invoice_payment_term_id")
        )
        payment_journal_id = int(
            params.get_param("traffic_infraction.payment_journal_id")
        )
        product_category_id = int(
            params.get_param("traffic_infraction.product_category_id")
        )
        product_product_id = int(
            params.get_param("traffic_infraction.product_product_id")
        )

        for infraction in self:
            if not infraction.driver_id:
                raise UserError(
                    _("There is no driver assigned for this traffic infraction.")
                )

            # Get the driver's partner record
            partner = infraction.driver_id

            # Search for the product based on the product name structure
            product_name = f"[MLT{infraction.codigo_infracao}] Multa CTB"
            product = product_obj.search([("name", "=", product_name)], limit=1)

            # If the product is not found, create a new one
            if not product:
                product = product_obj.create(
                    {
                        "name": f"{product_name}",
                        "type": "service",
                        "sale_ok": True,
                        "purchase_ok": True,
                        "invoice_policy": "order",
                        "categ_id": product_category_id,
                    }
                )

            inv_line_values = [
                {
                    "product_id": product.id or False,
                    "name": f"{infraction.descricao_infracao} \
                    Chave da Infracao: {infraction.chave_infracao}"
                    or None,
                    "price_unit": infraction.valor_multa or None,
                    "quantity": 1,
                }
            ]
            if product_product_id:
                inv_line_values.append(
                    {
                        "product_id": product_product_id,
                        "quantity": infraction.valor_multa or None,
                        "price_unit": product_obj.search(
                            [("id", "=", product_product_id)], limit=1
                        ).lst_price
                        or None,
                    }
                )
            # Create the invoice
            invoice_vals = {
                "partner_id": partner.id,
                "type": "out_invoice",
                "invoice_date": fields.Date.today(),
                "narration": f"Debt collection for traffic infraction {infraction.name}",
                "invoice_line_ids": inv_line_values,
                "invoice_origin": infraction.name,
                "invoice_payment_term_id": invoice_payment_term_id,  # 30, #boleto d+7 hardcode
                "auto_post": True,
                "payment_journal_id": payment_journal_id,  # 18, #banco inter hardcode
                "l10n_br_edoc_policy": None,
                "ref": "Multa de Transito",
            }

            # Create the invoice and post it
            invoice = account_move_obj.create(invoice_vals)
            # invoice.action_post()
            # Optionally, you can link the invoice to
            # the traffic infraction for future reference
            infraction.write({"out_invoice_ids": invoice.id})

            records = infraction.filtered(lambda rec: rec.state in ["invoice"])
            records.write({"state": "bill"})

            # Return the invoice (or its ID) if needed
            return invoice

    def get_orgao_autuador_description(self, code):
        orgao_autuador = self.env["traffic_infractions.orgao_autuador"].search(
            [("code", "=", code)]
        )
        if orgao_autuador:
            return orgao_autuador.description
        else:
            return None

    def _get_partner_orgao_autuador(self):
        # Get the gov authoritys's partner record
        partner_name = self.get_orgao_autuador_description(self.codigo_orgao_autuador)
        partner = self.env["res.partner"].search([("name", "=", partner_name)])
        # If the gov authoritys's is not found, create a new one
        if not partner:
            partner = self.env["res.partner"].create(
                {
                    "name": partner_name,
                    "company_type": "company",
                }
            )
        return partner

    def create_bill(self):
        account_move_obj = self.env["account.move"]
        product_obj = self.env["product.product"]

        for infraction in self:
            if not infraction.driver_id:
                raise UserError(
                    _("There is no driver assigned for this traffic infraction.")
                )
            if not infraction.data_vencimento:
                raise UserError(
                    _("There is no due date assigned for this traffic infraction.")
                )

            # Get the gov authoritys's partner record
            partner = self._get_partner_orgao_autuador()

            # Search for the product based on the product name structure
            product_name = f"[MLT{infraction.codigo_infracao} Multa CTB]"
            product = product_obj.search([("name", "=", product_name)], limit=1)

            # If the product is not found, create a new one
            if not product:
                product = product_obj.create(
                    {
                        "name": product_name,
                        "type": "service",
                        "sale_ok": True,
                        "purchase_ok": True,
                        "invoice_policy": "order",
                    }
                )

            inv_line_values = {
                "product_id": product.id or False,
                "name": f"{infraction.descricao_infracao} \
                    Chave da Infracao: {infraction.chave_infracao}"
                or None,
                "price_unit": infraction.valor_multa or None,
                "quantity": 1,
                "account_id": self.env["account.account"].search(
                    [("name", "=", "Multas de Transito de Terceiros")], limit=1
                ),
            }
            # Create the invoice
            invoice_vals = {
                "partner_id": partner.id,
                # orgao autuador: https://tinyurl.com/5n6ha8b6
                "type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "narration": f"Payment bill for for traffic \
                    infraction {infraction.name} [{infraction.vehicle_id.tax_id}]",
                "invoice_line_ids": [(0, 0, inv_line_values)],
                "invoice_origin": self.name,
                "auto_post": True,
                "l10n_br_edoc_policy": None,
                "invoice_date_due": infraction.data_vencimento,
                "ref": infraction.name,
            }

            # Create the invoice and post it
            invoice = account_move_obj.create(invoice_vals)
            # invoice.action_post()
            # Optionally, you can link the invoice to
            # the traffic infraction for future reference
            infraction.write({"in_invoice_ids": invoice.id})

            records = infraction.filtered(lambda rec: rec.state in ["bill"])
            records.write({"state": "processed"})

            # Return the invoice (or its ID) if needed
            return invoice

    def update_traffic_infractions(self):
        for rec in self:
            rec.vehicle_id.fetch_traffic_infractions()

    def _batch_create_invoice(self):
        _logger.info("Starting _cron_get_orgao_autuador_description...")
        _logger.info(f"infraction: {self}")
        for infraction in self.search(
            [("state", "=", "invoice"), ("driver_id", "!=", False)]
        ):
            _logger.info(f"infraction: {infraction.name}")
            infraction.create_invoice()

    def _batch_create_bill(self):
        _logger.info("Starting _cron_get_orgao_autuador_description...")

        for infraction in self.search(
            [("state", "=", "bill"), ("data_vencimento", "!=", False)]
        ):
            _logger.info(f"infraction: {infraction.name}")
            infraction.create_bill()

    def process_infraction_json(self, data, vehicle):
        def timestamp_to_datetime(timestamp):
            timestamp = (
                timestamp / 1000
            )  # Divide by 1000 to convert from milliseconds to seconds

            # Create a datetime object from the timestamp in UTC
            dt = datetime.datetime.utcfromtimestamp(timestamp)

            # Create a timedelta object to represent the UTC-3 offset (3 hours behind UTC)
            utc_offset = datetime.timedelta(hours=3)

            # Subtract the UTC-3 offset from the datetime object
            dt -= utc_offset

            return dt

        if data:
            for infraction_data in data["multas"]:
                infraction_values = {
                    "vehicle_id": vehicle.id,
                    "chave_infracao": infraction_data.get("chaveInfracao", False),
                    "codigo_infracao": infraction_data.get("codigoInfracao", False),
                    "codigo_orgao_autuador": infraction_data.get(
                        "codigoOrgaoAutuador", False
                    ),
                    "data_hora_infracao": timestamp_to_datetime(
                        infraction_data["dataHoraInfracao"]
                    )
                    if "dataHoraInfracao" in infraction_data
                    else False,
                    "data_registro_pagamento": infraction_data.get(
                        "dataRegistroPagamento", False
                    ),
                    "data_vencimento": infraction_data.get("dataVencimento", False),
                    "descricao_infracao": infraction_data.get(
                        "descricaoInfracao", False
                    ),
                    "numero_auto_infracao": infraction_data.get(
                        "numeroAutoInfracao", False
                    ),
                    "numero_identificacao_proprietario": infraction_data.get(
                        "numeroIdentificacaoProprietario", False
                    ),
                    "permite_boleto_sne": infraction_data.get(
                        "permiteBoletoSne", False
                    ),
                    "placa": infraction_data.get("placa", False),
                    "situacao": infraction_data.get("situacao", False),
                    "valor_multa": infraction_data.get("valorMulta", False),
                    "driver_id": vehicle.get_driver_on_date(
                        vehicle.id,
                        timestamp_to_datetime(infraction_data["dataHoraInfracao"]),
                    ).id,
                }

                infraction = vehicle.traffic_infractions_ids.search(
                    [("chave_infracao", "=", infraction_data["chaveInfracao"])], limit=1
                )
                if infraction:
                    infraction.write(infraction_values)
                else:
                    vehicle.traffic_infractions_ids.create(infraction_values)


class TrafficInfractionTimeline(models.Model):
    _name = "fleet.vehicle.traffic_infractions.timeline"
    _description = "Traffic Infractions Timeline"

    infraction_id = fields.Many2one(
        "fleet.vehicle.traffic_infractions", string="Traffic Infractions"
    )
    id = fields.Integer("ID")
    titulo = fields.Char("Título")
    descricao = fields.Char("Descrição")
    data = fields.Date("Data")
    status = fields.Integer("Status")
