import { Suspense } from "react";

import { Dashboard } from "./dashboard";

export default function HomePage() {
  return (
    <Suspense fallback={<main className="shell">Loading radar...</main>}>
      <Dashboard />
    </Suspense>
  );
}
