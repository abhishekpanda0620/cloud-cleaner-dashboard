# Security Policy

## Supported Versions

We deploy critical security updates to the following versions of Cloud Cleaner Dashboard:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you have found a security vulnerability, we would appreciate it if you could report it to us privately.

**Please do not report security vulnerabilities through public GitHub issues.**

### How to Report

To report a vulnerability, please create issue on GitHub repository.

In your report, please include:

1.  A description of the vulnerability.
2.  Steps to reproduce the vulnerability.
3.  Any relevant logs or screenshots.

We will acknowledge your report within 48 hours and will work to verify and resolve the issue as quickly as possible.

## Security Best Practices

### Credentials Management

*   **Never commit credentials or secrets** to the repository (e.g., in `.env` files).
*   Use environment variables for all sensitive configuration.
*   The `.env.example` file is provided as a template and should not contain real secrets.

### Dependency Auditing

*   We use `npm audit` and `pip-audit` (or `bandit`) to regularly check for vulnerabilities in our dependencies.
*   Please ensure you run these checks before submitting a PR.
