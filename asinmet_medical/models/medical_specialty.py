from odoo import fields, models


class MedicalSpecialty(models.Model):
    _name = 'medical.specialty'
    _description = 'Especialidad Médica'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código', required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'El código de especialidad debe ser único.'),
    ]
