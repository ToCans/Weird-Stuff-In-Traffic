import React, { useCallback } from "react";
import Image from "next/image";
import { Download, ExternalLink } from "lucide-react";

interface ImageDisplayProps {
  imageUrls: string[]; // Will take array instead of single URL
  isLoading?: boolean; // Will manage loading state
  altTextPrefix?: string;
  onImageSelect?: (selectedImage: string, index: number) => void;
  isDetecting?: boolean; // New prop: Is detection loading?
  selectedImageIndex?: number | null; // New prop: Selected index from parent
  detectedImageUrl?: string | null; // Optional: Base64 URL from detection API
  onShare?: (imageUrl: string) => void; // New prop for handling share
}

export const ImageDisplay: React.FC<ImageDisplayProps> = ({
  imageUrls,
  isLoading = false, // Default value false
  altTextPrefix = "Generated image",
  onImageSelect,
  isDetecting = false, // Default value for new prop
  selectedImageIndex = null, // Default value for new prop
  detectedImageUrl = null, // Optional: Base64 URL from detection API
  onShare,
}) => {
  const handleImageClick = useCallback(
    (imageUrl: string, index: number) => {
      // Directly notify parent of clicked index
      if (onImageSelect) {
        onImageSelect(imageUrl, index);
      }
      console.log(`Selected image index: ${index}, URL: ${imageUrl}`);
    },
    [onImageSelect]
  );

  const handleDownload = useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      event.stopPropagation(); // Prevent triggering image selection again
      if (selectedImageIndex === null || !imageUrls[selectedImageIndex]) return;

      // Prioritize detected image URL for download, fallback to original
      const imageUrlToDownload =
        detectedImageUrl ?? imageUrls[selectedImageIndex];
      // Use a more descriptive filename if possible, maybe based on prompt or index
      const fileName = `detected-image-${selectedImageIndex + 1}.png`; // Example filename

      // Create a temporary link element
      const link = document.createElement("a");
      link.href = imageUrlToDownload; // Use the potentially detected URL
      link.download = fileName; // Set the download attribute

      // Append to the document, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      console.log("Attempting to download:", fileName);
    },
    [imageUrls, selectedImageIndex, detectedImageUrl] // Add detectedImageUrl dependency
  );

  // Keyboard accessibility for download button
  const handleDownloadKeyDown = (
    event: React.KeyboardEvent<HTMLButtonElement>
  ) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      event.stopPropagation();
      handleDownload(event as any); // Type assertion might be needed depending on strictness
    }
  };

  const handleShare = useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      event.stopPropagation(); // Prevent triggering image selection or other parent events
      if (selectedImageIndex === null || !imageUrls[selectedImageIndex]) return;

      const imageUrlToShare = detectedImageUrl ?? imageUrls[selectedImageIndex];

      if (onShare) {
        onShare(imageUrlToShare);
      }
      console.log("Attempting to share:", imageUrlToShare);
    },
    [imageUrls, selectedImageIndex, detectedImageUrl, onShare]
  );

  const handleShareKeyDown = (
    event: React.KeyboardEvent<HTMLButtonElement>
  ) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      event.stopPropagation();
      // We need to ensure handleShare has access to the event if it needs it,
      // but since it's a simple button click, casting to `any` or creating a synthetic event is fine.
      handleShare(event as any);
    }
  };

  // Show nothing if imageUrls is empty AND not in loading state
  if ((!imageUrls || imageUrls.length === 0) && !isLoading) {
    return null;
  }

  return (
    // Main container should have some padding and background
    <div className="w-full p-1 rounded-4xl bg-[#1f1f1f]">
      {selectedImageIndex !== null ? (
        <div className="relative w-full aspect-video rounded-4xl transition-all duration-300 group">
          <Image
            // Select correct image from state, prioritize detected image
            src={detectedImageUrl ?? imageUrls[selectedImageIndex]}
            alt={`${altTextPrefix} ${selectedImageIndex + 1}`}
            fill // Set to fill container
            className="object-cover rounded-4xl" // Round corners
            priority // Load with priority
            sizes="100vw" // Optimization for different screen sizes
          />

          {/* Action Buttons Container - Appears on hover over the container div */}
          <div className="absolute top-4 right-4 z-20 flex gap-2 opacity-0 group-hover:opacity-100 transition-all duration-200">
            {/* Download Button */}
            <button
              onClick={handleDownload}
              onKeyDown={handleDownloadKeyDown}
              aria-label="Download image"
              tabIndex={0}
              className="p-2 text-white rounded-full hover:bg-[var(--gray)] cursor-pointer"
            >
              <Download size={20} />
            </button>

            {/* Share Button */}
            {onShare && ( // Only render if onShare is provided
              <button
                onClick={handleShare}
                onKeyDown={handleShareKeyDown}
                aria-label="Share image"
                tabIndex={0}
                className="p-2 text-white rounded-full hover:bg-[var(--gray)] cursor-pointer"
              >
                <ExternalLink size={20} />
              </button>
            )}
          </div>

          {/* If detection is loading, show the indicator and overlay */}
          {/* Ensure overlay is below the download button (lower z-index or appears later in DOM) */}
          {isDetecting && (
            <div className="absolute inset-0 flex items-center justify-center bg-[rgba(0,0,0,0.5)] rounded-4xl border-2 border-[var(--green)] z-10">
              {/* Spinner */}
              <div className="w-10 h-10 border-4 border-transparent border-t-[var(--green)] rounded-full animate-spin"></div>
            </div>
          )}
        </div>
      ) : (
        // Grid view
        <div className="grid grid-cols-2 gap-3">
          {isLoading
            ? // If loading, show 4 skeletons (placeholders)
              [...Array(4)].map((_, index) => (
                <div
                  key={`loading-${index}`}
                  className="skeleton aspect-video w-full"
                />
              ))
            : // If loading finished, show images
              imageUrls.map((imageUrl, index) => (
                // Each image is a clickable button
                <button
                  key={index}
                  onClick={() => handleImageClick(imageUrl, index)}
                  className="relative w-full aspect-video overflow-hidden rounded-4xl border-2 border-[var(--gray)] hover:border-2 hover:border-[var(--green)] transition-all duration-200 cursor-pointer group focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background focus:ring-[var(--green)]"
                  aria-label={`Select image ${index + 1}`}
                  tabIndex={0}
                >
                  <Image
                    src={imageUrl}
                    alt={`${altTextPrefix} ${index + 1}`}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-200"
                    priority={index < 2}
                    sizes="(max-width: 768px) 50vw, (max-width: 1200px) 30vw, 25vw"
                    onError={(e) => {
                      console.error("Image failed to load:", imageUrl);
                      e.currentTarget.style.display = "none";
                    }}
                  />
                </button>
              ))}
        </div>
      )}
    </div>
  );
};
