from odoo import fields, models


class MedicalStudyType(models.Model):
    _name = 'medical.study.type'
    _description = 'Tipo de Estudio Médico'
    _order = 'name'

    name = fields.Char('Nombre', required=True)  # Ej: "Electrocardiograma"
    code = fields.Char('Código', required=True)   # Ej: "ECG"
    specialty_id = fields.Many2one('medical.specialty', string='Especialidad')

    # Parámetros esperados (template de resultado)
    parameter_ids = fields.One2many(
        'medical.study.type.line', 'study_type_id', string='Parámetros',
    )

    # Configuración
    requires_attachment = fields.Boolean('Requiere Adjunto (PDF/Imagen)', default=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'El código de tipo de estudio debe ser único.'),
    ]


class MedicalStudyTypeLine(models.Model):
    _name = 'medical.study.type.line'
    _description = 'Parámetro de Tipo de Estudio'
    _order = 'sequence, id'

    study_type_id = fields.Many2one(
        'medical.study.type', string='Tipo de Estudio',
        required=True, ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    parameter = fields.Char('Parámetro', required=True)  # Ej: "Glucemia"
    unit = fields.Char('Unidad')                          # Ej: "g/l"
    reference_min = fields.Float('Ref. Mínimo')           # Ej: 0.70
    reference_max = fields.Float('Ref. Máximo')           # Ej: 1.10
