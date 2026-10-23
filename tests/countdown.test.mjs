import {test} from 'node:test';
import assert from 'node:assert/strict';
import {clampCountdown,secondsRemaining} from '../lib/countdown.mjs';
test('countdown is a whole 1–15 seconds, including saved older profiles',()=>{assert.equal(clampCountdown(0),1);assert.equal(clampCountdown(16),15);assert.equal(clampCountdown(7),7);assert.equal(clampCountdown('invalid'),3)});
test('countdown uses a deadline so delayed browser timers do not extend it',()=>{assert.equal(secondsRemaining(15000,0),15);assert.equal(secondsRemaining(15000,4100),11);assert.equal(secondsRemaining(15000,14999),1);assert.equal(secondsRemaining(15000,17000),0)});
