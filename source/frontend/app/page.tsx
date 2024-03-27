export const dynamic = "force-dynamic";
import Header from "@/components/Header";
import HomePage from "@/pages/HomePage";

export default function Home() {
  return (
    <>
      <main className="container mx-auto mt-4 ">
        <Header />
        <HomePage />
      </main>
    </>
  );
}
