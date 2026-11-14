# LUMENIA — Arquitectura objetivo

## Estado
El portal inicial es estático y no tiene login, pagos, evaluaciones ni certificados operativos.

## Roadmap
1. Frontend y catálogo preliminar (implementado).
2. Backend PostgreSQL y autenticación con roles: alumno, docente, administrador.
3. Gestión de cursos, módulos, lecciones, matrículas y progreso.
4. Evaluaciones: banco de preguntas, intentos, puntuación y aprobación.
5. Certificados PDF privados con identificador único, QR y verificación pública.
6. Pagos con Mercado Pago y webhooks validados en servidor.
7. Importación de Google Drive de solo lectura, revisión de derechos y trazabilidad.

## Entidades previstas
users, roles, courses, modules, lessons, enrollments, lesson_progress, question_banks, questions, choices, exam_attempts, answers, certificates, payments, source_documents, audit_events.

## Seguridad
Validar autorización en servidor, restringir materiales a alumnos matriculados, no exponer tokens de Drive, usar variables de entorno y registro de auditoría.

## Editorial
No distribuir documentos ajenos sin licencia. No atribuir reconocimiento oficial a certificados privados ni eficacia clínica no demostrada a prácticas tradicionales.
