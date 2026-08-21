import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];
const required = ['.cursor-plugin/plugin.json','README.md','LICENSE','mcp.json','hooks/hooks.json'];
for (const f of required) if (!fs.existsSync(path.join(root,f))) errors.push(`missing ${f}`);

function readJson(f){
  try { return JSON.parse(fs.readFileSync(path.join(root,f),'utf8')); }
  catch(e){ errors.push(`invalid JSON ${f}: ${e.message}`); return {}; }
}

function isSafeRel(p){
  if (typeof p !== 'string' || p.trim() === '') return false;
  const norm = p.replace(/\\/g,'/');
  if (path.isAbsolute(p) || path.win32.isAbsolute(p)) return false;
  if (norm.startsWith('/') || /^[a-zA-Z]:/.test(norm)) return false;
  const parts = norm.split('/').filter(Boolean);
  return !parts.includes('..');
}

const plugin = readJson('.cursor-plugin/plugin.json');
if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(plugin.name ?? '')) errors.push('plugin name must be lowercase kebab-case');
if (plugin.displayName !== 'DevOS') errors.push('displayName must be DevOS');
for (const field of ['name','displayName','version','description','author','license']) if (!(field in plugin)) errors.push(`manifest missing ${field}`);

const declared = [
  ['skills', plugin.skills],
  ['rules', plugin.rules],
  ['agents', plugin.agents],
  ['commands', plugin.commands],
  ['hooks', plugin.hooks],
  ['mcpServers', plugin.mcpServers],
];
for (const [field, p] of declared) {
  if (!p) { errors.push(`manifest missing path ${field}`); continue; }
  if (!isSafeRel(p)) errors.push(`path must be relative and inside the plugin: ${field}=${p}`);
  else if (!fs.existsSync(path.join(root, p))) errors.push(`declared path missing: ${field}=${p}`);
}

for (const [field, dir] of [['skills','skills'],['rules','rules'],['agents','agents'],['commands','commands']]) {
  if (!fs.existsSync(path.join(root,dir))) errors.push(`missing ${dir}/`);
}

function walk(dir){
  const abs=path.join(root,dir); if (!fs.existsSync(abs)) return [];
  return fs.readdirSync(abs,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
}

function frontmatter(text){
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  return m ? m[1] : '';
}

function fmField(fm, key){
  const m = fm.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'));
  return m ? m[1].trim() : '';
}

for (const f of walk('skills').filter(x=>x.endsWith('SKILL.md'))) {
  const t=fs.readFileSync(path.join(root,f),'utf8');
  const fm=frontmatter(t);
  if (!fm) errors.push(`missing frontmatter ${f}`);
  else {
    if (!fmField(fm,'name')) errors.push(`missing skill name ${f}`);
    if (!fmField(fm,'description')) errors.push(`missing skill description ${f}`);
  }
}
for (const f of walk('rules').filter(x=>x.endsWith('.mdc'))) {
  const t=fs.readFileSync(path.join(root,f),'utf8');
  const fm=frontmatter(t);
  if (!fm) errors.push(`missing frontmatter ${f}`);
  else {
    if (!fmField(fm,'description')) errors.push(`missing rule description ${f}`);
    if (!/alwaysApply:\s*(true|false)/.test(fm)) errors.push(`missing alwaysApply ${f}`);
  }
}
for (const dir of ['agents','commands']) {
  for (const f of walk(dir).filter(x=>/\.md$/.test(x))) {
    const t=fs.readFileSync(path.join(root,f),'utf8');
    const fm=frontmatter(t);
    if (!fm) errors.push(`missing frontmatter ${f}`);
    else {
      if (!fmField(fm,'name')) errors.push(`missing name ${f}`);
      if (!fmField(fm,'description')) errors.push(`missing description ${f}`);
    }
  }
}

const hook = readJson('hooks/hooks.json');
const mcp = readJson('mcp.json');
if (!hook.hooks) errors.push('hooks.json missing hooks object');
if (!mcp.mcpServers) errors.push('mcp.json missing mcpServers');
if (!fs.existsSync(path.join(root,'hooks/guard_prompt.py'))) errors.push('missing hooks/guard_prompt.py');
if (!fs.existsSync(path.join(root,'mcp/project_intel.py'))) errors.push('missing mcp/project_intel.py');

if (errors.length){ console.error('DevOS validation FAILED'); for(const e of errors) console.error(`- ${e}`); process.exit(1); }
console.log('DevOS validation PASSED');
console.log(`name=${plugin.name} displayName=${plugin.displayName} version=${plugin.version}`);
console.log(`skills=${walk('skills').filter(x=>x.endsWith('SKILL.md')).length}`);
console.log(`rules=${walk('rules').length}`);
console.log(`agents=${walk('agents').filter(x=>x.endsWith('.md')).length}`);
console.log(`commands=${walk('commands').filter(x=>x.endsWith('.md')).length}`);
