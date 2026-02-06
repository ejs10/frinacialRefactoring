import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

interface RiskScoreBarProps {
  score: number;
  className?: string;
}

export function RiskScoreBar({ score, className }: RiskScoreBarProps) {
  const [animatedWidth, setAnimatedWidth] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedWidth(score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  const getGradientClass = () => {
    if (score >= 80) return "gradient-danger";
    if (score >= 60) return "gradient-warning";
    if (score >= 40) return "bg-warning/70";
    return "gradient-success";
  };

  const getScoreColor = () => {
    if (score >= 80) return "text-danger";
    if (score >= 60) return "text-warning";
    if (score >= 40) return "text-warning/80";
    return "text-success";
  };

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-muted-foreground">위험도 점수</span>
        <span className={cn("text-2xl font-bold", getScoreColor())}>
          {score}
        </span>
      </div>
      <div className="h-3 bg-muted rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-1000 ease-out",
            getGradientClass()
          )}
          style={{ width: `${animatedWidth}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>안전</span>
        <span>위험</span>
      </div>
    </div>
  );
}
