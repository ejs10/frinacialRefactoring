import { cn } from "@/lib/utils";
import { Shield, ShieldAlert, ShieldCheck, ShieldQuestion } from "lucide-react";

export type RiskLevel = "very_high" | "high" | "medium" | "low" | "safe";

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
}

const riskConfig: Record<RiskLevel, { 
  label: string; 
  icon: typeof ShieldAlert; 
  bgClass: string;
  textClass: string;
  ringClass: string;
}> = {
  very_high: {
    label: "매우높음",
    icon: ShieldAlert,
    bgClass: "gradient-danger",
    textClass: "text-danger-foreground",
    ringClass: "bg-danger/30",
  },
  high: {
    label: "높음",
    icon: ShieldAlert,
    bgClass: "bg-danger",
    textClass: "text-danger-foreground",
    ringClass: "bg-danger/30",
  },
  medium: {
    label: "주의",
    icon: ShieldQuestion,
    bgClass: "gradient-warning",
    textClass: "text-warning-foreground",
    ringClass: "bg-warning/30",
  },
  low: {
    label: "낮음",
    icon: Shield,
    bgClass: "bg-success/80",
    textClass: "text-success-foreground",
    ringClass: "bg-success/30",
  },
  safe: {
    label: "안전",
    icon: ShieldCheck,
    bgClass: "gradient-success",
    textClass: "text-success-foreground",
    ringClass: "bg-success/30",
  },
};

export function RiskBadge({ level, className }: RiskBadgeProps) {
  const config = riskConfig[level];
  const Icon = config.icon;

  return (
    <div className={cn("relative inline-flex items-center gap-2", className)}>
      {/* Pulse ring for high risk */}
      {(level === "very_high" || level === "high") && (
        <span className={cn(
          "absolute inset-0 rounded-full animate-pulse-ring",
          config.ringClass
        )} />
      )}
      <div className={cn(
        "relative flex items-center gap-2 px-4 py-2 rounded-full font-semibold",
        config.bgClass,
        config.textClass
      )}>
        <Icon className="w-5 h-5" />
        <span>{config.label}</span>
      </div>
    </div>
  );
}
