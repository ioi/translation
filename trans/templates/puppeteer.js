const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto("file://{{html_file_path}}", {
    waitUntil: 'networkidle2',
  });
  await page.pdf({ path: "{{pdf_file_path}}", format: 'a4',
    printBackground: true,
    margin: {
      'top': '0.62in',
      'left': '0.75in',
      'right': '0.75in',
      'bottom': '1in'
    }
  });

  await browser.close();
})();

