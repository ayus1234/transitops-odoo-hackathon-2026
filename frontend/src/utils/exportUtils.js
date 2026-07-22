import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

export const getFormattedDate = () => {
  const d = new Date();
  const pad = (n) => n.toString().padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}_${pad(d.getHours())}-${pad(d.getMinutes())}-${pad(d.getSeconds())}`;
};

export const downloadBlobFromResponse = (response, defaultFilename) => {
  const disposition = response.headers['content-disposition'] || response.headers.get?.('content-disposition');
  let filename = defaultFilename;
  
  if (disposition && disposition.indexOf('filename=') !== -1) {
    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
    const matches = filenameRegex.exec(disposition);
    if (matches != null && matches[1]) {
      filename = matches[1].replace(/['"]/g, '');
    }
  }

  // Fallback to default if somehow UUID or empty
  if (!filename || filename.length === 36 || filename.includes('-4')) {
    filename = defaultFilename; 
  }

  const url = window.URL.createObjectURL(new Blob([response.data || response]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
};

export const downloadCSV = (data, filename, columns = null) => {
  if (!data || data.length === 0) {
    alert("No data available to download.");
    return;
  }
  
  // Extract headers
  const headers = columns ? columns.map(c => c.label) : Object.keys(data[0]);
  const keys = columns ? columns.map(c => c.key) : Object.keys(data[0]);
  
  // Convert data to CSV format
  const csvContent = [
    headers.join(','),
    ...data.map(row => 
      keys.map(fieldName => {
        let value = row[fieldName];
        
        // Custom value mapping if defined in columns
        if (columns) {
          const colDef = columns.find(c => c.key === fieldName);
          if (colDef && colDef.format) {
            value = colDef.format(value, row);
          }
        }

        // Handle objects (like nested relationships) by stringifying or picking a name
        if (typeof value === 'object' && value !== null) {
          value = value.name || value.registration_number || value.id || JSON.stringify(value);
        }
        // Escape quotes and wrap in quotes if there's a comma
        let stringValue = String(value ?? '').replace(/"/g, '""');
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          stringValue = `"${stringValue}"`;
        }
        return stringValue;
      }).join(',')
    )
  ].join('\n');

  // Trigger download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  // If filename already has a date pattern like YYYY-MM-DD, don't append another timestamp
  const hasDate = /\d{4}-\d{2}-\d{2}/.test(filename);
  const safeFilename = hasDate ? filename : filename.replace(/\.csv$/, `_${getFormattedDate()}.csv`);
  link.setAttribute("download", safeFilename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const downloadPDF = (data, filename, title, columns = null) => {
  if (!data || data.length === 0) {
    alert("No data available to download.");
    return;
  }

  const doc = new jsPDF('landscape');
  doc.setFontSize(18);
  doc.text(title || 'Exported Data', 14, 22);
  
  const headers = columns ? columns.map(c => c.label) : Object.keys(data[0]).map(key => key.replace(/_/g, ' ').toUpperCase());
  const keys = columns ? columns.map(c => c.key) : Object.keys(data[0]);
  
  const tableData = data.map(row => 
    keys.map(fieldName => {
      let value = row[fieldName];
      
      if (columns) {
        const colDef = columns.find(c => c.key === fieldName);
        if (colDef && colDef.format) {
          value = colDef.format(value, row);
        }
      }

      if (typeof value === 'object' && value !== null) {
        if (Array.isArray(value)) return value.join(', ');
        return value.name || value.registration_number || value.id || JSON.stringify(value);
      }
      return String(value ?? '');
    })
  );

  autoTable(doc, {
    startY: 30,
    head: [headers],
    body: tableData,
    styles: { fontSize: 8 },
    headStyles: { fillColor: [33, 150, 243] },
  });

  const hasDate = /\d{4}-\d{2}-\d{2}/.test(filename);
  const safeFilename = hasDate ? filename : filename.replace(/\.pdf$/, `_${getFormattedDate()}.pdf`);
  doc.save(safeFilename);
};
