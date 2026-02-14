# Diseño Módulo `asinmet_medical` - Exámenes Preocupacionales
## Odoo 19 Enterprise

---

## 1. Investigación Internacional - Estado del Arte

### 1.1 Soluciones Evaluadas

| Solución | Plataforma | Salud Ocupacional | Odoo 19 | Veredicto |
|----------|-----------|-------------------|---------|-----------|
| **OCA vertical-medical** | Odoo | No nativo | Inactivo desde v14 | Base de referencia para modelos |
| **GNU Health** | Tryton (no Odoo) | Sí (`health_occupational`) | No compatible | Referencia de arquitectura |
| **Creu Blanca (tegin)** | Odoo | Parcial | Solo hasta v14 | Mejor referencia FHIR en Odoo |
| **Odoo Apps (Hospital)** | Odoo | No | Variable | Demasiado genérico |
| **OpenMRS** | Java standalone | No | No compatible | Descartado |

### 1.2 Conclusión de la Investigación

**No existe módulo listo** que cubra exámenes preocupacionales con múltiples estudios, múltiples técnicos y firma digital para Odoo 17+.

**Decisión:** Desarrollo a medida tomando como referencia:
- **Nomenclatura HL7 FHIR** para interoperabilidad futura
- **Estructura OCA vertical-medical** para herencia de `res.partner`
- **Workflow GNU Health** para el flujo de salud ocupacional
- **Legislación argentina SRT** para campos obligatorios

### 1.3 GNU Health - Modelo de Referencia

GNU Health (sobre Tryton) es el sistema open source más completo en salud ocupacional. Módulos relevantes:

| Módulo GNU Health | Funcionalidad | Equivalente en nuestro diseño |
|-------------------|---------------|-------------------------------|
| `health` | Pacientes, encuentros | `medical.patient`, `medical.examination.order` |
| `health_occupational` | Riesgos laborales, exámenes ocupacionales | `medical.examination.order` + `medical.study.type` |
| `health_lab` | Laboratorio, muestras, resultados | `medical.study.result` (tipo laboratorio) |
| `health_imaging` | Imágenes (Rx, ECG) | `medical.study.result` (tipo imagen) |
| `health_ophthalmology` | Oftalmología | `medical.study.result` (tipo vista) |
| `health_dentistry` | Odontología | `medical.study.result` (tipo dental) |

### 1.4 HL7 FHIR - Mapeo de Recursos

Modelamos siguiendo FHIR para interoperabilidad futura con obras sociales, SRT y otros sistemas de salud:

| Recurso FHIR | Modelo Odoo | Descripción |
|--------------|-------------|-------------|
| `Patient` | `medical.patient` | Trabajador/paciente |
| `Practitioner` | `medical.practitioner` | Médico, técnico, profesional |
| `Organization` | `res.partner` (empresa) | Empresa empleadora |
| `Encounter` | `medical.examination.order` | Orden de examen (visita) |
| `ServiceRequest` | `medical.study.request` | Solicitud de estudio individual |
| `DiagnosticReport` | `medical.study.result` | Resultado del estudio |
| `Observation` | `medical.study.result.line` | Valor medido individual |
| `Composition` | `medical.certificate` | Certificado final de aptitud |
| `DocumentReference` | `ir.attachment` | Archivos adjuntos (PDF, imágenes) |

### 1.5 Legislación Argentina - Res. SRT 37/2010 y 905/2015

#### Tipos de exámenes obligatorios (Art. 2, Ley 19.587)

| Tipo | Cuándo | Obligatorio |
|------|--------|-------------|
| **Preocupacional** | Antes del ingreso | Sí, siempre |
| **Periódico** | Anual o según riesgo | Sí, según actividad |
| **Previo a transferencia** | Cambio de puesto con nuevos riesgos | Condicional |
| **Posterior a ausencia prolongada** | Reintegro tras licencia | Condicional |
| **Previo a terminación** | Al egreso | Optativo |

