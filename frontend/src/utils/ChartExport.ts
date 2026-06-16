import { toPng } from "html-to-image";
import JSZip from "jszip";
import { saveAs } from "file-saver";

function sanitizeFileName(name: string): string {
  return name
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9-_ ]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .toLowerCase();
}

export async function downloadChartAsPng(
  elementId: string,
  fileName: string
): Promise<void> {
  const element = document.getElementById(elementId);

  if (!element) {
    throw new Error(`Elemento ${elementId} não encontrado.`);
  }

  const dataUrl = await toPng(element, {
    cacheBust: true,
    pixelRatio: 2,
    backgroundColor: "#ffffff",
  });

  const link = document.createElement("a");
  link.download = `${sanitizeFileName(fileName)}.png`;
  link.href = dataUrl;
  link.click();
}

export async function downloadAllChartsAsZip(): Promise<void> {
  const chartElements = document.querySelectorAll<HTMLElement>(
    "[data-chart-export='true']"
  );

  if (chartElements.length === 0) {
    throw new Error("Nenhum gráfico encontrado para exportação.");
  }

  const zip = new JSZip();
  const folder = zip.folder("graficos-analise");

  for (const element of chartElements) {
    const title = element.dataset.chartTitle || "grafico";
    const fileName = sanitizeFileName(title);

    const dataUrl = await toPng(element, {
      cacheBust: true,
      pixelRatio: 2,
      backgroundColor: "#ffffff",
    });

    const base64Data = dataUrl.split(",")[1];

    folder?.file(`${fileName}.png`, base64Data, {
      base64: true,
    });
  }

  const content = await zip.generateAsync({ type: "blob" });
  saveAs(content, "graficos-analise.zip");
}