import { useState } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { MessageForm } from "@/components/MessageForm";
import { AnalysisCard } from "@/components/AnalysisCard";
import { RiskLevel } from "@/components/RiskBadge";
import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface AnalysisResult {
  isScam: boolean;
  riskLevel: RiskLevel;
  riskScore: number;
  scamType: string;
  confidence: number;
  processingTime: string;
  riskFactors: string[];
  analysis: string;
  patternsCount: number;
  casesCount: number;
}

// Map Korean risk level to RiskLevel type
const mapRiskLevel = (level: string): RiskLevel => {
  switch (level) {
    case "매우높음":
      return "very_high";
    case "높음":
      return "high";
    case "보통":
      return "medium";
    case "낮음":
      return "low";
    default:
      return "safe";
  }
};

const analyzeMessage = async (message: string, sender: string): Promise<AnalysisResult> => {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const response = await fetch(`${API_BASE_URL}/api/v1/detect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, sender })
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.error || "분석 중 오류가 발생했습니다.");
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || "분석에 실패했습니다.");
  }

  return {
    isScam: data.is_scam,
    riskLevel: mapRiskLevel(data.risk_level),
    riskScore: data.risk_score,
    scamType: data.scam_type,
    confidence: Math.round(data.confidence * 100),
    processingTime: `${data.processing_time}초`,
    riskFactors: data.risk_factors || [],
    analysis: data.analysis,
    patternsCount: data.matched_patterns_count || 0,
    casesCount: data.similar_cases_count || 0,
  };
};

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (message: string, sender: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await analyzeMessage(message, sender);
      setResult(analysisResult);
      toast.success("분석이 완료되었습니다!");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "분석 중 오류가 발생했습니다.";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />

      <main className="flex-1 container max-w-3xl mx-auto px-4 py-8 space-y-6">
        {!result && !error && (
          <MessageForm onSubmit={handleSubmit} isLoading={isLoading} />
        )}

        {result && (
          <AnalysisCard result={result} onReset={handleReset} />
        )}

        {error && (
          <div className="bg-card rounded-xl shadow-card p-6 border border-danger/20">
            <div className="flex items-start gap-3 text-danger mb-4">
              <AlertCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-lg">오류 발생</h3>
                <p className="text-sm text-muted-foreground mt-1">{error}</p>
              </div>
            </div>
            <Button onClick={handleReset} variant="outline" className="w-full">
              <RotateCcw className="w-4 h-4 mr-2" />
              다시 시도하기
            </Button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default Index;
