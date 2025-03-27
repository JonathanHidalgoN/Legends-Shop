import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import pLimit from 'p-limit';

const PARALLEL_DOWNLOADS = 5;

async function downloadItemHDImage(
  itemName: string,
  destFolder: string,
  imageFile: string
): Promise<boolean> {
  const baseUrl = "https://leagueoflegends.fandom.com/wiki";
  const url = `${baseUrl}/${itemName}?file=${imageFile}`;
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(10000) });
    if (!response.ok) {
      throw new Error(`Failed to fetch image, status: ${response.status}`);
    }
    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const filePath = path.join(destFolder, imageFile);
    await fs.writeFile(filePath, buffer);
    return true;
  } catch (error) {
    return false;
  }
}

async function downloadHDImageParallel(
  itemName: string,
  destDir: string
): Promise<void> {
  const urlEncodedItemName = encodeURIComponent(itemName);
  const imageFile = `${itemName}_item_HD.png`;
  const filePath = path.join(destDir, imageFile);

  try {
    await fs.access(filePath);
    return;
  } catch {
  }

  await downloadItemHDImage(urlEncodedItemName, destDir, imageFile);
}

export async function getHDItemImages(itemNames: string[]): Promise<void> {
  const destDir = path.join(process.cwd(), 'public', 'hd_images');
  await fs.mkdir(destDir, { recursive: true });

  const limit = pLimit(PARALLEL_DOWNLOADS);
  const downloadPromises = itemNames.map(itemName =>
    limit(() => downloadHDImageParallel(itemName, destDir))
  );
  await Promise.all(downloadPromises);
}

export async function PUT(request: Request) {
  try {
    const { itemNames } = await request.json();
    if (!Array.isArray(itemNames)) {
      return NextResponse.json({ error: 'itemNames must be an array' }, { status: 400 });
    }
    await getHDItemImages(itemNames);
    return NextResponse.json({ message: 'HD images downloaded successfully.' });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
