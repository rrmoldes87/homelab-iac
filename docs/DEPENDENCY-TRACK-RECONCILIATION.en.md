# DependencyTrack — 2026-11-20

Read-only reconciliation, not another migration: all three source Deployments have zero replicas and both PVCs remain Bound. Backend and PostgreSQL were already cold-restored on VM103 using exact images, matching hashes and verified tables. Stale API/DB flags and frontend scope were corrected. HTTPS/direct API, runtime images and database tables were checked without restarts. Authenticated login, restart durability and current-data rollback remain untested. No acceptance rerun or additional writer.

Configuration: `3f51851b6d5e224c3f7eeeb909d2d69c8fe9bd36`. Routing: `1e23dd441420baccbed803fd1d67bcb96450c6b8`.
