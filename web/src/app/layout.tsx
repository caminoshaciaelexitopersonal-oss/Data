import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SADI - Next.js",
  description: "Sistema de Analítica de Datos Inteligente",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
