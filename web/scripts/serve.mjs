import {createServer} from "node:http";
import {readFile,stat} from "node:fs/promises";
import path from "node:path";
const root=path.resolve("out");
const base=(process.env.NEXT_PUBLIC_BASE_PATH??"").replace(/\/$/,"");
const port=Number(process.env.PORT??3016);
const mime={".html":"text/html; charset=utf-8",".js":"text/javascript",".css":"text/css",".json":"application/json",".svg":"image/svg+xml",".png":"image/png",".md":"text/markdown; charset=utf-8",".woff2":"font/woff2",".txt":"text/plain; charset=utf-8"};
createServer(async(req,res)=>{try{let pathname=decodeURIComponent(new URL(req.url,"http://localhost").pathname);if(base&&pathname.startsWith(`${base}/`))pathname=pathname.slice(base.length);else if(base&&pathname===base)pathname="/";let target=path.resolve(root,`.${pathname}`);if(target!==root&&!target.startsWith(root+path.sep))throw new Error("Invalid path");if((await stat(target)).isDirectory())target=path.join(target,"index.html");const content=await readFile(target);res.writeHead(200,{"Content-Type":mime[path.extname(target)]??"application/octet-stream","X-Content-Type-Options":"nosniff"});res.end(content);}catch{res.writeHead(404,{"Content-Type":"text/plain"});res.end("Page not found");}}).listen(port,"127.0.0.1",()=>process.stdout.write(`readout static preview: http://localhost:${port}${base}/\n`));
