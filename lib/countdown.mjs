export function clampCountdown(value){const n=Number(value);return Number.isFinite(n)?Math.min(15,Math.max(1,Math.round(n))):3;}
export function secondsRemaining(deadline,now=Date.now()){return Math.max(0,Math.ceil((deadline-now)/1000));}
