# NIST SP 800-53 — Access Control (AC) Family Summary

**Synthetic demo document — abbreviated subset for ATO triage.**

## Part 1 — Family Overview
The AC family addresses authentication, authorization, account management, and session controls.

## AC-2 Account Management
- Identifies and selects account types.
- Establishes conditions for group/role membership.
- Notifies account managers of account creation, modification, disabling, removal.
- Annual recertification of access for privileged accounts.

**Applicability for ATO**: HIGH for any system with user-facing access, application service accounts, or third-party identity federation.

## AC-3 Access Enforcement
- Enforces approved authorizations for logical access to information and resources.

**Applicability for ATO**: HIGH — required for every authenticated system.

## AC-6 Least Privilege
- Employs least privilege for system access. Restricts privileged actions to authorized personnel.

**Applicability for ATO**: HIGH for any system with elevated/admin functions or production data access.

## AC-17 Remote Access
- Establishes and documents usage restrictions for remote access.
- Cryptographic mechanisms to protect confidentiality and integrity of remote sessions.

**Applicability for ATO**: HIGH if any operator or admin connects from outside the trusted network.
