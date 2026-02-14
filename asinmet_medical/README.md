# ASINMET - Medicina Laboral (`asinmet_medical`)

## Odoo 19 Enterprise

---

## 1. Introduccion

### Que hace Odoo nativamente

Odoo gestiona contactos, facturacion, calendario y portal web. No incluye ningun modulo de salud ocupacional ni gestion de examenes medicos. Los modulos de terceros disponibles (OCA vertical-medical, Creu Blanca) quedaron abandonados en Odoo 14 y no cubren el flujo de examenes preocupacionales con multiples estudios, multiples tecnicos y certificado de aptitud.

### Que limitacion existe

ASINMET necesita gestionar diariamente 30+ examenes preocupacionales donde cada paciente pasa por 8-10 estudios diferentes (laboratorio, ECG, Rx, oftalmologia, audiometria, psicologia, toxicologia). Cada estudio lo realiza un tecnico distinto, en un consultorio distinto, y el medico auditor necesita ver todos los resultados consolidados para emitir un certificado de aptitud.

Sin este modulo, el flujo se gestiona con planillas de papel, Excel y WhatsApp entre tecnicos. No hay trazabilidad, no hay historial del paciente, y el certificado se emite manualmente en Word.

### Que mejora propone este modulo

Un sistema completo de medicina laboral que:

- **Gestiona el flujo completo**: desde que el paciente llega hasta que se entrega el certificado
- **Coordina multiples tecnicos**: cada profesional ve solo los estudios de su especialidad
- **Detecta anomalias automaticamente**: valores fuera de rango se marcan en rojo
- **Emite certificados con firma electronica**: cumple Ley 25.506 Art. 5
- **Genera PDF del certificado**: con datos del paciente, estudios, dictamen y firma
- **Mantiene historial longitudinal**: el paciente conserva su historial aunque cambie de empresa

### Base tecnica

| Referencia | Uso |
|------------|-----|
| HL7 FHIR | Nomenclatura de modelos (Patient, Encounter, ServiceRequest, DiagnosticReport, Observation) |
| OCA vertical-medical | Patron de herencia `_inherits` sobre `res.partner` |
| GNU Health | Flujo de salud ocupacional (orden -> estudios -> certificado) |
| Res. SRT 37/2010 y 905/2015 | Campos obligatorios del certificado de aptitud |

---

## 2. Funcionamiento para el usuario final

### 2.1 Flujo completo paso a paso

```
Recepcion crea orden → Confirma → Sistema genera estudios automaticamente
    ↓
Cada tecnico ve su cola de trabajo (kanban por especialidad)
    ↓
Tecnico inicia estudio → Carga resultados → Completa
    ↓
Cuando TODOS los estudios estan completos → auto-notificacion al auditor
    ↓
Medico auditor revisa estudios → Emite dictamen → Firma certificado
    ↓
Recepcion entrega certificado al paciente/empresa
```

### 2.2 Roles y que ve cada uno

| Rol | Que ve en pantalla | Que puede hacer |
|-----|-------------------|-----------------|
| **Recepcion** | Panel kanban con ordenes del dia, listado de pacientes | Crear pacientes, crear ordenes, confirmar, entregar certificados |
| **Tecnico** | Cola kanban filtrada por su especialidad (ej: solo ECG) | Iniciar estudio, cargar valores, adjuntar archivos, completar |
| **Medico Auditor** | Vista de certificacion con resumen de todos los estudios | Validar estudios, emitir dictamen (APTO/NO APTO), firmar |
| **Administrador** | Todo + configuracion | Gestionar especialidades, tipos de estudio, plantillas, profesionales |

### 2.3 Recepcion: crear una orden de examen

1. Ir a **Medicina Laboral > Operaciones > Ordenes de Examen**
2. Click en **Nuevo**
3. Seleccionar **Paciente** (si no existe, crearlo desde ahi)
   - Al seleccionar paciente, se autocompleta la empresa y puesto
4. Seleccionar **Tipo de Examen** (ej: "Preocupacional Estandar")
5. Seleccionar **Fecha del Turno**
6. Click en **Confirmar**
   - El sistema genera automaticamente las solicitudes de estudio segun la plantilla
   - Ejemplo: si la plantilla tiene 8 estudios, se crean 8 solicitudes

### 2.4 Tecnico: completar un estudio

1. Ir a **Medicina Laboral > Operaciones > Estudios**
   - Ve solo los estudios de su especialidad (ej: Cardiologia)
   - Vista kanban: columnas Pendiente / En Proceso / Completado
