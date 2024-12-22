set -exo
# rm *.md *.pdf
python generate.py
for file in *.md; do pandoc "$file" -o "${file%.md}.pdf"; done