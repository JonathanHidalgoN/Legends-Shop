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
    attention: { tag: "span", className: "text-red-600 font-extrabold" },
    passive: {
      tag: "span",
      className: "text-purple-600 font-bold italic tracking-wide",
    },
    gold: {
      tag: "span",
      className: "text-yellow-400 font-extrabold drop-shadow",
    },
    spellName: { tag: "span", className: "text-indigo-600 font-bold" },
    speed: { tag: "span", className: "text-sky-400 font-medium" },
    slow: { tag: "span", className: "text-cyan-500 font-medium italic" },
    shield: { tag: "span", className: "text-blue-500 font-medium" },
    active: { tag: "span", className: "text-blue-500 font-semibold italic" },
    rarityMythic: {
      tag: "span",
      className: "text-pink-500 font-bold uppercase tracking-widest",
    },
    rarityLegendary: {
      tag: "span",
      className: "text-violet-500 font-semibold uppercase",
    },
    scaleHealt: { tag: "span", className: "text-teal-500 font-medium" },
    scaleAD: { tag: "span", className: "text-orange-400 font-medium" },
    scaleAP: { tag: "span", className: "text-fuchsia-500 font-medium" },
    scaleArmor: { tag: "span", className: "text-yellow-600 font-medium" },
    scaleMR: { tag: "span", className: "text-emerald-500 font-medium" },
    scaleMana: { tag: "span", className: "text-blue-400 font-medium" },
    scaleLevel: { tag: "span", className: "text-gray-500 font-medium italic" },
    healing: { tag: "span", className: "text-green-500 font-semibold" },
    scaleHealth: { tag: "span", className: "text-green-300 font-semibold" },
    lifeSteal: {
      tag: "span",
      className: "text-green-400 font-semibold italic",
    },
    attackSpeed: { tag: "span", className: "text-lime-500 font-semibold" },
    physicalDamage: { tag: "span", className: "text-rose-500 font-semibold" },
    magicDamage: { tag: "span", className: "text-purple-500 font-semibold" },
    trueDamage: { tag: "span", className: "text-blue-500 font-semibold " },
    OnHit: { tag: "span", className: "text-amber-400 font-semibold" },
    rules: { tag: "span", className: "text-gray-500 italic text-sm" },
    stats: { tag: "span", className: "text-gray-700 font-medium" },
    buffedStat: { tag: "span", className: "text-green-400 font-medium" },
    mainText: {
      tag: "div",
      className: "max-h-60 overflow-auto p-2 bg-var(--white) rounded",
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
