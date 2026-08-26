import os
from app.models.manager import model_manager

class RiskIntelligenceService:
    def __init__(self):
        self.critical_keywords = ["kill", "die", "bomb", "attack", "destroy", "revenge", "weapon", "end it"]
        self.moderate_keywords = ["hate", "angry", "never", "always", "suffer"]

    def analyze_payload(self, text: str) -> dict:
        mode = os.getenv("AI_MODE", "real").lower()
        
        if mode == "real":
            nlp_pipe = model_manager.get_nlp_pipeline()
            nlp_result = nlp_pipe(text)[0]
            label = nlp_result["label"]
            score = float(nlp_result["score"])
        else:
            label = "NEGATIVE" if any(w in text.lower() for w in self.critical_keywords) else "POSITIVE"
            score = 0.85

        if label.upper() == "NEGATIVE":
            base_risk = 50.0 + (score * 50.0)
        else:
            base_risk = (1.0 - score) * 30.0

        text_lower = text.lower()
        multiplier = 1.0
        flags = []

        for word in self.critical_keywords:
            if word in text_lower:
                multiplier += 0.3
                flags.append(f"Critical threat marker: '{word}'")

        for word in self.moderate_keywords:
            if word in text_lower:
                multiplier += 0.1
                flags.append(f"Stress marker: '{word}'")

        final_score = min(round(base_risk * multiplier, 2), 100.0)

        if final_score >= 85:
            level = "CRITICAL"
        elif final_score >= 65:
            level = "HIGH"
        elif final_score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"

        if not flags:
            flags.append("No explicit behavioral markers detected.")

        return {
            "mode": mode,
            "sentiment": {
                "label": label,
                "confidence": round(score, 4)
            },
            "risk_analysis": {
                "score": final_score,
                "level": level,
                "reasoning": flags
            }
        }

risk_service = RiskIntelligenceService()
