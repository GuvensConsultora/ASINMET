# Propuesta Funcional - ASINMET
## Implementación Odoo 19 Enterprise

**Cliente:** Asociación de Industriales Metalúrgicos de Mendoza (ASINMET)
**CUIT:** 30-55085607-3
**Domicilio:** Lateral Norte Acceso Este 868, Guaymallén, Mendoza
**Implementador:** YAGÜVEN C.G.
**Fecha:** 13/02/2026

---

## 1. Introducción

### Qué hace Odoo nativamente
Odoo es un ERP modular que cubre ventas, compras, inventario, contabilidad, CRM, RRHH, marketing, eventos y más. Incluye localización argentina (facturación electrónica AFIP, plan de cuentas AR, impuestos).

### Limitación actual de ASINMET
- Sistema clínico del 2013 (obsoleto, sin integración digital)
- Sistema contable Bixid (sin conexión con el resto)
- Procesos en papel: resultados médicos, firmas, entregas físicas
- Sin trazabilidad gerencial ni control de gestión unificado
- Información dispersa entre áreas sin visibilidad cruzada
- Dependencia del conocimiento de personas individuales

### Qué propone esta implementación
Unificar en Odoo 19 Enterprise toda la operación de ASINMET: servicios médicos preocupacionales, contabilidad, gestión comercial/CRM, turnos, centro tecnológico, comunicación y encuestas de satisfacción. Con un módulo a medida para el flujo de exámenes preocupacionales.

---

## 2. Alcance por Etapas (Pareto)

### ETAPA 1 - Core (Prioridad Alta)

| Módulo Odoo | Área ASINMET | Funcionalidad |
|-------------|-------------|---------------|
| **Módulo custom `asinmet_medical`** | Preocupacionales | Gestión completa de exámenes pre/postocupacionales |
| **Appointments / Calendar** | Turnos | Agenda centralizada, capacidad diaria, priorización |
| **Accounting (l10n_ar)** | Contabilidad | Plan de cuentas AR, facturación electrónica AFIP |
| **Invoicing** | Facturación | Facturación de servicios médicos a empresas |
| **Contacts** | Base de datos | Empresas socias (200+), clientes (700+), pacientes, profesionales |
| **CRM** | Comercial | Pipeline de ventas, seguimiento por email, KPIs |

### ETAPA 2 - Expansión (Prioridad Media)

| Módulo Odoo | Área ASINMET | Funcionalidad |
|-------------|-------------|---------------|
| **Sales** | Comisiones | Reglas de comisión por vendedor, por servicio, por cliente nuevo |
| **Inventory** | Insumos médicos | Stock de insumos (gel, jeringas, EPP), consumo por servicio |
| **Sign** | Firma electrónica | Firma de profesionales médicos en certificados |
| **Portal** | Acceso externo | Profesionales médicos firman desde fuera sin usuario interno |

### ETAPA 3 - Complementarios (Prioridad Baja)

| Módulo Odoo | Área ASINMET | Funcionalidad |
|-------------|-------------|---------------|
| **Events** | Centro Tecnológico | Cursos de soldadura, capacitaciones, inscripciones |
| **Survey** | Calidad | Encuestas de satisfacción a empresas y pacientes |
| **Email Marketing** | Comunicación | Campañas de difusión de servicios |
| **Social Marketing** | Redes sociales | Gestión de Instagram, Facebook, X |
| **Website** | Presencia web | Publicación de servicios, cursos, formularios de contacto |
| **Assets** | Activos fijos | Inventario de equipamiento del centro tecnológico |

---

## 3. Módulos Odoo 19 Enterprise a Instalar

### Etapa 1

| Módulo técnico | Nombre | Tipo | Descripción |
|----------------|--------|------|-------------|
| `contacts` | Contactos | CE | Base de datos de empresas, pacientes, profesionales |
| `account` | Contabilidad | CE | Contabilidad general |
| `l10n_ar` | Localización Argentina | CE | Plan de cuentas AR, tipos de responsabilidad AFIP |
| `l10n_ar_edi` | Facturación electrónica AR | EE | Conexión AFIP para factura electrónica |
| `crm` | CRM | CE | Pipeline comercial, seguimiento de oportunidades |
| `calendar` | Calendario | CE | Agenda compartida, citas |
| `appointment` | Citas Online | EE | Reserva de turnos, capacidad por recurso |
| `mail` | Discuss | CE | Comunicación interna, chatter, notificaciones |
| `asinmet_medical` | **Módulo custom** | Custom | Exámenes preocupacionales (desarrollo a medida) |

