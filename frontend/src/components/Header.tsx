import { Shield } from "lucide-react";

export function Header() {
  return (
    <header className="gradient-header text-primary-foreground py-8 px-4">
      <div className="container max-w-3xl mx-auto text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/10 backdrop-blur-sm mb-4 animate-float">
          <Shield className="w-8 h-8" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">
          🛡️ 사기 탐지 AI 에이전트
        </h1>
        <p className="text-primary-foreground/80 text-sm sm:text-base">
          의심스러운 메시지를 분석하여 사기 여부를 판단합니다
        </p>
      </div>
    </header>
  );
}