2. Tomar una tarjeta de la columna "Pendiente" → click → **Iniciar**
3. Cargar resultados:
   - Completar la tabla de parametros (ej: Glucemia = 0.95 g/l)
   - Valores fuera de rango se marcan automaticamente en rojo
   - Adjuntar PDF o imagen del equipo si corresponde
   - Seleccionar resultado: Normal / Anormal / Con Observaciones
   - Escribir conclusion
4. Click en **Completar**
   - Si es el ultimo estudio pendiente, la orden pasa automaticamente a "Estudios Completos"
   - Se crea una actividad para el medico auditor

### 2.5 Medico auditor: emitir certificado

1. Ir a **Medicina Laboral > Operaciones > Certificados**
2. Crear nuevo certificado vinculado a la orden
3. Revisar el resumen de estudios:
   - Valores fuera de rango aparecen destacados
   - Puede abrir cada resultado en detalle
4. Seleccionar **Dictamen**: APTO / NO APTO / APTO CON OBSERVACIONES
5. Si tiene observaciones, completar el campo
6. Click en **Firmar y Emitir**
   - Se estampa la firma electronica del profesional
   - Se genera el numero de certificado (CERT-2026-00001)
   - Se registra en el chatter quien firmo y cuando (audit trail)
   - Se puede imprimir el PDF del certificado

### 2.6 Estados de la orden

| Estado | Significado | Quien lo activa |
|--------|------------|-----------------|
| Borrador | Orden creada, sin confirmar | Recepcion |
| Confirmado | Estudios generados, listos para realizar | Recepcion (boton Confirmar) |
| En Proceso | Al menos un tecnico inicio un estudio | Automatico al iniciar primer estudio |
| Estudios Completos | Todos los estudios finalizados | Automatico al completar ultimo estudio |
| Certificado Emitido | Auditor firmo el certificado | Auditor (boton Firmar) |
| Entregado | Certificado entregado al paciente/empresa | Recepcion (boton Entregar) |
| Cancelado | Orden cancelada | Recepcion |

### 2.7 Barra de progreso

En la orden de examen se muestra una barra de progreso visual:

```
Estudios: 5/8 completados  [██████░░░░] 62%
```

Se actualiza en tiempo real cada vez que un tecnico completa un estudio.

---

## 3. Parametrizacion

### 3.1 Especialidades medicas

**Menu:** Medicina Laboral > Configuracion > Especialidades

El modulo viene con 10 especialidades precargadas:

| Codigo | Especialidad |
|--------|-------------|
| CLI | Clinica Medica |
| CAR | Cardiologia |
| RAD | Radiologia |
| OFT | Oftalmologia |
| FON | Fonoaudiologia |
| PSI | Psicologia |
| LAB | Laboratorio |
| TOX | Toxicologia |
| NEU | Neumonologia |
| LAB_MED | Medicina Laboral |

Se pueden agregar mas desde la lista editable.

### 3.2 Tipos de estudio

**Menu:** Medicina Laboral > Configuracion > Tipos de Estudio

El modulo viene con 10 tipos de estudio precargados segun Res. SRT 37/2010:

| Codigo | Estudio | Especialidad | Requiere adjunto |
|--------|---------|-------------|-----------------|
| CLIN | Examen Clinico General | Clinica Medica | No |
| LAB | Analisis de Laboratorio | Laboratorio | Si |
| ECG | Electrocardiograma | Cardiologia | Si |
| RX_TX | Radiografia de Torax | Radiologia | Si |
| OFT | Examen Oftalmologico | Oftalmologia | Si |
| AUD | Audiometria | Fonoaudiologia | Si |
| PSI | Examen Psicologico | Psicologia | No |
| TOX | Analisis Toxicologico | Toxicologia | Si |
| ESP | Espirometria | Neumonologia | Si |
| ERG | Ergometria (ECG esfuerzo) | Cardiologia | Si |

**Parametros de laboratorio precargados** (para el tipo "Analisis de Laboratorio"):

| Parametro | Unidad | Ref. Min | Ref. Max |
|-----------|--------|----------|----------|
| Glucemia | g/l | 0.70 | 1.10 |
| Urea | mg/dl | 15.0 | 45.0 |
| Creatinina | mg/dl | 0.70 | 1.30 |
| Hemoglobina | g/dl | 12.0 | 17.0 |
| Hematocrito | % | 36.0 | 50.0 |
| Colesterol Total | mg/dl | 0.0 | 200.0 |

