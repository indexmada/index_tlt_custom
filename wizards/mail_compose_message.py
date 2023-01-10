# -*- coding: utf-8 -*-

from odoo import api, models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        ctx = self._context
        template_change_date = self.env['ir.model.data'].get_object_reference('transit_operation_management', 'mail_template_avis_changement_date')[1]

        if ctx.get('default_model') == 'transit.management.line' and ctx.get('transit_id'):
            transit = self.env['transit.management'].browse([ctx['transit_id']])
            # Changement de dates
            if ctx.get('default_template_id') == template_change_date and len(transit.line_to_mail_ids) <= 1:
                transit.is_departure_date_changed = False
                transit.is_arrival_date_changed = False

            # Afficher un à un les popup composition de message pour chaque ligne
            if len(transit.line_to_mail_ids) > 1 and ctx.get('default_res_id'):
                super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
                transit.line_to_mail_ids = [(3, ctx.get('default_res_id'))]
                transit_select_mail = self.env['wiz.select.mail'].create(
                    {'transit_id': transit.id,
                     'template_id': ctx.get('default_template_id'),
                     'line_to_mail_ids': [(6,0,transit.line_to_mail_ids.ids)]})
                return transit_select_mail.validate()

        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
