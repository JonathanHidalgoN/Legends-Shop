import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    // Get the absolute path to the public/icons directory
    const iconsDir = path.join(process.cwd(), "public", "icons");

    // Read the directory contents
    const files = fs.readdirSync(iconsDir);

    // Filter for image files and create the response objects
    const iconFiles = files
      .filter(
        (file) =>
          file.endsWith(".png") ||
          file.endsWith(".jpg") ||
          file.endsWith(".jpeg"),
      )
      .map((file) => ({
        src: `/icons/${file}`,
        alt: file.replace(/\.(png|jpg|jpeg)$/, ""),
      }));

    return NextResponse.json(iconFiles);
  } catch (error) {
    console.error("Error reading icons directory:", error);
    return NextResponse.json(
      { error: "Failed to fetch icons" },
      { status: 500 },
    );
  }
}
