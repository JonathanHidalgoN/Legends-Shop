export function mapDescriptionToHtml(description: string): string {
  // /<(\w+)>\s*<\/\1>/g
  // <(\w+)>: Matches an opening tag like <stats>, <br>, <mainText>, etc.
  // \w+ matches one or more "word characters" (letters, numbers, underscore).
  // () creates a capture group, which can be referenced later.
  // <\/\1>: Matches a closing tag like </stats> where:
  // \s*: Matches zero or more whitespace characters (spaces, tabs, newlines) — this is the content between the tags.
  // \/ is an escaped forward slash.
  // \1 refers back to the same tag name as in the opening tag (from the first (\w+)).
  // The g flag means it applies globally (finds all such occurrences in the string).
  let html = description.replace(/<(\w+)>\s*<\/\1>/g, "");

  // /(<br>\s*){2,}/g
  // Collapses multiple <br> tags in a row into just one.
  // <br>\s*: Matches a <br> followed by optional whitespace.
  // {2,}: Looks for two or more of those in a row.
  // Replaces them with just a single <br>.

  ///^<br>/
  // Purpose:
  // Removes a <br> if it appears at the very start of the string.
  //  Explanation:
  // ^: Anchors the match to the start of the string.

  //<br>$/
  //  Purpose:
  // Removes a <br> if it appears at the very end of the string.
  //  Explanation:
  // <br>: Matches the literal string.
  // $: Anchors the match to the end of the string./ <br>: Matches that literal string.
  html = html
    .replace(/(<br>\s*){2,}/g, "<br>")
    .replace(/^<br>/, "")
    .replace(/<br>$/, "");

  const tagMap: Record<string, { tag: "span" | "div"; className: string }> = {
    attention: { tag: "span", className: "text-black font-extrabold" },
    passive: {
      tag: "span",
      className: "text-purple-600 font-bold italic tracking-wide",
    },
    gold: {
      tag: "span",
      className: "text-yellow-400 font-extrabold drop-shadow",
    },
    spellName: { tag: "span", className: "text-black font-bold" },
    speed: { tag: "span", className: "text-black font-bold" },
    slow: { tag: "span", className: "text-black font-bold" },
    shield: { tag: "span", className: "text-black font-bold" },
    active: { tag: "span", className: "text-blue-500 font-bold" },
    rarityMythic: {
      tag: "span",
      className: "text-black font-bold uppercase tracking-widest",
    },
    rarityLegendary: {
      tag: "span",
      className: "text-black font-semibold uppercase",
    },
    scaleHealt: { tag: "span", className: "text-black font-bold" },
    scaleAD: { tag: "span", className: "text-black font-bold" },
    scaleAP: { tag: "span", className: "text-black font-bold" },
    scaleArmor: { tag: "span", className: "text-black font-bold" },
    scaleMR: { tag: "span", className: "text-black font-bold" },
    scaleMana: { tag: "span", className: "text-black font-bold" },
    scaleLevel: { tag: "span", className: "text-black font-bold" },
    healing: { tag: "span", className: "text-black font-bold" },
    scaleHealth: { tag: "span", className: "text-black font-bold" },
    lifeSteal: {
      tag: "span",
      className: "text-black font-bold",
    },
    attackSpeed: { tag: "span", className: "text-black font-bold" },
    physicalDamage: { tag: "span", className: "text-black font-bold" },
    magicDamage: { tag: "span", className: "text-black font-bold" },
    trueDamage: { tag: "span", className: "text-black font-bold " },
    OnHit: { tag: "span", className: "text-black font-bold" },
    rules: { tag: "span", className: "text-black italic text-sm" },
    stats: { tag: "span", className: "text-black font-bold" },
    buffedStat: { tag: "span", className: "text-black font-bold" },
    mainText: {
      tag: "div",
      className: "max-h-24 overflow-auto p-2 bg-var(--white) rounded",
    },
  };

  for (const [tag, { tag: htmlTag, className }] of Object.entries(tagMap)) {
    const regex = new RegExp(`<${tag}>(.*?)</${tag}>`, "gis");
    html = html.replace(
      regex,
      (_, content) =>
        `<${htmlTag} class="${className}">${content}</${htmlTag}>`,
    );
  }

  return html;
}

export default function DescriptionTextMapper({
  description,
}: {
  description: string;
}) {
  const mappedHtmlDescription = mapDescriptionToHtml(description);
  return <div dangerouslySetInnerHTML={{ __html: mappedHtmlDescription }} />;
}
