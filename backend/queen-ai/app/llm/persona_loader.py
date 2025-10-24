from pathlib import Path
from typing import Optional

from app.config.settings import settings


def _resolve_persona_path() -> Optional[Path]:
    """Try likely locations for the persona file."""
    fname = settings.PERSONA_FILE or "QUEEN_PERSONALITY.md"
    candidates = [
        Path(fname),
        Path(__file__).resolve().parents[5] / fname,  # repo root fallback
        Path(__file__).resolve().parents[4] / fname,  # backend root fallback
        Path(__file__).resolve().parents[2] / fname,  # app root fallback
    ]
    for p in candidates:
        try:
            if p and p.exists() and p.is_file():
                return p
        except Exception:
            continue
    return None


def _default_header() -> str:
    return (
        "You are Queen AI of the OMK Hive (senior architect and orchestrator). "
        "Prime directives: safety (protected files, no secrets, on-chain guardrails), "
        "truthful with citations, concise with next actions, delegate to specialized bees, "
        "and persist memory of rules and decisions. Tone: calm, precise, supportive."
    )


def _extract_between(text: str, start_marker: str) -> str:
    idx = text.find(start_marker)
    if idx == -1:
        return ""
    return text[idx: idx + 1000]


def get_persona_header() -> str:
    """Return a concise header derived from QUEEN_PERSONALITY.md with safe fallback."""
    path = _resolve_persona_path()
    if not path:
        return _default_header()

    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")

        # Heuristic: pull Identity and Prime Directives bullets to craft a 1–2 sentence header
        ident = _extract_between(raw, "## 1) Identity")
        primes = _extract_between(raw, "## 3) Prime Directives")

        role_line = "Queen AI of the OMK Hive (senior architect and orchestrator)"
        if "Role:" in ident:
            for line in ident.splitlines():
                if line.strip().startswith("- Role:"):
                    role_line = line.split(":", 1)[1].strip()
                    break

        # Collect 3 prime directives bullets
        prime_bullets = []
        for line in primes.splitlines():
            t = line.strip()
            if t.startswith("-"):
                prime_bullets.append(t.lstrip("- "))
            if len(prime_bullets) >= 3:
                break

        primes_sentence = "; ".join(prime_bullets) if prime_bullets else (
            "safety, truth with citations, concise next actions, correct delegation, and memory persistence"
        )

        header = (
            f"You are Queen AI of the OMK Hive (senior architect and orchestrator). "
            f"Role: {role_line}. Prime directives: {primes_sentence}. "
            f"Tone: calm, precise, supportive."
        )
        # Keep it short
        return header[:600]
    except Exception:
        return _default_header()
