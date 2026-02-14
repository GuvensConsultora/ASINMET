from odoo import fields, models


class MedicalPractitioner(models.Model):
    _name = 'medical.practitioner'
    _description = 'Profesional Médico'
    # Por qué _inherits: el profesional es un contacto de Odoo,
    # puede ser usuario de portal sin licencia paga
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name'

    partner_id = fields.Many2one(
        'res.partner', string='Contacto', required=True, ondelete='cascade',
    )

    license_number = fields.Char('Matrícula Profesional')
    specialty_id = fields.Many2one('medical.specialty', string='Especialidad')

    # Firma electrónica (imagen) — Etapa 1: firma simple con audit trail
    signature = fields.Binary('Firma')

    # --- Relaciones inversas ---
    study_request_ids = fields.One2many(
        'medical.study.request', 'practitioner_id',
        string='Estudios Asignados',
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('license_uniq', 'unique(license_number)',
         'Ya existe un profesional con esa matrícula.'),
    ]