### Etapa 2

| Módulo técnico | Nombre | Tipo |
|----------------|--------|------|
| `sale` | Ventas | CE |
| `sale_commission` | Comisiones | Custom/OCA |
| `stock` | Inventario | CE |
| `sign` | Firma electrónica | EE |
| `portal` | Portal | CE |

### Etapa 3

| Módulo técnico | Nombre | Tipo |
|----------------|--------|------|
| `event` | Eventos | CE |
| `survey` | Encuestas | CE |
| `mass_mailing` | Email Marketing | CE |
| `social` | Social Marketing | EE |
| `website` | Sitio Web | CE |
| `account_asset` | Activos | EE |

CE = Community Edition (incluido) | EE = Enterprise (incluido en licencia) | Custom = Desarrollo a medida

---

## 4. Usuarios

| # | Rol | Permisos | Tipo |
|---|-----|----------|------|
| 1 | **Gerencia** | Acceso total (admin) + implementación | Interno |
| 2 | **Jefa de Administración** | Contabilidad, facturación, pagos, contactos | Interno |
| 3 | **Contable** | Contabilidad, asientos, conciliación bancaria | Interno |
| 4 | **Comercial** | CRM, ventas, contactos, comisiones | Interno |
| 5 | **Encargada Medicina** | Módulo médico, turnos, pacientes, resultados | Interno |
| 6+ | **Profesionales médicos** (20-30) | Firma de resultados, consulta de estudios asignados | Portal (sin costo) |
| 7+ | **Empresas clientes** | Consulta de resultados, descarga de certificados | Portal (sin costo) |

**Costo licencia Odoo.sh:** 5 usuarios internos + hosting
**Usuarios portal:** Ilimitados, sin costo adicional

---

## 5. Flujos Operativos Principales

### 5.1 Flujo Preocupacional

```
1. EMPRESA solicita turnos (email/teléfono/portal)
       ↓
2. RECEPCIÓN crea Orden de Examen en Odoo
   - Selecciona empresa, paciente(s), tipo de examen
   - Sistema genera automáticamente los estudios según template
   - Asigna turnos en calendario
       ↓
3. PACIENTE llega a la sede
   - Check-in en recepción
   - Se activan los estudios pendientes para cada técnico
       ↓
4. TÉCNICOS realizan estudios (en paralelo o secuencial)
   - Cada técnico ve SU cola de trabajo (kanban filtrado por especialidad)
   - Sangre → Técnico de laboratorio
   - ECG → Técnico cardiólogo
   - Rayos X → Técnico radiólogo
   - Vista → Oftalmólogo
   - Psicológico → Psicólogo
   - Cada uno carga resultado + adjunta archivo (PDF/imagen)
       ↓
5. SISTEMA detecta que TODOS los estudios están completos
   - Notifica al médico auditor
       ↓
6. MÉDICO AUDITOR revisa todos los resultados
   - Vista unificada de todos los estudios del paciente
   - Emite dictamen: APTO / NO APTO / APTO CON OBSERVACIONES
   - Firma electrónica/digital
       ↓
7. SISTEMA genera CERTIFICADO PDF
   - Datos del paciente y empresa
   - Resumen de todos los estudios
   - Dictamen + firma del médico
       ↓
8. EMPRESA recibe certificado
   - Por email automático y/o descarga desde portal
   - Se elimina el proceso en papel
       ↓
9. FACTURACIÓN automática
   - Se genera factura a la empresa por los servicios prestados
```

### 5.2 Flujo Comercial / CRM

```
1. LEAD ingresa (referido, email, web)
       ↓
2. COMERCIAL gestiona en pipeline CRM
   - Contacta por email (desde Odoo, queda registrado)
   - Califica oportunidad
   - Propone servicios (preocupacional, HyS, capacitación, etc.)
       ↓
3. CONVERSIÓN → Cliente
   - Se crea contacto empresa
   - Se asignan servicios contratados
       ↓
4. SEGUIMIENTO
   - Actividades programadas
   - KPIs: cantidad de contactos por servicio, tasa de conversión
   - Comisiones calculadas automáticamente
```

### 5.3 Flujo Contable

```
1. FACTURACIÓN de servicios → Factura electrónica AFIP
2. COBROS → Registración de pagos (CREDICOOP, Santander)
3. GASTOS → Registro de proveedores (laboratorio, profesionales)
4. BANCOS → Conciliación bancaria automática
5. REPORTES → Balance, estado de resultados, flujo de fondos
6. VISIBILIDAD → Dashboard para comisión directiva
```

