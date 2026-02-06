import { ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-card border-t border-border py-6 px-4 mt-auto">
      <div className="container max-w-3xl mx-auto text-center space-y-3">
        <p className="text-sm text-muted-foreground">
          &copy; 2024 사기 탐지 AI 에이전트 | Powered by LangGraph & Upstage Solar
        </p>
        <div className="flex justify-center gap-4 text-sm">
          <a
            href="https://www.police.go.kr"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-primary transition-colors inline-flex items-center gap-1"
          >
            경찰청
            <ExternalLink className="w-3 h-3" />
          </a>
          <a
            href="https://www.fss.or.kr"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-primary transition-colors inline-flex items-center gap-1"
          >
            금융감독원
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </footer>
  );
}
