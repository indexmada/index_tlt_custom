# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class TransitManagement(models.Model):
    _name = "transit.management"
    _inherit = ["mail.thread"]
    _description = "Manifeste"
    
    name = fields.Char(string=u"Référence", required=True, copy=False, default=lambda self: _('New'), readonly=True)
    ref_groupage = fields.Char(string=u'Réf Groupage', index=True)
    groupage = fields.Char(string="Groupage")
    ref_shipping = fields.Char(string=u"Réf Shipping")
    vessel = fields.Char(string="Vessel")
    travel = fields.Char(string="Voyage")
    loading_port = fields.Char(string="Port of Loading")
    discharge_port = fields.Char(string="Port of Discharge")
    
    security_key = fields.Char(string=u"Clé de securite")
    operator = fields.Many2one(comodel_name="res.users", string=u"Opérateur")
    departure_date = fields.Date(string=u"Date de départ")
    arrival_date = fields.Date(string=u"Date d'arrivée")
    
    line_ids = fields.One2many(comodel_name="transit.management.line", inverse_name="transit_id", string=u"Ligne de MANIFESTE", copy=True)
    shipper_id = fields.Many2one(string=u"Shipper", comodel_name="res.shipper", related="line_ids.shipper_id")
    cnee = fields.Many2one(string=u"CNEE sur FIATA", comodel_name="res.partner", related="line_ids.cnee")
    currency_id = fields.Many2one(comodel_name="res.currency", string=u"Valeurs Declarées", related="line_ids.currency_id", store=True)
    
    state = fields.Selection(string="Etat", selection=[('new', 'Nouveau'), ('confirmed', u'Validé')], default="new")

    last_departure_date = fields.Date(string=u"Dernière date départ enregistrée")
    last_arrival_date = fields.Date(string=u"Dernière date d'arrivée enregistrée")
    is_departure_date_changed = fields.Boolean(string=u"Date de départ modifiée ?")
    is_arrival_date_changed = fields.Boolean(string=u"Date d'arrivée modifiée ?")
    line_to_mail_ids = fields.Many2many(string=u"Ligne à envoyer par mail", comodel_name="transit.management.line", help=u"Utilisé pour avoir les lignes restantes à envoyer par mail")

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        self.line_to_mail_ids = self.line_ids

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('transit.management') or _('New')
        return super(TransitManagement, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('departure_date'):
            self.last_departure_date = self.departure_date
            self.is_departure_date_changed = True
        if vals.get('arrival_date'):
            self.last_arrival_date = self.arrival_date
            self.is_arrival_date_changed = True
        return super(TransitManagement, self).write(vals)

    @api.multi
    def validate(self):
        self.state = 'confirmed'

    @api.multi
    def action_cancel(self):
        self.state = 'new'

    @api.multi
    def wiz_select_mail(self):
        # First of all, fullfill line_to_mail_ids
        self.line_to_mail_ids = self.line_ids

        view = self.env.ref('transit_operation_management.view_wiz_select_mail_form')
        ctx = self._context.copy()
        ctx['date_changed'] = True if (self.is_arrival_date_changed or self.is_departure_date_changed) else False
        ctx['default_transit_id'] = self.id
        ctx['default_line_to_mail_ids'] = self.line_to_mail_ids.ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Selection type de mail',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.select.mail',
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def send_mail_date_changed(self):
        self.ensure_one()

        # First of all, fullfill line_to_mail_ids
        self.line_to_mail_ids = self.line_ids
        ir_model_data = self.env['ir.model.data']

        line = self.line_to_mail_ids[:1] #Take the first element and avoid index error if list empty
        try:
            template_id = ir_model_data.xmlid_to_object('transit_operation_management.mail_template_avis_changement_date')
            template_id.email_to = line.email
        except:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        ctx = dict()
        ctx.update({
            'default_model': 'transit.management.line',
            'default_res_id': line.id,
            'transit_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class TransitManagementLine(models.Model):
    _name = "transit.management.line"
    _inherit = ["mail.thread"]
    _description = "Ligne de Manifeste"

    name = fields.Char(string=u"Référence", required=True)
    shipper_id = fields.Many2one(string=u"Shipper", comodel_name="res.shipper")
    cnee = fields.Many2one(string=u"CNEE sur FIATA", comodel_name="res.partner", domain=[('customer', '=', True)])
    colis_number = fields.Float(string=u"Nbre de Colis")
    packaging = fields.Char(string=u"Emballage")
    description = fields.Char(string=u"Descriptif des Marchandises")
    currency_id = fields.Many2one(comodel_name="res.currency", string="Devise")
    amount = fields.Float(string=u"Valeurs Declarées")
    weight = fields.Float(string=u"Poids")
    m3 = fields.Float(string=u"M3")
    phone = fields.Char(string=u"Téléphone")
    email = fields.Char(string=u"Email")
    transit_id = fields.Many2one(comodel_name="transit.management", string=u"Transit")
    company_id = fields.Many2one(string=u"Société", comodel_name="res.company", default=lambda self:self.env.user.company_id.id)

    @api.onchange('cnee')
    def _onchange_cnee(self):
        self.phone = self.cnee.phone
        self.email = self.cnee.email

    @api.multi
    def print_fcr_original(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'transit_operation_management.fcr_report')

    @api.multi
    def print_fcr_duplicatas(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'transit_operation_management.fcr_report_duplicatas')

    @api.multi
    def print_bad(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'transit_operation_management.bad_report')