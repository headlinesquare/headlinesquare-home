cd ..
hugo
call wrangler pages deploy public --project-name headlinesquare

cd public
git add .
git commit -m "Update site content"
git push

pause


