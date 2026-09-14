import fs from 'node:fs';

const path = process.argv[2] ?? 'public/research-data.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));
const errors = [];

if (data.status?.fixed_prime !== 147457) errors.push('fixed_prime must be 147457');
if (data.status?.fixed_degree !== 87) errors.push('fixed_degree must be 87');
if (data.status?.recovery_divisor !== 10) errors.push('recovery_divisor must be 10');
if (data.soundness_history?.verification_threshold !== 2) errors.push('graph verification threshold must be 2');

const verified = new Map((data.candidates?.verified ?? []).map((item) => [item.job_id, item]));
let previous = 1;
for (const [index, point] of (data.soundness_history?.points ?? []).entries()) {
  if (!(point.soundness > 0 && point.soundness < previous)) errors.push(`history point ${index} is not a strict improvement`);
  previous = point.soundness;
  if (new Set(point.verifier_ids ?? []).size !== 2) errors.push(`history point ${index} lacks two distinct verifiers`);
  const candidate = verified.get(point.job_id);
  if (!candidate?.double_verified) errors.push(`history point ${index} is not a doubly verified candidate`);
  if (candidate?.claimed_soundness !== point.soundness) errors.push(`history point ${index} changes claimed soundness`);
  if (candidate?.theorem_sha256 !== point.theorem_sha256) errors.push(`history point ${index} changes theorem hash`);
  if ((candidate?.audits ?? []).length !== 2) errors.push(`history point ${index} lacks two audits`);
  for (const audit of candidate?.audits ?? []) {
    if (audit.verdict !== 'accept') errors.push(`history point ${index} includes a non-accept audit`);
    if (audit.verified_claim_sha256 !== point.theorem_sha256) errors.push(`history point ${index} audit checked another claim`);
    if (audit.verified_soundness !== point.soundness) errors.push(`history point ${index} audit checked another soundness`);
  }
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log(JSON.stringify({ passed: true, promoted_points: data.soundness_history?.points?.length ?? 0 }));
