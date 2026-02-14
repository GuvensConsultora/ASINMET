# Preparación Demo ASINMET - Odoo 19 Enterprise

## Objetivo
Preparar un entorno demo funcional para la segunda reunión con ASINMET,
donde se muestre el flujo completo de un examen preocupacional.

---

## 1. Configuración Base (Odoo.sh Trial)

### 1.1 Crear instancia
```
- URL: asinmet-demo.odoo.com (trial 15 días)
- Versión: Odoo 19 Enterprise
- País: Argentina
- Idioma: Español (AR)
```

### 1.2 Datos de la compañía
```
- Nombre: Asociación de Industriales Metalúrgicos de Mendoza - ASINMET
- CUIT: 30-55085607-3
- Dirección: Lateral Norte Acceso Este 868, Guaymallén, Mendoza
- Responsabilidad AFIP: IVA Exento
- Logo: descargar de asinmet.com
```

### 1.3 Módulos a instalar
```
1. contacts          → Base de contactos
2. account           → Contabilidad
3. l10n_ar           → Localización argentina
4. crm              → Pipeline comercial
5. calendar          → Agenda
6. appointment       → Citas online
7. sign             → Firma electrónica
8. survey           → Encuestas
9. event            → Eventos (cursos)
10. mail            → Comunicación
11. portal          → Acceso externo
```

---

## 2. Datos Demo

### 2.1 Empresas (Contactos tipo empresa)

| Nombre | CUIT | Tipo | Servicio |
|--------|------|------|----------|
| Minera Manfield SA | 30-xxxxx-x | Cliente | Preocupacional Minería |
| YPF Refinería Luján | 30-xxxxx-x | Cliente | Preocupacional Refinería |
| Hols Mining SA | 30-xxxxx-x | Cliente | Preocupacional Minería |
| IPF Construcciones | 30-xxxxx-x | Cliente | Preocupacional Estándar |
| Restaurant El Bodegón | 30-xxxxx-x | Cliente | Preocupacional Básico |
| Metalúrgica San Martín | 30-xxxxx-x | Socio | Preocupacional Estándar |
| Laboratorio BioAnálisis | 30-xxxxx-x | Proveedor | Análisis clínicos |

### 2.2 Pacientes demo

| Nombre | DNI | Empresa | Puesto |
|--------|-----|---------|--------|
| Juan Pérez | 28.456.789 | Minera Manfield | Operador de planta |
| María González | 32.123.456 | Restaurant El Bodegón | Cocinera |
| Pedro López | 35.789.012 | YPF Refinería | Técnico químico |
| Ana Rodríguez | 29.567.890 | IPF Construcciones | Conductora |

### 2.3 Profesionales médicos

| Nombre | Matrícula | Especialidad | Rol |
|--------|-----------|-------------|-----|
| Dr. Carlos Méndez | MP 12345 | Medicina Laboral | Médico Auditor |
| Dr. Laura Vega | MP 23456 | Cardiología | Cardiólogo |
| Lic. Roberto Sánchez | LP 34567 | Psicología | Psicólogo |
| Tec. Silvia Torres | TL 45678 | Laboratorio | Técnica lab |
| Tec. Mario Ruiz | TR 56789 | Radiología | Técnico Rx |
| Dra. Patricia Olmos | MO 67890 | Oftalmología | Oftalmóloga |

### 2.4 Tipos de estudio

| Código | Nombre | Especialidad | Adjunto |
|--------|--------|-------------|---------|
| LAB | Laboratorio Clínico | Laboratorio | PDF |
| ECG | Electrocardiograma | Cardiología | PDF |
| RXT | Radiografía de Tórax | Radiología | Imagen |
| OFT | Examen Oftalmológico | Oftalmología | - |
| AUD | Audiometría | Fonoaudiología | PDF |
| PSI | Examen Psicológico | Psicología | - |
| TOX | Toxicológico | Laboratorio | PDF |
| EEG | Electroencefalograma | Neurología | PDF |
| ESP | Espirometría | Neumonología | PDF |
| ODO | Examen Odontológico | Odontología | - |

