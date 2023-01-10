# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """Corriger les IGG admin"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    state_form = env['state.form.line']
    state_form.fix_user_id()