#### Estudios mínimos obligatorios (Preocupacional estándar)

| Estudio | Profesional | Resultado |
|---------|-------------|-----------|
| Examen clínico general | Médico laboral | Apto/No apto |
| Análisis de laboratorio | Bioquímico | Valores + interpretación |
| Electrocardiograma (ECG) | Cardiólogo | Normal/Anormal |
| Radiografía de tórax | Radiólogo | Normal/Anormal |
| Examen oftalmológico | Oftalmólogo | Agudeza visual |
| Audiometría | Fonoaudiólogo | Umbral auditivo |
| Examen psicológico | Psicólogo | Apto/No apto |
| Análisis toxicológico | Bioquímico | Positivo/Negativo |

#### Estudios adicionales según riesgo

| Riesgo | Estudios adicionales |
|--------|---------------------|
| Minería/altura | Espirometría, ergometría, EEG |
| Ruido intenso | Audiometría completa |
| Sustancias químicas | Panel toxicológico ampliado |
| Trabajo en altura | ECG de esfuerzo, EEG |
| Conducción de vehículos | EEG, examen psicotécnico |

#### Certificado final - Campos obligatorios

- Datos del trabajador (nombre, DNI, fecha nacimiento, domicilio)
- Datos de la empresa empleadora (razón social, CUIT)
- Puesto de trabajo / tarea a desempeñar
- Listado de estudios realizados con resultado
- Dictamen: APTO / NO APTO / APTO CON OBSERVACIONES
- Observaciones (si aplica)
- Datos del profesional médico responsable (nombre, matrícula)
- Firma y sello del profesional
- Fecha de emisión
- Número de certificado

---

## 2. Arquitectura del Módulo

### 2.1 Nombre técnico
```
asinmet_medical
```

### 2.2 Dependencias
```python
'depends': [
    'base',
    'contacts',
    'calendar',
    'appointment',
    'account',
    'mail',
    'portal',
    'sign',  # Etapa 2
],
```

### 2.3 Diagrama de Modelos

```
res.partner (Odoo nativo)
    ├── medical.patient (hereda res.partner, tipo=paciente)
    ├── medical.practitioner (hereda res.partner, tipo=profesional)
    └── empresa empleadora (res.partner estándar, tipo=empresa)

medical.study.category
    └── Agrupa tipos de estudio (Laboratorio, Cardiología, Imágenes, etc.)

medical.study.type
    └── Define cada tipo de estudio (ECG, Rx Tórax, Hemograma, etc.)
        └── medical.study.type.line (parámetros/valores esperados por estudio)

medical.examination.template
    └── Plantilla de paquete de estudios (Ej: "Preocupacional Minería")
        └── medical.examination.template.line → medical.study.type (M2M)

medical.examination.order  ← MODELO CENTRAL
    ├── patient_id → medical.patient
    ├── employer_id → res.partner (empresa)
    ├── template_id → medical.examination.template
    ├── study_request_ids → [medical.study.request]  (One2many)
    └── certificate_id → medical.certificate

medical.study.request
    ├── order_id → medical.examination.order
    ├── study_type_id → medical.study.type
    ├── practitioner_id → medical.practitioner (técnico/profesional asignado)
    ├── result_id → medical.study.result
    └── state: borrador → en_proceso → completado → validado

medical.study.result
    ├── request_id → medical.study.request
    ├── practitioner_id → medical.practitioner
    ├── result_line_ids → [medical.study.result.line]  (One2many)
    ├── attachment_ids → [ir.attachment]  (archivos PDF/imágenes)
    ├── conclusion: texto libre
    └── aptitude: apto / no_apto / observaciones

medical.study.result.line
    ├── result_id → medical.study.result
    ├── parameter: nombre del parámetro (ej: "Glucemia")
    ├── value: valor obtenido (ej: "0.95")
    ├── unit: unidad (ej: "g/l")
    ├── reference_min / reference_max: rango normal
    └── is_abnormal: boolean computado

medical.certificate
    ├── order_id → medical.examination.order
    ├── patient_id → medical.patient
    ├── employer_id → res.partner
    ├── dictamen: apto / no_apto / apto_con_observaciones
    ├── observations: texto
    ├── practitioner_id → medical.practitioner (médico auditor)
    ├── signature → Binary (firma electrónica)
    ├── signed_date → Datetime
    └── state: borrador → firmado → entregado
```

