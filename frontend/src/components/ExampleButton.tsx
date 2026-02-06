import { cn } from "@/lib/utils";

interface ExampleButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  className?: string;
}

export function ExampleButton({ children, onClick, className }: ExampleButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "px-3 py-1.5 text-sm font-medium rounded-full",
        "bg-secondary text-secondary-foreground",
        "border border-border",
        "hover:bg-primary/10 hover:border-primary/30 hover:text-primary",
        "transition-all duration-200",
        className
      )}
    >
      {children}
    </button>
  );
}
