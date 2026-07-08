#!/usr/bin/env bash
set -e

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add data/home_games.json

if git diff --cached --quiet
then
  echo "No changes to commit."
else
  git commit -m "Update Durham Bulls schedule"
  git pull --rebase origin main
  git push origin main
fi
