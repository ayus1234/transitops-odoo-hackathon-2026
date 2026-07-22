const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'src');

function processDir(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      processDir(fullPath);
    } else if (fullPath.endsWith('.jsx')) {
      let content = fs.readFileSync(fullPath, 'utf8');
      let originalContent = content;

      // 1. Pagination responsiveness: flex items-center justify-between -> flex flex-col md:flex-row items-start md:items-center justify-between flex-wrap gap-4
      // Look for the footer div which usually has "border-t border-outline-variant flex items-center justify-between"
      content = content.replace(
        /className="([^"]*?)mt-auto p-md border-t border-outline-variant flex items-center justify-between([^"]*?)"/g,
        'className="$1mt-auto p-md border-t border-outline-variant flex flex-col md:flex-row items-center justify-between gap-4 flex-wrap$2"'
      );

      // 2. Toolbar responsiveness: search + filter row.
      // Usually "flex items-center gap-sm" or "flex flex-wrap items-center justify-between gap-md"
      content = content.replace(
        /className="([^"]*?)flex flex-wrap items-center justify-between gap-md([^"]*?)"/g,
        'className="$1flex flex-col md:flex-row flex-wrap items-stretch md:items-center justify-between gap-md$2"'
      );

      content = content.replace(
        /className="([^"]*?)flex items-center gap-sm([^"]*?)"/g,
        'className="$1flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto$2"'
      );

      // 3. Ensure Table Wrappers don't blowout
      // from `<div className="flex-1 bg-surface border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col"`
      // to include `min-w-0`
      content = content.replace(
        /className="([^"]*?)overflow-hidden flex flex-col([^"]*?)"/g,
        (match, p1, p2) => {
          if (!p2.includes('min-w-0')) {
             return `className="${p1}overflow-hidden flex flex-col min-w-0${p2}"`;
          }
          return match;
        }
      );

      // 4. Modal constraints
      content = content.replace(
        /<div\s+className="([^"]*?fixed inset-0 z-\[100\][^"]*?)"/g,
        (match, p1) => {
          if (!p1.includes('p-4 sm:p-6')) {
            return `<div className="${p1.replace(/p-\w+/g, '')} p-4 sm:p-6"`;
          }
          return match;
        }
      );

      // 5. Grid responsiveness in forms (e.g. grid-cols-2 to grid-cols-1 md:grid-cols-2)
      content = content.replace(
        /className="([^"]*?)\bgrid grid-cols-2\b([^"]*?)"/g,
        'className="$1grid grid-cols-1 md:grid-cols-2$2"'
      );

      // 6. Ensure overflow-x-auto on tables just in case
      content = content.replace(
        /<table className="([^"]*?w-full[^"]*?)"/g,
        (match, p1) => {
          if (!p1.includes('min-w-[')) {
            return `<table className="${p1} min-w-[800px]"`;
          }
          return match;
        }
      );

      if (content !== originalContent) {
        fs.writeFileSync(fullPath, content, 'utf8');
        console.log(`Updated ${fullPath}`);
      }
    }
  }
}

processDir(srcDir);
