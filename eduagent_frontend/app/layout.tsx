import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "EduAgent"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <div className="w-full bg-amber-50 border-b border-amber-200 px-4 py-2 text-center text-sm text-amber-800">
          EduAgent is currently under maintenance. Functionality may or may not be available. Thank you for your understanding.
        </div>
        {children}
      </body>
    </html>
  );
}
