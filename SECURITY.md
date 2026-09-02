# Security policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability or exposed secret. Use the private security-reporting channel configured on the VirtuJudge GitHub organization. Until that channel is configured, contact the repository owners privately and avoid including real user media, documents, transcripts, tokens, or credentials in the first message.

Include the affected component/version, impact, safe reproduction steps, and any suggested mitigation. Use synthetic data where possible.

## Supported versions

During the MVP, only the current `main` branch and current staging release receive security fixes. A version support table should replace this statement once tagged releases exist.

## Project security boundaries

- Customer media and documents are private and must not be attached to public issues.
- Invitation, bearer, object-storage, and provider tokens are secrets.
- Model output is untrusted and must pass schema, evidence, ownership, and bounds validation.
- A public identifier is not authorization; every resource is checked through Team ownership.
- Customer content is not used to train models.

See [Security, Privacy, and Retention](./Architecture/Security-Privacy-and-Retention.md) for the current design.
