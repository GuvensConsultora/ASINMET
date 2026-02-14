{
    'name': 'ASINMET - Medicina Laboral',
    'version': '19.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Gestión de exámenes preocupacionales y postocupacionales',
    'description': """
        Módulo de medicina laboral para ASINMET.
        Gestión completa de exámenes médicos ocupacionales:
        - Preocupacionales, periódicos, egreso
        - Múltiples estudios por orden
        - Certificado de aptitud con firma
        - Basado en HL7 FHIR + Legislación SRT Argentina
    """,
    'author': 'Guvens Consultora',
    'website': 'https://guvens.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
        'calendar',
        'account',
        'mail',
        'portal',
    ],
    'data': [
        # Seguridad primero
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        # Datos iniciales
        'data/medical_sequence_data.xml',
        'data/medical_specialty_data.xml',
        'data/medical_study_type_data.xml',
        # Vistas
        'views/medical_specialty_views.xml',
        'views/medical_patient_views.xml',
        'views/medical_practitioner_views.xml',
        'views/medical_study_type_views.xml',
        'views/medical_examination_template_views.xml',
        'views/medical_examination_order_views.xml',
        'views/medical_study_request_views.xml',
        'views/medical_study_result_views.xml',
        'views/medical_certificate_views.xml',
        'views/medical_menus.xml',
        # Reportes
        'report/medical_certificate_report.xml',
        'report/medical_certificate_templates.xml',
    ],
    'installable': True,
    'application': True,
}
