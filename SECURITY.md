# Security policy

Do not report a vulnerability or exposed credential in a public issue. Contact the maintainers privately through the repository owner and include only the minimum reproduction information required.

## Sensitive configuration

The following must remain outside Git:

- MariaDB credentials and database dumps;
- `JWT_SECRET` and issued tokens;
- Firebase Admin service-account files and device tokens;
- `google-services.json` for privately managed Firebase projects;
- SSH keys and CI/CD secrets.

If any credential has appeared in a commit, documentation file, log, artifact, or screenshot, removing the current file is not sufficient. Rotate the credential first, then remove it from history using GitHub's documented sensitive-data procedure and coordinate with every contributor who has a clone.

The historical course deployment is not a supported security target. Use new infrastructure, least-privilege credentials, and synthetic data for any demonstration environment.
