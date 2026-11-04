/**
 * Utility functions for exporting table datasets to CSV and JSON formats.
 */

export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columns?: { key: keyof T; label: string }[]
) {
  if (!data || data.length === 0) return;

  const cols =
    columns ??
    (Object.keys(data[0]).map((key) => ({
      key: key as keyof T,
      label: key,
    })) as { key: keyof T; label: string }[]);

  const headerLine = cols
    .map((c) => `"${String(c.label).replace(/"/g, '""')}"`)
    .join(",");

  const rowLines = data.map((row) =>
    cols
      .map((col) => {
        let val: any = row[col.key];
        if (val === null || val === undefined) val = "";
        else if (Array.isArray(val)) val = val.join(", ");
        else if (typeof val === "object") val = JSON.stringify(val);
        return `"${String(val).replace(/"/g, '""')}"`;
      })
      .join(",")
  );

  const csvContent = "\uFEFF" + [headerLine, ...rowLines].join("\r\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function exportToJSON<T>(data: T[], filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}.json`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
