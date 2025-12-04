const http = require('http');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;
const publicDir = path.resolve('.');

const mimeTypes = {
  '.html': 'text/html; charset=UTF-8',
  '.js': 'application/javascript; charset=UTF-8',
  '.css': 'text/css; charset=UTF-8',
  '.json': 'application/json; charset=UTF-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.pdf': 'application/pdf'
};

function sendFile(res, filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const contentType = mimeTypes[ext] || 'application/octet-stream';
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain; charset=UTF-8' });
      res.end('Internal Server Error');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  try {
    let requestPath = decodeURIComponent(req.url.split('?')[0]);
    if (requestPath === '/' || requestPath === '') {
      requestPath = '/index.html';
    }
    const filePath = path.join(publicDir, path.normalize(requestPath));

    // Prevent directory traversal
    if (!filePath.startsWith(publicDir)) {
      res.writeHead(403, { 'Content-Type': 'text/plain; charset=UTF-8' });
      res.end('Forbidden');
      return;
    }

    fs.stat(filePath, (err, stats) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=UTF-8' });
        res.end('Not Found');
        return;
      }
      if (stats.isDirectory()) {
        const indexPath = path.join(filePath, 'index.html');
        fs.access(indexPath, fs.constants.F_OK, (idxErr) => {
          if (idxErr) {
            res.writeHead(403, { 'Content-Type': 'text/plain; charset=UTF-8' });
            res.end('Forbidden');
          } else {
            sendFile(res, indexPath);
          }
        });
      } else {
        sendFile(res, filePath);
      }
    });
  } catch (e) {
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=UTF-8' });
    res.end('Internal Server Error');
  }
});

server.listen(port, () => {
  console.log(`Static server running at http://localhost:${port}`);
});
