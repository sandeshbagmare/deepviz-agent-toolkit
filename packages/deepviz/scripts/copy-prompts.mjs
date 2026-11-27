import {copyFile, mkdir} from 'node:fs/promises';

const source=new URL('../../../prompts/v1/',import.meta.url);
const destination=new URL('../dist/prompts/v1/',import.meta.url);
await mkdir(destination,{recursive:true});
for(const filename of ['README.md','system.md','request.md']) {
  await copyFile(new URL(filename,source),new URL(filename,destination));
}
