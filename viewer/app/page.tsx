import manifest from "@/public/data/manifest.json";
import type { Manifest } from "@/lib/types";
import { ViewerShell } from "@/components/ViewerShell";

const data = manifest as Manifest;

export default function Home() {
  return <ViewerShell manifest={data} />;
}
