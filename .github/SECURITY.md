# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

**Note**: As this project is currently in early development (0.1.0), we only provide security updates for the latest version. Once we reach a stable release (1.0.0+), we will maintain security support for the current major version and the previous major version.

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Instead, please report security vulnerabilities by one of the following methods:
   - Open a [GitHub Security Advisory](https://github.com/Andreas-Garcia/audiometa-python/security/advisories/new)
   - Or contact the maintainer directly (contact information available on GitHub profile)

### What to Include

When reporting a security vulnerability, please include:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Suggested fix (if you have one)
- Your contact information (so we can reach out if we need more information)

### Response Time

We will acknowledge receipt of your security report within **48 hours** and provide an initial assessment within **7 days**. We will keep you informed of our progress and work with you to address the vulnerability.

## Disclosure Policy

- We will work with you to understand and resolve the issue quickly
- We will not disclose the vulnerability publicly until a fix is available
- Once a fix is ready, we will:
  1. Release a security update
  2. Credit you (if desired) for discovering the vulnerability
  3. Publish a security advisory with details of the vulnerability and fix

## Security Best Practices

When using this library:

- Keep your dependencies up to date
- Review and validate audio file inputs before processing
- Be cautious when processing files from untrusted sources
- Follow secure coding practices when integrating this library into your applications

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.0 → 0.1.1) and will be clearly marked in the changelog.

Thank you for helping keep AudioMeta Python and its users safe!
