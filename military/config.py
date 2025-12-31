"""SheerID military verification configuration."""

# SheerID API configuration
# Update PROGRAM_ID to the latest military programId before running.
PROGRAM_ID = "CHANGE_ME"
SHEERID_BASE_URL = "https://services.sheerid.com"
MY_SHEERID_URL = "https://my.sheerid.com"

# File size limits
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# Military branch configuration (replace IDs with valid organization IDs if required)
BRANCHES = {
    "US Army": {
        "id": 101,
        "idExtended": "101",
        "name": "US Army",
        "country": "US",
        "type": "MILITARY",
        "domain": "army.mil",
    },
    "US Navy": {
        "id": 102,
        "idExtended": "102",
        "name": "US Navy",
        "country": "US",
        "type": "MILITARY",
        "domain": "navy.mil",
    },
    "US Air Force": {
        "id": 103,
        "idExtended": "103",
        "name": "US Air Force",
        "country": "US",
        "type": "MILITARY",
        "domain": "us.af.mil",
    },
    "US Marine Corps": {
        "id": 104,
        "idExtended": "104",
        "name": "US Marine Corps",
        "country": "US",
        "type": "MILITARY",
        "domain": "usmc.mil",
    },
    "US Coast Guard": {
        "id": 105,
        "idExtended": "105",
        "name": "US Coast Guard",
        "country": "US",
        "type": "MILITARY",
        "domain": "uscg.mil",
    },
}

DEFAULT_BRANCH_NAME = "US Army"
