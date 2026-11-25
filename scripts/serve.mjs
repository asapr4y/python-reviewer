import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
const root = resolve(process.env.SERVE_DIR || 'public');
const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.png':'image/png','.pdf':'application/pdf','.svg':'image/svg+xml'};
createServer(async(req,res)=>{try{const path=resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(path!==root&&!path.startsWith(root+sep)){res.writeHead(403).end();return;}const target=(await stat(path)).isDirectory()?resolve(path,'index.html'):path;res.writeHead(200,{'Content-Type':types[extname(target)]||'application/octet-stream','Cache-Control':'no-cache'});res.end(await readFile(target));}catch{res.writeHead(404).end('Not found');}}).listen(Number(process.env.PORT||4173),'0.0.0.0',()=>console.log('Python reviewer running at http://localhost:'+ (process.env.PORT||4173)));
