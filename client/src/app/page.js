"use client"
import { Button } from "@/components/ui/button";
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleButtonClick = () => {
    router.push('/home');
  };
  return (
    <main>
     <div className="flex flex-col justify-center items-center h-screen text-[5rem]">
     Custom Chatgpt
     <Button onClick={handleButtonClick} className="text-[1.5rem] bg-cyan-700">Go to Home</Button>
     </div>

    </main>
  );
}