---

## 3. Modelos Detallados

### 3.1 `medical.patient` (hereda `res.partner`)

```python
class MedicalPatient(models.Model):
    _name = 'medical.patient'
    _description = 'Paciente / Trabajador'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')

    # Datos personales específicos
    dni = fields.Char('DNI', size=10)
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

    # Datos laborales
    employer_id = fields.Many2one('res.partner', 'Empresa Empleadora',
        domain=[('is_company', '=', True)])
    job_position = fields.Char('Puesto de Trabajo')

    # Historial
    examination_order_ids = fields.One2many('medical.examination.order', 'patient_id',
        string='Historial de Exámenes')
    examination_count = fields.Integer(compute='_compute_examination_count')

    # Por qué: permite historial médico longitudinal del trabajador
    # aunque cambie de empresa (rotación típica en metalurgia)
```

### 3.2 `medical.practitioner` (hereda `res.partner`)

```python
class MedicalPractitioner(models.Model):
    _name = 'medical.practitioner'
    _description = 'Profesional Médico'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')

    license_number = fields.Char('Matrícula Profesional')
    specialty_id = fields.Many2one('medical.specialty', 'Especialidad')

    # Firma electrónica
    signature = fields.Binary('Firma')
    signature_date = fields.Date('Firma válida desde')

    # Por qué: el profesional es usuario de portal, no interno
    # Puede firmar desde cualquier lugar sin usuario pago
    portal_user_id = fields.Many2one('res.users', 'Usuario Portal',
        compute='_compute_portal_user', store=True)

    # Estudios asignados pendientes de validación
    pending_result_ids = fields.One2many('medical.study.request', 'practitioner_id',
        domain=[('state', '=', 'completado')],
        string='Resultados Pendientes de Validación')
```

### 3.3 `medical.study.type`

```python
class MedicalStudyType(models.Model):
    _name = 'medical.study.type'
    _description = 'Tipo de Estudio Médico'

    name = fields.Char('Nombre', required=True)  # Ej: "Electrocardiograma"
    code = fields.Char('Código', required=True)   # Ej: "ECG"
    category_id = fields.Many2one('medical.study.category', 'Categoría')

    # Especialidad requerida para realizar este estudio
    specialty_id = fields.Many2one('medical.specialty', 'Especialidad')

    # Parámetros esperados (template de resultado)
    parameter_ids = fields.One2many('medical.study.type.line', 'study_type_id',
        string='Parámetros')

    # Configuración
    requires_attachment = fields.Boolean('Requiere Adjunto (PDF/Imagen)', default=True)
    has_api = fields.Boolean('Equipo con API', default=False)
    api_endpoint = fields.Char('Endpoint API del Equipo')

    # Por qué: has_api permite integración futura con equipos médicos
    # que tienen API (ECG digital, analizador de sangre, etc.)
    # Sin API se carga manualmente o se adjunta PDF
```

### 3.4 `medical.examination.template`

```python
class MedicalExaminationTemplate(models.Model):
    _name = 'medical.examination.template'
    _description = 'Plantilla de Examen'

    name = fields.Char('Nombre', required=True)
    # Ej: "Preocupacional Estándar", "Preocupacional Minería",
    #     "Preocupacional Alimentos", "Postocupacional"

    study_type_ids = fields.Many2many('medical.study.type',
        string='Estudios Incluidos')

    # Por qué: distintas empresas requieren distintos paquetes
    # Minera = más estudios (ergometría, EEG) = más ingresos
    # Restaurant = paquete básico
    # Esto permite priorizar turnos por rentabilidad

    estimated_duration = fields.Float('Duración Estimada (horas)', default=2.0)
    price = fields.Float('Precio Base')
```

