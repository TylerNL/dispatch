export type CardItem = {
  tag: string;
  tint: 'amber' | 'green';
  title: string;
  body: string;
};

export const cards: CardItem[] = [
  {
    tag: 'Research',
    tint: 'amber',
    title: 'Cutting-edge papers',
    body: "arXiv drops in cs.LG, cs.CL, cs.CR — ranked by what's getting discussed, not just what's new.",
  },
  {
    tag: 'Labs',
    tint: 'amber',
    title: 'Anthropic, OpenAI, DeepMind',
    body: 'Release notes, blog posts, model cards, and research announcements from every major lab — the hour they drop.',
  },
  {
    tag: 'Startups',
    tint: 'amber',
    title: 'Funding & launches',
    body: 'TechCrunch and Crunchbase filtered for signal: meaningful rounds, real launches, not press-release noise.',
  },
  {
    tag: 'Community',
    tint: 'amber',
    title: 'What HN & Lobsters are reading',
    body: 'The top stories and their top comments, summarized. Know what your timeline will be arguing about by lunch.',
  },
  {
    tag: 'Security',
    tint: 'green',
    title: 'CVEs & post-mortems',
    body: "Project Zero, r/netsec, disclosure threads. If it matters for what you ship, it's in the digest.",
  },
  {
    tag: 'Signal',
    tint: 'green',
    title: 'Cited answers, always',
    body: "Every chat response links to the exact articles it drew from. If the model doesn't know, it says so.",
  },
];
