import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
const route=readFileSync('platforms/sites/account-route.ts','utf8');
const statements=[...route.matchAll(/prepare\('([^']+)'\)/g)].map(x=>x[1]);
const query=(prefix)=>statements.find(x=>x.startsWith(prefix));
function db(){const d=new DatabaseSync(':memory:');for(const f of readdirSync('drizzle').filter(x=>x.endsWith('.sql')))d.exec(readFileSync('drizzle/'+f,'utf8'));for(const id of ['alice','bob'])d.prepare(query('INSERT OR IGNORE INTO accounts')).run(id,id+'@example.com');return d}
test('free limit is atomic, edits remain possible, and owners cannot overwrite or delete another profile',()=>{const d=db(),save=d.prepare(query('INSERT INTO profiles'));const put=(id,owner,name=id,limit=2)=>save.run(id,owner,name,'{}',owner,limit,id,owner).changes;assert.equal(put('a','alice'),1);assert.equal(put('b','alice'),1);assert.equal(put('c','alice'),0);assert.equal(put('a','alice','renamed'),1);assert.equal(put('a','bob','attack'),0);d.prepare(query('DELETE FROM profiles')).run('a','bob');assert.equal(d.prepare('SELECT name FROM profiles WHERE id=?').get('a').name,'renamed');assert.equal(put('c','alice','trial',50),1);assert.equal(put('d','alice','expired'),0);assert.equal(put('c','alice','retained'),1);d.close()});
test('trial starts once and session starts stop at Free allowance',()=>{const d=db();const trial=d.prepare(query('UPDATE accounts SET trial_start'));assert.equal(trial.run(1000,'alice').changes,1);assert.equal(trial.run(2000,'alice').changes,0);assert.equal(d.prepare('SELECT trial_start FROM accounts WHERE id=?').get('alice').trial_start,1000);const start=d.prepare(query('UPDATE accounts SET sessions=sessions+1'));for(let i=0;i<10;i++)assert.equal(start.run(Date.now(),'alice',0).changes,1);assert.equal(start.run(Date.now(),'alice',0).changes,0);assert.equal(start.run(Date.now(),'alice',1).changes,1);assert.equal(start.run(Date.now(),'bob',0).changes,1);d.close()});
test('cloud schema and API never store or accept source text',()=>{assert.ok(!readFileSync('db/schema.ts','utf8').includes('source'));assert.ok(!route.includes('b.text'));assert.ok(route.includes("req.headers.get('origin')!==new URL(req.url).origin"));assert.ok(route.includes('a.suspended'));});

