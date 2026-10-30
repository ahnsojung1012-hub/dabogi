const crypto=require('crypto');
const norm=s=>String(s||'').normalize('NFKC').replace(/[−–]/g,'-').replace(/\s+/g,'').toLowerCase();
const xor=(a,b)=>Buffer.from(a.map((x,i)=>x^b[i]));
const kdf=(salt,i,v)=>crypto.createHash('sha256').update('k|'+salt+'|'+i+'|'+norm(v)).digest();
function lock(salt,alts,obj){
  const master=crypto.randomBytes(32);const shares=alts.map(()=>crypto.randomBytes(32));
  shares[shares.length-1]=shares.slice(0,-1).reduce((acc,s)=>xor(acc,s),master);
  const wraps=alts.map((as,i)=>as.map(a=>xor(shares[i],kdf(salt,i,a)).toString('hex')));
  const iv=crypto.randomBytes(12);const c=crypto.createCipheriv('aes-256-gcm',master,iv);
  const ct=Buffer.concat([c.update(JSON.stringify(obj)),c.final(),c.getAuthTag()]);
  return {wraps,iv:iv.toString('base64'),ct:ct.toString('base64')};
}
function unlock(L,salt,hashesAlts,answers){let m=Buffer.alloc(32);answers.forEach((v,i)=>{const j=hashesAlts[i].map(norm).indexOf(norm(v));m=xor(m,xor(Buffer.from(L.wraps[i][j],'hex'),kdf(salt,i,v)))});
  const raw=Buffer.from(L.ct,'base64');const d=crypto.createDecipheriv('aes-256-gcm',m,Buffer.from(L.iv,'base64'));d.setAuthTag(raw.subarray(-16));return JSON.parse(Buffer.concat([d.update(raw.subarray(0,-16)),d.final()]))}
module.exports={lock,unlock};
