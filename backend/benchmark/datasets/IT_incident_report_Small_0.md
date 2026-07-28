# Incident Report

## Incident ID: **INC-20231026-001**

*   **Date/Time Reported:** 2023-10-26 09:15 AM PST
*   **Date/Time Resolved:** 2023-10-26 10:05 AM PST
*   **Reported By:** Sarah Chen (Marketing Department)
*   **Service Affected:** Marketing Shared Drive (\\nexuscorp-fs01\MarketingShare)
*   **Impact Level:** **Medium** - Localized disruption preventing essential file access for one department.

---

### Incident Summary

The Marketing department's primary shared network drive became intermittently inaccessible for approximately 50 minutes, preventing users from accessing critical project files and collaborate effectively.

### Detailed Description

At 09:15 AM PST, multiple users in the Marketing department reported an inability to connect to or access files on their primary shared network drive. Attempts to browse the share resulted in "Network path not found" or significantly delayed connections. Other network services and shared drives on the same file server (`nexuscorp-fs01`) remained unaffected. Initial troubleshooting confirmed the issue was isolated to the `MarketingShare` volume.

### Root Cause

The issue was traced to a **stuck Server Message Block (SMB) session** specifically impacting the `MarketingShare` volume on `nexuscorp-fs01`. This was likely triggered by an abrupt client disconnection during a large file operation, exhausting available session handlers for that particular share.

### Resolution Steps

1.  Confirmed issue isolation to the `MarketingShare`.
2.  Attempted to clear active SMB sessions on `nexuscorp-fs01` via administrative PowerShell, which yielded no immediate change.
3.  **Restarted the SMB service** on `nexuscorp-fs01` at 09:55 AM PST.
4.  Verified access and functionality for multiple Marketing users.
5.  Confirmed full resolution and restored functionality at 10:05 AM PST.

### Follow-up Actions & Recommendations

*   **Review server event logs** for `nexuscorp-fs01` for any recurring patterns or precursors to stuck SMB sessions.
*   **Investigate increasing SMB session limits** or implementing more robust session management policies on file servers.
*   Communicate resolution to the affected Marketing department.