import { Search, AlignLeft, MessageSquare, type LucideIcon } from 'lucide-react';

export type Step = {
  number: string;
  icon: LucideIcon;
  title: string;
  body: string;
};

export const steps: Step[] = [
  {
    number: '01',
    icon: Search,
    title: 'Ingest the firehose',
    body: 'We pull from 8+ feeds continuously — HN, Lobsters, arXiv, r/ML, TC, Crunchbase, Bluesky, lab blogs. Dedupe, embed, classify.',
  },
  {
    number: '02',
    icon: AlignLeft,
    title: 'Filter & summarize',
    body: 'A classifier scores every item for signal vs. noise. You get a ranked digest by topic — AI, research, security, startups — not a firehose.',
  },
  {
    number: '03',
    icon: MessageSquare,
    title: 'Ask anything',
    body: 'Chat with the index. "What did Anthropic ship this week?" Get an answer with citations to every source it pulled from.',
  },
];
