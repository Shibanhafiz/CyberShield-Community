# Limitations (stated plainly —also in README)

1. ML baseline trained on 100 dev messages (accuracy 0.65): pipeline
   check, not product accuracy; 2 classes score F1 0.00.
2. Risk scores are an uncalibrated heuristic, not fraud probabilities.
3. Static URL analysis cannot prove maliciousness or safety.
4. Community reports are unverified user observations.
5. Awareness deltas measure quiz performance, not real-world immunity.
6. No field evidence collected yet — no impact claim exists.
7. Per-process rate limits (proxy must enforce); no JWT revocation list
   (60-min expiry instead); Python-side aggregation at scale.
8. No local Postgres staging, no Docker image builds, no real-device
   pass performed in the build environment (all documented, none faked).
9. No retention auto-purge; no backup infrastructure running here.
