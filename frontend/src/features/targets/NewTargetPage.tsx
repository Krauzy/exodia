import { Card } from "../../components/ui/Card";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { TargetForm } from "./TargetForm";

export function NewTargetPage() {
  return (
    <>
      <SectionHeader
        title="New Target"
        description="Register only assets you own, control, or are explicitly authorized to assess."
      />
      <Card>
        <TargetForm />
      </Card>
    </>
  );
}

