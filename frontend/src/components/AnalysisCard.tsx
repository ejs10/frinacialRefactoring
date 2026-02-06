import { cn } from "@/lib/utils";
import { RiskBadge, RiskLevel } from "./RiskBadge";
import { RiskScoreBar } from "./RiskScoreBar";
import { AlertTriangle, BarChart3, Clock, FileSearch, RotateCcw } from "lucide-react";
import { Button } from "./ui/button";

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

interface AnalysisCardProps {
  result: AnalysisResult;
  onReset: () => void;
  className?: string;
}

export function AnalysisCard({ result, onReset, className }: AnalysisCardProps) {
  return (
    <div className={cn("bg-card rounded-xl shadow-card p-6 space-y-6", className)}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <RiskBadge level={result.riskLevel} />
        <div className="flex-1">
          <h2 className="text-xl font-bold text-card-foreground">
            {result.isScam ? "사기로 판단됩니다" : "정상 메시지입니다"}
          </h2>
          <p className="text-sm text-muted-foreground mt-1 flex flex-wrap gap-x-3 gap-y-1">
            <span>사기 유형: <strong className="text-card-foreground">{result.scamType}</strong></span>
            <span>신뢰도: <strong className="text-card-foreground">{result.confidence}%</strong></span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {result.processingTime}
            </span>
          </p>
        </div>
      </div>

      {/* Risk Score */}
      <RiskScoreBar score={result.riskScore} />

      {/* Risk Factors */}
      {result.riskFactors.length > 0 && (
        <div className="space-y-3">
          <h3 className="flex items-center gap-2 font-semibold text-card-foreground">
            <AlertTriangle className="w-5 h-5 text-warning" />
            감지된 위험 요인
          </h3>
          <ul className="space-y-2">
            {result.riskFactors.map((factor, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm text-muted-foreground bg-warning/5 border border-warning/20 rounded-lg px-3 py-2"
              >
                <span className="text-warning font-bold">•</span>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* AI Analysis */}
      <div className="space-y-3">
        <h3 className="flex items-center gap-2 font-semibold text-card-foreground">
          <FileSearch className="w-5 h-5 text-primary" />
          AI 종합 분석
        </h3>
        <div className="bg-primary/5 border border-primary/10 rounded-lg p-4">
          <p className="text-sm text-card-foreground leading-relaxed whitespace-pre-wrap">
            {result.analysis}
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-muted/50 rounded-lg p-4 text-center">
          <div className="flex items-center justify-center gap-2 text-muted-foreground text-sm mb-1">
            <BarChart3 className="w-4 h-4" />
            매칭된 패턴
          </div>
          <div className="text-2xl font-bold text-primary">{result.patternsCount}</div>
        </div>
        <div className="bg-muted/50 rounded-lg p-4 text-center">
          <div className="flex items-center justify-center gap-2 text-muted-foreground text-sm mb-1">
            <FileSearch className="w-4 h-4" />
            유사 사례
          </div>
          <div className="text-2xl font-bold text-primary">{result.casesCount}</div>
        </div>
      </div>

      {/* Reset Button */}
      <Button
        onClick={onReset}
        variant="outline"
        className="w-full"
      >
        <RotateCcw className="w-4 h-4 mr-2" />
        새로운 메시지 분석하기
      </Button>
    </div>
  );
}
