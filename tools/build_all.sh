#!/bin/sh
# Rebuild every student page and the teacher record page from state.json (the teacher artifact's embedded state).
# Usage: sh tools/build_all.sh state.json
set -e
cd "$(dirname "$0")/.."
EP=$(node -e "try{console.log(require('./tools/config.json').endpoint||'')}catch(e){console.log('')}")
node -e "const fs=require('fs');fs.writeFileSync('teacher.html',fs.readFileSync('tools/teacher-template.html','utf8').replace('__ENDPOINT__',process.argv[1]))" "$EP"
node -e "
const fs=require('fs');const m=JSON.parse(fs.readFileSync('tools/pages.json','utf8'));
for(const [file,id] of Object.entries(m)){require('child_process').execFileSync('node',['tools/make_student.js',process.argv[1],id,file],{stdio:'inherit'})}" "$1"
