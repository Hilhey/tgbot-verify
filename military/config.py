"""Konfigurasi verifikasi militer SheerID"""

SHEERID_BASE_URL = "https://services.sheerid.com"

MILITARY_STATUS = "VETERAN"

MILITARY_ORGANIZATIONS = [
    {
        "id": 4070,
        "idExtended": "4070",
        "name": "Army",
        "country": "US",
        "type": "MILITARY",
    },
    {
        "id": 4073,
        "idExtended": "4073",
        "name": "Air Force",
        "country": "US",
        "type": "MILITARY",
    },
    {
        "id": 4072,
        "idExtended": "4072",
        "name": "Navy",
        "country": "US",
        "type": "MILITARY",
    },
    {
        "id": 4071,
        "idExtended": "4071",
        "name": "Marine Corps",
        "country": "US",
        "type": "MILITARY",
    },
    {
        "id": 4074,
        "idExtended": "4074",
        "name": "Coast Guard",
        "country": "US",
        "type": "MILITARY",
    },
    {
        "id": 4544268,
        "idExtended": "4544268",
        "name": "Space Force",
        "country": "US",
        "type": "MILITARY",
    },
]

ORGANIZATION_BY_NAME = {org["name"]: org for org in MILITARY_ORGANIZATIONS}

SUBMISSION_FLAGS = (
    '{"doc-upload-considerations":"default","doc-upload-may24":"default",'
    '"doc-upload-redesign-use-legacy-message-keys":false,'
    '"docUpload-assertion-checklist":"default","include-cvec-field-france-student":"not-labeled-optional",'
    '"org-search-overlay":"default","org-selected-display":"default"}'
)

SUBMISSION_OPT_IN = (
    "By submitting the personal information above, I acknowledge that my personal information "
    "is being collected under the <a target=\"_blank\" rel=\"noopener noreferrer\" class=\"sid-privacy-policy "
    "sid-link\" href=\"https://openai.com/policies/privacy-policy/\">privacy policy</a> of the business "
    "from which I am seeking a discount, and I understand that my personal information will be shared "
    "with SheerID as a processor/third-party service provider in order for SheerID to confirm my "
    "eligibility for a special offer. Contact OpenAI Support for further assistance at support@openai.com"
)

TEMPMAIL_API_BASE = "https://www.1secmail.com/api/v1/"
TEMPMAIL_POLL_INTERVAL = 5
TEMPMAIL_POLL_TIMEOUT = 120
