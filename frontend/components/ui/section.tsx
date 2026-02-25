import { PropsWithChildren } from "react";

type SectionProps = PropsWithChildren<{
  id?: string;
  className?: string;
}>;

export function Section({ id, className, children }: SectionProps) {
  return (
    <section id={id} className={`mx-auto w-full max-w-6xl px-6 py-16 sm:py-20 ${className ?? ""}`}>
      {children}
    </section>
  );
}
