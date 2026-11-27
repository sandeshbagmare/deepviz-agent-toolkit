import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const directory=path.resolve(process.argv[2]);
const browser=await chromium.launch({headless:true});
try{
  for(const format of ['svg','html']){
    const page=await browser.newPage();page.setDefaultTimeout(5000);page.setDefaultNavigationTimeout(5000);
    page.on('console',message=>console.log(format,'console',message.type(),message.text()));
    page.on('pageerror',error=>console.log(format,'pageerror',error.message));
    const start=performance.now();
    try{
      console.log(format,'goto-start');
      await page.goto(pathToFileURL(path.join(directory,`line-positive-240.${format}`)).href,{waitUntil:'load'});
      console.log(format,'goto-done',performance.now()-start);
      console.log(format,'DOM',await page.evaluate(()=>({contentType:document.contentType,svg:!!document.querySelector('svg[role="img"]'),
        node:typeof Node,ready:globalThis.deepvizReady??null,fonts:document.fonts.status,
        pointIterable:typeof document.querySelector('polyline').points[Symbol.iterator]})));
      await page.screenshot({path:path.join(directory,`navigation-control-viewport-${format}.png`),fullPage:false,timeout:5000});
      console.log(format,'screenshot-done',performance.now()-start);
    }catch(error){console.log(format,'ERROR',error.stack,performance.now()-start);}
    await page.close();
  }
}finally{await browser.close();}