### 3.5 `medical.examination.order` (Modelo Central)

```python
class MedicalExaminationOrder(models.Model):
    _name = 'medical.examination.order'
    _description = 'Orden de Examen Médico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char('Número', readonly=True, default='Nuevo', copy=False)

    # Relaciones principales
    patient_id = fields.Many2one('medical.patient', 'Paciente', required=True,
        tracking=True)
    employer_id = fields.Many2one('res.partner', 'Empresa Empleadora',
        domain=[('is_company', '=', True)], required=True, tracking=True)
    template_id = fields.Many2one('medical.examination.template', 'Tipo de Examen',
        required=True, tracking=True)

    # Datos del examen
    examination_type = fields.Selection([
        ('preocupacional', 'Preocupacional'),
        ('periodico', 'Periódico'),
        ('transferencia', 'Previo a Transferencia'),
        ('reintegro', 'Posterior a Ausencia'),
        ('egreso', 'Previo a Terminación'),
    ], string='Tipo', default='preocupacional', required=True)

    date = fields.Date('Fecha del Turno', required=True, tracking=True)
    job_position = fields.Char('Puesto de Trabajo')

    # Estudios generados
    study_request_ids = fields.One2many('medical.study.request', 'order_id',
        string='Estudios Solicitados')

    # Certificado
    certificate_id = fields.One2many('medical.certificate', 'order_id',
        string='Certificado')

    # Estado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En Proceso'),
        ('studies_complete', 'Estudios Completos'),
        ('certified', 'Certificado Emitido'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ], default='draft', tracking=True)

    # Progreso
    studies_total = fields.Integer(compute='_compute_progress')
    studies_completed = fields.Integer(compute='_compute_progress')
    progress = fields.Float(compute='_compute_progress')  # % completado

    # Facturación
    invoice_id = fields.Many2one('account.move', 'Factura')

    # Por qué: al confirmar la orden, se generan automáticamente
    # los study.request según el template seleccionado
    def action_confirm(self):
        """Confirma la orden y genera solicitudes de estudio según template."""
        for order in self:
            order.name = self.env['ir.sequence'].next_by_code('medical.examination.order')
            for study_type in order.template_id.study_type_ids:
                self.env['medical.study.request'].create({
                    'order_id': order.id,
                    'study_type_id': study_type.id,
                })
            order.state = 'confirmed'

    # Por qué: cuando todos los estudios están completos,
    # se notifica automáticamente al médico auditor
    @api.depends('study_request_ids.state')
    def _compute_progress(self):
        for order in self:
            total = len(order.study_request_ids)
            completed = len(order.study_request_ids.filtered(
                lambda r: r.state in ('completado', 'validado')))
            order.studies_total = total
            order.studies_completed = completed
            order.progress = (completed / total * 100) if total else 0
            # Auto-transición cuando todos completos
            if total and completed == total and order.state == 'in_progress':
                order.state = 'studies_complete'
                # Notificar al médico auditor
                order.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary='Todos los estudios completos - Emitir certificado',
                )
```

### 3.6 `medical.study.request`

