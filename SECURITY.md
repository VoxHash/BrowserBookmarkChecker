# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **contact@voxhash.dev**. You will receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What NOT to Do

- Do not open a public GitHub issue
- Do not disclose the vulnerability publicly until it has been addressed

## Security Best Practices

This tool processes bookmark files locally and does not:
- Send data over the network
- Store bookmarks in cloud services
- Collect telemetry or usage statistics
- Access external APIs without user consent

All processing is done offline on the user's machine.
