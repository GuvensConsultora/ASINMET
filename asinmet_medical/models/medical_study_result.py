from odoo import api, fields, models


class MedicalStudyResult(models.Model):
    _name = 'medical.study.result'
    _description = 'Resultado de Estudio'
    _inherit = ['mail.thread']

    request_id = fields.Many2one(
        'medical.study.request', string='Solicitud', ondelete='cascade',
    )
    study_type_id = fields.Many2one(
        related='request_id.study_type_id', store=True, string='Tipo de Estudio',
    )
    practitioner_id = fields.Many2one(
        'medical.practitioner', string='Realizado por',
    )

    # Valores medidos
    result_line_ids = fields.One2many(
        'medical.study.result.line', 'result_id', string='Parámetros',
    )

    # Archivos adjuntos (PDF del equipo, imagen Rx, etc.)
    attachment_ids = fields.Many2many('ir.attachment', string='Archivos Adjuntos')

    # Conclusión del profesional
    conclusion = fields.Text('Conclusión')
    aptitude = fields.Selection([
        ('normal', 'Normal / Sin Particularidades'),
        ('anormal', 'Anormal'),
        ('observaciones', 'Con Observaciones'),
    ], string='Resultado')

    date = fields.Datetime('Fecha/Hora del Estudio', default=fields.Datetime.now)

    # Firma del profesional
    signed = fields.Boolean('Firmado')
    signature = fields.Binary('Firma')
    signed_date = fields.Datetime('Fecha de Firma')


class MedicalStudyResultLine(models.Model):
    _name = 'medical.study.result.line'
    _description = 'Línea de Resultado (Observación FHIR)'
    _order = 'sequence, id'

    result_id = fields.Many2one(
        'medical.study.result', string='Resultado',
        required=True, ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    parameter = fields.Char('Parámetro', required=True)
    value = fields.Char('Valor')
    unit = fields.Char('Unidad')
    reference_min = fields.Float('Ref. Mínimo')
    reference_max = fields.Float('Ref. Máximo')

    # Por qué compute + store: detecta automáticamente valores fuera de rango
    # para que el auditor vea alertas visuales sin revisar cada número
    is_abnormal = fields.Boolean(
        'Fuera de Rango', compute='_compute_abnormal', store=True,
    )

    @api.depends('value', 'reference_min', 'reference_max')
    def _compute_abnormal(self):
        for line in self:
            try:
                val = float(line.value) if line.value else 0.0
                line.is_abnormal = bool(
                    (line.reference_min and val < line.reference_min)
                    or (line.reference_max and val > line.reference_max)
                )
            except (ValueError, TypeError):
                line.is_abnormal = False
