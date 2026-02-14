from odoo import fields, models


class MedicalCertificate(models.Model):
    _name = 'medical.certificate'
    _description = 'Certificado de Aptitud'
    _inherit = ['mail.thread']
    _order = 'signed_date desc, id desc'

    name = fields.Char('Número', readonly=True, default='Nuevo', copy=False)

    order_id = fields.Many2one(
        'medical.examination.order', string='Orden de Examen', required=True,
    )
    patient_id = fields.Many2one(
        related='order_id.patient_id', store=True, string='Paciente',
    )
    employer_id = fields.Many2one(
        related='order_id.employer_id', store=True, string='Empresa',
    )

    # --- Dictamen (Res. SRT 37/2010) ---
    dictamen = fields.Selection([
        ('apto', 'APTO'),
        ('no_apto', 'NO APTO'),
        ('apto_obs', 'APTO CON OBSERVACIONES'),
    ], string='Dictamen', required=True, tracking=True)
    observations = fields.Text('Observaciones')

    # Médico responsable (auditor que emite el certificado)
    practitioner_id = fields.Many2one(
        'medical.practitioner', string='Médico Responsable', required=True,
    )

    # --- Estado y firma ---
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('signed', 'Firmado'),
        ('delivered', 'Entregado'),
    ], default='draft', tracking=True, string='Estado')

    signature = fields.Binary('Firma Digital')
    signed_date = fields.Datetime('Fecha de Firma')

    # Por qué: al firmar se estampa firma + timestamp + genera PDF
    # Etapa 1: firma electrónica simple (imagen + audit trail)
    def action_sign(self):
        self.ensure_one()
        if self.name == 'Nuevo':
            self.name = self.env['ir.sequence'].next_by_code(
                'medical.certificate'
            ) or 'Nuevo'
        self.signature = self.practitioner_id.signature
        self.signed_date = fields.Datetime.now()
        self.state = 'signed'
        self.order_id.state = 'certified'
        # Log en chatter para audit trail
        self.message_post(
            body=f'Certificado firmado por {self.practitioner_id.name} '
                 f'- Matrícula: {self.practitioner_id.license_number}',
        )

    def action_deliver(self):
        self.ensure_one()
        self.state = 'delivered'
        self.order_id.state = 'delivered'