Para agregar parametros a otros tipos de estudio:
1. Abrir el tipo de estudio
2. Ir a la pestana "Parametros"
3. Agregar lineas con nombre, unidad y rango de referencia

### 3.3 Plantillas de examen

**Menu:** Medicina Laboral > Configuracion > Plantillas de Examen

Las plantillas definen que estudios incluye cada tipo de examen. Ejemplos a crear:

**Preocupacional Estandar** (8 estudios):
- Examen Clinico General, Laboratorio, ECG, Rx Torax, Oftalmologia, Audiometria, Psicologico, Toxicologico

**Preocupacional Mineria** (10 estudios):
- Todos los anteriores + Espirometria + Ergometria

**Periodico Basico** (4 estudios):
- Examen Clinico General, Laboratorio, Audiometria, Rx Torax

Pasos para crear una plantilla:
1. Click en **Nuevo**
2. Nombre: ej. "Preocupacional Estandar"
3. Duracion estimada: ej. 2 horas
4. Precio base: ej. 25000
5. Pestana "Estudios Incluidos": agregar los tipos de estudio

### 3.4 Profesionales

**Menu:** Medicina Laboral > Registros > Profesionales

Para cada profesional cargar:
1. **Nombre** (se crea como contacto de Odoo)
2. **Matricula profesional**
3. **Especialidad** (vincula con los tipos de estudio que puede realizar)
4. **Firma electronica** (imagen PNG/JPG de la firma, se estampa en certificados)
5. Datos de contacto (telefono, email)

### 3.5 Pacientes

**Menu:** Medicina Laboral > Registros > Pacientes

Para cada paciente cargar:
1. **Nombre** (se crea como contacto de Odoo)
2. **DNI** (unico, no se puede repetir)
3. **Fecha de nacimiento**
4. **Genero**
5. **Grupo sanguineo**
6. **Empresa empleadora** (seleccionar de contactos tipo empresa)
7. **Puesto de trabajo**

### 3.6 Grupos de seguridad

**Menu:** Ajustes > Usuarios > (seleccionar usuario) > pestana Medicina Laboral

| Grupo | Para quien |
|-------|-----------|
| Recepcion | Personal administrativo que recibe pacientes |
| Tecnico / Profesional | Cada tecnico que realiza estudios |
| Medico Auditor | Medico que firma certificados |
| Administrador Medicina Laboral | Responsable del area, configura todo |

Los grupos son jerarquicos: Administrador incluye Auditor, que incluye Tecnico, que incluye Recepcion.

---

## 4. Referencia tecnica

### 4.1 Arquitectura de modelos

```
res.partner (Odoo nativo)
    |
    +-- medical.patient (_inherits res.partner)
    |     dni, birth_date, gender, blood_type, employer_id, job_position
    |
    +-- medical.practitioner (_inherits res.partner)
          license_number, specialty_id, signature

medical.specialty
    name, code

medical.study.type
    name, code, specialty_id, requires_attachment
    +-- medical.study.type.line (One2many)
          parameter, unit, reference_min, reference_max

medical.examination.template
    name, study_type_ids (Many2many), estimated_duration, price

medical.examination.order  [mail.thread, mail.activity.mixin]
    patient_id, employer_id, template_id, examination_type, date, job_position
    state: draft -> confirmed -> in_progress -> studies_complete -> certified -> delivered
    +-- medical.study.request (One2many)
    +-- medical.certificate (One2many)

medical.study.request  [mail.thread]
    order_id, study_type_id, practitioner_id, specialty_id
    state: pendiente -> en_proceso -> completado -> validado
    +-- medical.study.result (One2many)

medical.study.result  [mail.thread]
    request_id, practitioner_id, conclusion, aptitude, attachment_ids
    +-- medical.study.result.line (One2many)
          parameter, value, unit, reference_min, reference_max, is_abnormal (computed)

medical.certificate  [mail.thread]
    order_id, patient_id, employer_id, practitioner_id
    dictamen: apto / no_apto / apto_obs
    state: draft -> signed -> delivered
    signature, signed_date
```

### 4.2 Patron de herencia: `_inherits`

`medical.patient` y `medical.practitioner` usan `_inherits` (delegacion) sobre `res.partner`:

```python
class MedicalPatient(models.Model):
    _name = 'medical.patient'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
```