### 5.4 Flujo de Turnos

```
1. SOLICITUD de turno (teléfono/email/portal)
       ↓
2. SISTEMA muestra disponibilidad
   - Capacidad diaria: 30-35 pacientes
   - Slots ocupados vs disponibles
   - Priorización configurable (minera > restaurante)
       ↓
3. ASIGNACIÓN
   - Bloqueo de slots
   - Confirmación al solicitante
   - Si hay sobredemanda: lista de espera
       ↓
4. RECORDATORIO automático (email/SMS)
```

---

## 6. Integraciones

| Sistema externo | Tipo integración | Prioridad |
|----------------|-----------------|-----------|
| **AFIP** | Facturación electrónica (nativo Odoo AR) | Etapa 1 |
| **Bancos (CREDICOOP/Santander)** | Importación de extractos bancarios | Etapa 1 |
| **Equipos médicos** (ECG, Rayos X, etc.) | API REST si disponible / carga manual PDF | Etapa 1-2 |
| **Laboratorio tercerizado** | Recepción de resultados (email/API) | Etapa 2 |
| **Email** | Integración con correo existente (IMAP/SMTP) | Etapa 1 |

---

## 7. Entregables por Etapa

### Etapa 1
- [ ] Instalación y configuración Odoo 19 Enterprise en Odoo.sh
- [ ] Configuración compañía ASINMET (datos fiscales, logo, cuentas bancarias)
- [ ] Configuración contabilidad argentina (plan de cuentas, impuestos, AFIP)
- [ ] Desarrollo módulo `asinmet_medical` (preocupacionales)
- [ ] Configuración CRM (pipeline, etapas, equipos)
- [ ] Configuración de turnos/agenda
- [ ] Migración de datos (empresas, contactos, pacientes históricos)
- [ ] Capacitación usuarios (5 sesiones)
- [ ] Documentación operativa
- [ ] Go-live con soporte post-implementación (1 mes)

### Etapa 2
- [ ] Módulo de comisiones comerciales
- [ ] Configuración de inventario (insumos médicos)
- [ ] Implementación firma electrónica (Odoo Sign)
- [ ] Portal para profesionales médicos y empresas
- [ ] Capacitación adicional

### Etapa 3
- [ ] Módulo de eventos (cursos centro tecnológico)
- [ ] Encuestas de satisfacción
- [ ] Email/Social Marketing
- [ ] Website
- [ ] Activos fijos (equipamiento centro tecnológico)

---

## 8. Cronograma Estimado

| Etapa | Duración | Período |
|-------|----------|---------|
| Etapa 1 | 8-10 semanas | Mes 1-3 |
| Etapa 2 | 4-6 semanas | Mes 3-4 |
| Etapa 3 | 4-6 semanas | Mes 5-6 |
| **Total** | **16-22 semanas** | **~5 meses** |

---

## 9. Inversión

### Costos Odoo.sh (licencia anual)

| Concepto | Costo estimado |
|----------|---------------|
| Hosting Odoo.sh (1 worker) | ~USD 72/mes |
| 5 usuarios Enterprise | ~USD 150-180/usuario/año |
| **Subtotal anual** | ~USD 1,614 - 1,764/año |
| **Descuento 20% primer año** | ~USD 1,291 - 1,411/año |

*Precios sujetos a cotización oficial de Odoo S.A.*

### Costos de Implementación (YAGUVEN)

| Concepto | Detalle |
|----------|---------|
| Etapa 1 - Core + Módulo médico | A presupuestar |
| Etapa 2 - Comisiones, inventario, firma, portal | A presupuestar |
| Etapa 3 - Eventos, encuestas, marketing, web | A presupuestar |
| Soporte mensual post go-live | A presupuestar |

*Se detallará en presupuesto formal tras segunda reunión con equipo administrativo.*

---

## 10. Próximos Pasos

1. **ASINMET** envía a Horacio los 3-4 puntos prioritarios
2. **YAGUVEN** prepara demo funcional con flujo preocupacional
3. **Reunión 2** con equipo administrativo de ASINMET:
   - Demostración del sistema
   - Relevamiento detallado con jefa de administración y encargada de medicina
   - Ajuste de requerimientos
4. **YAGUVEN** entrega presupuesto formal (licencia + implementación)
5. **Firma de contrato** y arranque de Etapa 1
6. **Posible extensión** a CETEM San Rafael (Antonella Tassaroli)