```python
class MedicalStudyRequest(models.Model):
    _name = 'medical.study.request'
    _description = 'Solicitud de Estudio'
    _inherit = ['mail.thread']

    order_id = fields.Many2one('medical.examination.order', 'Orden', required=True,
        ondelete='cascade')
    study_type_id = fields.Many2one('medical.study.type', 'Tipo de Estudio',
        required=True)

    # Profesional asignado (técnico que realiza el estudio)
    practitioner_id = fields.Many2one('medical.practitioner', 'Profesional',
        domain="[('specialty_id', '=', specialty_id)]")
    specialty_id = fields.Many2one(related='study_type_id.specialty_id', store=True)

    # Resultado
    result_id = fields.Many2one('medical.study.result', 'Resultado')

    # Estado
    state = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('validado', 'Validado'),
    ], default='pendiente', tracking=True)

    # Datos de la orden (para vistas filtradas por técnico)
    patient_id = fields.Many2one(related='order_id.patient_id', store=True)
    date = fields.Date(related='order_id.date', store=True)

    # Por qué: cada técnico ve SOLO los estudios de su especialidad
    # Patrón: vista kanban filtrada por specialty_id del usuario actual
```

### 3.7 `medical.study.result`

```python
class MedicalStudyResult(models.Model):
    _name = 'medical.study.result'
    _description = 'Resultado de Estudio'
    _inherit = ['mail.thread']

    request_id = fields.Many2one('medical.study.request', 'Solicitud')
    study_type_id = fields.Many2one(related='request_id.study_type_id', store=True)
    practitioner_id = fields.Many2one('medical.practitioner', 'Realizado por')

    # Valores medidos
    result_line_ids = fields.One2many('medical.study.result.line', 'result_id',
        string='Parámetros')

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

    # Firma del profesional que realizó el estudio
    signed = fields.Boolean('Firmado')
    signature = fields.Binary('Firma')
    signed_date = fields.Datetime('Fecha de Firma')
```

### 3.8 `medical.study.result.line`

```python
class MedicalStudyResultLine(models.Model):
    _name = 'medical.study.result.line'
    _description = 'Línea de Resultado (Observación FHIR)'

    result_id = fields.Many2one('medical.study.result', ondelete='cascade')

    parameter = fields.Char('Parámetro', required=True)  # Ej: "Glucemia"
    value = fields.Char('Valor')                          # Ej: "0.95"
    unit = fields.Char('Unidad')                          # Ej: "g/l"
    reference_min = fields.Float('Ref. Mínimo')           # Ej: 0.70
    reference_max = fields.Float('Ref. Máximo')           # Ej: 1.10

    is_abnormal = fields.Boolean('Fuera de Rango', compute='_compute_abnormal',
        store=True)

    # Por qué: marcar automáticamente valores fuera de rango
    # permite al médico auditor detectar rápidamente anomalías
    @api.depends('value', 'reference_min', 'reference_max')
    def _compute_abnormal(self):
        for line in self:
            try:
                val = float(line.value) if line.value else 0
                line.is_abnormal = (
                    (line.reference_min and val < line.reference_min) or
                    (line.reference_max and val > line.reference_max)
                )
            except ValueError:
                line.is_abnormal = False
```

### 3.9 `medical.certificate`

```python
class MedicalCertificate(models.Model):
    _name = 'medical.certificate'
    _description = 'Certificado de Aptitud'
    _inherit = ['mail.thread']

    name = fields.Char('Número', readonly=True, default='Nuevo', copy=False)

    order_id = fields.Many2one('medical.examination.order', 'Orden de Examen',
        required=True)
    patient_id = fields.Many2one(related='order_id.patient_id', store=True)
    employer_id = fields.Many2one(related='order_id.employer_id', store=True)

    # Dictamen
    dictamen = fields.Selection([
        ('apto', 'APTO'),
        ('no_apto', 'NO APTO'),
        ('apto_obs', 'APTO CON OBSERVACIONES'),
    ], string='Dictamen', required=True, tracking=True)

    observations = fields.Text('Observaciones')

    # Médico responsable (auditor que emite el certificado)
    practitioner_id = fields.Many2one('medical.practitioner',
        'Médico Responsable', required=True)

    # Firma
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('signed', 'Firmado'),
        ('delivered', 'Entregado'),
    ], default='draft', tracking=True)

    signature = fields.Binary('Firma Digital')
    signed_date = fields.Datetime('Fecha de Firma')

    # PDF generado
    pdf_file = fields.Binary('Certificado PDF', attachment=True)
    pdf_filename = fields.Char('Nombre archivo')

    # Por qué: al firmar se genera el PDF final y se puede
    # enviar por email automáticamente a la empresa
    def action_sign(self):
        """Firma el certificado y genera PDF."""
        self.ensure_one()
        self.name = self.env['ir.sequence'].next_by_code('medical.certificate')
        self.signature = self.practitioner_id.signature
        self.signed_date = fields.Datetime.now()
        self.state = 'signed'
        self.order_id.state = 'certified'
        # Generar PDF con reporte QWeb
        # Enviar por email a la empresa

    def action_deliver(self):
        """Marca como entregado y notifica."""
        self.state = 'delivered'
        self.order_id.state = 'delivered'
```

