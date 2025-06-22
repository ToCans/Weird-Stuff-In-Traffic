import React from "react";
import clsx from "clsx";

interface IconButtonProps {
  id?: string;
  icon: React.ReactNode;
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
  ariaLabel: string;
  className?: string;
  disabled?: boolean;
  tabIndex?: number;
  variant?: "primary" | "secondary";
  innerClassName?: string;
  borderClassName?: string;
}

export const IconButton: React.FC<IconButtonProps> = ({
  id,
  icon,
  onClick,
  ariaLabel,
  className = "",
  disabled = false,
  tabIndex = 0,
  variant = "secondary",
  innerClassName: innerClassNameProp = "bg-[#2C2C2C]",
  borderClassName: borderClassNameProp = "bg-weird-gradient",
}) => {
  const handleButtonClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled) {
      event.preventDefault();
      return;
    }
    onClick(event);
  };

  const baseButtonStyles =
    "rounded-2xl transition-all duration-200 ease-in-out";

  if (variant === "primary") {
    return (
      <button
        id={id}
        type="button"
        onClick={handleButtonClick}
        aria-label={ariaLabel}
        aria-disabled={disabled}
        disabled={disabled}
        tabIndex={disabled ? -1 : tabIndex}
        className={clsx(
          baseButtonStyles,
          "p-3",
          {
            "bg-weird-gradient text-[#171717] hover:shadow-[0_0_16px_#B9E55A] cursor-pointer":
              !disabled,
            "bg-[#666666] text-gray-400 cursor-not-allowed": disabled,
          },
          className
        )}
      >
        {icon}
      </button>
    );
  }

  const outerButtonBaseStyles = "p-[2px]";
  const innerDivBaseStyles =
    "w-full h-full rounded-[14px] flex items-center justify-center p-1.5";

  return (
    <button
      id={id}
      type="button"
      onClick={handleButtonClick}
      aria-label={ariaLabel}
      aria-disabled={disabled}
      disabled={disabled}
      tabIndex={disabled ? -1 : tabIndex}
      className={clsx(
        baseButtonStyles,
        outerButtonBaseStyles,
        {
          [`${borderClassNameProp} hover:shadow-[0_0_16px_#B9E55A] cursor-pointer`]:
            !disabled,
          "border-2 border-[#666666] bg-transparent cursor-not-allowed opacity-50":
            disabled,
        },
        className
      )}
    >
      <div
        className={clsx(innerDivBaseStyles, {
          [innerClassNameProp]: !disabled,
          "bg-[#444444]": disabled,
        })}
      >
        <span className={clsx({ "opacity-50": disabled })}>{icon}</span>
      </div>
    </button>
  );
};
