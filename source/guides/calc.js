<script>
/* Guide calculators. Inputs use data-field (saved by the page), results go into [data-out]. */
(function(){
function q(s,r){return (r||document).querySelector(s);}
function qa(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function num(k){var e=q('[data-field="'+k+'"]');if(!e)return NaN;var v=String(e.value||'').replace(/[^0-9.,-]/g,'').replace(/,/g,'');return v===''?NaN:parseFloat(v);}
var CUR=document.body.getAttribute('data-cur')||'EUR';
function money(v,c){if(!isFinite(v))return '—';try{return new Intl.NumberFormat('en-US',{style:'currency',currency:c||CUR,maximumFractionDigits:0}).format(v);}catch(e){return Math.round(v)+' '+(c||CUR);}}
function big(v){if(!isFinite(v))return '—';if(Math.abs(v)>=1e9)return (v/1e9).toFixed(2).replace(/\.?0+$/,'')+' B';if(Math.abs(v)>=1e6)return (v/1e6).toFixed(1).replace(/\.0$/,'')+' M';return Math.round(v).toLocaleString('en-US');}
function out(root,k,t){var e=q('[data-out="'+k+'"]',root);if(e)e.textContent=t;}
function verdict(root,cls,t){var e=q('.verdict',root);if(!e)return;e.className='verdict'+(cls?' '+cls:'');e.textContent=t;e.hidden=!t;}
var CALC={
 /* Barcelona: is a flat with a tourist licence worth the premium? */
 hut:function(r){var p=num('bcn_hut_premium'),x=num('bcn_hut_extra'),y=num('bcn_hut_years');if(!isFinite(y))y=2;
  var tot=x*y;out(r,'tot',money(tot));out(r,'gap',money(tot-p));
  if(!isFinite(p)||!isFinite(x))return verdict(r,'','Fill in the premium and the extra profit per year.');
  verdict(r,tot>=p?'ok':'no',tot>=p?'The licence pays back its premium before 2028. Still plan what the flat becomes after.':'The licence does not pay back its premium before 2028. The mid-term model is the smarter play.');},
 /* Barcelona: sum-of-rooms rent cap */
 cap:function(r){var c=num('bcn_cap'),n=num('bcn_rooms'),p=num('bcn_room_rent');
  var sum=n*p,avg=c/n,over=sum-c,pct=over/c*100;out(r,'avg',money(avg));out(r,'sum',money(sum));out(r,'over',isFinite(over)?(over>0?'+':'')+money(over):'—');
  if(!isFinite(sum)||!isFinite(c))return verdict(r,'','Fill in the cap, the number of rooms and your planned rent per room.');
  if(over<=0)verdict(r,'ok','Within the cap. Your rooms can be rented like this.');
  else if(pct<=30)verdict(r,'no','Over the cap by '+pct.toFixed(0)+'%. That is a serious infringement. Lower the room rents.');
  else verdict(r,'no','Over the cap by '+pct.toFixed(0)+'%. That is a very serious infringement. Lower the room rents.');},
 /* Barcelona: monthly numbers of a flat */
 flat:function(r){var inc=['bcn_n_rent','bcn_n_clean','bcn_n_mgmt','bcn_n_extra'].map(num),cost=['bcn_n_mort','bcn_n_util','bcn_n_staff','bcn_n_fees'].map(num),vac=num('bcn_n_vac');
  var I=inc.reduce(function(a,b){return a+(isFinite(b)?b:0);},0),C=cost.reduce(function(a,b){return a+(isFinite(b)?b:0);},0);if(!isFinite(vac))vac=7;var V=I*vac/100,P=I-C-V;
  out(r,'inc',money(I));out(r,'vac',money(V));out(r,'profit',money(P));out(r,'year',money(P*12));
  if(!I)return verdict(r,'','Fill in your income and costs to see your monthly profit.');
  verdict(r,P>0?'ok':'no',P>0?'This flat makes '+money(P)+' a month before tax, after a '+vac+'% vacancy reserve.':'This flat loses money. If it only works above the cap, it is not a deal.');},
 /* Barcelona: profit through a micro-company */
 sl:function(r){var p=num('bcn_sl_profit');if(!isFinite(p)||p<=0){out(r,'ct','—');out(r,'div','—');out(r,'tot','—');out(r,'keep','—');return verdict(r,'','Fill in a yearly profit.');}
  var ct=Math.min(p,50000)*.19+Math.max(p-50000,0)*.21,left=p-ct,b=[[6000,.19],[50000,.21],[200000,.23],[300000,.27],[Infinity,.30]],prev=0,d=0;
  for(var i=0;i<b.length;i++){var top=Math.min(left,b[i][0]);if(top>prev){d+=(top-prev)*b[i][1];prev=top;}}
  out(r,'ct',money(ct));out(r,'div',money(d));out(r,'tot',money(ct+d));out(r,'keep',money(left));
  verdict(r,'ok','If you reinvest, you only pay '+money(ct)+' and keep '+money(left)+' in the company for the next flat.');},
 /* Bali: price per remaining lease year, two villas */
 lease:function(r){var a=num('bali_l_a_price'),ay=num('bali_l_a_years'),b=num('bali_l_b_price'),by=num('bali_l_b_years');var pa=a/ay,pb=b/by;
  out(r,'a',isFinite(pa)?'IDR '+big(pa):'—');out(r,'b',isFinite(pb)?'IDR '+big(pb):'—');
  if(!isFinite(pa)||!isFinite(pb))return verdict(r,'','Fill in the price and years left for both villas.');
  var cheaper=pa<pb?'Villa A':'Villa B',diff=Math.abs(pa-pb)/Math.max(pa,pb)*100;verdict(r,'ok',cheaper+' is '+diff.toFixed(0)+'% cheaper per remaining year.');},
 /* Bali: revenue check against the island average */
 rev:function(r){var adr=num('bali_r_adr'),occ=num('bali_r_occ');var y=adr*365*occ/100,tax=y*.1;
  out(r,'year',money(y,'USD'));out(r,'tax',money(tax,'USD'));out(r,'net',money(y-tax,'USD'));
  if(!isFinite(y))return verdict(r,'','Fill in your nightly rate and occupancy.');
  var avg=17700,diff=(y-avg)/avg*100;verdict(r,y>=avg?'ok':'no',y>=avg?'That is '+diff.toFixed(0)+'% above the Bali average listing (about USD 17,700 a year).':'That is '+Math.abs(diff).toFixed(0)+'% below the Bali average listing. Work on location, design or rate.');}
};
function run(){qa('[data-calc]').forEach(function(r){var f=CALC[r.getAttribute('data-calc')];if(f)try{f(r);}catch(e){}});
 qa('.sc-card').forEach(function(c){var n=qa('select',c).length;qa('[data-sc-total]',c).forEach(function(t){var k=t.getAttribute('data-sc-total'),s=0,m=0;qa('select[data-col="'+k+'"]',c).forEach(function(x){var v=parseInt(x.value,10);if(v){s+=v;m++;}});t.textContent=m?s:'—';t.parentNode.classList.remove('best');});
  var best=null,bv=0;qa('[data-sc-total]',c).forEach(function(t){var v=parseInt(t.textContent,10);if(v>bv){bv=v;best=t;}});if(best)best.parentNode.classList.add('best');});
 qa('.zone-pick').forEach(function(z){var v=(q('select',z)||{}).value;qa('[data-zone]',z).forEach(function(e){e.hidden=e.getAttribute('data-zone')!==v;});});}
document.addEventListener('input',run);document.addEventListener('change',run);
window.addEventListener('load',function(){setTimeout(run,60);});
})();
</script>
