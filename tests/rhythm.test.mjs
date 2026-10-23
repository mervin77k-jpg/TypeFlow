import {test} from 'node:test';
import assert from 'node:assert/strict';
import {nextDelay} from '../lib/rhythm.mjs';
const s={wpm:60,variation:20,boost:2,sentence:600,paragraph:1200,longEvery:10,longPause:2500};
test('WPM, variation and boost produce bounded pacing',()=>{assert.equal(nextDelay(s,'a',1,false,.5).delay,200);assert.equal(nextDelay(s,'a',1,true,.5).delay,100);assert.equal(nextDelay(s,'a',1,false,0).delay,160);assert.equal(nextDelay(s,'a',1,false,1).delay,240)});
test('punctuation and periodic thinking pauses add delay without losing a character',()=>{assert.equal(nextDelay(s,'.',1,false,.5).delay,800);assert.equal(nextDelay(s,'\n',1,false,.5).delay,1400);assert.deepEqual(nextDelay(s,'a',50,false,.5),{delay:2700,thinking:true});assert.deepEqual(nextDelay({...s,longEvery:0},'a',50,false,.5),{delay:200,thinking:false})});
