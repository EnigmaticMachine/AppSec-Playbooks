# Scenario 01: Tenant Hopping (Mass Assignment)

**Severity:** High (Critical Data Leakage)
**Vulnerability Type:** Logic Flaw / Mass Assignment / IDOR
**App Context:** "MediVault" - A Multi-Tenant SaaS for Medical Clinics.

---

## 1. The Scenario: MediVault

**MediVault** is a SaaS platform that allows doctors to manage their patient records. To keep costs low, the platform uses a **Shared Database** architecture. All clinics live in the same database tables, separated only by a `tenant_id` column.

### The Architecture


* **Tenant A:** "Downtown Clinic" (Dr. Alice).
* **Tenant B:** "Uptown Urgent Care" (Dr. Bob).
* **The Guardrail:** The application uses Django Admin as the dashboard. A custom filter (`get_queryset`) ensures Dr. Bob only sees patients belonging to Uptown Urgent Care.

### The Actors
1.  **Dr. Alice (Victim):** Has private patient data in Tenant ID `1`.
2.  **Dr. Bob (Attacker):** A legitimate user of the system (Tenant ID `2`) who wants to steal Alice's patient list.

---

## 2. The Vulnerability

The developer, in a rush to ship the "Edit Profile" feature, made a classic **Mass Assignment** mistake.

While they implemented a **Read Filter** (Dr. Bob can't *see* Tenant 1's data), they failed to implement a **Write Filter**. The Django Admin, by default, binds all POST data to the model instance.

If Dr. Bob intercepts the "Save Profile" request and manually injects `tenant=1`, the application will blindly accept it, effectively moving Dr. Bob's user account into Dr. Alice's clinic.

---

## 3. The Exploit

1.  **Intercept the Request:** Use a proxy like Burp Suite or Caido to intercept Dr. Bob's "Save Profile" request.
2.  **Inject Tenant ID:** Modify the request to include `tenant=1` (Dr. Alice's tenant).
3.  **Submit the Request:** Send the modified request to the server.
