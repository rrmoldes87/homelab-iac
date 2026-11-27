# DependencyTrack — 2026-11-20

Reconciliación sin nueva migración: los tres Deployment origen están a cero y los dos PVC siguen Bound. Backend y PostgreSQL ya fueron restaurados en frío en VM103 con imágenes exactas, hashes iguales y tablas verificadas. Se corrigieron los flags atrasados de API/DB y el alcance antiguo del frontend. API HTTPS y directa, imágenes y tablas comprobadas ahora sin reinicios. Login autenticado, durabilidad tras reinicio y rollback con datos actuales siguen sin probar. No se repite aceptación ni se inicia otro escritor.

Configuration: `3f51851b6d5e224c3f7eeeb909d2d69c8fe9bd36`. Routing: `1e23dd441420baccbed803fd1d67bcb96450c6b8`.
