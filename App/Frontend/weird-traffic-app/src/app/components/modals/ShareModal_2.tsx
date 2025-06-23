import React from "react";
import Image from "next/image";
import { X } from "lucide-react";
import {
  Instagram,
  Facebook,
  Linkedin,
  Twitter,
  MessageCircle,
} from "lucide-react"; // Social media icons
import { IconButton } from "../ui/IconButton";

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl?: string | null;
  accuracy?: number | null; // AI analysis accuracy
  pointsReceived?: number | null; // Points received for this specific share
  totalScore?: number; // User's total score
}

const SocialIcon: React.FC<{
  href: string;
  icon: React.ElementType;
  label: string;
}> = ({ href, icon: Icon, label }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    aria-label={`Share on ${label}`}
    className="p-2 rounded-full bg-gray-700 hover:bg-gray-600 transition-colors"
  >
    <Icon size={20} className="text-white" />
  </a>
);

export const ShareModal2: React.FC<ShareModalProps> = ({
  isOpen,
  onClose,
  imageUrl,
  accuracy,
  pointsReceived,
  totalScore,
}) => {
  if (!isOpen) return null;

  const displayImageUrl = imageUrl || "/placeholder-image.png";

  const currentAccuracy = accuracy ?? 0;
  const currentPointsReceived = pointsReceived ?? 0;
  const currentTotalScore = totalScore ?? 0;

  const handleModalContentClick = (e: React.MouseEvent<HTMLDivElement>) => {
    e.stopPropagation(); // Prevent click from bubbling to the overlay
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="share-modal-title"
    >
      <div
        className="bg-[var(--dark-gray)] p-6 sm:p-8 rounded-2xl shadow-xl w-full max-w-[850px] relative text-white font-mono animate-slide-up-fade-in"
        onClick={handleModalContentClick} // Stop propagation for content clicks
      >
        {/* Close Button */}
        <div className="absolute top-10 right-10">
          <IconButton
            icon={<X size={20} />}
            onClick={onClose}
            ariaLabel="Close modal"
            className="w-[42px] h-[42px]"
          />
        </div>
        <h2 id="share-modal-title" className="text-xl mb-6 text-left mt-4 ">
          Share your result:
        </h2>

        {/* Image Preview */}
        {displayImageUrl && (
          <div className="mt-10 mb-10 w-[70%] aspect-[16/10] relative rounded-4xl overflow-hidden mx-auto">
            <Image
              src={displayImageUrl}
              alt="Shared content preview"
              fill
              className="object-cover"
              sizes="(max-width: 640px) 90vw, (max-width: 768px) 80vw, 400px"
            />
          </div>
        )}

        {/* AI Analysis & Points */}
        <p className="text-m mb-2 text-center">
          AI analysis: {currentAccuracy}% accuracy. You&apos;ve received{" "}
          {currentPointsReceived} points.
        </p>

        {/* Total Score */}
        <p className="text-lg mb-8 text-center">
          Your total score so far:{" "}
          <span className="text-gradient-weird font-bold text-3xl">
            {currentTotalScore}
          </span>
        </p>

        {/* Social Media Icons */}
        <div className="flex justify-center items-center gap-3 sm:gap-4">
          <SocialIcon
            href="https://www.instagram.com/"
            icon={Instagram}
            label="Instagram"
          />
          <SocialIcon
            href="https://www.facebook.com/"
            icon={Facebook}
            label="Facebook"
          />
          <SocialIcon
            href="https://twitter.com/"
            icon={Twitter}
            label="Twitter"
          />
          <SocialIcon
            href="https://wa.me/"
            icon={MessageCircle}
            label="WhatsApp"
          />
          <SocialIcon
            href="https://www.linkedin.com/"
            icon={Linkedin}
            label="LinkedIn"
          />
        </div>
      </div>
    </div>
  );
};
