export function nextDelay(settings,character,index,boost,random=Math.random()){
 const base=60000/(settings.wpm*5)*(1+(random*2-1)*settings.variation/100)/(boost?settings.boost:1);
 const punctuation=character==='\n'?settings.paragraph:/[.!?]/.test(character)?settings.sentence:0;
 const thinking=settings.longEvery>0&&index%(settings.longEvery*5)===0;
 return {delay:base+punctuation+(thinking?settings.longPause:0),thinking};
}
