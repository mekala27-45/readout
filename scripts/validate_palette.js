// WCAG relative-luminance checks for both semantic palettes.
// The mark threshold is 3:1; normal text requires 4.5:1.
const fs = require("node:fs");
const path = require("node:path");
const {spawnSync}=require("node:child_process");
const palettes = {
  dark: {surface:"#0B0F14",panel:"#10171F",text:"#FAFAFA",muted:"#96A3B4",control:"#94A3B8",treatment:"#0891B2",accent:"#50D5EF",positive:"#60BDA5",warn:"#E9B567",danger:"#F28C8C"},
  light: {surface:"#FAFAFA",panel:"#FFFFFF",text:"#111C29",muted:"#58687D",control:"#475569",treatment:"#0891B2",accent:"#08758E",positive:"#237761",warn:"#925B14",danger:"#B53D43"}
};
function luminance(hex){const rgb=hex.slice(1).match(/../g).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2];}
function contrast(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
const checks=[];
for(const [mode,p] of Object.entries(palettes))for(const surface of ["surface","panel"]){for(const key of ["text","muted","accent","positive","warn","danger"]){const ratio=contrast(p[key],p[surface]);checks.push({mode,foreground:key,background:surface,ratio:Number(ratio.toFixed(3)),threshold:4.5,pass:ratio>=4.5});}for(const key of ["control","treatment"]){const ratio=contrast(p[key],p[surface]);checks.push({mode,foreground:key,background:surface,role:"graphical mark",ratio:Number(ratio.toFixed(3)),threshold:3,pass:ratio>=3});}}
const buttonRatio=contrast("#061820","#0891B2");checks.push({mode:"both",foreground:"#061820",background:"#0891B2",role:"button label",ratio:Number(buttonRatio.toFixed(3)),threshold:4.5,pass:buttonRatio>=4.5});
const upstream=[];
for(const [mode,p] of Object.entries(palettes))for(const surface of ["surface","panel"]){const validation=spawnSync(process.execPath,[path.join(__dirname,"palette_core.cjs"),`${p.control},${p.treatment},#D97706`,"--mode",mode,"--surface",p[surface],"--pairs","all","--json"],{encoding:"utf8"});if(!validation.stdout)throw new Error(validation.stderr||"Upstream palette validator returned no result");upstream.push({...JSON.parse(validation.stdout),surface_role:surface,raw_exit_code:validation.status});}
const result={standard:"WCAG 2.2 relative luminance plus original cityflow OKLab and CVD validator",source:{repository:"cityflow",commit:"2163b362d75458e8485f3f78fdec85b7322e6fd7",ported_file:"scripts/palette_core.cjs"},method:"Control and treatment hues are fixed by the requested design. Treatment uses the accent token for body text. Status always includes an icon and label. Dashed lines, hollow markers, direct labels and table views redundantly encode series. There is no diverging ramp.",palettes,checks,upstream,known_mandated_conflict:"The requested dark control #94A3B8 and treatment #0891B2 have worst CVD delta E 7.7 under protanopia, below the inherited floor of 8. The failure is retained; hues are not silently changed. The third series #D97706 passes all pairwise checks in both modes.",pass:checks.every(x=>x.pass)&&upstream.every(x=>x.failures===0)};
const failures=upstream.flatMap(x=>x.rows.filter(r=>!r.pass).map(r=>({mode:x.mode,surface:x.surface,...r})));
const source=fs.readFileSync(path.resolve(__dirname,"../web/src/components/charts.tsx"),"utf8");
const redundant_encodings={dashed_lines:source.includes("strokeDasharray"),hollow_markers:source.includes('fill: "var(--panel)"')||source.includes('fill:"var(--panel)"'),named_legend:source.includes("s.label"),table_toggle:source.includes("setTable(true)")&&source.includes("DataTable")};
const exact_exception=failures.length===2&&failures.every(r=>r.mode==="dark"&&["#0B0F14","#10171F"].includes(r.surface)&&r.subject==="#94A3B8 to #0891B2"&&r.check==="worst colour vision deficiency delta E"&&r.value===7.7&&r.floor===8&&r.extra==="protanopia");
const allow=process.argv.includes("--allow-mandated-palette-exception");
result.redundant_encodings=redundant_encodings;
result.exception_policy="Only the exact fixed dark control/treatment protanopia separation result is eligible, on both declared surfaces, with line pattern, hollow mark, labels and table encodings present. Any other failure rejects validation.";
result.known_exception_verified=exact_exception&&checks.every(r=>r.pass)&&Object.values(redundant_encodings).every(Boolean);
result.validation_accepted=result.pass||(allow&&result.known_exception_verified);
result.exception_explicitly_allowed=allow;
const out=path.resolve(__dirname,"../artifacts/palette-validation.json");fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(result,null,2)+"\n");console.log(`${result.pass?"PASS":result.validation_accepted?"ACCEPTED WITH ONE DOCUMENTED MANDATED-PALETTE EXCEPTION":"FAIL"}: ${checks.length} text/contrast checks and ${upstream.reduce((n,v)=>n+v.rows.length,0)} original palette checks across both modes. ${path.relative(process.cwd(),out)}`);if(!result.pass){console.error(JSON.stringify({contrast:checks.filter(x=>!x.pass),separation:upstream.flatMap(x=>x.rows.filter(r=>!r.pass).map(r=>({mode:x.mode,surface:x.surface,...r})))},null,2));if(!result.validation_accepted)process.exitCode=1;}
