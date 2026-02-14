from odoo import api, fields, models


class MedicalStudyRequest(models.Model):
    _name = 'medical.study.request'
    _description = 'Solicitud de Estudio'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    order_id = fields.Many2one(
        'medical.examination.order', string='Orden', required=True,
        ondelete='cascade',
    )
    study_type_id = fields.Many2one(
        'medical.study.type', string='Tipo de Estudio', required=True,
    )

    # Profesional asignado (técnico que realiza el estudio)
    practitioner_id = fields.Many2one(
        'medical.practitioner', string='Profesional',
        domain="[('specialty_id', '=', specialty_id)]",
    )
    # Por qué store=True: permite filtrar vistas por especialidad del usuario
    specialty_id = fields.Many2one(
        related='study_type_id.specialty_id', store=True, string='Especialidad',
    )

    # Resultado (One2many inverso)
    result_ids = fields.One2many(
        'medical.study.result', 'request_id', string='Resultados',
    )

    # Estado
    state = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('validado', 'Validado'),
    ], default='pendiente', tracking=True, string='Estado')

    # Datos de la orden (stored para vistas filtradas por técnico)
    patient_id = fields.Many2one(
        related='order_id.patient_id', store=True, string='Paciente',
    )
    date = fields.Date(related='order_id.date', store=True, string='Fecha')

    def action_start(self):
        """Técnico inicia el estudio."""
        for request in self:
            request.state = 'en_proceso'
            # Pasar orden a 'en proceso' si está en 'confirmado'
            if request.order_id.state == 'confirmed':
                request.order_id.action_start()

    def action_complete(self):
        """Técnico marca el estudio como completado."""
        for request in self:
            request.state = 'completado'
            # Verificar si todos los estudios de la orden están completos
            request.order_id._check_studies_complete()

    def action_validate(self):
        """Auditor valida el estudio."""
        for request in self:
            request.state = 'validado'

    @api.model_create_multi
    def create(self, vals_list):
        """Al crear, copiar parámetros del tipo de estudio como líneas de resultado."""
        requests = super().create(vals_list)
        for request in requests:
            # Crear resultado con líneas basadas en los parámetros del tipo
            if request.study_type_id.parameter_ids:
                result_lines = []
                for param in request.study_type_id.parameter_ids:
                    result_lines.append((0, 0, {
                        'parameter': param.parameter,
                        'unit': param.unit,
                        'reference_min': param.reference_min,
                        'reference_max': param.reference_max,
                    }))
                self.env['medical.study.result'].create({
                    'request_id': request.id,
                    'result_line_ids': result_lines,
                })
        return requests
