import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parse } from '@babel/parser';
import traverseModule from '@babel/traverse';
const traverse = traverseModule.default;
import chalk from 'chalk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const allowedExtensions = ['.js', '.jsx', '.ts', '.tsx'];

// 📌 함수 추출 로직
function extractFunctionsFromFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  // console.log(chalk.gray(`📄 [읽는 중] ${filePath}`));

  let ast;
  try {
    ast = parse(content, {
      sourceType: 'module',
      plugins: ['jsx', 'typescript', 'classProperties'],
    });
  } catch (err) {
    console.log(chalk.red(`❌ [파싱 오류] ${filePath}: ${err.message}`));
    return { error: err.message, functions: [] };
  }

  const functions = [];

  traverse(ast, {
    FunctionDeclaration(path) {
      const name = path.node.id?.name || '익명 함수';
      const loc = path.node.loc;
      const summary = extractDocSummary(path.node);
      functions.push({ name, loc, summary });
    },
    VariableDeclarator(path) {
      const id = path.node.id;
      const init = path.node.init;
      if (
        (init?.type === 'ArrowFunctionExpression' || init?.type === 'FunctionExpression') &&
        id.type === 'Identifier'
      ) {
        const name = id.name;
        const loc = init.loc;
        const summary = extractDocSummary(init);
        functions.push({ name, loc, summary });
      }
    },
    ExportNamedDeclaration(path) {
      const decl = path.node.declaration;
      if (decl?.type === 'VariableDeclaration') {
        decl.declarations.forEach((d) => {
          const id = d.id;
          const init = d.init;
          if (
            (init?.type === 'ArrowFunctionExpression' || init?.type === 'FunctionExpression') &&
            id.type === 'Identifier'
          ) {
            const name = id.name;
            const loc = init.loc;
            const summary = extractDocSummary(init);
            functions.push({ name, loc, summary });
          }
        });
      }
      if (decl?.type === 'FunctionDeclaration') {
        const name = decl.id?.name || '익명 함수';
        const loc = decl.loc;
        const summary = extractDocSummary(decl);
        functions.push({ name, loc, summary });
      }
    },
    ExportDefaultDeclaration(path) {
      const decl = path.node.declaration;
      if (
        decl.type === 'FunctionDeclaration' ||
        decl.type === 'FunctionExpression' ||
        decl.type === 'ArrowFunctionExpression'
      ) {
        const name = decl.id?.name || 'defaultExport';
        const loc = decl.loc;
        const summary = extractDocSummary(decl);
        functions.push({ name, loc, summary });
      }
    },
    ObjectProperty(path) {
      const value = path.node.value;
      if (
        value.type === 'ArrowFunctionExpression' ||
        value.type === 'FunctionExpression'
      ) {
        const name = path.node.key.name || '(anonymous)';
        const loc = value.loc;
        const summary = extractDocSummary(value);
        functions.push({ name, loc, summary });
      }
    },
    ObjectMethod(path) {
      const name = path.node.key.name || '(anonymous)';
      const loc = path.node.loc;
      const summary = extractDocSummary(path.node);
      functions.push({ name, loc, summary });
    },
  });

  // console.log(chalk.magenta(`🧪 [Parsed] ${filePath} ⇒ ${functions.length}개 함수 추출됨`));
  return { error: null, functions };
}

// 📌 JSDoc 요약 추출
function extractDocSummary(node) {
  const comments = node.leadingComments;
  if (!comments || comments.length === 0) return '';
  const doc = comments[comments.length - 1].value.trim();
  const firstLine = doc.split('\n')[0].replace(/[*\/]/g, '').trim();
  return firstLine;
}

// 📌 디렉토리 순회
function walkDir(currentPath, callback) {
  const stat = fs.statSync(currentPath);
  if (stat.isDirectory()) {
    const files = fs.readdirSync(currentPath);
    for (const file of files) {
      const fullPath = path.join(currentPath, file);
      walkDir(fullPath, callback);
    }
  } else if (stat.isFile()) {
    const ext = path.extname(currentPath).toLowerCase();
    if (allowedExtensions.includes(ext)) {
      callback(currentPath);
    }
  }
}

// 📌 결과 출력
function printResults(allFunctions) {
  if (allFunctions.length === 0) {
    console.log(chalk.yellow('⚠️ 함수 요약 결과가 없습니다.'));
    return;
  }

  for (const { file, error, functions } of allFunctions) {
    // console.log(chalk.cyan(`📄 ${path.relative('.', file)}`));
    if (error) {
      console.log(chalk.red(`  ❌ 파싱 실패: ${error}`));
      continue;
    }
    for (const fn of functions) {
      const location = fn.loc ? ` (Line ${fn.loc.start.line})` : '';
      const summary = fn.summary ? ` // ${fn.summary}` : '';
      console.log(`  - function ${chalk.green(fn.name)}${location}${summary}`);
    }
    // console.log();
  }
}

// 📌 메인 실행
function main(targetDir) {
  const allFunctions = [];

  walkDir(targetDir, (filePath) => {
    const { error, functions } = extractFunctionsFromFile(filePath);
    allFunctions.push({ file: filePath, error, functions });
  });

  printResults(allFunctions);
}

// 📌 CLI 실행
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const targetDir = process.argv[2];
  if (!targetDir) {
    // console.log(chalk.red('Usage: node extract_js_functions.js <target_directory>'));
    process.exit(1);
  }

  main(targetDir);
}
