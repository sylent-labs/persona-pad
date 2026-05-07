import type { ReactNode } from "react";

import { StatusBar } from "./StatusBar";

interface PhoneFrameProps {
  children: ReactNode;
}

export function PhoneFrame({ children }: PhoneFrameProps) {
  return (
    <div className="phone-frame">
      <div className="phone-screen">
        <StatusBar />
        {children}
      </div>
    </div>
  );
}
