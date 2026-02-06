import { useState } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { ExampleButton } from "./ExampleButton";
import { Loader2, Search, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

interface MessageFormProps {
  onSubmit: (message: string, sender: string) => void;
  isLoading: boolean;
  className?: string;
}

const examples = [
  {
    label: "보이스피싱",
    message: "금융감독원입니다. 귀하의 계좌가 범죄에 연루되어 안전계좌로 이체해야 합니다. 지금 바로 아래 계좌로 송금하세요.",
    sender: "02-1234-5678",
  },
  {
    label: "대출사기",
    message: "저금리 대출 가능! 신용등급 상관없이 최대 5천만원까지 당일 대출 가능합니다. 수수료 선입금 후 바로 대출 실행됩니다.",
    sender: "010-9999-8888",
  },
  {
    label: "정상 메시지",
    message: "안녕하세요, 배송 예정 안내드립니다. 주문하신 상품이 내일 도착 예정입니다. 문의사항은 고객센터 1588-1234로 연락주세요.",
    sender: "1588-1234",
  },
];

export function MessageForm({ onSubmit, isLoading, className }: MessageFormProps) {
  const [message, setMessage] = useState("");
  const [sender, setSender] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSubmit(message, sender);
    }
  };

  const handleExample = (example: typeof examples[0]) => {
    setMessage(example.message);
    setSender(example.sender);
  };

  return (
    <div className={cn("bg-card rounded-xl shadow-card p-6", className)}>
      <h2 className="flex items-center gap-2 text-xl font-bold text-card-foreground mb-6">
        📱 메시지 분석
      </h2>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="message" className="text-sm font-medium">
            의심 메시지 <span className="text-danger">*</span>
          </Label>
          <Textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="예: 금융감독원입니다. 안전계좌로 이체하세요..."
            rows={5}
            required
            className="resize-none bg-background"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="sender" className="text-sm font-medium">
            발신자 정보 <span className="text-muted-foreground">(선택)</span>
          </Label>
          <Input
            id="sender"
            value={sender}
            onChange={(e) => setSender(e.target.value)}
            placeholder="예: 010-1234-5678 또는 02-1234-5678"
            className="bg-background"
          />
        </div>

        <Button
          type="submit"
          disabled={isLoading || !message.trim()}
          className="w-full h-12 text-base font-semibold gradient-primary hover:opacity-90 transition-opacity"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              분석 중...
            </>
          ) : (
            <>
              <Search className="w-5 h-5 mr-2" />
              분석하기
            </>
          )}
        </Button>
      </form>

      {/* Examples */}
      <div className="mt-6 pt-6 border-t border-border">
        <p className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
          <Lightbulb className="w-4 h-4" />
          예시:
        </p>
        <div className="flex flex-wrap gap-2">
          {examples.map((example) => (
            <ExampleButton
              key={example.label}
              onClick={() => handleExample(example)}
            >
              {example.label}
            </ExampleButton>
          ))}
        </div>
      </div>
    </div>
  );
}
