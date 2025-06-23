"use client";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
  variant?: "primary" | "secondary" | "active" | "ghost";
  size?: "sm" | "md" | "lg";
  "aria-pressed"?: boolean;
  "aria-label"?: string;
  tabIndex?: number;
}

const baseStyles =
  "flex items-center justify-center rounded-[16px] font-mono font-medium transition-all duration-200 ease-in-out";

const variants = {
  primary:
    "text-[#171717] bg-weird-gradient hover:shadow-[0_0_8px_#B9E55A] hover:scale-[1.02] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:scale-100",
  secondary:
    "bg-[#383838] text-[white] hover:shadow-[0_0_16px_#B9E55A] hover:scale-[1.02] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:scale-100",
  active:
    "text-[#171717] bg-weird-gradient scale-[1.03] cursor-pointer hover:shadow-[0_0_16px_#B9E55A] disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:scale-100",
  ghost:
    "bg-transparent border border-[#B9E55A] text-[#B9E55A] hover:bg-[#B9E55A] hover:text-dark-gray focus:bg-[#B9E55A] focus:text-dark-gray disabled:opacity-50 disabled:cursor-not-allowed disabled:text-gray-500 disabled:border-gray-500 disabled:bg-transparent",
};

const sizes = {
  sm: "text-sm px-3 py-2",
  md: "text-base px-8 py-4",
  lg: "text-lg px-8 py-4",
};

export function Button({
  children,
  disabled,
  onClick,
  className = "",
  variant = "primary",
  size = "md",
  "aria-pressed": ariaPressed,
  "aria-label": ariaLabel,
  tabIndex = 0,
}: ButtonProps) {
  const handleClick = () => {
    if (!disabled && onClick) {
      onClick();
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      aria-pressed={ariaPressed}
      aria-label={
        ariaLabel ?? (typeof children === "string" ? children : undefined)
      }
      tabIndex={disabled ? -1 : tabIndex}
      aria-disabled={disabled}
    >
      {children}
    </button>
  );
}
