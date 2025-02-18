export interface TagTransformation {
  openerTag: string,
  endingTag: string,
  openerChange: string,
  endingChange: string
}

export const activeTransformation: TagTransformation = {
  openerTag: "<active>",
  endingTag: "</active>",
  openerChange: '<br /><span style="color: var(--pink2)"><strong>',
  endingChange: "</strong></span><br />"
}

export const passiveTransformation: TagTransformation = {
  openerTag: "<passive>",
  endingTag: "</passive>",
  openerChange: '<br><span style="color: var(--pink2)"><strong> (Passive) ',
  endingChange: "</strong></span><br>"
}

export const mainTextTransformation: TagTransformation = {
  openerTag: "<mainText>",
  endingTag: "</mainText>",
  openerChange: "",
  endingChange: ""
}

export const statsTransformation: TagTransformation = {
  openerTag: "<stats>",
  endingTag: "</stats>",
  openerChange: "",
  endingChange: ""
}

export const atentionTransformation: TagTransformation = {
  openerTag: "<attention>",
  endingTag: "</attention>",
  openerChange: '<span style="color: var(--orange)"><strong>&nbsp',
  endingChange: "</strong></span>&nbsp;"
}

export const healingTransformation: TagTransformation = {
  openerTag: "<healing>",
  endingTag: "</healing>",
  openerChange: '<span style="color: green"><strong>',
  endingChange: "</strong></span>"
}

export const brTransformation: TagTransformation = {
  openerTag: "<br>",
  endingTag: "</br>",
  openerChange: '',
  endingChange: ""
}

export const spellNameTransformation: TagTransformation = {
  openerTag: "<spellName>",
  endingTag: "</spellName>",
  openerChange: '<br><span style="color: var(--pink1)"><strong>',
  endingChange: "</strong></span>"
}

export const fontTransformation: TagTransformation = {
  openerTag: "<font>",
  endingTag: "</font>",
  openerChange: '<span style="color: var(--pink1)"><strong>',
  endingChange: "</strong></span>"
}

export const magicDamageTransformation: TagTransformation = {
  openerTag: "<magicDamage>",
  endingTag: "</magicDamage>",
  openerChange: '<span style="color: blue"><strong>',
  endingChange: "</strong></span>"
}

export const rulesTransformation: TagTransformation = {
  openerTag: "<rules>",
  endingTag: "</rules>",
  openerChange: '<br><span style="color: gray"><strong>',
  endingChange: "</strong></span>"
}


export const shieldTransformation: TagTransformation = {
  openerTag: "<shield>",
  endingTag: "</shield>",
  openerChange: '<span style="color: brown"><strong>',
  endingChange: "</strong></span>"
}

export const lifeStealTransformation: TagTransformation = {
  openerTag: "<lifeSteal>",
  endingTag: "</lifeSteal>",
  openerChange: '<span style="color: red"><strong>',
  endingChange: "</strong></span>"
}


export const scaleADTransformation: TagTransformation = {
  openerTag: "<scaleAD>",
  endingTag: "</scaleAD>",
  openerChange: '<span style="color: red"><strong>',
  endingChange: "</strong></span>"
}


export const scaleAPTransformation: TagTransformation = {
  openerTag: "<scaleAP>",
  endingTag: "</scaleAP>",
  openerChange: '<span style="color: blue"><strong>',
  endingChange: "</strong></span>"
}

export const scaleManaTransformation: TagTransformation = {
  openerTag: "<scaleMana>",
  endingTag: "</scaleMana>",
  openerChange: '<span style="color: blue"><strong>',
  endingChange: "</strong></span>"
}

export const scaleMRTransformation: TagTransformation = {
  openerTag: "<scaleMR>",
  endingTag: "</scaleMR>",
  openerChange: '<span style="color: aqua"><strong>',
  endingChange: "</strong></span>"
}

export const scaleArmorTransformation: TagTransformation = {
  openerTag: "<scaleArmor>",
  endingTag: "</scaleArmor>",
  openerChange: '<span style="color: olive"><strong>',
  endingChange: "</strong></span>"
}

export const slowTransformation: TagTransformation = {
  openerTag: "<slow>",
  endingTag: "</slow>",
  openerChange: '<span style="color: orange"><strong>',
  endingChange: "</strong></span>"
}

export const scaleLevelTransformation: TagTransformation = {
  openerTag: "<scaleLevel>",
  endingTag: "</scaleLevel>",
  openerChange: '<span style="color: fuchsia"><strong>',
  endingChange: "</strong></span>"
}

