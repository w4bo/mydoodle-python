set -exo
for file in *.md; do pandoc "$file" -o "${file%.md}.pdf"; done