- **Por que `_inherits` y no `_inherit`:** Crea tabla separada `medical_patient` con campos propios (DNI, grupo sanguineo) pero delega nombre, telefono, email, direccion a `res.partner`. El paciente ES un contacto de Odoo, puede facturarse, recibir emails, etc.
- **Alternativa descartada:** `_inherit = 'res.partner'` agregaria campos medicos a TODOS los contactos, contaminando el modelo base.

### 4.3 Workflow: confirmacion de orden

Al confirmar una orden (`action_confirm`):

```python
def action_confirm(self):
    for order in self:
        # Asignar numero secuencial EX-2026-00001
        if order.name == 'Nuevo':
            order.name = self.env['ir.sequence'].next_by_code(
                'medical.examination.order'
            ) or 'Nuevo'
        # Generar solicitudes de estudio segun plantilla
        for study_type in order.template_id.study_type_ids:
            self.env['medical.study.request'].create({
                'order_id': order.id,
                'study_type_id': study_type.id,
            })
        order.state = 'confirmed'
```

### 4.4 Auto-creacion de lineas de resultado

Al crear un `medical.study.request`, si el tipo de estudio tiene parametros definidos, se crea automaticamente un `medical.study.result` con lineas pre-cargadas:

```python
@api.model_create_multi
def create(self, vals_list):
    requests = super().create(vals_list)
    for request in requests:
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
```

- **Por que:** El tecnico de laboratorio abre el estudio y ya ve la tabla con Glucemia, Urea, Creatinina, etc. Solo necesita completar la columna "Valor". Reduce errores y tiempo de carga.

### 4.5 Deteccion automatica de valores anormales

```python
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
```

- **Por que `store=True`:** Permite filtrar y agrupar por valores anormales. El auditor puede buscar rapidamente "todos los estudios con algun parametro fuera de rango".
- **Por que `try/except`:** El campo `value` es `Char` (no Float) porque algunos resultados son textuales ("Positivo", "Negativo"). Solo se evalua rango cuando el valor es numerico.

### 4.6 Auto-transicion de la orden

Cuando un tecnico completa el ultimo estudio, la orden transiciona automaticamente:

```python
def _check_studies_complete(self):
    for order in self:
        if (order.state == 'in_progress'
                and order.studies_total
                and order.studies_completed == order.studies_total):
            order.state = 'studies_complete'
            order.activity_schedule(
                'mail.mail_activity_data_todo',
                summary='Todos los estudios completos - Emitir certificado',
            )
```

- **Por que no en `_compute_progress`:** Los computes no deben tener side-effects (escribir en otros campos). El metodo `_check_studies_complete` se invoca explicitamente desde `action_complete` de la solicitud.

### 4.7 Firma electronica (Etapa 1)

```python
def action_sign(self):
    self.ensure_one()
    if self.name == 'Nuevo':
        self.name = self.env['ir.sequence'].next_by_code('medical.certificate') or 'Nuevo'
    self.signature = self.practitioner_id.signature
    self.signed_date = fields.Datetime.now()
    self.state = 'signed'
    self.order_id.state = 'certified'
    self.message_post(
        body=f'Certificado firmado por {self.practitioner_id.name} '
             f'- Matricula: {self.practitioner_id.license_number}',
    )
```

- **Etapa 1:** Firma electronica simple (imagen + audit trail en chatter). Cumple Ley 25.506 Art. 5.
- **Etapa 2 (futuro):** Integracion con Odoo Sign.
- **Etapa 3 (futuro):** Firma digital certificada (Encode/TAD).

### 4.8 Seguridad

**Grupos** (jerarquicos, en `security/medical_security.xml`):

```
group_reception
    └── group_technician
        └── group_auditor
            └── group_manager
```

**Permisos CRUD** (`security/ir.model.access.csv`):

| Modelo | Recepcion | Tecnico | Auditor | Manager |
|--------|-----------|---------|---------|---------|
| medical.specialty | R | R | R | CRUD |
| medical.patient | CRW | CRW | CRW | CRUD |
| medical.practitioner | R | R | R | CRUD |
| medical.study.type | R | R | R | CRUD |
| medical.examination.template | R | R | R | CRUD |
| medical.examination.order | CRW | CRW | CRW | CRUD |
| medical.study.request | R | RW | RW | CRUD |
| medical.study.result | - | CRW | CRW | CRUD |
| medical.study.result.line | - | CRW | CRW | CRUD |
| medical.certificate | - | - | CRW | CRUD |

**Regla de registro** — Tecnico solo ve solicitudes asignadas a el o sin asignar:

