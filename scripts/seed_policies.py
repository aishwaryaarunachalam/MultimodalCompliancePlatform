"""
Seed the database with 5 default compliance policies.

Usage:
    cd backend
    python ../scripts/seed_policies.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import AsyncSessionLocal, init_db
from app.db import crud

DEFAULT_POLICIES = [
    {
        "name": "GDPR Data Minimisation",
        "description": "Flag content that appears to collect or share personal data beyond what is necessary.",
        "rules": [
            {"type": "keyword",  "value": "personal data",     "severity": "medium",   "description": "Data privacy keyword"},
            {"type": "keyword",  "value": "data subject",      "severity": "medium",   "description": "GDPR terminology"},
            {"type": "semantic", "value": "Collection or sharing of personal data beyond stated purpose", "severity": "high", "description": "GDPR data minimisation principle"},
        ],
    },
    {
        "name": "Hate Speech Prohibition",
        "description": "Detect content that implies superiority or inferiority based on race, ethnicity, gender, religion, or other protected characteristics.",
        "rules": [
            {"type": "semantic", "value": "Content that implies racial, ethnic, gender, or religious superiority or inferiority", "severity": "critical", "description": "Hate speech detection"},
            {"type": "semantic", "value": "Dehumanising language targeting a group of people",                                   "severity": "critical", "description": "Dehumanisation"},
        ],
    },
    {
        "name": "Unapproved Medical Claims",
        "description": "Flag misleading efficacy claims, cure promises, or unsubstantiated health statements.",
        "rules": [
            {"type": "regex",    "value": r"\b(cure[sd]?|guaranteed\s+to|100\%\s+effective|proven\s+to\s+cure)\b", "severity": "high",   "description": "Absolute efficacy claim"},
            {"type": "keyword",  "value": "treats cancer",    "severity": "critical", "description": "Unsubstantiated cancer claim"},
            {"type": "keyword",  "value": "FDA approved",     "severity": "high",     "description": "Potentially false FDA claim"},
            {"type": "semantic", "value": "Medical treatment claims without scientific backing or regulatory approval", "severity": "high", "description": "Unsubstantiated health claim"},
        ],
    },
    {
        "name": "Misleading Financial Claims",
        "description": "Detect promises of guaranteed returns, misleading investment performance, or unlicensed financial advice.",
        "rules": [
            {"type": "regex",    "value": r"\bguaranteed\s+(return|profit|income|yield)\b",  "severity": "high",   "description": "Guaranteed return claim"},
            {"type": "keyword",  "value": "risk-free investment", "severity": "high",        "description": "Risk-free investment claim"},
            {"type": "semantic", "value": "Promises of guaranteed financial returns or risk-free investments without disclaimers", "severity": "high", "description": "Misleading investment claim"},
        ],
    },
    {
        "name": "Prompt Injection Detection",
        "description": "Detect attempts to manipulate AI systems via injected instructions in uploaded documents.",
        "rules": [
            {"type": "keyword",  "value": "ignore previous instructions", "severity": "critical", "description": "Classic prompt injection"},
            {"type": "keyword",  "value": "disregard your instructions",  "severity": "critical", "description": "Prompt override attempt"},
            {"type": "regex",    "value": r"\bact\s+as\s+(a\s+)?(?:DAN|evil|unfiltered)\b", "severity": "critical", "description": "Jailbreak pattern"},
            {"type": "semantic", "value": "Instructions attempting to override AI system directives or extract system prompts", "severity": "critical", "description": "Prompt injection"},
        ],
    },
]


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        existing = await crud.list_policies(db)
        existing_names = {p.name for p in existing}

        created = 0
        for policy_data in DEFAULT_POLICIES:
            if policy_data["name"] in existing_names:
                print(f"  ✓ Already exists: {policy_data['name']}")
                continue
            await crud.create_policy(
                db,
                name=policy_data["name"],
                description=policy_data["description"],
                rules=policy_data["rules"],
                is_active=True,
            )
            created += 1
            print(f"  + Created: {policy_data['name']} ({len(policy_data['rules'])} rules)")

        await db.commit()

    print(f"\nDone. {created} new policies created.")


if __name__ == "__main__":
    asyncio.run(seed())
