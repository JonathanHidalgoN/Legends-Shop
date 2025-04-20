import fsPromises from "fs/promises";
import fs from "fs";
import path from "path";
import pLimit from "p-limit";

const PARALLEL_DOWNLOADS = 3;

async function downloadItemHDImage(
  itemName: string,
  destFolder: string,
  imageFile: string,
): Promise<boolean> {
  const baseUrl = "https://wiki.leagueoflegends.com/en-us/images";
  const formattedItemName = itemName.replace(/ /g, "_");
  const urlEncodedName = encodeURIComponent(formattedItemName);

  const hdUrl = `${baseUrl}/${urlEncodedName}_item_HD.png`;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(hdUrl, {
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const arrayBuffer = await response.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      const filePath = path.join(destFolder, imageFile);
      await fsPromises.writeFile(filePath, buffer);
      return true;
    }
  } catch (error) {}

  const regularUrl = `${baseUrl}/${urlEncodedName}_item.png`;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(regularUrl, {
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const arrayBuffer = await response.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      const filePath = path.join(destFolder, imageFile);
      await fsPromises.writeFile(filePath, buffer);
      return true;
    }
  } catch (error) {}

  console.log(
    `Failed to download image for item: ${itemName} from both HD and regular versions ${hdUrl} ${regularUrl}`,
  );
  return false;
}

async function downloadHDImageParallel(
  itemName: string,
  destDir: string,
): Promise<void> {
  const imageFile = `${itemName}.png`;
  const filePath = path.join(destDir, itemName);

  try {
    await fsPromises.access(filePath);
    return;
  } catch {}

  await downloadItemHDImage(itemName, destDir, imageFile);
}

export async function getHDItemImages(itemNames: string[]): Promise<void> {
  const destDir = path.join(process.cwd(), "public", "hd_images");
  await fsPromises.mkdir(destDir, { recursive: true });

  const limit = pLimit(PARALLEL_DOWNLOADS);
  const downloadPromises = itemNames.map((itemName) =>
    limit(() => downloadHDImageParallel(itemName, destDir)),
  );
  await Promise.all(downloadPromises);
}

export function checkIfHDImageAvailable(
  itemName: string,
  serverImagePath: string,
): string {
  const fileName = `${itemName}.png`;
  const filePath = path.join(process.cwd(), "public", "hd_images", fileName);
  if (fs.existsSync(filePath)) {
    return `/hd_images/${fileName}`;
  } else {
    return serverImagePath;
  }
}
