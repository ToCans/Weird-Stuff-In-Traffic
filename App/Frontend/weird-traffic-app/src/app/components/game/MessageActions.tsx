import React, { useState, useEffect } from "react";
import { Copy, Pencil } from "lucide-react"; // Import icons
// Remove IconButton import as it's no longer used
// import { IconButton } from "../ui/IconButton";

interface MessageActionsProps {
  messageContent: string;
  onCopy: () => void;
  onEdit: () => void;
}

export const MessageActions: React.FC<MessageActionsProps> = ({
  messageContent,
  onCopy,
  onEdit,
}) => {
  const [showCopiedTooltip, setShowCopiedTooltip] = useState(false); // State for tooltip

  const handleCopy = (
    event:
      | React.MouseEvent<HTMLButtonElement>
      | React.KeyboardEvent<HTMLButtonElement>
  ) => {
    event.stopPropagation(); // Prevent triggering parent hover/click events if any
    navigator.clipboard
      .writeText(messageContent)
      .then(() => {
        console.log("Message copied to clipboard");
        setShowCopiedTooltip(true); // Show tooltip
        // Timer is handled by useEffect now
      })
      .catch((err) => {
        console.error("Failed to copy message: ", err);
      });
    onCopy(); // Call the passed handler
  };

  // useEffect cleanup for tooltip timeout
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (showCopiedTooltip) {
      timer = setTimeout(() => {
        setShowCopiedTooltip(false);
      }, 1500);
    }
    return () => clearTimeout(timer);
  }, [showCopiedTooltip]);

  const handleEdit = (
    event:
      | React.MouseEvent<HTMLButtonElement>
      | React.KeyboardEvent<HTMLButtonElement>
  ) => {
    event.stopPropagation();
    console.log("Edit button clicked");
    onEdit(); // Call the passed handler
  };

  // Generic keydown handler for buttons
  const handleButtonKeyDown = (
    event: React.KeyboardEvent<HTMLButtonElement>,
    action: (e: React.KeyboardEvent<HTMLButtonElement>) => void
  ) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      action(event);
    }
  };

  return (
    <div className="absolute bottom-[-32px] right-2 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10">
      {/* Relative positioning for the tooltip container */}
      <div className="relative">
        {/* Standard button for Copy */}
        <button
          onClick={handleCopy}
          onKeyDown={(e) => handleButtonKeyDown(e, handleCopy)}
          aria-label="Copy message"
          tabIndex={0}
          className="p-2 rounded-full group-hover:opacity-100 hover:bg-[var(--gray)] transition-all duration-200 cursor-pointer transition-colors duration-200 cursor-pointer"
        >
          <Copy size={14} />
        </button>
        {/* Tooltip */}
        {showCopiedTooltip && (
          <span className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 px-2 py-1 text-xs text-white bg-black rounded shadow-md whitespace-nowrap z-20">
            Copied
          </span>
        )}
      </div>
      {/* Standard button for Edit */}
      <button
        onClick={handleEdit}
        onKeyDown={(e) => handleButtonKeyDown(e, handleEdit)}
        aria-label="Edit message"
        tabIndex={0}
        className="p-2 rounded-full group-hover:opacity-100 hover:bg-[var(--gray)] transition-all duration-200 cursor-pointer transition-colors duration-200 cursor-pointer"
      >
        <Pencil size={14} />
      </button>
    </div>
  );
};
