from odoo import api, fields, models


class MedicalExaminationOrder(models.Model):
    _name = 'medical.examination.order'
    _description = 'Orden de Examen Médico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char('Número', readonly=True, default='Nuevo', copy=False)

    # --- Relaciones principales ---
    patient_id = fields.Many2one(
        'medical.patient', string='Paciente', required=True, tracking=True,
    )
    employer_id = fields.Many2one(
        'res.partner', string='Empresa Empleadora',
        domain=[('is_company', '=', True)], required=True, tracking=True,
    )
    template_id = fields.Many2one(
        'medical.examination.template', string='Tipo de Examen',
        required=True, tracking=True,
    )

    # --- Datos del examen ---
    examination_type = fields.Selection([
        ('preocupacional', 'Preocupacional'),
        ('periodico', 'Periódico'),
        ('transferencia', 'Previo a Transferencia'),
        ('reintegro', 'Posterior a Ausencia'),
        ('egreso', 'Previo a Terminación'),
    ], string='Tipo', default='preocupacional', required=True)
    date = fields.Date('Fecha del Turno', required=True, tracking=True)
    job_position = fields.Char('Puesto de Trabajo')

    # --- Estudios generados ---
    study_request_ids = fields.One2many(
        'medical.study.request', 'order_id', string='Estudios Solicitados',
    )

    # --- Certificado ---
    certificate_ids = fields.One2many(
        'medical.certificate', 'order_id', string='Certificados',
    )

    # --- Estado ---
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En Proceso'),
        ('studies_complete', 'Estudios Completos'),
        ('certified', 'Certificado Emitido'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ], default='draft', tracking=True, string='Estado')

    # --- Progreso ---
    studies_total = fields.Integer(compute='_compute_progress', string='Total Estudios')
    studies_completed = fields.Integer(compute='_compute_progress', string='Estudios Completados')
    progress = fields.Float(compute='_compute_progress', string='Progreso (%)')

    # --- Facturación ---
    invoice_id = fields.Many2one('account.move', string='Factura')

    # Por qué onchange: al seleccionar paciente, autocompletar empresa y puesto
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            self.employer_id = self.patient_id.employer_id
            self.job_position = self.patient_id.job_position

    # Por qué: al confirmar se generan study.request automáticamente
    # según el template, evitando carga manual repetitiva
    def action_confirm(self):
        for order in self:
            if order.name == 'Nuevo':
                order.name = self.env['ir.sequence'].next_by_code(
                    'medical.examination.order'
                ) or 'Nuevo'
            # Generar solicitudes de estudio según plantilla
            for study_type in order.template_id.study_type_ids:
                self.env['medical.study.request'].create({
                    'order_id': order.id,
                    'study_type_id': study_type.id,
                })
            order.state = 'confirmed'

    def action_start(self):
        for order in self:
            order.state = 'in_progress'

    def action_cancel(self):
        for order in self:
            order.state = 'cancelled'

    def action_draft(self):
        for order in self:
            order.state = 'draft'

    # Por qué depends en study_request_ids.state: recalcula progreso
    # cada vez que un técnico completa un estudio
    @api.depends('study_request_ids.state')
    def _compute_progress(self):
        for order in self:
            total = len(order.study_request_ids)
            completed = len(order.study_request_ids.filtered(
                lambda r: r.state in ('completado', 'validado')
            ))
            order.studies_total = total
            order.studies_completed = completed
            order.progress = (completed / total * 100) if total else 0

    def _check_studies_complete(self):
        """Auto-transición cuando todos los estudios están completos."""
        for order in self:
            if (order.state == 'in_progress'
                    and order.studies_total
                    and order.studies_completed == order.studies_total):
                order.state = 'studies_complete'
                # Notificar al médico auditor via actividad
                order.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary='Todos los estudios completos - Emitir certificado',
                )
