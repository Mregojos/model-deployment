# sh g* 
# sh git-push.sh

# Cleanup environment variables
rm -f ./.env.*
rm -f ./*/.env.*
rm -f ./*/*/.env.*
rm -f ./*/*/*/.env.*
rm -f ./*/*/*/*/.env.*
echo "Cleanup Successful"

git add .
# git config --global user.email "<EMAIL_ADDRESS>"
# git config --global user.email ""
git config --global user.name "Matt"
git commit -m "Add and modify files"
git push

# username
# password/token

