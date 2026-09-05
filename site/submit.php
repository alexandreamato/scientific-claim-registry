<?php
/* SCR — minimal submission inbox (Layer 1 "front door").
 * Receives a proposed scientific QUESTION (or claim) and appends it to a queue that the
 * local Python loop drains, validates, dedups, classifies (LLM) and versions.
 * It is a DUMB inbox: no validation of truth, no DB writes to the registry.
 *
 * Queue lives OUTSIDE public_html (one level up) so `rsync --delete` never wipes it:
 *   /home/alexandre/web/scientificclaims.org/submissions.jsonl
 * Drain locally:  scp alexandre@91.98.19.157:web/scientificclaims.org/submissions.jsonl ./
 */
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: https://scientificclaims.org');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['ok'=>false,'error'=>'POST only']); exit; }

// accept JSON body or form-encoded
$raw = file_get_contents('php://input');
$in = json_decode($raw, true);
if (!is_array($in)) { $in = $_POST; }

$honey = trim($in['website'] ?? '');           // honeypot: bots fill it, humans don't
if ($honey !== '') { echo json_encode(['ok'=>true]); exit; }   // silently drop

$question = trim($in['question'] ?? '');
$kind     = (($in['kind'] ?? 'question') === 'claim') ? 'claim' : 'question';
$domain   = preg_replace('/[^A-Za-z]/', '', $in['domain'] ?? 'LIP');
$email    = trim($in['email'] ?? '');
$notes    = trim($in['notes'] ?? '');

if (strlen($question) < 10 || strlen($question) > 400) {
  http_response_code(422); echo json_encode(['ok'=>false,'error'=>'question must be 10–400 chars']); exit;
}

$rec = [
  'ts'       => gmdate('c'),
  'kind'     => $kind,
  'domain'   => strtoupper(substr($domain ?: 'LIP', 0, 4)),
  'question' => $question,
  'email'    => substr($email, 0, 160),
  'notes'    => substr($notes, 0, 1000),
  'ip'       => $_SERVER['REMOTE_ADDR'] ?? '',
  'status'   => 'pending',
];

/* Queue lives inside public_html in a protected dir, but is EXCLUDED from `rsync --delete`
 * (add --exclude='.inbox' to the deploy) so deploys never wipe it. Drain locally with:
 *   scp alexandre@91.98.19.157:web/scientificclaims.org/public_html/.inbox/submissions.jsonl . */
$dir = __DIR__ . '/.inbox';
if (!is_dir($dir)) {
  @mkdir($dir, 0750, true);
  @file_put_contents($dir . '/.htaccess', "Require all denied\nDeny from all\n");   // Apache
  @file_put_contents($dir . '/index.html', '');                                      // no listing
}
$queue = $dir . '/submissions.jsonl';
$fh = @fopen($queue, 'a');
if ($fh === false) { http_response_code(500); echo json_encode(['ok'=>false,'error'=>'queue unavailable']); exit; }
fwrite($fh, json_encode($rec, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
fclose($fh);

echo json_encode(['ok'=>true,'message'=>'Proposal queued for review. It will be processed by the registry pipeline.']);