### 2.5 Templates de examen

| Template | Estudios incluidos | Precio |
|----------|-------------------|--------|
| Preocupacional Estándar | LAB, ECG, RXT, OFT, AUD, PSI, TOX | $XX.XXX |
| Preocupacional Minería | Estándar + EEG, ESP | $XX.XXX |
| Preocupacional Alimentos | LAB, OFT, PSI, TOX, ODO | $XX.XXX |
| Postocupacional | LAB, ECG, RXT, AUD | $XX.XXX |

---

## 3. Flujo Demo para la Reunión

### Escenario 1: Preocupacional completo (5 min)

**Narración:** "Minera Manfield necesita incorporar un operador de planta. Nos solicitan un preocupacional para minería."

1. **Recepción** crea orden de examen
   - Selecciona empresa: Minera Manfield
   - Crea paciente: Juan Pérez
   - Template: Preocupacional Minería
   - Fecha: hoy
   - → Click "Confirmar" → Se generan 9 estudios automáticamente

2. **Técnico de laboratorio** ve su cola (vista filtrada)
   - Solo ve estudios LAB y TOX
   - Carga valores (glucemia, hemograma, etc.)
   - Adjunta PDF del analizador
   - Marca "Completado"

3. **Cardiólogo** ve su cola
   - Solo ve estudio ECG
   - Adjunta PDF del electrocardiógrafo
   - Escribe "Normal, ritmo sinusal"
   - Marca "Completado"

4. **Barra de progreso** en la orden se va llenando (7/9, 8/9...)

5. **Todos completos** → Notificación al Dr. Méndez (médico auditor)

6. **Dr. Méndez** abre el certificado
   - Ve resumen de todos los estudios
   - Un estudio con valor fuera de rango se destaca en rojo
   - Selecciona dictamen: "APTO"
   - Click "Firmar y Emitir"
   - → Se genera PDF con todos los datos + firma

7. **Resultado final**
   - PDF del certificado (mostrar en pantalla)
   - Email automático a Minera Manfield
   - Factura generada por el servicio

### Escenario 2: CRM (2 min)

1. Llega un email de nueva empresa interesada
2. Se crea oportunidad en CRM
3. Pipeline: Nuevo → Contactado → Propuesta → Ganado
4. Se muestra dashboard con KPIs

### Escenario 3: Turnos (2 min)

1. Vista calendario con 30 turnos del día
2. Mostrar cómo se bloquean slots
3. Vista de capacidad disponible vs ocupada

### Escenario 4: Contabilidad (2 min)

1. Factura generada automáticamente
2. Plan de cuentas argentino
3. Conciliación bancaria

---

## 4. Preparación Técnica

### 4.1 Módulo demo `asinmet_medical_demo`

Módulo con datos demo precargados para la presentación:
- Secuencias configuradas
- Datos de ejemplo cargados
- Vistas personalizadas

### 4.2 Screenshots/Video de respaldo

Grabar video del flujo completo como backup en caso de problemas
técnicos durante la reunión.

### 4.3 Checklist pre-reunión

- [ ] Instancia Odoo.sh funcionando
- [ ] Módulo `asinmet_medical` instalado y funcional
- [ ] Datos demo cargados
- [ ] Flujo probado de punta a punta
- [ ] PDF de certificado generándose correctamente
- [ ] CRM configurado con pipeline
- [ ] Contabilidad AR configurada
- [ ] Turnos/Calendario funcionando
- [ ] Portal configurado (acceso para profesionales)
- [ ] Video de backup grabado

---

## 5. Accesos Demo

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin@asinmet.com | [demo] | Administrador / Gerencia |
| recepcion@asinmet.com | [demo] | Recepción |
| comercial@asinmet.com | [demo] | Comercial / CRM |
| contable@asinmet.com | [demo] | Contable |
| medicina@asinmet.com | [demo] | Encargada Medicina |
| dr.mendez@portal | [demo] | Médico auditor (portal) |
