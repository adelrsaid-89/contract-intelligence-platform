# Sample Contract Documents

This directory contains sample contract documents for the Contract Intelligence Platform POC.

## Files

- `sample-airport-contract.html` - Transportation Hub Infrastructure Development Contract
- `sample-mall-contract.html` - Commercial Retail Complex Development Contract

## Converting HTML to PDF

To convert the HTML files to PDF format for use in the system:

### Option 1: Using wkhtmltopdf (Recommended)
```bash
# Install wkhtmltopdf
sudo apt-get install wkhtmltopdf

# Convert to PDF
wkhtmltopdf sample-airport-contract.html sample-airport-contract.pdf
wkhtmltopdf sample-mall-contract.html sample-mall-contract.pdf
```

### Option 2: Using Puppeteer (Node.js)
```javascript
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function convertToPdf(htmlFile, outputFile) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    const htmlContent = fs.readFileSync(htmlFile, 'utf8');

    await page.setContent(htmlContent);
    await page.pdf({
        path: outputFile,
        format: 'A4',
        printBackground: true,
        margin: {
            top: '20mm',
            bottom: '20mm',
            left: '15mm',
            right: '15mm'
        }
    });

    await browser.close();
}

// Convert files
convertToPdf('sample-airport-contract.html', 'sample-airport-contract.pdf');
convertToPdf('sample-mall-contract.html', 'sample-mall-contract.pdf');
```

### Option 3: Using Chrome/Chromium Browser
1. Open the HTML file in Chrome/Chromium
2. Press Ctrl+P (or Cmd+P on Mac)
3. Select "Save as PDF" as destination
4. Configure page settings as needed
5. Save as PDF

## Contract Content Overview

### Transportation Hub Contract (TH-2024-001)
- **Value**: $45,750,000 USD
- **Duration**: 3 years (March 2024 - February 2027)
- **Key Obligations**: 8 main obligations with various frequencies
- **Penalties**: Multiple penalty structures including liquidated damages
- **Focus**: Infrastructure development with emphasis on safety and environmental compliance

### Commercial Retail Complex Contract (CRC-2024-002)
- **Value**: $28,950,000 USD
- **Duration**: 2 years (June 2024 - May 2026)
- **Key Obligations**: 10 main obligations with various frequencies
- **Penalties**: Quality and tenant-focused penalty structures
- **Focus**: Commercial construction with emphasis on retail operations and tenant coordination

## Usage in POC

These contracts are designed to test:
1. **AI Metadata Extraction** - Rich metadata fields for extraction
2. **Obligation Identification** - Multiple obligations with clear frequencies and deadlines
3. **Penalty Recognition** - Various penalty structures and amounts
4. **Search and Q&A** - Diverse content for testing search capabilities
5. **User Workflows** - Different contract types for different user scenarios

## Customization

The contracts contain placeholder data and can be customized by:
1. Modifying the HTML files directly
2. Changing project names, values, dates, and other metadata
3. Adding or removing obligations and penalties
4. Adjusting KPIs and SLAs

Remember to regenerate PDF files after making changes to HTML content.