```xml
<record id="rule_technician_own_specialty" model="ir.rule">
    <field name="domain_force">[
        '|',
        ('practitioner_id.partner_id.user_ids', 'in', [user.id]),
        ('practitioner_id', '=', False)
    ]</field>
</record>
```

### 4.9 Secuencias

| Secuencia | Formato | Ejemplo |
|-----------|---------|---------|
| Orden de Examen | `EX-%(year)s-NNNNN` | EX-2026-00001 |
| Certificado | `CERT-%(year)s-NNNNN` | CERT-2026-00001 |

### 4.10 Reporte PDF del certificado

Template QWeb `report_medical_certificate` que incluye:

- Encabezado con numero de certificado
- Datos del paciente (nombre, DNI, fecha nacimiento)
- Datos de la empresa (razon social, puesto, tipo de examen)
- Tabla de estudios realizados (estudio, profesional, resultado, fecha)
- Dictamen en recuadro destacado (APTO / NO APTO / APTO CON OBSERVACIONES)
- Observaciones (si aplica)
- Firma del medico responsable (imagen + matricula + fecha)

### 4.11 Dependencias

```python
'depends': ['base', 'contacts', 'calendar', 'account', 'mail', 'portal']
```

| Modulo | Por que |
|--------|---------|
| `base` | Modelos base, `res.partner` |
| `contacts` | Gestion de contactos (pacientes, profesionales, empresas) |
| `calendar` | Turnos y agenda (futuro) |
| `account` | Facturacion de examenes |
| `mail` | Chatter, tracking, actividades, notificaciones |
| `portal` | Acceso web para profesionales externos (futuro) |

### 4.12 Estructura de archivos

```
asinmet_medical/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── medical_specialty.py          # Especialidades medicas
│   ├── medical_patient.py            # Paciente (_inherits res.partner)
│   ├── medical_practitioner.py       # Profesional (_inherits res.partner)
│   ├── medical_study_type.py         # Tipos de estudio + lineas parametros
│   ├── medical_examination_template.py  # Plantillas de paquetes
│   ├── medical_examination_order.py  # Orden de examen (modelo central)
│   ├── medical_study_request.py      # Solicitud de estudio individual
│   ├── medical_study_result.py       # Resultado + lineas de valores
│   └── medical_certificate.py        # Certificado de aptitud
├── views/
│   ├── medical_specialty_views.xml
│   ├── medical_patient_views.xml
│   ├── medical_practitioner_views.xml
│   ├── medical_study_type_views.xml
│   ├── medical_examination_template_views.xml
│   ├── medical_examination_order_views.xml   # Form + List + Kanban + Search
│   ├── medical_study_request_views.xml       # Form + List + Kanban + Search
│   ├── medical_study_result_views.xml
│   ├── medical_certificate_views.xml
│   └── medical_menus.xml                     # Menu principal + submenus
├── security/
│   ├── medical_security.xml          # Grupos y reglas de registro
│   └── ir.model.access.csv          # Permisos CRUD por grupo
├── data/
│   ├── medical_sequence_data.xml     # Secuencias EX- y CERT-
│   ├── medical_specialty_data.xml    # 10 especialidades precargadas
│   └── medical_study_type_data.xml   # 10 tipos de estudio + parametros lab
├── report/
│   ├── medical_certificate_report.xml       # Definicion del reporte
│   └── medical_certificate_templates.xml    # Template QWeb del PDF
└── static/
    └── description/
        └── icon.png
```

### 4.13 Verificacion post-instalacion

1. **Instalar modulo:** Aplicaciones > buscar "ASINMET" > Instalar
2. **Verificar menu:** debe aparecer "Medicina Laboral" en la barra superior
3. **Verificar datos:** Configuracion > Especialidades (10 registros), Tipos de Estudio (10 registros)
4. **Crear plantilla:** Configuracion > Plantillas de Examen > crear "Preocupacional Estandar" con 8 estudios
5. **Crear profesional:** Registros > Profesionales > crear con matricula y especialidad
6. **Crear paciente:** Registros > Pacientes > crear con DNI y empresa
7. **Crear orden:** Operaciones > Ordenes > crear, seleccionar paciente y plantilla, confirmar
8. **Verificar estudios:** deben generarse 8 solicitudes automaticamente
9. **Completar estudios:** abrir cada solicitud, iniciar, cargar valores, completar
10. **Verificar auto-transicion:** al completar el ultimo estudio, la orden pasa a "Estudios Completos"
11. **Emitir certificado:** crear certificado, seleccionar dictamen, firmar
12. **Imprimir PDF:** Imprimir > Certificado de Aptitud
