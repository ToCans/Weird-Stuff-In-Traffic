import Image from "next/image";
import { Button } from "@/app/components/ui/Button";
import { Dialog } from "@/app/components/ui/Dialog";
import { Header } from "../app/components/game/Header";
import Link from "next/link";

export default function Home() {
  return (
    <>
      <Header earnedPoints={0} trainingProgress={0} />
      <div className="min-h-screen bg-[#1A1A1A] flex flex-col items-center justify-center p-4 sm:p-8 pt-24 sm:pt-32 ">
        <div className="flex flex-col items-center gap-8 max-w-2xl mx-auto animate-slide-up-fade-in mb-10 sm:mb-0">
          <Dialog>
            <div className="flex flex-col gap-6">
              Hi there, your imagination feeds me — the more twisted your
              prompt, the better I become at averting real-world disasters. So
              go ahead... surprise me. Or are you too scared to fail?
              <div className="flex justify-end mb-2">
                <Link href="/chat">
                  <Button
                    variant="primary"
                    size="lg"
                    className="w-[182px] h-[62px]"
                  >
                    Start Game
                  </Button>
                </Link>
              </div>
            </div>
          </Dialog>

          <div className="relative w-48 h-48 sm:w-64 sm:h-64 animate-slide-left-fade-in ">
            <Image
              src="/car_1.png"
              alt="Weird Car"
              fill
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              className="object-contain"
              priority
            />
          </div>
        </div>
      </div>
    </>
  );
}
