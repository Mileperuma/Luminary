import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
  loading?: boolean;
}

export default function Button({
  variant = "primary",
  loading,
  children,
  disabled,
  className = "",
  ...rest
}: ButtonProps) {
  const base =
    "w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors duration-150 " +
    "disabled:opacity-50 disabled:cursor-not-allowed";
  const styles =
    variant === "primary"
      ? "bg-ink text-cream hover:bg-ink/90"
      : "bg-transparent text-ink border border-line hover:border-ink";
  return (
    <button
      className={`${base} ${styles} ${className}`}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? "Please wait…" : children}
    </button>
  );
}
