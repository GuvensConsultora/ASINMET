from odoo import fields, models


class MedicalExaminationTemplate(models.Model):
    _name = 'medical.examination.template'
    _description = 'Plantilla de Examen'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    # Ej: "Preocupacional Estándar", "Preocupacional Minería"

    # Por qué Many2many: un tipo de estudio puede estar en varias plantillas
    # y una plantilla agrupa varios tipos de estudio
    study_type_ids = fields.Many2many(
        'medical.study.type', string='Estudios Incluidos',
    )

    estimated_duration = fields.Float('Duración Estimada (horas)', default=2.0)
    price = fields.Float('Precio Base')
    active = fields.Boolean(default=True)
    study_count = fields.Integer(
        compute='_compute_study_count', string='Cant. Estudios',
    )

    def _compute_study_count(self):
        for template in self:
            template.study_count = len(template.study_type_ids)
