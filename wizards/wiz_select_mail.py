# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging
_logger = logging.getLogger(__name__)


class WizSelectMail(models.TransientModel):
    _name = 'wiz.select.mail'
    _description = 'Selection de mail'

    @api.model
    def _get_template_id_domain(self):
        domain = [('model_id.model', '=', 'transit.management')]
        if not self._context.get('date_changed'):
            res = self.env['ir.model.data'].get_object_reference('transit_operation_management', 'mail_template_avis_changement_date')
            print (res)
            domain.append(('id', '!=', res[1]))
        return str(domain)

    template_id = fields.Many2one(string=u"Modèle de mail", comodel_name="mail.template", domain=_get_template_id_domain, required=True)
    transit_id = fields.Many2one(string="Manifeste", comodel_name="transit.management")
    line_to_mail_ids = fields.Many2many(string=u"Ligne à envoyer par mail", comodel_name="transit.management.line", help=u"Liste des lignes restantes à envoyer par mail")

    @api.multi
    def validate(self):
        '''
        This function opens a window to compose an email, with the mail template selected
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']

        line = self.line_to_mail_ids[:1] #Take the first element and avoid index error if list empty
        self.template_id.email_to = line.email
        template_id = self.template_id.id
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        ctx = self._context.copy()
        ctx.update({
            'default_model': 'transit.management.line',
            'default_res_id': line.id,
            'transit_id': self.transit_id.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'wiz_select_mail': True,
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
