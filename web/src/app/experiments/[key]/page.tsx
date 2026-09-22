import { Readout } from "@/components/readout";
import { experimentKeys } from "@/lib/data";
export function generateStaticParams() {
  return experimentKeys.map((key) => ({ key }));
}
export default async function Page({
  params,
}: {
  params: Promise<{ key: string }>;
}) {
  return <Readout experimentKey={(await params).key} />;
}
