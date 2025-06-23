import React from "react";
import { X } from "lucide-react"; // Using lucide-react for the close icon
import { IconButton } from "../ui/IconButton";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  content: React.ReactNode; // Replaced children with content
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  content, // Use content prop
}) => {
  // Early return if the modal is not open
  if (!isOpen) {
    return null;
  }

  // Handle Escape key press to close the modal
  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      onClose();
    }
  };

  // Prevent clicks inside the modal from closing it
  const handleModalContentClick = (event: React.MouseEvent<HTMLDivElement>) => {
    event.stopPropagation();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose} // Close when clicking the overlay
      onKeyDown={handleKeyDown} // Handle Escape key
      role="dialog" // Accessibility: role
      aria-modal="true" // Accessibility: aria-modal
      aria-labelledby={title ? "modal-title" : undefined} // Accessibility: aria-labelledby
    >
      <div
        className="bg-[#1F1F1F] rounded-[32px] shadow-xl p-12 w-full max-w-3xl relative text-white animate-slide-up-fade-in flex flex-col"
        onClick={handleModalContentClick} // Prevent closing when clicking inside
        role="document" // Accessibility: role for inner container
      >
        {/* Close button */}
        <div className="absolute top-10 right-10">
          <IconButton
            icon={<X size={20} />}
            onClick={onClose}
            ariaLabel="Close modal"
            className="w-[42px] h-[42px]"
          />
        </div>
        {/* Optional Title */}
        {title && (
          <h2
            id="modal-title"
            className="text-xl font-semibold mb-4 text-center"
          >
            {title}
          </h2>
        )}
        {/* Content */}
        <div className="">{content}</div>
      </div>
    </div>
  );
};
