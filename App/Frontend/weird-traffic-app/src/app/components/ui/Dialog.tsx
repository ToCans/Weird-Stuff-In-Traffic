"use client";
interface DialogProps {
  children: React.ReactNode;
}

export function Dialog({ children }: DialogProps) {
  return (
    <div className="bg-[var(--dark-gray)] text-white p-6 rounded-4xl max-w-md relative shadow-lg">
      <div className="absolute w-6 h-6 bg-[var(--dark-gray)] transform rotate-45 -bottom-3 left-1/2 -translate-x-1/2 md:left-auto md:translate-x-0 md:right-10"></div>
      <div className="font-regular text-base font-mono tracking-[-0.011em] leading-[180%]">
        {children}
      </div>
    </div>
  );
}
