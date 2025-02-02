"""Constants used throughout the application"""

# Scam Types
SCAM_TYPES = [
    "FAKE_AUTHORITY",
    "UPI_SCAM",
    "OTP_FRAUD",
    "FAKE_SELLER",
    "PHISHING",
    "VIDEO_CALL",
    "BANK_FRAUD",
    "JOB_SCAM",
    "LOTTERY_SCAM",
    "IDENTITY_THEFT"
]

# Prompts
ANALYSIS_PROMPT = """
Analyze the following text and determine the type of scam it describes.
Available scam types:
{scam_types}

Text to analyze:
{text}

For each possible scam type, provide a confidence score between 0 and 1.
Format your response as:
SCAM_TYPE: confidence_score
"""

# API Settings
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Noob Busts Scams"

# Security
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate Limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Monitoring
COMET_PROJECT = "noob-busts-scams"
MODEL_MONITORING_METRICS = [
    "prediction_confidence",
    "response_time",
    "error_rate"
]


