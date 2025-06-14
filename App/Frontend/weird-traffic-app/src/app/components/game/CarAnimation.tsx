"use client";

import Image from "next/image";
import React, { useState, useEffect, useMemo, useRef } from "react";
import type { CarAnimationState } from "@/app/hooks/useChatLogic";

interface CarAnimationProps {
  animationState: CarAnimationState;
}

// animationAssets will now only contain static states or fallbacks.
const animationAssets = {
  idle: "/car_1.png",
  default: "/car_1.png",
};

// Define SVG frames for each animation state.
const speakingSvgFrames = [
  "/speaking/emotion=speaking, Step=1.svg",
  "/speaking/emotion=speaking, Step=2.svg",
  "/speaking/emotion=speaking, Step=3.svg",
  "/speaking/emotion=speaking, Step=4.svg",
  "/speaking/emotion=speaking, Step=5.svg",
  "/speaking/emotion=speaking, Step=6.svg",
  "/speaking/emotion=speaking, Step=7.svg",
  "/speaking/emotion=speaking, Step=8.svg",
];

const waitingSvgFrames = [
  "/waiting/emotion=waiting, Step=1.svg",
  "/waiting/emotion=waiting, Step=2.svg",
  "/waiting/emotion=waiting, Step=3.svg",
  "/waiting/emotion=waiting, Step=4.svg",
  "/waiting/emotion=waiting, Step=5.svg",
  "/waiting/emotion=waiting, Step=6.svg",
  "/waiting/emotion=waiting, Step=7.svg",
  "/waiting/emotion=waiting, Step=8.svg",
];

const laughingSvgFrames = [
  "/laughing/emotion=laughing, Step=1.svg",
  "/laughing/emotion=laughing, Step=2.svg",
  "/laughing/emotion=laughing, Step=3.svg",
  "/laughing/emotion=laughing, Step=4.svg",
  "/laughing/emotion=laughing, Step=5.svg",
  "/laughing/emotion=laughing, Step=6.svg",
  "/laughing/emotion=laughing, Step=7.svg",
  "/laughing/emotion=laughing, Step=8.svg",
];

const sadSvgFrames = [
  "/sad/emotion=sad, Step=1.svg",
  "/sad/emotion=sad, Step=2.svg",
  "/sad/emotion=sad, Step=3.svg",
  "/sad/emotion=sad, Step=4.svg",
  "/sad/emotion=sad, Step=5.svg",
  "/sad/emotion=sad, Step=6.svg",
  "/sad/emotion=sad, Step=7.svg",
  "/sad/emotion=sad, Step=8.svg",
];

const scanSvgFrames = [
  // 6 steps for the "detecting" folder
  "/detecting/emotion=scan, Step=1.svg",
  "/detecting/emotion=scan, Step=2.svg",
  "/detecting/emotion=scan, Step=3.svg",
  "/detecting/emotion=scan, Step=4.svg",
  "/detecting/emotion=scan, Step=5.svg",
  "/detecting/emotion=scan, Step=6.svg",
];

// We are collecting animation frames and speeds in a map.
const frameAnimationDetails: Partial<
  Record<CarAnimationState, { frames: string[]; speed: number }>
> = {
  speaking: { frames: speakingSvgFrames, speed: 150 },
  waiting: { frames: waitingSvgFrames, speed: 150 },
  laughing: { frames: laughingSvgFrames, speed: 120 },
  sad: { frames: sadSvgFrames, speed: 200 },
  scan: { frames: scanSvgFrames, speed: 160 },
};

const CarAnimation: React.FC<CarAnimationProps> = ({ animationState }) => {
  const [currentFrame, setCurrentFrame] = useState(0);

  const activeAnimation = useMemo(
    () => frameAnimationDetails[animationState],
    [animationState]
  );

  useEffect(() => {
    let intervalId: NodeJS.Timeout | undefined;

    if (activeAnimation) {
      setCurrentFrame(0); // Start from the first frame when the animation changes
      intervalId = setInterval(() => {
        setCurrentFrame(
          (prevFrame) => (prevFrame + 1) % activeAnimation.frames.length
        );
      }, activeAnimation.speed);
    } else {
      setCurrentFrame(0); // Reset frame if not an animated state
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [activeAnimation]); // Only run useEffect when activeAnimation changes

  let currentImageSrc: string = animationAssets.default;
  let imageKey: string = animationState;

  if (activeAnimation && activeAnimation.frames.length > 0) {
    const frameIndex = currentFrame % activeAnimation.frames.length;
    if (
      activeAnimation.frames[frameIndex] &&
      activeAnimation.frames[frameIndex].trim() !== ""
    ) {
      currentImageSrc = activeAnimation.frames[frameIndex];
      imageKey = `${animationState}-${frameIndex}`;
    } else {
      imageKey = `${animationState}-default-fallback-frame`;
    }
  } else if (animationAssets[animationState as keyof typeof animationAssets]) {
    currentImageSrc =
      animationAssets[animationState as keyof typeof animationAssets];
    imageKey = animationState;
  }

  return (
    <div className="relative w-40 h-40 md:w-60 md:h-60 self-center md:self-start md:ml-10 animate-slide-left-fade-in mb-4 md:mb-0">
      <Image
        src={currentImageSrc}
        alt={`Car is ${animationState}${
          activeAnimation ? ` (frame ${currentFrame + 1})` : ""
        }`}
        fill
        className="object-contain"
        priority
        key={animationState}
      />
    </div>
  );
};

export default CarAnimation;