export const physicalDamageTransformation: TagTransformation = {
  openerTag: "<physicalDamage>",
  endingTag: "</physicalDamage>",
  openerChange: '<span style="color: red"><strong>',
  endingChange: "</strong></span>"
}

export const attackSpeedTransformation: TagTransformation = {
  openerTag: "<attackSpeed>",
  endingTag: "</attackSpeed>",
  openerChange: '<span style="color: indianRed"><strong>',
  endingChange: "</strong></span>"
}

export const speedTransformation: TagTransformation = {
  openerTag: "<speed>",
  endingTag: "</speed>",
  openerChange: '<span style="color: skyBlue"><strong>',
  endingChange: "</strong></span>"
}

export const keywordMajorTransformation: TagTransformation = {
  openerTag: "<keywordMajor>",
  endingTag: "</keywordMajor>",
  openerChange: '<span style="color: darkRed"><strong>',
  endingChange: "</strong></span>"
}

export const buffedStatTransformation: TagTransformation = {
  openerTag: "<buffedStat>",
  endingTag: "</buffedStat>",
  openerChange: '<span style="color: blueViolet"><strong>',
  endingChange: "</strong></span>"
}

export const onHitTransformation: TagTransformation = {
  openerTag: "<OnHit>",
  endingTag: "</OnHit>",
  openerChange: '<span style="color: darkStateGray"><strong>',
  endingChange: "</strong></span>"
}

export const keywordTransformation: TagTransformation = {
  openerTag: "<keyword>",
  endingTag: "</keyword>",
  openerChange: '<span style="color: plum"><strong>',
  endingChange: "</strong></span>"
}

export function descriptionMapper(description: string): string {
  let newDescription = description.replace(
    new RegExp("<br></br>", 'g'), ""
  ).replace(
    new RegExp("<stats></stats>", 'g'), ""
  ).replace(
    new RegExp("<font\\b[^>]*>", 'g'), "<font>"
  ).replace(
    new RegExp("<li>", 'g'), ""
  ).replace(
    new RegExp("(0s)", 'g'), ""
  ).replace(
    new RegExp("()", 'g'), ""
  );
  newDescription = applyTagTransformation(newDescription, activeTransformation);
  newDescription = applyTagTransformation(newDescription, mainTextTransformation);
  newDescription = applyTagTransformation(newDescription, statsTransformation);
  newDescription = applyTagTransformation(newDescription, atentionTransformation);
  newDescription = applyTagTransformation(newDescription, brTransformation);
  newDescription = applyTagTransformation(newDescription, passiveTransformation);
  newDescription = applyTagTransformation(newDescription, spellNameTransformation);
  newDescription = applyTagTransformation(newDescription, fontTransformation);
  newDescription = applyTagTransformation(newDescription, healingTransformation);
  newDescription = applyTagTransformation(newDescription, magicDamageTransformation);
  newDescription = applyTagTransformation(newDescription, rulesTransformation);
  newDescription = applyTagTransformation(newDescription, shieldTransformation);
  newDescription = applyTagTransformation(newDescription, lifeStealTransformation);
  newDescription = applyTagTransformation(newDescription, scaleADTransformation);
  newDescription = applyTagTransformation(newDescription, scaleAPTransformation);
  newDescription = applyTagTransformation(newDescription, scaleManaTransformation);
  newDescription = applyTagTransformation(newDescription, scaleArmorTransformation);
  newDescription = applyTagTransformation(newDescription, scaleMRTransformation);
  newDescription = applyTagTransformation(newDescription, slowTransformation);
  newDescription = applyTagTransformation(newDescription, scaleLevelTransformation);
  newDescription = applyTagTransformation(newDescription, physicalDamageTransformation);
  newDescription = applyTagTransformation(newDescription, attackSpeedTransformation);
  newDescription = applyTagTransformation(newDescription, speedTransformation);
  newDescription = applyTagTransformation(newDescription, keywordMajorTransformation);
  newDescription = applyTagTransformation(newDescription, buffedStatTransformation);
  newDescription = applyTagTransformation(newDescription, onHitTransformation);
  newDescription = applyTagTransformation(newDescription, keywordTransformation);
  return newDescription
}

export function applyTagTransformation(text: string, tagTransformation: TagTransformation) {
  let newText = text;
  newText = newText.replace(new RegExp(tagTransformation.openerTag, 'g'), tagTransformation.openerChange);
  newText = newText.replace(new RegExp(tagTransformation.endingTag, 'g'), tagTransformation.endingChange);
  return newText;
}

export default function DescriptionTextMapper({ description }: { description: string }) {
  const mappedDescription: string = descriptionMapper(description);
  return <div dangerouslySetInnerHTML={{ __html: mappedDescription }} />;
}
