# Шпаргалка markdown

## Выделение текста

Вы можете выделять текст в markdown с помощью символов `_` или `*`. Например:

Пример _курсива_ и **жирного** текста.

## Заголовки

Заголовки можно создавать с помощью символа `#`. Чем больше `#`, тем меньше заголовок. Например:

# Заголовок первого уровня
## Заголовок второго уровня
### Заголовок третьего уровня

## Выделение кода

Чтобы выделить текст как код, поместите его в тройные кавычки `````. 

```
mkdir my_project
cd my_project
git init
```

#Commands used by setting your git profile:
git config --global user.name 
git config --global user.email

##Create and setup your git repo:
cd C:\your_project
git init(delete your local repo: rm -rf .git)
git status
git add
touch (ex. filename.txt)
git add . (add all files)
git commit -m example text (comment)
git log (commits history)

###Generate shh in git for github:
ssh-keygen -t ed25519 -C "example_email@example.com"
clip < ~/.ssh/id_ed25519.pub

###Sync local and cloud repositories:
git remote add origin SSH LINK FROM LOCLAL REPO
git remote add origin
git remote -v
git push

https://github.com/Derubs/defrepo.git