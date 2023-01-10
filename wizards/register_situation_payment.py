# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class RegisterSituationPayment(models.TransientModel):

    _name = 'register.situation.payment'
    _description = 'Enregistrer un paiement pour la situation'

    name = fields.Char(string="Nom")
    state_form_id = fields.Many2one(string="Situation", comodel_name="state.form")
    journal_id = fields.Many2one(string=u"Méthode de paiement", comodel_name="account.journal", domain=[('type', 'in', ('bank', 'cash'))])
    payment_date = fields.Date(string=u"Date de règlement", default=fields.Date.context_today, required=True)
    amount = fields.Monetary(string="Montant du paiement", required=True, readonly=True)
    currency_id = fields.Many2one(string="Devise", comodel_name="res.currency")

    @api.multi
    def post(self):
        if not self.journal_id:
            raise exceptions.ValidationError(_("Veuillez renseigner le méthode de paiement"))
        state_form = self.state_form_id
        # Create Customer Payment and POST it
        vals = {'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': state_form.partner_id.id,
                'journal_id': self.journal_id.id,
                'amount': self.amount,
                'currency_id': self.journal_id.currency_id.id or self.currency_id.id,
                'payment_date': self.payment_date,
                'payment_method_id': self.journal_id.inbound_payment_method_ids[:1].id,
                'communication': self.name
                }
        payment = self.env['account.payment'].create(vals)
        payment.post()
        state_form.payment_ids = [(6, 0, payment.ids)]
        state_form.state = 'confirmed'

    @api.multi
    def validate(self):
        self.state_form_id.state = 'confirmed'