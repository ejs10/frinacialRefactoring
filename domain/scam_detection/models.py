"""사기 탐지 도메인 모델"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any

class RiskLevel(Enum):
    """위험도 단계"""
    CRITICAL = "매우높음"
    HIGH = "높음"
    MEDIUM = "중간"
    LOW = "낮음"
    SAFE = "안전"

@dataclass
class ScamPattern:
    """매칭된 사기 패턴"""
    scam_type: str
    danger_lavel: str
    mathch_keywords: List[str]
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return{
            "scam_type": self.scam_type,
            "danger_level": self.danger_level,
            "matched_keywords": self.matched_keywords,
            "confidence_score": self.confidence_score,
        }
    
@dataclass
class PatternAnalysisResult:
    """실시간 패턴 분석 결과"""
    query: str
    sender: Optional[str]
    highest_risk_level: Optional[str]
    risk_score: int
    is_high_risk: bool
    matched_patterns: List[ScamPattern] = field(default_factory=list)
    matched_keywords: Dict[str, List[str]] = field(default_factory=dict)
    legitimate_contacts: List[Dict[str, str]] = field(default_factory=list)

    def get_summary(self) -> str:
        """분석 결과 요약"""
        lines = []

        if self.highest_risk_level:
            lines.append(f"위험도: {self.highest_risk_level}")

        if self.matched_patterns:
            lines.append(f"매칭된 사기 유형: {len(self.matched_patterns)}개")
            for pattern in self.matched_patterns[:3]:
              lines.append(f"  - {pattern.scam_type} ({pattern.danger_level})")  

        if self.matched_keywords:
            lines.append("위험 키워드:")
            for level, words in list(self.matched_keywords.items())[:2]:
                lines.append(f"  - {level}: {', '.join(words[:3])}")
        
        return "\n".join(lines) if lines else "매칭된 패턴 없음"
    
@dataclass
class ScamAnalysisResponse:
    """최종 사기 분석 응답"""
    answer: str
    sources: List[Dict[str, Any]]
    pattern_analysis: PatternAnalysisult
    elapsed_time: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "sources": self.sources,
            "pattern_analysis": {
                "query": self.pattern_analysis.query,
                "sender": self.pattern_analysis.sender,
                "risk_summary": {
                    "highest_level": self.pattern_analysis.highest_risk_level,
                    "score": self.pattern_analysis.risk_score,
                    "is_high_risk": self.pattern_analysis.is_high_risk,
                },
                "scam_matches": [p.to_dict() for p in self.pattern_analysis.matched_patterns],
                "keyword_matches": self.pattern_analysis.matched_keywords,
                "legitimate_contacts": self.pattern_analysis.legitimate_contacts,
            },
            "elapsed_time": self.elapsed_time,
        }