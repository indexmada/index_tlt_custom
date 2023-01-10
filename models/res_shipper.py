# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.modules import get_module_resource


class ResShipper(models.Model):
    _name = "res.shipper"
    _description = "Shippers"
    
    name = fields.Char(string="Nom", required=True)
    image = fields.Binary(string="Image")
    street = fields.Char(string="Adresse 1")
    street2 = fields.Char(string="Adresse 2")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Téléphone")
    country_id = fields.Many2one(string="Pays", comodel_name="res.country")

    @api.model
    def create(self, vals):
    	if not vals.get('image'):
    		vals['image'] = self._get_default_image()
    	return super(ResShipper, self).create(vals)

    @api.model
    def _get_default_image(self):

        colorize, img_path, image = False, False, False

        if not image :
            img_path = get_module_resource('base', 'static/src/img', 'avatar.png')
            colorize = True

        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
        if image and colorize:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))