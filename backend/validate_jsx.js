/**
 * validate_jsx.js -- Validador de sintaxis JSX/TypeScript
 * ========================================================
 * Lee el codigo React desde stdin, verifica sintaxis con @babel/parser.
 * Exit 0 = valido. Exit 1 = error de sintaxis.
 *
 * Usado desde Python en step3_generate._validate_react_syntax()
 */
import parser from '@babel/parser';
let code = '';

process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { code += chunk; });
process.stdin.on('end', () => {
  try {
    parser.parse(code, {
      sourceType: 'module',
      plugins: ['typescript', 'jsx'],
      errorRecovery: false,
    });
    process.exit(0);
  } catch (err) {
    process.stderr.write('SyntaxError: ' + err.message + '\n');
    process.exit(1);
  }
});
