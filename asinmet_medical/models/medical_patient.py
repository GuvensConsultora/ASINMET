from odoo import api, fields, models


class MedicalPatient(models.Model):
    _name = 'medical.patient'
    _description = 'Paciente / Trabajador'
    # Por qué _inherits: delega campos de res.partner sin duplicar tabla,
    # permite usar el paciente como contacto estándar de Odoo
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name'

    partner_id = fields.Many2one(
        'res.partner', string='Contacto', required=True, ondelete='cascade',
    )

    # --- Datos personales ---
    dni = fields.Char('DNI', size=10, index=True)
    birth_date = fields.Date('Fecha de Nacimiento')
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
    ], string='Género')
    blood_type = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'),
        ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'),
        ('o+', 'O+'), ('o-', 'O-'),
    ], string='Grupo Sanguíneo')

    # --- Datos laborales ---
    # Por qué employer_id separado: el paciente puede cambiar de empresa
    # y mantener historial médico longitudinal
    employer_id = fields.Many2one(
        'res.partner', string='Empresa Empleadora',
        domain=[('is_company', '=', True)],
    )
    job_position = fields.Char('Puesto de Trabajo')

    # --- Historial ---
    examination_order_ids = fields.One2many(
        'medical.examination.order', 'patient_id',
        string='Historial de Exámenes',
    )
    examination_count = fields.Integer(
        compute='_compute_examination_count', string='Exámenes',
    )

    @api.depends('examination_order_ids')
    def _compute_examination_count(self):
        for patient in self:
            patient.examination_count = len(patient.examination_order_ids)

    _sql_constraints = [
        ('dni_uniq', 'unique(dni)', 'Ya existe un paciente con ese DNI.'),
    ]