---

## 4. Vistas

### 4.1 Dashboard Principal (Recepción)

```
┌─────────────────────────────────────────────────────────┐
│  EXÁMENES HOY: 28/35          PROGRESO: ████████░░ 80%  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  KANBAN: Órdenes del día                                │
│                                                         │
│  [Borrador] [Confirmado] [En Proceso] [Completos] [OK]  │
│   ┌──────┐  ┌──────┐    ┌──────┐     ┌──────┐          │
│   │Juan P│  │María│     │Pedro │     │Ana   │          │
│   │Minera│  │Rest.│     │YPF   │     │Manfi │          │
│   │7 est.│  │5 est│     │6/8 ✓│     │8/8 ✓│          │
│   └──────┘  └──────┘    └──────┘     └──────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Cola de Trabajo del Técnico (filtrada por especialidad)

```
┌─────────────────────────────────────────────────────────┐
│  MIS ESTUDIOS PENDIENTES (Cardiología)                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Pendiente]        [En Proceso]      [Completado]      │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐    │
│  │ECG - Juan P│    │ECG - María │    │ECG - Ana   │    │
│  │  Minera SA │    │  Rest. XX  │    │  ✓ Normal  │    │
│  │  09:30 hs  │    │  → Cargando│    │  Firmado   │    │
│  │ [Iniciar]  │    │  [Completar│    │            │    │
│  └────────────┘    └────────────┘    └────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Vista del Médico Auditor (certificación)

```
┌─────────────────────────────────────────────────────────┐
│  CERTIFICADO #2026-0045 | Juan Pérez | Minera Manfield  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Estudios Realizados:                                   │
│  ✅ Laboratorio clínico    - Normal     [Ver detalle]   │
│  ✅ ECG                    - Normal     [Ver PDF]       │
│  ✅ Rx Tórax               - Normal     [Ver imagen]    │
│  ✅ Oftalmología           - Normal     [Ver detalle]   │
│  ✅ Audiometría            - Normal     [Ver PDF]       │
│  ⚠️ Psicológico           - Obs.       [Ver detalle]   │
│  ✅ Toxicológico           - Negativo   [Ver detalle]   │
│  ✅ Espirometría           - Normal     [Ver PDF]       │
│                                                         │
│  Dictamen: [APTO ▼]  Observaciones: [____________]     │
│                                                         │
│  [🖊 FIRMAR Y EMITIR CERTIFICADO]                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Firma Electrónica / Digital

### 5.1 Opciones evaluadas

| Opción | Tipo | Validez legal | Implementación |
|--------|------|---------------|----------------|
| **Odoo Sign** (Enterprise) | Firma electrónica simple | Media (Ley 25.506 Art. 5) | Nativa, inmediata |
| **Firma con imagen + audit trail** | Firma electrónica | Media | Desarrollo simple |
| **Encode / TAD** | Firma digital certificada | Alta (Ley 25.506 Art. 2) | Integración API |
| **Token USB + pyHanko** | Firma digital certificada | Máxima | Desarrollo complejo |

### 5.2 Recomendación por etapa

**Etapa 1:** Firma electrónica con imagen + audit trail
- El profesional tiene una imagen de firma cargada en su perfil
- Al firmar se estampa la imagen + timestamp + IP + hash del documento
- Se registra en el chatter quién firmó, cuándo y desde dónde
- Cumple con firma electrónica simple (Ley 25.506 Art. 5)

**Etapa 2:** Odoo Sign
- Integración con módulo Sign de Odoo Enterprise
- Workflow de solicitud de firma → aprobación
- El profesional recibe email, firma desde el portal

**Etapa 3 (futuro):** Firma digital certificada
- Investigar con Colegio Médico de Mendoza la emisión de certificados
- Integrar con proveedor de firma digital (Encode, TAD, AC-ONTI)

---

## 6. Seguridad y Permisos

### 6.1 Grupos

| Grupo | Acceso |
|-------|--------|
| `asinmet_medical.group_reception` | Crear/editar órdenes, turnos, pacientes |
| `asinmet_medical.group_technician` | Ver/completar estudios de su especialidad |
| `asinmet_medical.group_auditor` | Revisar estudios, emitir/firmar certificados |
| `asinmet_medical.group_manager` | Acceso total, reportes, configuración |

### 6.2 Reglas de registro (ir.rule)

```xml
<!-- Técnico solo ve estudios de su especialidad -->
<record id="rule_technician_own_specialty" model="ir.rule">
    <field name="domain_force">
        [('specialty_id', '=', user.practitioner_id.specialty_id.id)]
    </field>
</record>
```

---

## 7. Reportes

### 7.1 Certificado de Aptitud (QWeb PDF)
- Logo ASINMET
- Datos del paciente y empresa
- Tabla con todos los estudios y resultados
- Dictamen en recuadro destacado
- Firma del médico + matrícula + fecha
- Código QR con link de verificación (portal)

### 7.2 Dashboard Gerencial
- Pacientes atendidos por día/semana/mes
- Ingresos por tipo de examen
- Distribución por empresa
- Estudios más solicitados
- Tiempos promedio de completitud
- Tasa de "No Apto"

---

## 8. Estructura de Archivos del Módulo

```
asinmet_medical/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── medical_patient.py
│   ├── medical_practitioner.py
│   ├── medical_specialty.py
│   ├── medical_study_type.py
│   ├── medical_examination_template.py
│   ├── medical_examination_order.py
│   ├── medical_study_request.py
│   ├── medical_study_result.py
│   ├── medical_certificate.py
│   └── res_partner.py          # Extensión para marcar tipo médico
├── views/
│   ├── medical_patient_views.xml
│   ├── medical_practitioner_views.xml
│   ├── medical_study_type_views.xml
│   ├── medical_examination_template_views.xml
│   ├── medical_examination_order_views.xml
│   ├── medical_study_request_views.xml
│   ├── medical_study_result_views.xml
│   ├── medical_certificate_views.xml
│   ├── medical_dashboard_views.xml
│   └── medical_menus.xml
├── security/
│   ├── medical_security.xml     # Grupos
│   └── ir.model.access.csv     # Permisos CRUD
├── data/
│   ├── medical_sequence_data.xml
│   ├── medical_specialty_data.xml    # Datos iniciales (especialidades)
│   ├── medical_study_type_data.xml   # Tipos de estudio predefinidos
│   └── medical_template_data.xml     # Templates de exámenes
├── report/
│   ├── medical_certificate_report.xml    # Template QWeb del certificado
│   └── medical_certificate_report_template.xml
├── wizard/
│   └── medical_create_invoice.py    # Wizard para facturar
├── controllers/
│   └── portal.py               # Acceso portal para profesionales
└── static/
    └── description/
        └── icon.png
```
