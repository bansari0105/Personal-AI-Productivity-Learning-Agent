import "./globals.css";
import React from "react";

export const metadata = {
  title: "Agentic AI Dashboard",
  description: "Personal AI Productivity Agent",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-100 text-gray-900">
        {children}
      </body>
    </html>
  );
}
