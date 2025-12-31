"""SheerID military verification configuration."""

# SheerID API configuration
# Update PROGRAM_ID to the latest military programId before running.
PROGRAM_ID = "CHANGE_ME"
SHEERID_BASE_URL = "https://services.sheerid.com"
MY_SHEERID_URL = "https://my.sheerid.com"

# File size limits
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# Military branch configuration (ChatGPT military program)
BRANCHES = {
    "US Army": {
        "id": 4070,
        "idExtended": "4070",
        "name": "Army",
        "country": "US",
        "type": "MILITARY",
        "domain": "army.mil",
    },
    "US Air Force": {
        "id": 4073,
        "idExtended": "4073",
        "name": "Air Force",
        "country": "US",
        "type": "MILITARY",
        "domain": "us.af.mil",
    },
    "US Navy": {
        "id": 4072,
        "idExtended": "4072",
        "name": "Navy",
        "country": "US",
        "type": "MILITARY",
        "domain": "navy.mil",
    },
    "US Marine Corps": {
        "id": 4071,
        "idExtended": "4071",
        "name": "Marine Corps",
        "country": "US",
        "type": "MILITARY",
        "domain": "usmc.mil",
    },
    "US Coast Guard": {
        "id": 4074,
        "idExtended": "4074",
        "name": "Coast Guard",
        "country": "US",
        "type": "MILITARY",
        "domain": "uscg.mil",
    },
    "US Space Force": {
        "id": 4544268,
        "idExtended": "4544268",
        "name": "Space Force",
        "country": "US",
        "type": "MILITARY",
        "domain": "spaceforce.mil",
    },
}

DEFAULT_BRANCH_NAME = "US Army"

DEFAULT_STATUS = "VETERAN"
