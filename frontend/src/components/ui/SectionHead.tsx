import type { ReactNode } from 'react';
import SectionLabel from './SectionLabel';

type Props = {
  kicker: string;
  title: ReactNode;
  description?: ReactNode;
  align?: 'left' | 'center';
};

export default function SectionHead({
  kicker,
  title,
  description,
  align = 'left',
}: Props) {
  const alignClasses =
    align === 'center' ? 'items-center text-center mx-auto' : 'items-start text-left';
  return (
    <div className={`flex flex-col ${alignClasses} max-w-[680px]`}>
      <SectionLabel className="mb-5">{kicker}</SectionLabel>
      <h2 className="headline text-[clamp(32px,4.4vw,52px)] headline-tight">
        {title}
      </h2>
      {description ? (
        <p className="mt-5 text-[17px] leading-[1.55] text-text-dim max-w-[620px]">
          {description}
        </p>
      ) : null}
    </div>
  );
}
