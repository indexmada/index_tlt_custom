# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class StateForm(models.Model):
    _name = "state.form"
    _description = "Feuille de situation"

    name = fields.Char(string=u"Référence", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    obs = fields.Char(string="OBS")
    transit_id = fields.Many2one(string=u"Réf Manifeste", comodel_name="transit.management")
    transit_line_id = fields.Many2one(string=u"Réf Ligne Manifeste", comodel_name="transit.management.line")
    dossier_number = fields.Char(string=u"N° Dossier")
    partner_id = fields.Many2one(string="Client", comodel_name="res.partner")
    merchandise = fields.Char(string="Nature")
    state = fields.Selection(string="Etat", selection=[('new', 'Nouveau'), ('confirmed', u'Validée')], default="new")
    payment_ids = fields.Many2many(string="Paiements", comodel_name="account.payment", copy=False)
    line_ids = fields.One2many(string="Ligne de la Feuille de situation",
                               comodel_name="state.form.line",
                               inverse_name="state_form_id",
                               copy=True)
    currency_id = fields.Many2one(string="Devise",
                                  comodel_name="res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    amount_total = fields.Monetary(string="Montant Total", compute="compute_amount")


    @api.onchange('transit_id')
    def _onchange_transit_id(self):
        res = {}
        if self.transit_id:
            res['domain'] = {'transit_line_id': [('transit_id', '=', self.transit_id.id)]}
        else:
            self.transit_line_id = False
        return res

    @api.onchange('transit_line_id')
    def _onchange_transit_line_id(self):
        self.merchandise = self.transit_line_id.description
        self.partner_id = self.transit_line_id.cnee

    @api.depends('line_ids')
    def compute_amount(self):
        self.amount_total = sum(self.line_ids.mapped('amount'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('state.form') or _('New')
        return super(StateForm, self).create(vals)

    @api.multi
    def validate(self):
        ctx = self._context.copy()
        ctx.update({'default_state_form_id': self.id,
                    'default_name': self.name,
                    'default_amount': self.amount_total,
                    'default_currency_id': self.currency_id.id,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enregistrer un paiement pour la situation',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'register.situation.payment',
            'views': [(self.env.ref('transit_operation_management.view_register_situation_payment_form').id, 'form')],
            'target': 'new',
            'context': ctx
        }

    @api.multi
    def action_view_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Paiement',
            'view_mode': 'form',
            'view_type': 'tree,form',
            'res_id': self.payment_ids[:1].id,
            'res_model': 'account.payment',
            'views': [(self.env.ref('account.view_account_payment_form').id, 'form')],
            'target': 'current',
        }

    @api.multi
    def action_cancel(self):
        self.state = 'new'

class StateFormLine(models.Model):
    _name = "state.form.line"
    _description = "Ligne de Feuille de situation"

    date = fields.Date(string="Date", copy=False, default=fields.Datetime.now)
    situation = fields.Char(string="Situation")
    amount = fields.Monetary(string=u"Provision Reçue")    
    currency_id = fields.Many2one(string="Devise",
                                  comodel_name="res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    partner_id = fields.Char(string=u"Obsérvation")
    shipping_address = fields.Char(string="Lieu de Livraison")
    state_form_id = fields.Many2one(string="Situation Correspondant", comodel_name="state.form")
    user_id = fields.Many2one(string="Utilisateur", comodel_name="res.users", default=lambda self:self.env.user)

    @api.model
    def fix_user_id(self):
        state_form_lines = self.search([('user_id', '!=', self.create_uid.id)])
        for rec in state_form_lines:
            rec.user_id = rec.create_uid
